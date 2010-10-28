import logging
from gridmonitor.lib.base import *
from gridmonitor.model.acl import meta
from gridmonitor.model.acl import schema 


log = logging.getLogger(__name__)

class MonadminController(BaseController):
    

    def __init__(self):
        self.admin = None
        self.access_denied = False  # XXX: change this

        # authorization and mapping
        # info about user
        unique_id = unicode(request.environ[config['shib_unique_id']], "utf-8")
        c.user_name = unicode(request.environ[config['shib_given_name']], 'utf-8')
        c.user_surname = unicode(request.environ[config['shib_surname']], 'utf-8')
        user_email = unicode(request.environ[config['shib_email']], "utf-8")
        user_home_org = unicode(request.environ[config['shib_home_org']], "utf-8")
        

        query = meta.Session.query(schema.Admin)

        """        
        admin = query.filter_by(shib_unique_id=unique_id).first()
        if admin:
            self.access_denied = False
        """
                
        # static menu information
        mng_resources = [('Admins','/monadmin/resources/admins'),
                        ('Sites & Services', '/monadmin/resources/site_services')]
    
        acl_editor = [('Admin to Site', '/monadmin/acl/admin2site'),
                      ('Site to Admin', '/monadmin/acl/site2admin')]
        

        c.top_nav= [('User','/user'),
            ('Site Admin', '/siteadmin'),
            ('VO/Grid Admin', '/gridadmin'),
            ('Monitor Admin', '/monadmin'),
            ('Help','/help')]

         
        c.menu = [('Manage Resources', '/monadmin/resources', mng_resources),
                ('Map','/monadmin/acl', acl_editor)]

        c.top_nav_active="Monitor Admin"
 
    def index(self):
        
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "Manage Resources"
        return render('/base/monadmin.html')
  
