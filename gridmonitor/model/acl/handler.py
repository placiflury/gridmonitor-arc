"""
Dealing with ACL for siteadmin 
"""
import gridmonitor.model.acl.schema as schema

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
        admin = self.session.query(schema.Admin).filter_by(shib_unique_id=shib_unique_id).first()
        if admin:
            print "Admin '%s, %s' exists already" % (shib_surname, shib_given_name)
            if (admin.shib_given_name != shib_given_name) or \
                 (admin.shib_surname != shib_surname) or \
                 (admin.shib_email != shib_email) or \
                 (admin.shib_affiliation != shib_affiliation) or \
                 (admin.shib_homeorg != shib_homeorg):
                print "Updating records of '%s, %s'" % (shib_surname, shib_given_name)
                admin.shib_given_name = shib_given_name
                admin.shib_surname = shib_surname
                admin.shib_email = shib_email
                admin.shib_affiliation = shib_affiliation
                admin.shib_homeorg = shib_homeorg
                self.session.flush()
        else:
            print "Adding admin '%s, %s'" % (shib_surname, shib_given_name)
            admin = schema.Admin(shib_unique_id, 
                shib_surname, shib_given_name, shib_email,
                shib_affiliation, shib_homeorg)
            self.session.save(admin)
            self.session.flush() 

    def remove_admin(self, shib_unique_id):
        admin = self.session.query(schema.Admin).filter_by(shib_unique_id = shib_unique_id).first()
        if admin:
            print "Removing  admin '%s, %s'" % \
                (admin.shib_surname, admin.shib_given_name)
            self.session.delete(admin)
            self.session.flush()

class SitesPool():
    
    def __init__(self, session):
        self.session = session

    def add_site(self,name,alias=None):
        site = self.session.query(schema.Site).filter_by(name=name).first()
        if site:
            print "Site '%s' exists already" % name
            if site.alias != alias:
                print "Udating site '%s'" % name
                site.alias = alias
                self.session.flush()
        else:
            print "Adding site '%s'" % name
            site = schema.Site(name,alias)
            self.session.save(site)
            self.session.flush()

    def add_admin(self, site_name, shib_unique_id):
        site = self.session.query(schema.Site).filter_by(name = site_name).first()
        admin = self.session.query(schema.Admin).filter_by(shib_unique_id = shib_unique_id).first()
    
        if not site:
            print "WARNING: site '%s' does not exist. Can't add admin '%s' to it" % \
                (site_name, shib_unique_id)
            return
        
        if not admin:
            print "WARNING: admin '%s' does not exist. Can't add admin to site '%s'" % \
                (shib_unique_id, site_name)
            return
        
        if not admin in site.admins:
            print "Adding '%s %s' to admins of site '%s'" % \
                (admin.shib_surname, admin.shib_given_name, site_name)
            site.admins.append(admin)
            self.session.flush()

    def remove_site(self, name):
        site = self.session.query(schema.Site).filter_by(name=name).first()
        if site:
            print "Removing site '%s'" % name 
            self.session.delete(site)
            self.session.flush()


    def remove_admin(self, site_name, shib_unique_id):
        site = self.session.query(schema.Site).filter_by(name = site_name).first()
        admin = self.session.query(schema.Admin).filter_by(shib_unique_id = shib_unique_id).first()

        if not site or not admin:
            return
        
        print "Removing admin '%s %s' from  site '%s'" % \
            (admin.shib_surname, admin.shib_given_name, site_name)
        site.admins.remove(admin)
        self.session.flush()

 
class ServicesPool():
    
    VALID_TYPES = ['cluster','other']
    
    def __init__(self, session):
        self.session = session

    def add_service(self,name, site_name, type, hostname, alias=None):
        
        if type not in ServicesPool.VALID_TYPES:
            print "ERROR: Invalid type '%s' for service '%s' of site '%s'" % \
                (type, name, site_name)

        # if site service belongs to does not exist -> create it
        site = self.session.query(schema.Site).filter_by(name=site_name).first()
        if not site:
            print "Adding site '%s'" % name
            site = schema.Site(name)
            self.session.save(site)

        service = self.session.query(schema.Service).filter_by(name=name, hostname=hostname).first()
        if service:
            print "Service '%s' ('%s') exists already" % (name, hostname)
            if (service.type != type or \
                 service.hostname != hostname or \
                 service.alias != alias):
                service.type = type
                service.hostname = hostname
                service.alias = alias
        else:
            print "Adding service '%s' (%s)" % (name, hostname)
            service = schema.Service(name, site_name, type, hostname, alias)
            self.session.save(service)

        self.session.flush()
        


    def add_admin(self, name, hostname,  shib_unique_id):
        service = self.session.query(schema.Service).filter_by(name=name, hostname=hostname).first()
        admin = self.session.query(schema.Admin).filter_by(shib_unique_id=shib_unique_id).first()
    
        if not service:
            print "WARNING: service '%s' does not exist. Can't add admin '%s' to it" % \
                (name, shib_unique_id)
            return
                
        if not admin:
            print "WARNING: admin '%s' does not exist. Can't add admin to service '%s'" % \
                (shib_unique_id, name)
            return
        if not admin in service.admins:
            print "Adding '%s %s' to admins of service '%s' (%s)" % \
                (admin.shib_surname, admin.shib_given_name, name, hostname)
            service.admins.append(admin)
            self.session.flush()

    def remove_service(self, name, hostname):
        service = self.session.query(schema.Service).filter_by(name=name, hostname=hostname).first()
        if service:
            print "Removing service '%s' (%s)" % (name, hostname) 
            self.session.delete(service)
            self.session.flush()


    def remove_admin(self, name, hostname, shib_unique_id):
        service = self.session.query(schema.Site).filter_by(name=name, hostname=hostname).first()
        admin = self.session.query(schema.Admin).filter_by(shib_unique_id = shib_unique_id).first()

        if not service or not admin:
            return
        
        print "Removing admin '%s %s' from  service '%s' (%s)" % \
            (admin.shib_surname, admin.shib_given_name, name, hostname)
        service.admins.remove(admin)
        self.session.flush()
