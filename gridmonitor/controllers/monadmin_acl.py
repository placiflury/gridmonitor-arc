import logging
from gridmonitor.lib.base import *
from monadmin import MonadminController
from monadmin import *
from hashlib import md5


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
        c.heading = "Manage ACLs for Sites and Services"
        if self.authorized == False:
            return render('/derived/monadmin/error/access_denied.html')
            
        c.service_names = config['acl_service_types'].split(',')
        c.sites = self.sites_pool.list_sites()
        c.services = list()

        return render('/derived/monadmin/acl/admin2site.html')
    
    def site2admin(self):
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "Manage ACL"
        c.heading = "Manage ACLs for Administrators"
        if self.authorized == False:
            return render('/derived/monadmin/error/access_denied.html')
        
        return render('/derived/monadmin/acl/site2admin.html')
    
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
    
    def __parse_http_post__(self):
        """
        Parser for special HTTP_POST structure where keywords can appear
        multiple times.
        Returns a dict of lists with the keywords 'add', 'del', 'source'
        """
        ## My little Parser (DON'T TOUCH)
        add_members = list()
        del_members = list()
        source = dict()
        for k in request.POST:
            k_list = k.replace('[',']').replace(']]',']').rstrip(']').split(']')
            if k_list[0] == 'add':
                try: 
                    add_members[int(k_list[1])]
                except:
                    add_members.append(dict())
                add_members[int(k_list[1])][k_list[2]] = request.POST[k]
            elif k_list[0] == 'del':
                try:
                    del_members[int(k_list[1])]
                except:
                    del_members.append(dict())
                del_members[int(k_list[1])][k_list[2]] = request.POST[k]
            elif k_list[0] == 'source':
                source[k_list[1]] = request.POST[k]
        return {'add': add_members, 'del': del_members, 'source': source}
    
    
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
            raise Exception('Wrong identifier: HTTP_GET[' + target_id + ']')
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
        elif source_id == 'MA_service_list':
            try:
                inverse = request.GET['inverse']
            except:
                inverse = None
            if inverse:
                adm_list_inactive = list()
                for admin in self.admins_pool.list_admins():
                    if not (admin in self.services_pool.list_admins(request.GET['name'], request.GET['hostname'])):
                        adm_list_inactive.append(admin)
                adm_list = adm_list_inactive
            else:
                adm_list = self.services_pool.list_admins(request.GET['name'], request.GET['hostname'])
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
            else:
                return "ERROR;;;Unrecognized HTTP POST request."
        except ACLError, e:
            return "ERROR;;;%s" % e.message
        except Exception, e1:
            return "ERROR;;;%r" % e1
        return "ERROR;;;Unrecognized HTTP POST request."

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
    
    
    def save(self):
        """
        Switch to call apropriate save function.
        Return value is a string starting with 'OK;;;' or 'ERROR;;;'
                (sets the color of the message on the client side).
        """
        target_id = request.POST['target_id']
        source_id = request.POST['source_id']
        if source_id == 'MA_site_list' and target_id == 'MA_adm_list':
            return self.save_adm_list()
        elif source_id == 'MA_adm_list' and target_id == 'MA_site_list':
            return self.save_site_list()
        elif source_id == 'MA_adm_list' and target_id == 'MA_service_list':
            return self.save_service_list()
        elif source_id == 'MA_service_list' and target_id == 'MA_adm_list':
            return self.save_adm_list2()
        return "ERROR;;;Unrecognized HTTP POST request."
    
    def save_adm_list(self):
        """
        Save new admins and remove deleted admins for corresponding site.
        Return value is a string starting with 'OK;;;' or 'ERROR;;;'
                (sets the color of the message on the client side).
        """
        data = self.__parse_http_post__()
        try:
            for k in data['add']:
                log.info('Added admin ' + k.__str__() + " for " + data['source'].__str__())
                self.sites_pool.add_admin(data['source']['name'], k['shib_unique_id'])
            for k in data['del']:
                log.info('Deleted admin ' + k.__str__() + " for " + data['source'].__str__())
                self.sites_pool.remove_admin(data['source']['name'], k['shib_unique_id'])
            return "OK;;;Successfully saved admins for site " + data['source']['name']
        except:
            return "ERROR;;;Failed to save admins for site " + data['source']['name']

    def save_adm_list2(self):
        """
        Save new admins and remove deleted admins for corresponding site.
        Return value is a string starting with 'OK;;;' or 'ERROR;;;'
                (sets the color of the message on the client side).
        """
        data = self.__parse_http_post__()
        try:
            for k in data['add']:
                log.info('Added admin ' + k.__str__() + " for " + data['source'].__str__())
                self.services_pool.add_admin(data['source']['name'], data['source']['hostname'], k['shib_unique_id'])
            for k in data['del']:
                log.info('Deleted admin ' + k.__str__() + " for " + data['source'].__str__())
                self.services_pool.remove_admin(data['source']['name'], data['source']['hostname'], k['shib_unique_id'])
            return "OK;;;Successfully saved admins for service " + data['source']['name'] + data['source']['hostname']
        except:
            return "ERROR;;;Failed to save admins for service " + data['source']['name'] + data['source']['hostname']
            
    def save_site_list(self):
        """
        Save new sites and remove deleted sites for corresponding admin.
        Return value is a string starting with 'OK;;;' or 'ERROR;;;'
                (sets the color of the message on the client side).
        """
        data = self.__parse_http_post__()
        try:
            for k in data['add']:
                log.info('Added site ' + k.__str__() + " for " + data['source'].__str__())
                self.sites_pool.add_admin(k['name'], data['source']['shib_unique_id'])
            for k in data['del']:
                log.info('Deleted site ' + k.__str__() + " for " + data['source'].__str__())
                self.sites_pool.remove_admin(k['name'], data['source']['shib_unique_id'])
            return "OK;;;Successfully saved sites for admin " + data['source']['shib_unique_id']
        except:
            return "ERROR;;;Failed to save sites for admin " + data['source']['shib_unique_id']
            
    def save_service_list(self):
        """
        Save new services and remove deleted services for corresponding admin.
        Return value is a string starting with 'OK;;;' or 'ERROR;;;'
                (sets the color of the message on the client side).
        """
        data = self.__parse_http_post__()
        try:
            for k in data['add']:
                log.info('Added service ' + k.__str__() + " for " + data['source'].__str__())
                self.services_pool.add_admin(k['name'], k['hostname'], data['source']['shib_unique_id'])
            for k in data['del']:
                log.info('Deleted service ' + k.__str__() + " for " + data['source'].__str__())
                self.services_pool.remove_admin(k['name'], k['hostname'], data['source']['shib_unique_id'])
            return "OK;;;Successfully saved services for admin " + data['source']['shib_unique_id']
        except:
            return "ERROR;;;Failed to save services for admin " + data['source']['shib_unique_id']
