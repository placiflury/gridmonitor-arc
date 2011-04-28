import logging
from pylons import session
from pylons import config
from pylons import tmpl_context as c
from pylons import app_globals as g
from pylons.templating import render_mako as render

import gridmonitor.lib.helpers as h
from gridmonitor.lib.base import BaseController
from gridmonitor.model.acl import *
from gridmonitor.model.acl.name_mapping import *
from gridmonitor.model.sft.name_mapping import *
from sft.db.cluster_handler import *
from sft.db.sft_handler import *
from sft.db.test_handler import *
from sft.db.user_handler import *
from sft.db.vo_handler import *

import simplejson as json

log = logging.getLogger(__name__)

class MonadminController(BaseController):

    def __init__(self):
        BaseController.__init__(self)

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
        acl_editor = [('Sites & Services', '/monadmin/acl/siteservices'),
                      ('Administrators', '/monadmin/acl/admins')]
        sft_editor = [('Users', '/monadmin/sft/users'),
                      ('VOs', '/monadmin/sft/vos'),
                      ('Clusters', '/monadmin/sft/clusters'),
                      ('Tests', '/monadmin/sft/tests'),
                      ('Edit SFTs', '/monadmin/sft/edit')]
        
        c.top_nav= session['top_nav_bar']
        
        c.menu = list()
        if 'ACL' in authorized_sections:
            c.menu.append(('ACL Manager','/monadmin/acl', acl_editor))

        self.sft_clusters = None
        self.sft_cluster_groups = None
        self.sfts = None
        self.sft_tests = None
        self.sft_test_suits = None
        self.sft_users = None
        self.sft_vos = None
        self.sft_vo_groups = None 
        self.sft_vo_users = None
        if 'SFT' in authorized_sections: 
            self.sft_clusters = ClusterPool()
            self.sft_cluster_groups = ClusterGroupPool() 
            self.sfts = SFTPool()
            self.sft_tests = TestPool()
            self.sft_test_suits = TestSuitPool() 
            self.sft_users = UserPool()
            self.sft_vo_users = VOUserPool()
            self.sft_vos = VOPool()
            self.sft_vo_groups = VOGroupPool()
            c.menu.append(('SFTs','/monadmin/sft', sft_editor))


        c.top_nav_active="Monitor Admin"
        
 
    def index(self):
        
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "Manage Resources"
        c.heading = "Monitor Admin"
        
        if self.authorized == False:
            return render('/derived/monadmin/error/access_denied.html')        
        return render('/derived/monadmin/index.html')
  
