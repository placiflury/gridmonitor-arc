# -*- coding: utf-8 -*-
"""
Interface for ACL of GridMonitor portal 
"""
__all__=['AdminsPool','SitesPool','ServicesPool']


import schema
from errors import *
import logging

log = logging.getLogger(__name__)

def strip_args(func):
    """ Decorator that strips the input parameters 
        of a function. If arg is a string
        it gets explicitly passed to the function 
        as 'unicode'.
    """
    def new_func(*args, **kwargs):
        args_stripped = list()
        kwargs_stripped = dict()

        for arg in args:    
            if type(arg) == str:
                args_stripped.append(unicode(arg.strip()))
            else:
                args_stripped.append(arg)
        
        if kwargs:
            for k, v in kwargs.items():
                if type(v) == str:
                    kwargs_stripped[k] = unicode(v.strip())
                else:
                    kwargs_stripped[k] = v
               
        return func(*args_stripped, **kwargs_stripped)
        
    return new_func 


class AdminsPool():
    """ Pool of Administrators """
    
    def __init__(self, session):
        self.session = session
    
    @strip_args
    def show_admin(self, unique_id):
        """ Find admin for given unique_id
            returns: admin object | None
        """
        return self.session.query(schema.Admin).filter_by(shib_unique_id=unique_id).first()

    @strip_args
    def add_admin(self, unique_id, surname, 
                given_name, email):
        """ Adds an Administrator to the ACL. If the administrator exists
            already, he/she will be updated.
            Params: unique_id -- a  unique ID to identify administrator
                    surname    -- surname of administrator
                    given_name -- given name of administrator
                    email  -- email of administrator
            Raises: ACLInserError -- for missing or invalid parameters
        """
        if not unique_id:
            raise ACLInsertError("Empty unique ID", 
                "The unique ID for adding a administrator is missing ")

        if not surname or not given_name or not email:
            raise ACLInsertError("Required parameter mssing",
                "Either surname,given_name, emaii missing")
        
        admin = self.session.query(schema.Admin).filter_by(shib_unique_id=unique_id).first()
        if admin:
            if (admin.shib_given_name != given_name) or \
                 (admin.shib_surname != surname) or (admin.shib_email != email):
                log.info("Updating records of '%s, %s'" % (surname, given_name))
                admin.shib_given_name = given_name
                admin.shib_surname = surname
                admin.shib_email = email
                self.session.add(admin)
        else:
            log.info("Adding admin '%s, %s'" % (surname, given_name))
            admin = schema.Admin(unique_id, 
                surname, given_name, email)
            self.session.add(admin)

        try:
            self.session.commit() 
        except Exception, e:
            log.error("While adding/updating admin, got %r" % e)
            self.session.rollback()
            raise ACLInsertError("Failed to add/update admin", \
                "Could not add admin '%s, %s'." % (surname,given_name))
    
    @strip_args 
    def update_admin(self, unique_id, surname, 
                given_name, email):
        """ Updates an administrator of the ACL. If the administrator does notexists
            already, he/she will be created.
            Params: unique_id -- a  unique ID to identify administrator
                    surname    -- surname of administrator
                    given_name -- given name of administrator
                    email  -- email of administrator
        """
        self.add_admin(unique_id, surname, given_name, email)

    @strip_args
    def remove_admin(self, unique_id):
        """ Remove administrator for administrator pool. 
            Params: unique_id -- unique ID of admnistrator
            Raises ACLInsertError -- if admin can't be removed due to db error.
        """
        admin = self.session.query(schema.Admin).filter_by(shib_unique_id = unique_id).first()
        if admin:
            log.info("Removing  admin '%s, %s'" % \
                (admin.shib_surname, admin.shib_given_name))
            self.session.delete(admin)
            self.session.commit()
            try:
                self.session.commit() 
            except Exception, e:
                log.error("While removing  admin, got %r" % e)
                self.session.rollback()
                raise ACLInsertError("Failed to remove admin", 
                    "Could not remove admin '%s'." % (unique_id))
    

    def list_admins(self):
        """ Lists all administrators that are currently in the 
            administrator pool.
            returns:   list of admin objects
        """
        return self.session.query(schema.Admin).all()

    
    @strip_args
    def list_admin_sites(self, unique_id):
        """ List all sites where admin has administrator rights.
            Params: unique_id -- unique id of admin
            Return: list of site objects 
        """
        admin = self.session.query(schema.Admin).filter_by(shib_unique_id = unique_id).first()
        if admin:
            return admin.sites
        return list()
    
    @strip_args
    def list_admin_services(self, unique_id):
        """ List all services where admin has administrator rights.
            Params: unique_id -- unique id of admin
            Return: list of service objects 
        """
        
        admin = self.session.query(schema.Admin).filter_by(shib_unique_id = unique_id).first()
        if admin:
            return admin.services
        return list()


class SitesPool():
        
    def __init__(self, session):
        self.session = session
    
    @strip_args
    def add_site(self, name, alias=None):
        """ Adding a site to pool of sites used for defining ACL
            Params: name -- name of the site 
                    alias -- some alias for site (optional)
            Raise ACLInsertError -- if site could not be added.
        """
        if not name:
            raise ACLInserError("Site 'name' is empty", "Site with not 'name' can't be created.")
        
        site = self.session.query(schema.Site).filter_by(name=name).first()
        if site:
            if site.alias != alias:
                log.info("Updating site '%s'" % name)
                site.alias = alias
                self.session.add(site)
        else:
            log.info("Adding site '%s'" % name)
            site = schema.Site(name, alias)
            self.session.add(site)
        
        try:
            self.session.commit()
        except Exception, e:
            log.error("While adding site '%s' got '%r'" % (name, e))
            self.session.rollback()
            raise ACLInsertError("Failed to add new site.", \
                "Failed to add site '%s'" % name)

    @strip_args
    def add_admin(self, site_name, unique_id):
        """ Adding an administrator to a site.
            Params: site_name -- name of the site 
                    unique_id -- Unique ID of administrator
            Raises ACLNoRecError -- if admin or site does not exist. 
            Raises ACLInsertError -- if admin could not be added
        """
        site = self.session.query(schema.Site).filter_by(name = site_name).first()
        admin = self.session.query(schema.Admin).filter_by(shib_unique_id = unique_id).first()
    
        if not site:
            raise ACLNoRecError("Site does not exist", \
                "Site '%s' does not exist. Can't add admin '%s' to it" % \
                (site_name, unique_id))
        
        if not admin:
            raise ACLNoRecError("Admin does not exist", \
                "Admin '%s' does not exist. Can't add admin '%s' to site '%s'." % \
                (unique_id, site_name, unique_id))

        if not admin in site.admins:
            log.info( "Adding '%s %s' to admins of site '%s'" % \
                (admin.shib_surname, admin.shib_given_name, site_name))
            site.admins.append(admin)

        try:        
            self.session.commit()
        except Exception, e:
            log.error("Failed to add admin to site, got '%r'." % e)
            self.session.rollback()
            raise ACLInsertError("Failed to add admin to site.", \
                "Failed to add admin '%s' to site '%s'" % (unique_id, site_name)) 


    @strip_args
    def remove_site(self, name):
        """ Removing a site from the ACL pool of sites.
            Params: name -- name of the site  
            Raises ACLInsertError -- if site can't be removed due to db error.
        """

        site = self.session.query(schema.Site).filter_by(name=name).first()
        if site:
            log.info("Removing site '%s'" % name)
            self.session.delete(site)
            try:
                self.session.commit()
            except Exception, e:
                log.error("Failed to remove to site, got '%r'." % e)
                self.session.rollback()
                raise ACLInsertError("Failed to remove site.", \
                    "Failed to remove site '%s'." % (name)) 

    @strip_args
    def remove_admin(self, site_name, unique_id):
        """ Removing an admin from a site. 
            Params:  site_name -- name of the site
                    unique_id -- unique ID of the administrator to remove.
        """

        site = self.session.query(schema.Site).filter_by(name = site_name).first()
        admin = self.session.query(schema.Admin).filter_by(shib_unique_id = unique_id).first()

        if not site or not admin:
            log.info("Either site '%s' or admin with id '%s' did not exist. Nothing to remove" % \
                    (site_name, unique_id))
            return
        
        log.info("Removing admin '%s %s' from  site '%s'" % \
            (admin.shib_surname, admin.shib_given_name, site_name))
        site.admins.remove(admin)
        try:
            self.session.commit()
        except Exception, e:
            log.error("Failed to remove to admin from site, got '%r'." % e)
            self.session.rollback()
            raise ACLInsertError("Failed to remove admin form site.", \
                "Failed to remove admin '%s from site  '%s'." % (unique_id, site_name)) 

    def list_sites(self):
        """ Listing of all sites in ACL pool. 
            Return: list of site objects 
        """
        return self.session.query(schema.Site).all()
        
    
    @strip_args
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

    @strip_args
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
    
    @strip_args
    def show_site(self, site_name):
        """ Listing of site with name=site_name in ACL pool. 
            Return: site object 
        """
        return self.session.query(schema.Site).filter_by(name=site_name).first()



class ServicesPool():
    
    def __init__(self, session, valid_types=None):
        self.session = session
        if not valid_types:
            self.valid_types = ['CE', 'VOMS', 'VASH', 'GIIS', 'BDII', 'RT', 'other']
        else:
            self.valid_types = [x.strip() for x in valid_types.split(',')]
        
    @strip_args
    def add_service(self, name, site_name, type, hostname, alias=None):
        """ Adding a service to the ACL pool. 
            Params: name -- name of the service 
                    site_name -- name of the site    
                    type    -- service type (currently either 'cluster' or 'other')
                    hostname -- host name (FQDN) where service runs
                    alias   -- alias ofr service (optional)
            Raise   ACLInsertError - it type invalid, site does not exist etc.
        """
        if type not in self.valid_types:
            log.error("Invalid type '%s' for service '%s' of site '%s'" % \
                (type, name, site_name))
            raise ACLInsertError("Invalid service 'type'", \
                "Service with type '%s' can't be created." % type)

        # if site service belongs to does not exist -> raise execption
        site = self.session.query(schema.Site).filter_by(name=site_name).first()
        if not site:
            log.error("Service '%s' can't be added to non-existing site '%s'" % \
                (name, site_name))

            raise ACLInsertError("Site does not exist", \
                "Service '%s' can't be added to non-existing site '%s'" % \
                (name, site_name))

        service = self.session.query(schema.Service).filter_by(name=name, hostname=hostname).first()
            
        if service:
            log.info("Service '%s' ('%s') exists already" % (name, hostname))
            if (service.type != type or \
                 service.hostname != hostname or \
                 service.alias != alias):
                service.type = type
                service.hostname = hostname
                service.alias = alias
                self.session.add(service)
        else:
            log.info("Adding service '%s' (%s)" % (name, hostname))
            service = schema.Service(name, site_name, type, hostname, alias)
            self.session.add(service)

        try:
            self.session.commit()
        except Exception, e:
            log.error("While adding/updating service, got %r" % e)
            self.session.rollback()
            raise ACLInsertError("Failing to add service", \
                "Failing to add service '%s' to sites '%s'" % \
                (name, site_name))

    @strip_args 
    def add_admin(self, name, hostname,  unique_id):
        """ Adding an administrator to a service. 
            Params: name -- name of the service
                    hostname -- hostname (FQDN) of the service
                    unique_id -- unique ID of admin
        """
        
        service = self.session.query(schema.Service).filter_by(name=name, hostname=hostname).first()
        admin = self.session.query(schema.Admin).filter_by(shib_unique_id=unique_id).first()
        
        if not service:
            log.warn("Service '%s' does not exist. Can't add admin '%s' to it" % \
                (name, unique_id))
            raise ACLNoRecError("Service does not exist", \
                "Service '%s/%s' does not exist. Can't add admin '%s' to it" % \
                (name, hostname, unique_id))
        
        if not admin:
            log.warn("WARNING: admin '%s' does not exist. Can't add admin to service '%s'" % \
                (unique_id, name))
            raise ACLNoRecError("Admin does not exist", \
                "Admin '%s' does not exist. Can't add admin to service '%s/%s'." % \
                (unique_id, name, hostname))

        if not admin in service.admins:
            log.info("Adding '%s %s' to admins of service '%s' (%s)" % \
                (admin.shib_surname, admin.shib_given_name, name, hostname))
            service.admins.append(admin)
        try:
            self.session.commit()
        except Exception, e:
            log.error("While adding admin to  service, got %r" % e)
            self.session.rollback()
            raise ACLInsertError("Failing to add admin to service", \
                "Failing to add admin '%s' to service '%s/%s'" % \
                (unique_id, name, hostname))
            
    @strip_args
    def remove_service(self, name, hostname):
        """ Removing a service from ACL service pool.   
            Params: name -- name of service
                    hostname -- hostname (FQDN) of host where service runs
        """
        service = self.session.query(schema.Service).filter_by(name=name, hostname=hostname).first()
        if service:
            log.info("Removing service '%s' (%s)" % (name, hostname))
            self.session.delete(service)
            try:
                self.session.commit()
            except Exception, e:
                log.error("Failed to remove service got %r" % e)
                self.session.rollback()
                raise ACLInsertError("Failing to remove service", \
                    "Failing to remove service '%s/%s'" % \
                    (name, hostname))

    @strip_args
    def remove_admin(self, name, hostname, unique_id):
        """ Removing an admin from a service.   
            Params: name -- name of service
                    hostname -- hostname (FQDN) of host where service runs
                    unique_id -- unique ID of the admin
            Raises ACLInsertError -- if access to db is failing
        """
        service = self.session.query(schema.Service).filter_by(name=name, hostname=hostname).first()
        admin = self.session.query(schema.Admin).filter_by(shib_unique_id = unique_id).first()

        if not service or not admin:
            log.info("Nothing to remove, since either service '%s/%s' or admin '%s' is missing" %\
                    (name, hostname, unique_id))
            return
        
            log.info("Removing admin '%s %s' from  service '%s' (%s)" % \
            (admin.shib_surname, admin.shib_given_name, name, hostname))
        service.admins.remove(admin)
        try:
            self.session.commit()
        except Exception, e:
            log.error("Failed to remove admin got %r" % e)
            self.session.rollback()
            raise ACLInsertError("Failing to remove admin", \
                "Failing to remove admin '%s' from service '%s/%s'" % \
                (unique_id, name, hostname))
    
    def list_services(self):
        """ List all services in ACL service pool
            Returns list of services objects """
        return self.session.query(schema.Service).all()

    @strip_args
    def list_admins(self, name, hostname):
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
        
    @strip_args
    def get_site(self, name, hostname):
        """ Get site object for service
            Params: name -- name of service
                    hostname -- hostname (FQDN) where service runs
            Returns: site object
        """
        service = self.session.query(schema.Service).filter_by(name=name, hostname=hostname).first()
        if not service:
            log.warn("Service '%s/%s' does not exist; no site to return" % (name, hostname))
            return None
        return service.site[0]

    @strip_args 
    def show_service(self, hostname):
        """ Listing of site with hostname=hostname in ACL pool. 
            Return: service object 
        """
        return self.session.query(schema.Service).filter_by(hostname=hostname).first()
