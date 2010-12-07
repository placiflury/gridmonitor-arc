import logging
from gridmonitor.lib.base import *
from monadmin import MonadminController


log = logging.getLogger(__name__)
class MonadminAclController(MonadminController):    
    
    def index(self):
        
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "Manage ACL"
        c.heading = "Listing current ACLs"
        # XXX fill in logic
        
        return render('/derived/monadmin/acl/index.html')
    

    def admin2site(self):
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "Manage ACL"
        c.heading = "Add  Administrator to Site/Service"
        
        c.sites = self.sites_pool.list_sites()
        return render('/derived/monadmin/acl/admin2site.html')
    
    def site2admin(self):
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "Manage ACL"
        c.heading = "Add  Site/Service to Administrator"
        
        c.admins = self.admins_pool.list_admins()
        return render('/derived/monadmin/acl/site2admin.html')

    def getadms(self):
        c.admins = self.admins_pool.list_admins()
        c.listOnChange = "map('/monadmin/acl/map_sitoadm/', '#admin_list', '#list2_container', 'map', true);changeRes(this,'admin','show')"
        c.list = 'list1'
        return render('/derived/monadmin/includes/getadms.mako')
        
    def getsites(self):
        c.sites = self.sites_pool.list_sites()
        c.listOnChange = "map('/monadmin/acl/map_admtosi/', '#site_list', '#list2_container', 'map', true)"
        c.list = 'list1'
        return render('/derived/monadmin/includes/getsites.mako')

    def map_sitoadm(self,id):
        """docstring for map"""
        c.active = 'active'
        c.services = self.admins_pool.list_admin_services(id)
        c.sites = self.admins_pool.list_admin_sites(id)        
        c.services_grp = dict()
        for service in c.services:
            if c.services_grp.has_key(service.site_name):
                c.services_grp[service.site_name].append([service.name,service.hostname])
            else:
                c.services_grp[service.site_name] = [[service.name,service.hostname]]
        c.lists = 'list2'
        return render('/derived/monadmin/includes/map_sitoadm.mako')
        
    def map_admtosi(self,id):
        """docstring for map"""
        # TODO urldecode for id
        c.active = 'active'
        c.admins = self.sites_pool.list_admins(id)
        c.list = 'list2'
        c.listOnChange = "changeRes(this,'admin','show')"
        return render('/derived/monadmin/includes/getadms.mako')
        
    def exchange_sitoadm(self,id):
        """docstring"""
        c.active = 'inactive'
        c.my_services = self.admins_pool.list_admin_services(id)
        c.my_sites = self.admins_pool.list_admin_sites(id)
        c.services = self.services_pool.list_services()
        
        for service in c.my_services:
            c.services.remove(service)
        c.sites = self.sites_pool.list_sites()
        for site in c.my_sites:
            c.sites.remove(site)
        c.services_grp = dict()
        for service in c.services:
            if c.services_grp.has_key(service.site_name):
                c.services_grp[service.site_name].append([service.name,service.hostname])
            else:
                c.services_grp[service.site_name] = [[service.name,service.hostname]]
        c.lists = 'list3'
        return render('/derived/monadmin/includes/map_sitoadm.mako')
        
    def exchange_admtosi(self,id):
        """docstring"""
        c.active = 'inactive'
        c.my_admins = self.sites_pool.list_admins(id)
        
        c.admins = self.admins_pool.list_admins()
        for admin in c.my_admins:
            c.admins.remove(admin)
        c.list = 'list3'
        c.listOnChange = "changeRes(this,'admin','show')"
        return render('/derived/monadmin/includes/getadms.mako')
        
    def info(self,id):
        """docstring for info"""
        c.admin = self.admins_pool.show_admin(id)
        return render('/derived/monadmin/includes/adminfo.mako')

    def save_sitoadm(self):
        try:
            mode = request.POST['mode']
        except:
            raise Exception('Mode has to be set in the HTTP POST params.')
        try:
            shib_unique_id = request.POST['admin']
        except:
            return 'Error: No admin defined.'
            
        for site in request.params.getall('add_site'):
            self.sites_pool.add_admin(site, shib_unique_id)
        for site in request.params.getall('remove_site'):
            self.sites_pool.remove_admin(site, shib_unique_id)
        for service in request.params.getall('add_service'):
            service = service.split(',',2)
            self.services_pool.add_admin(service[0], service[1], shib_unique_id)
        for service in request.params.getall('remove_service'):
            service = service.split(',',2)
            self.services_pool.remove_admin(service[0], service[1], shib_unique_id)
        return 'Sites and Services for Admin ' + shib_unique_id + ' saved.'
        
    def save_admtosi(self):
        try:
            mode = request.POST['mode']
        except:
            raise Exception('Mode has to be set in the HTTP POST params.')
        try:
            site = request.POST['site']
        except:
            return 'Error: No site defined.'

        for admin in request.params.getall('add_admin'):
            self.sites_pool.add_admin(site, admin)
        for admin in request.params.getall('remove_admin'):
            self.sites_pool.remove_admin(site, admin)
        return 'Admins for Site ' + site + ' saved.'
        

