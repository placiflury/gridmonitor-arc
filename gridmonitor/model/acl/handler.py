"""
Dealing with ACL for siteadmin 
"""
import gridmonitor.model.acl.schema as schema
import logging

log = logging.getLogger(__name__)

class AdminsPool():
    """ Pool of Administrators """
    
    def __init__(self, session):
        self.session = session

    def add_admin(self, shib_unique_id,
                shib_surname, 
                shib_given_name, 
                shib_email,
                shib_affiliation = None,
                shib_homeorg = None):
        """ Adds an Administrator to the ACL. If the administrator exists
            already, he/she will be updated.
            Params: shib_unique_id -- a  unique ID to identify administrator
                    shib_surname    -- surname of administrator
                    shib_given_name -- given name of administrator
                    shib_email  -- email of administrator
                    shib_affiliation -- affiliation (optional)
                    shib_homeorg    -- home organization (institution) (optional)
        """
        admin = self.session.query(schema.Admin).filter_by(shib_unique_id=shib_unique_id).first()
        if admin:
            if (admin.shib_given_name != shib_given_name) or \
                 (admin.shib_surname != shib_surname) or \
                 (admin.shib_email != shib_email) or \
                 (admin.shib_affiliation != shib_affiliation) or \
                 (admin.shib_homeorg != shib_homeorg):
                log.info("Updating records of '%s, %s'" % (shib_surname, shib_given_name))
                admin.shib_given_name = shib_given_name
                admin.shib_surname = shib_surname
                admin.shib_email = shib_email
                admin.shib_affiliation = shib_affiliation
                admin.shib_homeorg = shib_homeorg
        else:
            log.info("Adding admin '%s, %s'" % (shib_surname, shib_given_name))
            admin = schema.Admin(shib_unique_id, 
                shib_surname, shib_given_name, shib_email,
                shib_affiliation, shib_homeorg)
            self.session.add(admin)
        
        self.session.commit() 
    
    def update_admin(self, shib_unique_id,
                shib_surname, 
                shib_given_name, 
                shib_email,
                shib_affiliation = None,
                shib_homeorg = None):
        """ Updates an administrator of the ACL. If the administrator does notexists
            already, he/she will be created.
            Params: shib_unique_id -- a  unique ID to identify administrator
                    shib_surname    -- surname of administrator
                    shib_given_name -- given name of administrator
                    shib_email  -- email of administrator
                    shib_affiliation -- affiliation (optional)
                    shib_homeorg    -- home organization (institution) (optional)
        """
        self.add_admin(shib_unique_id, 
                shib_surname, 
                shib_given_name, 
                shib_email,
                shib_affiliation = None,
                shib_homeorg = None)

    def remove_admin(self, shib_unique_id):
        """ Remove administrator for administrator pool. 
            Params: shib_unique_id -- unique ID of admnistrator
        """
        admin = self.session.query(schema.Admin).filter_by(shib_unique_id = shib_unique_id).first()
        if admin:
            log.info("Removing  admin '%s, %s'" % \
                (admin.shib_surname, admin.shib_given_name))
            self.session.delete(admin)
            self.session.commit()
    

    def list_admins(self):
        """ Lists all administrators that are currently in the 
            administrator pool.
            returns:   list of admin objects
        """
        return self.session.query(schema.Admin).all()

    def list_admin_sites(self, shib_unique_id):
        """ List all sites where admin has administrator rights.
            Params: shib_unique_id -- unique id of admin
            Return: list of site objects """
        
        admin = self.session.query(schema.Admin).filter_by(shib_unique_id = shib_unique_id).first()
        if admin:
            return admin.sites
        log.warn("Admin '%s' does not exist, no sites to list" % (shib_unique_id))
        return []
    
    def list_admin_services(self, shib_unique_id):
        """ List all services where admin has administrator rights.
            Params: shib_unique_id -- unique id of admin
            Return: list of service objects """
        
        admin = self.session.query(schema.Admin).filter_by(shib_unique_id = shib_unique_id).first()
        if admin:
            return admin.services
        log.warn("Admin '%s' does not exist, no services to list" % (shib_unique_id))
        return []


class SitesPool():
    
    def __init__(self, session):
        self.session = session

    def add_site(self, name, alias=None):
        """ Adding a site to pool of sites used for defining ACL
            Params: name -- name of the site 
                    alias -- some alias for site (optional)
            """
        site = self.session.query(schema.Site).filter_by(name=name).first()
        if site:
            if site.alias != alias:
                log.info("Udating site '%s'" % name)
                site.alias = alias
                self.session.commit()
        else:
            log.info("Adding site '%s'" % name)
            site = schema.Site(name,alias)
            self.session.add(site)
            self.session.commit()

    def add_admin(self, site_name, shib_unique_id):
        """ Adding an administrator to a site.
            Params: site_name -- name of the site 
                    shib_unique_id -- Unique ID of administrator
        """
        site = self.session.query(schema.Site).filter_by(name = site_name).first()
        admin = self.session.query(schema.Admin).filter_by(shib_unique_id = shib_unique_id).first()
    
        if not site:
            log.warn( "WARNING: site '%s' does not exist. Can't add admin '%s' to it" % \
                (site_name, shib_unique_id))
            return
        
        if not admin:
            log.warn("WARNING: admin '%s' does not exist. Can't add admin to site '%s'" % \
                (shib_unique_id, site_name))
            return
        
        if not admin in site.admins:
            log.info( "Adding '%s %s' to admins of site '%s'" % \
                (admin.shib_surname, admin.shib_given_name, site_name))
            site.admins.append(admin)
            self.session.commit()

    def remove_site(self, name):
        """ Removing a site from the ACL pool of sites.
            Parmas: name -- name of the site  """

        site = self.session.query(schema.Site).filter_by(name=name).first()
        if site:
            log.info("Removing site '%s'" % name)
            self.session.delete(site)
            self.session.commit()


    def remove_admin(self, site_name, shib_unique_id):
        """ Removing an admin from a site. 
            Params:  site_name -- name of the site
                    shib_unique_id -- unique ID of the administrator to remove.
        """

        site = self.session.query(schema.Site).filter_by(name = site_name).first()
        admin = self.session.query(schema.Admin).filter_by(shib_unique_id = shib_unique_id).first()

        if not site or not admin:
            log.info("Either site '%s' or admin with id '%s' did not exist. Nothing to remove" % \
                    (site_name, shib_unique_id))
            return
        
        log.info("Removing admin '%s %s' from  site '%s'" % \
            (admin.shib_surname, admin.shib_given_name, site_name))
        site.admins.remove(admin)
        self.session.commit()

    def list_sites(self):
        """ Listing of all sites in ACL pool. 
            Return: list of site objects 
        """
        return self.session.query(schema.Site).filter_by(name = site_name).all()
        
    
    def list_services(self, site_name):
        """ Listing of services of a site.
            Params: site_name -- name of the site
            Returns: list of services object
        """
        
        site = self.session.query(schema.Site).filter_by(name = site_name).first()
        if not site:
            log.info("Site '%s' does not exist" % site_name)
            return None
        return site.services


    def list_admins(self, site_name):
        """ Listing of administrators of a site.
            Params: site_name -- name of the site
            Returns: list of admins object
        """
        site = self.session.query(schema.Site).filter_by(name = site_name).first()
        if not site:
            log.info("Site '%s' does not exist" % site_name)
            return None
        return site.admins 



class ServicesPool():
    
    VALID_TYPES = ['cluster','other']
    
    def __init__(self, session):
        self.session = session

    def add_service(self, name, site_name, type, hostname, alias=None):
        """ Adding a service to the ACL pool. 
            Params: name -- name of the service 
                    site_name -- name of the site    
                    type    -- service type (currently either 'cluster' or 'other')
                    hostname -- host name (FQDN) where service runs
                    alias   -- alias ofr service (optional)
        """
        if type not in ServicesPool.VALID_TYPES:
            log.warn("Invalid type '%s' for service '%s' of site '%s'" % \
                (type, name, site_name))

        # if site service belongs to does not exist -> create it
        site = self.session.query(schema.Site).filter_by(name=site_name).first()
        if not site:
            log.info("Adding site '%s'" % name)
            site = schema.Site(name)
            self.session.add(site)

        service = self.session.query(schema.Service).filter_by(name=name, hostname=hostname).first()
        if service:
            log.info("Service '%s' ('%s') exists already" % (name, hostname))
            if (service.type != type or \
                 service.hostname != hostname or \
                 service.alias != alias):
                service.type = type
                service.hostname = hostname
                service.alias = alias
        else:
            log.info("Adding service '%s' (%s)" % (name, hostname))
            service = schema.Service(name, site_name, type, hostname, alias)
            self.session.add(service)

        self.session.commit()
        
    def add_admin(self, name, hostname,  shib_unique_id):
        """ Adding an administrator to a service. 
            Params: name -- name of the service
                    hostname -- hostname (FQDN) of the service
                    shib_unique_id -- unique ID of admin
        """
        
        service = self.session.query(schema.Service).filter_by(name=name, hostname=hostname).first()
        admin = self.session.query(schema.Admin).filter_by(shib_unique_id=shib_unique_id).first()
    
        if not service:
            log.warn("Service '%s' does not exist. Can't add admin '%s' to it" % \
                (name, shib_unique_id))
            return
                
        if not admin:
            log.warn("WARNING: admin '%s' does not exist. Can't add admin to service '%s'" % \
                (shib_unique_id, name))
            return
        if not admin in service.admins:
            log.info("Adding '%s %s' to admins of service '%s' (%s)" % \
                (admin.shib_surname, admin.shib_given_name, name, hostname))
            service.admins.append(admin)
            self.session.commit()

    def remove_service(self, name, hostname):
        """ Removing a service from ACL service pool.   
            Params: name -- name of service
                    hostname -- hostname (FQDN) of host where service runs
        """
        service = self.session.query(schema.Service).filter_by(name=name, hostname=hostname).first()
        if service:
            log("Removing service '%s' (%s)" % (name, hostname))
            self.session.delete(service)
            self.session.commit()


    def remove_admin(self, name, hostname, shib_unique_id):
        """ Removing an admin from a service.   
            Params: name -- name of service
                    hostname -- hostname (FQDN) of host where service runs
                    shib_unique_id -- unique ID of the admin
        """
        service = self.session.query(schema.Service).filter_by(name=name, hostname=hostname).first()
        admin = self.session.query(schema.Admin).filter_by(shib_unique_id = shib_unique_id).first()

        if not service or not admin:
            log.info("Nothing to remove, since either service '%s/%s' or admin '%s' is missing" %\
                    (name, hostname, shib_unique_id))
            return
        
            log.info("Removing admin '%s %s' from  service '%s' (%s)" % \
            (admin.shib_surname, admin.shib_given_name, name, hostname))
        service.admins.remove(admin)
        self.session.commit()
    
    def list_services(self):
        """ List all services in ACL service pool
            Returns list of services objects """
        return self.session.query(schema.Service).all()


    def list_admins(self,name,hostname):
        """ List all admins of service.
            Params: name -- name of service
                    hostname -- hostname (FQDN) where service runs
            Returns: list of admin objects
        """
        
        service = self.session.query(schema.Service).filter_by(name=name, hostname=hostname).first()
        if not service:
            log.warn("Service '%s/%s' does not exist; no admins to return" % (name,hostname))
            return None
        return service.admins
