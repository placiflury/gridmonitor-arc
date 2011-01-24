import logging
from gridmonitor.lib.base import *
from monadmin import MonadminController
from monadmin import *
from hashlib import md5

log = logging.getLogger(__name__)
class MonadminSftController(MonadminController):
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
        c.menu_active = "Manage SFT"
        c.heading = "Listing current SFTs"
        # XXX fill in logic
        
        return render('/derived/monadmin/sft/index.html')
    
    def list(self):
        
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "View SFTs (dummy)"
        c.heading = "Listing current SFTs"
        # XXX fill in logic
        
        return render('/derived/monadmin/sft/index.html')
    
    def edit(self):
        
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "Edit SFTs (dummy)"
        c.heading = "Editing current SFTs"
        # XXX fill in logic
        
        return render('/derived/monadmin/sft/index.html')
        
    def clusters(self):
        
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "View SFTs (dummy)"
        c.heading = "Listing current SFTs"
        return render('/derived/monadmin/sft/clusters.html')
        
    def listusers(self):
        adm_list = self.admins_pool.list_admins()
        return self.__build_json__(adm_list, ADMIN_KEYMAP, ADMIN_KEYMAP_ORDER, { \
                            'id_key': 'shib_unique_id', \
                            'show_keys': [ 'shib_surname', 'shib_given_name'], \
                            })
        
    def listvos(self):
        adm_list = self.admins_pool.list_admins()
        return self.__build_json__(adm_list, ADMIN_KEYMAP, ADMIN_KEYMAP_ORDER, { \
                            'id_key': 'shib_unique_id', \
                            'show_keys': [ 'shib_surname', 'shib_given_name'], \
                            })
                            
    def listclusters(self):
        adm_list = self.admins_pool.list_admins()
        return self.__build_json__(adm_list, ADMIN_KEYMAP, ADMIN_KEYMAP_ORDER, { \
                            'id_key': 'shib_unique_id', \
                            'show_keys': [ 'shib_surname', 'shib_given_name'], \
                            })
                            
    def listtests(self):
        adm_list = self.admins_pool.list_admins()
        return self.__build_json__(adm_list, ADMIN_KEYMAP, ADMIN_KEYMAP_ORDER, { \
                            'id_key': 'shib_unique_id', \
                            'show_keys': [ 'shib_surname', 'shib_given_name'], \
                            })
