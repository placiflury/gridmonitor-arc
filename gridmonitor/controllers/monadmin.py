import logging
from gridmonitor.lib.base import *
from gridmonitor.model.acl import *
from gridmonitor.model.acl.name_mapping import *
import simplejson as json

log = logging.getLogger(__name__)

class MonadminController(BaseController):

    def __init__(self):
        self.admin = None
        self.authorized = False
        authorized_sections = list() # what parts of webpage

        self.__before__() # call base class for authentication info
        c.user_name = session['user_name']
        c.user_surname = session['user_surname']
        
        if session.has_key('user_unique_id'):
            user_unique_id = session['user_unique_id']
            db_session = meta.Session()
            self.admins_pool = handler.AdminsPool(db_session)
            self.sites_pool = handler.SitesPool(db_session)
            self.services_pool = handler.ServicesPool(db_session, config['acl_service_types'])
            for site in self.admins_pool.list_admin_sites(user_unique_id):
                log.debug("Checking whether '%s' is a super admin" % user_unique_id)
                if site.name == 'GridMonitor' and site.alias == 'not_a_real_site': # super admin
                    self.authorized = True
                    log.info("Got super admin with ID '%s'" % user_unique_id)
                    for service in site.services:
                        authorized_sections.append(service.name)
                    break
            if not self.authorized: # check whether access to sub-set 
                log.debug("Checking whether '%s' has admin rights" % user_unique_id)
                admin = self.admins_pool.show_admin(user_unique_id)
                if admin:
                    log.info('got admin object')
                    log.info("%r" % admin.services)
                    for service in admin.services:
                        log.info("%s-%s" % (service.name, service.site_name))
                        if service.name in ['ACL','SFT'] and service.site_name == 'GridMonitor': 
                            self.authorized = True
                            log.info("yes hs has")
                            authorized_sections.append(service.name)

                
        # static menu information
        mng_resources = [('Admins','/monadmin/resources/admins'),
                        ('Sites & Services', '/monadmin/resources/site_services')]
    
        acl_editor = [('Admin to Site', '/monadmin/acl/admin2site'),
                      ('Site to Admin', '/monadmin/acl/site2admin')]
        sft_editor = [('View SFTs (dummy)', '/monadmin/sft/list'),
                      ('Edit SFTs (dummy)', '/monadmin/sft/edit')]
        
        c.top_nav= session['top_nav_bar']
        
        c.menu = list()
        log.info('XXX %r' % authorized_sections)
        if 'ACL' in authorized_sections:
                c.menu.append(('Manage Resources', '/monadmin/resources', mng_resources))
                c.menu.append(('Map','/monadmin/acl', acl_editor))

        if 'SFT' in authorized_sections: 
                c.menu.append(('SFTs','/monadmin/sft', sft_editor))


        c.top_nav_active="Monitor Admin"
        
 
    def index(self):
        
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "Manage Resources"
        if self.authorized == False:
            return render('/derived/monadmin/error/access_denied.html')        
        return render('/base/monadmin.html')
  
