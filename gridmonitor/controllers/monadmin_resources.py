from monadmin import *

log = logging.getLogger(__name__)

class MonadminResourcesController(MonadminController):    

    def __init__(self):
        MonadminController.__init__(self)        
        db_session = meta.Session()
        self.admins_pool = handler.AdminsPool(db_session)
        self.sites_pool = handler.SitesPool(db_session)
        self.service_pool = handler.ServicesPool(db_session)
    
    def index(self):
        
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "Manage Resources"
        c.heading = "Listing Administrators and Resources"  # default
        # XXX fill in logic

        return render('/derived/monadmin/resources/index.html')
        

    def admins(self):
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "Manage Resources"
        c.heading = "Manage Administrators of Grid Sites and Grid Services"
        
        c.admins = self.admins_pool.list_admins()
        return render('/derived/monadmin/resources/admin.html')
    
    def getadms(self):
        c.admins = self.admins_pool.list_admins()
        c.listOnChange = "changeRes(this,'admin','show')"
        c.list = 'list1'
        return render('/derived/monadmin/includes/getadms.mako')
    
    def site_services(self):
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "Manage Resources"
        c.heading = "Manage Grid Sites and Services"
        
        c.sites = self.sites_pool.list_sites()
        c.services = list()
        return render('/derived/monadmin/resources/site_services.html')
    
    def getsites(self):
        c.sites = self.sites_pool.list_sites()
        c.list = 'list1'
        c.listOnChange = "map('/monadmin/resources/map/', '#site_list', '#list2_container', 'map', true)"
        c.listOnChange += ";changeRes(this,'site','show')"
        return render('/derived/monadmin/includes/getsites.mako')
    
    def map(self,id=''):
        # TODO urldecode of id
        c.services = self.sites_pool.list_services(id)
        c.list = 'list2'
        c.listOnChange = "changeRes(this,'service','show')"
        return render('/derived/monadmin/includes/res_getservices.mako')
        
    def changeadm(self):
        """docstring for changeadmin"""
        return render('/derived/monadmin/includes/changeadm.mako')

    def getadm(self):
        """docstring for getadm"""
        try:
            c.shib_unique_id = request.POST['adm_unique_id']
            button = request.POST['button']
            mode = request.POST['mode']
        except:
            return 'Wrong HTTP POST params.'
        finally:
            if button == 'save':
                c.shib_surname = request.POST['surname']
                c.shib_given_name = request.POST['given_name']
                c.shib_email = request.POST['email']
                
                if mode == 'new':
                    self.admins_pool.add_admin(     c.shib_unique_id, \
                                                    c.shib_surname, \
                                                    c.shib_given_name, \
                                                    c.shib_email )
                    return 'New User ' + c.shib_given_name + ' ' + c.shib_surname + ' has been created'
                elif mode == 'edit':
                    self.admins_pool.update_admin(  c.shib_unique_id, \
                                                    c.shib_surname, \
                                                    c.shib_given_name, \
                                                    c.shib_email )
                    return 'User ' + c.shib_given_name + ' ' + c.shib_surname + ' has been updated'
                else:
                    return 'In this mode you cannot save.'
            elif button == 'del' and mode == 'del':
                self.admins_pool.remove_admin(c.shib_unique_id)
                return 'User ' + c.shib_given_name + ' ' + c.shib_surname + ' has been deleted'
            elif button == 'show':
                c.admin = self.admins_pool.show_admin(c.shib_unique_id)
                return render('/derived/monadmin/includes/getadm_xml.mako')
            else:
                return 'Error: No action specified.'
            
    def changesite(self):
        """docstring for changesite"""
        return render('/derived/monadmin/includes/changesite.mako')

    def getsite(self):
        """docstring for getsite"""
        try:
            button = request.POST['button']
            mode = request.POST['mode']
        except:
            return 'Wrong HTTP POST params.'
        finally:
            if button == 'save' and mode == 'new':
                c.site_name = request.POST['site_name']
                c.site_alias = request.POST['site_alias']
                self.sites_pool.add_site(c.site_name, c.site_alias)
                return 'Site ' + c.site_name + ' has been added.'
            elif button == 'del' and mode == 'del':
                c.site_name = request.POST['site_name']
                self.sites_pool.remove_site(c.site_name)
                return 'Site ' + c.site_name + ' has been deleted.'
            elif button == 'show':
                c.site = self.sites_pool.show_site(request.POST['site_name'])
                return render('/derived/monadmin/includes/getsite_xml.mako')
                
    def changeservice(self):
        """docstring for changservice"""
        c.service_names = config['acl_service_names'].split(',')
        #raise Exception(c.service_names)
        return render('/derived/monadmin/includes/changeservice.mako')

    def getservice(self):
        try:
            button = request.POST['button']
            mode = request.POST['mode']
        except:
            return 'Wrong HTTP POST params.'
        finally:
            if button == 'save' and mode == 'new':
                hostname = request.POST['hostname']
                name = request.POST['name']
                site_name = request.POST['site_name']
                type = request.POST['type']
                alias = request.POST['alias']
                self.services_pool.add_service(name, site_name, type, hostname, alias)
                return 'Service ' + name + ' - ' + hostname + ' has been added.'
            elif button == 'del' and mode == 'del':
                name = request.POST['name']
                hostname = request.POST['hostname']
                self.services_pool.remove_service(name, hostname)
                return 'Service ' + hostname + ' has been deleted.'
            elif button == 'show':
                c.service = self.services_pool.show_service(request.POST['hostname'])
                return render('/derived/monadmin/includes/getservice_xml.mako')
