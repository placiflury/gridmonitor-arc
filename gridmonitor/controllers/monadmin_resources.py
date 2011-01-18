from monadmin import *
from hashlib import md5 

log = logging.getLogger(__name__)

class MonadminResourcesController(MonadminController):    
    def __build_json__(self, data_list, keymap, keymap_order, opt_params):
        """
        Creates a valid JSON syntax of SQLAlchemy Objects.
        Parameters:
        data_list: list of SQLAlchemy objects
        keymap: Dict of human readable strings for every key
        keymap_order: List of all keys to guarantee right order
        opt_params: Dict of params that should be appended (without processing) to the JSON string
                    currently: string id_key, list show_keys, string parent_key
        """
        json_data = dict()
        json_data['order_keys'] = keymap_order;
        json_data['names'] = dict()
        for k in keymap.keys():
            json_data['names'][k] = keymap[k][0]
        json_data['members'] = list()
        for item in data_list:
            item_dict = dict()
            for k in keymap.keys():
                try:
                    item_dict[k] = item.__dict__[k]
                except:
                    pass
            log.info('Key: %s' % k)
            if opt_params['id_key'] == 'hash':
                item_dict['hash'] = hash(item_dict.__str__())
            json_data['members'].append(item_dict)
        for p in opt_params:
            json_data[p] = opt_params[p]
        return json.dumps(json_data)

    def index(self):
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "Manage Resources"
        c.heading = "Listing Administrators and Resources"
        
        if self.authorized == False:
            return render('/derived/monadmin/error/access_denied.html')

        return render('/derived/monadmin/resources/index.html')

    def admins(self):
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "Manage Resources"
        c.heading = "Manage Administrators of Grid Sites and Grid Services"

        if self.authorized == False:
            return render('/derived/monadmin/error/access_denied.html')

        c.admins = self.admins_pool.list_admins()
        return render('/derived/monadmin/resources/admin.html')

    def site_services(self):
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "Manage Resources"
        c.heading = "Manage Grid Sites and Services"

        if self.authorized == False:
            return render('/derived/monadmin/error/access_denied.html')

        c.service_names = config['acl_service_types'].split(',')
        c.sites = self.sites_pool.list_sites()
        c.services = list()
        return render('/derived/monadmin/resources/site_services.html')

    def getadms(self):
        """
        Build JSON string with all administrators or just the ones that are responsible for a special site.
        """
        ## Needed for LC_Mapper:
        try:
            source_id = request.GET['source_id']
            target_id = request.GET['target_id']
        except:
            source_id = None;
            target_id = 'MA_adm_list';
        if target_id != 'MA_adm_list':
            raise 'Wrong identifier: HTTP_GET[' + target_id + ']'
        if source_id == 'MA_site_list':
            try:
                inverse = request.GET['inverse']
            except:
                inverse = None
            if inverse:
                adm_list_inactive = list()
                for admin in self.admins_pool.list_admins():
                    if not (admin in self.sites_pool.list_admins(request.GET['name'])):
                        adm_list_inactive.append(admin)
                adm_list = adm_list_inactive
            else:
                adm_list = self.sites_pool.list_admins(request.GET['name'])
        elif source_id == None:
            adm_list = self.admins_pool.list_admins()
        # If NOT AAI enabled:
        if not(request.environ.has_key(config['shib_given_name'])):
            ADMIN_KEYMAP['aai-DN'] = ["DN:"]
            ADMIN_KEYMAP['aai-CA'] = ["CA:"]
            ADMIN_KEYMAP_ORDER.pop(0)
            ADMIN_KEYMAP_ORDER.insert(0, 'aai-DN')
            ADMIN_KEYMAP_ORDER.insert(1, 'aai-CA')
        # AAI enabled:
        return self.__build_json__(adm_list, ADMIN_KEYMAP, ADMIN_KEYMAP_ORDER, { \
                            'id_key': 'shib_unique_id', \
                            'show_keys': ['shib_given_name', 'shib_surname'], \
                            })

    def changeadm(self):
        """
        Store a newly added or changed admin from the db.
        Remove a deleted admin from the db.
        Return value is a string starting with 'OK;;;' or 'ERROR;;;'
                (sets the color of the message on the client side).
        """
        try:
            if request.POST['button'] == 'del':
                self.admins_pool.remove_admin(request.POST['shib_unique_id'])
                return "OK;;;Deleted admin " + request.POST['shib_given_name'] + " " + request.POST['shib_surname'] + " successfully."
            elif request.POST['button'] == 'save':
                # If NOT AAI enabled:
                if not(request.environ.has_key(config['shib_given_name'])):
                    dn = request.POST['aai-DN']
                    ca = request.POST['aai-CA']
                    if dn and ca:
                        shib_unique_id = md5(dn + ca).hexdigest()
                    log.info('DN: %r, CA: %r, UID: %r' % (dn, ca, shib_unique_id))
                # AAI enabled:
                else:
                    shib_unique_id = request.POST['shib_unique_id']
                self.admins_pool.update_admin(  shib_unique_id, \
                                                request.POST['shib_surname'], \
                                                request.POST['shib_given_name'], \
                                                request.POST['shib_email'] )
                return "OK;;;Changed admin " + request.POST['shib_given_name'] + " " + request.POST['shib_surname'] + " successfully."
        except ACLError, e:
            return "ERROR;;;%s" % e.message
        except Exception, e1:
            return "ERROR;;;%r" % e1
        
    def getsites(self):
        """
        Build JSON string with all sites or just the ones that are managed by a special admin.
        """
        try:
            source_id = request.GET['source_id']
            target_id = request.GET['target_id']
        except:
            source_id = None;
            target_id = 'MA_site_list';
        if target_id != 'MA_site_list':
            raise 'Wrong identifier: HTTP_GET[' + target_id + ']'
        if source_id == 'MA_adm_list':
            try:
                inverse = request.GET['inverse']
            except:
                inverse = None
            if inverse:
                site_list_inactive = list()
                for site in self.sites_pool.list_sites():
                    if not (site in self.admins_pool.list_admin_sites(request.GET['shib_unique_id'])):
                        site_list_inactive.append(site)
                site_list = site_list_inactive
            else:
                site_list = self.admins_pool.list_admin_sites(request.GET['shib_unique_id'])
        elif source_id == None:
            site_list = self.sites_pool.list_sites()
        return self.__build_json__(site_list, SITE_KEYMAP, SITE_KEYMAP_ORDER, { \
                            'id_key': 'hash', \
                            'show_keys': ['name']})

    def changesite(self):
        """
        Store a newly added or changed site from the db.
        Remove a deleted site from the db.
        Return value is a string starting with 'OK;;;' or 'ERROR;;;'
                (sets the color of the message on the client side).
        """
        try:
            if request.POST['button'] == 'del':
                self.sites_pool.remove_site(request.POST['name'])
                return "OK;;;Deleted site " + request.POST['name'] + " successfully."
            elif request.POST['button'] == 'save':
                self.sites_pool.add_site(request.POST['name'], request.POST['alias'])
                return "OK;;;Changed site " + request.POST['name'] + " successfully."
        except ACLError, e:
            return "ERROR;;;%s" % e.message
        except Exception, e1:
            return "ERROR;;;%r" % e1

    def getservices(self):
        """
        Build JSON string with all services or just the ones that belong to a special site or
        the ones that are managed by a special admin.
        """
        try:
            source_id = request.GET['source_id']
            target_id = request.GET['target_id']
        except:
            source_id = None;
            target_id = 'MA_service_list';
        if target_id != 'MA_service_list':
            raise 'Wrong identifier: HTTP_GET[' + target_id + ']'
        if source_id == 'MA_site_list':
            try:
                inverse = request.GET['inverse']
            except:
                inverse = None
            if inverse:
                service_list_inactive = list()
                for service in self.services_pool.list_services():
                    if not (service in self.sites_pool.list_services(request.GET['name'])):
                        service_list_inactive.append(service)
                service_list = service_list_inactive
            else:
                service_list = self.sites_pool.list_services(request.GET['name'])
        if source_id == 'MA_adm_list':
            try:
                inverse = request.GET['inverse']
            except:
                inverse = None
            if inverse:
                service_list_inactive = list()
                for service in self.services_pool.list_services():
                    if not (service in self.admins_pool.list_admin_services(request.GET['shib_unique_id'])):
                        service_list_inactive.append(service)
                service_list = service_list_inactive
            else:
                service_list = self.admins_pool.list_admin_services(request.GET['shib_unique_id'])
        elif source_id == None:
            service_list = self.services_pool.list_services()
        return self.__build_json__(service_list, SERVICE_KEYMAP, SERVICE_KEYMAP_ORDER, { \
                            'id_key': 'hash', \
                            'show_keys': ['name', 'hostname'], \
                            'parent_key': 'site_name'})

    def changeservice(self):
        """
        Store a new added or changed service from the db.
        Remove a deleted service from the db.
        Return value is a string starting with 'OK;;;' or 'ERROR;;;'
                (sets the color of the message on the client side).
        """
        try:
            if request.POST['button'] == 'del':
                self.services_pool.remove_service(request.POST['name'], request.POST['hostname'])
                return "OK;;;Deleted service " + request.POST['name'] + " successfully."
            elif request.POST['button'] == 'save':
                self.services_pool.add_service( request.POST['name'], \
                                                request.POST['site_name'], \
                                                request.POST['type'], \
                                                request.POST['hostname'], \
                                                request.POST['alias'])
                return "OK;;;Changed service " + request.POST['name'] + " successfully."
        except ACLError, e:
            return "ERROR;;;%s" % e.message
        except Exception, e1:
            return "ERROR;;;%r" % e1
