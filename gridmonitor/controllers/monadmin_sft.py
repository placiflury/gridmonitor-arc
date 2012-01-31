import logging
import json 

from pylons import request
from pylons import tmpl_context as c
from pylons.templating import render_mako as render

from gridmonitor.model.sft.name_mapping import * 
from sft.utils import helpers

from monadmin import MonadminController

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
        json_data = self.__build_json_parsable__(data_list, keymap, keymap_order, opt_params)
        return json.dumps(json_data)
        
    def __build_json_parsable__(self, data_list, keymap, keymap_order, opt_params):
        """
        Creates a valid JSON syntax of SQLAlchemy Objects.
        Parameters:
        data_list: list of SQLAlchemy objects
        keymap: Dict of human readable strings for every key
        keymap_order: List of all keys to guarantee right order
        opt_params: Dict of params that should be appended (without processing) to the JSON string
                    currently: string id_key, list show_keys, string parent_key
        """
        if data_list == None:
            data_list = list()
        if opt_params == None:
            opt_params = dict()
        json_data = dict()
        json_data['order_keys'] = keymap_order
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
            if opt_params['id_key'] == 'hash':
                item_dict['hash'] = hash(item_dict.__str__())
            json_data['members'].append(item_dict)
        for p in opt_params:
            json_data[p] = opt_params[p]
        return json_data
        
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
        
    def index(self):
        
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "Manage SFTs"
        c.heading = "Manage Site Functional Tests (SFTs)"
        # XXX fill in logic
        
        return render('/derived/monadmin/sft/index.html')
        
    def edit(self):
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "View SFTs (dummy)"
        c.heading = "Listing current SFTs"
        
        c.list_title = 'SFTs'
        c.list_url = 'listsfts'
        c.list_editor_url = 'changesft'
        return render('/derived/monadmin/sft/sfts.html')
        
    def clusters(self):
        
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "View SFTs (dummy)"
        c.heading = "Manage clusters and cluster groups"
        
        c.list_title = 'Clusters'
        c.list_gr_title = 'Clusters groups'
        c.short_identifier = 'cluster'
        c.list_url = 'listclusters'
        c.list_gr_url = 'listclustergroups'
        c.list_editor_url = 'changecluster'
        c.list_gr_editor_url = 'changeclustergroup'
        c.exchanger_url = 'saveclusterexchange'
        return render('/derived/monadmin/sft/resources.html')
        
    def vos(self):
        
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "View SFTs (dummy)"
        c.heading = "Manage VOs and VO groups"
        
        c.list_title = 'VOs'
        c.list_gr_title = 'VO groups'
        c.short_identifier = 'vo'
        c.list_url = 'listvos'
        c.list_gr_url = 'listvogroups'
        c.list_editor_url = 'changevo'
        c.list_gr_editor_url = 'changevogroup'
        c.exchanger_url = 'savevoexchange'
        return render('/derived/monadmin/sft/resources.html')
        
    def users(self):
        
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "View SFTs (dummy)"
        c.heading = "Manage users and VO memberships"

        c.list_title = 'Users'
        c.list_gr_title = 'VOs'
        c.short_identifier = 'user'
        c.list_url = 'listusers'
        c.list_gr_url = 'listvos'
        c.list_editor_url = 'changeuser'
        c.list_gr_editor_url = 'changevo'
        c.exchanger_url = 'saveuserexchange'
        return render('/derived/monadmin/sft/resources.html')
        
    def tests(self):
        
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "View SFTs (dummy)"
        c.heading = "Manage XRSL-tests and test suits"
        
        c.list_title = 'Tests'
        c.list_gr_title = 'Testsuits'
        c.short_identifier = 'test'
        c.list_url = 'listtests'
        c.list_gr_url = 'listtestsuits'
        c.list_editor_url = 'changetest'
        c.list_gr_editor_url = 'changetestsuit'
        c.exchanger_url = 'savetestexchange'
        return render('/derived/monadmin/sft/resources.html')
        
    
    def listsfts(self):
        sft_list = self.sfts.list_sfts()
        return self.__build_json__(sft_list, SFT_KEYMAP, SFT_KEYMAP_ORDER, { \
                            'id_key': 'name', \
                            'show_keys': [ 'name'], \
                            })
    
    def changesft(self):
        try:
            if request.POST['button'] == 'del':
                self.sfts.remove_sft(request.POST['name'])
                return "OK;;;Deleted SFT " + request.POST['name'] + " successfully."
            elif request.POST['button'] == 'save':
                self.sfts.add_sft( request.POST['name'],\
                                        request.POST['cluster_group'],\
                                        request.POST['vo_group'],\
                                        request.POST['test_suit'])
                try:
                    helpers.parse_cron_entry(request.POST['minute'], 59)
                    helpers.parse_cron_entry(request.POST['hour'], 23)
                    helpers.parse_cron_entry(request.POST['day'], 31)
                    helpers.parse_cron_entry(request.POST['day_of_week'], 6)
                    helpers.parse_cron_entry(request.POST['month'], 12)
                except helpers.CronError, e:
                    return "ERROR;;;%s" % e.message
                self.sfts.set_exectime(request.POST['name'],\
                                            request.POST['minute'],\
                                            request.POST['hour'],\
                                            request.POST['day'],\
                                            request.POST['month'],\
                                            request.POST['day_of_week'])
                return "OK;;;Changed SFT " + request.POST['name'] + " successfully."
            else:
                return "ERROR;;;Unrecognized HTTP POST request."
        except Exception, e1:
            return "ERROR;;;%r" % e1
        return "ERROR;;;Unrecognized HTTP POST request."
        
    def listusers(self):
        try:
            source_id = request.GET['source_id']
            target_id = request.GET['target_id']
        except:
            source_id = None;
            target_id = 'MA_sft_user_list';
        if target_id != 'MA_sft_user_list':
            raise Exception('Wrong identifier: HTTP_GET[' + target_id + ']')
        if source_id == 'MA_sft_user_gr_list':
            try:
                inverse = request.GET['inverse']
            except:
                inverse = None
            if inverse:
                all_users_list = self.sft_users.list_users()
                user_list_inactive = list()
                user_list = self.sft_vo_users.list_users(request.GET['name'])
                if not (user_list):
                    user_list = list()
                if not (all_users_list):
                    all_users_list = list()
                for user in all_users_list:
                    if not (user in user_list):
                        user_list_inactive.append(user)
                user_list = user_list_inactive
            else:
                user_list = self.sft_vo_users.list_users(request.GET['name'])
        elif source_id == None:
            user_list = self.sft_users.list_users()
        return self.__build_json__(user_list, USER_KEYMAP, USER_KEYMAP_ORDER, { \
                            'id_key': 'DN', \
                            'show_keys': [ 'display_name'], \
                            })
    
    def changeuser(self):
        try:
            if request.POST['button'] == 'del':
                self.sft_users.remove_user(request.POST['DN'])
                return "OK;;;Deleted User " + request.POST['DN'] + " successfully."
            elif request.POST['button'] == 'save':
                self.sft_users.add_user(request.POST['DN'], request.POST['display_name'], '4bs0lut31n5ecurEp455WD')
                return "OK;;;Changed User " + request.POST['DN'] + " successfully."
            else:
                return "ERROR;;;Unrecognized HTTP POST request."
        except Exception, e1:
            return "ERROR;;;%r" % e1
        return "ERROR;;;Unrecognized HTTP POST request."
    
    def saveuserexchange(self):
        target_id = request.POST['target_id']
        source_id = request.POST['source_id']
        if (target_id != 'MA_sft_user_list' and source_id != 'MA_sft_vo_list'):
            return "ERROR;;;Unrecognized HTTP POST request."
        data = self.__parse_http_post__()
        try:
            changes = 0;
            for k in data['add']:
                log.info('Added user ' + k.__str__() + " for " + data['source'].__str__())
                self.sft_vo_users.add_user(data['source']['name'], k['DN'])
                changes += 1
            for k in data['del']:
                log.info('Deleted user ' + k.__str__() + " for " + data['source'].__str__())
                self.sft_vo_users.remove_user(data['source']['name'], k['DN'])
                changes += 1
            if changes > 0:
                return "OK;;;Successfully saved users for VO " + data['source']['name']
            else:
                return
        except:
            return "ERROR;;;Failed to save users for VO " + data['source']['name']
    
    def listvos(self):
        try:
            source_id = request.GET['source_id']
            target_id = request.GET['target_id']
        except:
            source_id = None;
            target_id = 'MA_sft_vo_list';
        if target_id != 'MA_sft_vo_list':
            raise Exception('Wrong identifier: HTTP_GET[' + target_id + ']')
        if source_id == 'MA_sft_vo_gr_list':
            try:
                inverse = request.GET['inverse']
            except:
                inverse = None
            if inverse:
                all_vos_list = self.sft_vos.list_vos()
                vo_list_inactive = list()
                vo_list = self.sft_vo_groups.list_vos(request.GET['name'])
                if not (vo_list):
                    vo_list = list()
                if not (all_vos_list):
                    all_vos_list = list()
                for vo in all_vos_list:
                    if not (vo in vo_list):
                        vo_list_inactive.append(vo)
                vo_list = vo_list_inactive
            else:
                vo_list = self.sft_vo_groups.list_vos(request.GET['name'])
        elif source_id == None:
            vo_list = self.sft_vos.list_vos()
        return self.__build_json__(vo_list, VO_KEYMAP, VO_KEYMAP_ORDER, { \
                            'id_key': 'name', \
                            'show_keys': [ 'name'], \
                            })
    
    def changevo(self):
        try:
            if request.POST['button'] == 'del':
                self.sft_vos.remove_vo(request.POST['name'])
                return "OK;;;Deleted vo " + request.POST['name'] + " successfully."
            elif request.POST['button'] == 'save':
                self.sft_vos.add_vo(request.POST['name'], request.POST['server'])
                return "OK;;;Changed vo " + request.POST['name'] + " successfully."
            else:
                return "ERROR;;;Unrecognized HTTP POST request."
        except Exception, e1:
            return "ERROR;;;%r" % e1
        return "ERROR;;;Unrecognized HTTP POST request."
    
    def listvogroups(self, id=None):
        vo_gr_list = self.sft_vo_groups.list_groups()
        if not id:
            return self.__build_json__(vo_gr_list, VO_GR_KEYMAP, VO_GR_KEYMAP_ORDER, { \
                                'id_key': 'name', \
                                'show_keys': [ 'name'], \
                                })
        else:
            json_data = self.__build_json_parsable__(vo_gr_list, VO_GR_KEYMAP, VO_GR_KEYMAP_ORDER, { \
                                'id_key': 'name', \
                                'show_keys': [ 'name'], \
                                })
            json_data['submembers'] = dict()
            for group in vo_gr_list:
                vo_list = self.sft_vo_groups.list_vos(group.name)
                json_data['submembers'][group.name] = self.__build_json_parsable__(vo_list, VO_KEYMAP, VO_KEYMAP_ORDER, { \
                                    'id_key': 'name', \
                                    'show_keys': [ 'name'], \
                                    })
                json_data['id'] = id
            return json.dumps(json_data)
    
    def changevogroup(self):
        try:
            if request.POST['button'] == 'del':
                self.sft_vo_groups.remove_group(request.POST['name'])
                return "OK;;;Deleted vo group " + request.POST['name'] + " successfully."
            elif request.POST['button'] == 'save':
                self.sft_vo_groups.create_group(request.POST['name'])
                return "OK;;;Changed vo group " + request.POST['name'] + " successfully."
            else:
                return "ERROR;;;Unrecognized HTTP POST request."
        except Exception, e1:
            return "ERROR;;;%r" % e1
        return "ERROR;;;Unrecognized HTTP POST request."
    
    def savevoexchange(self):
        target_id = request.POST['target_id']
        source_id = request.POST['source_id']
        if (target_id != 'MA_sft_vo_list' and source_id != 'MA_sft_vo_gr_list'):
            return "ERROR;;;Unrecognized HTTP POST request."
        data = self.__parse_http_post__()
        try:
            changes = 0;
            for k in data['add']:
                self.sft_vo_groups.add_vo(data['source']['name'], k['name'])
                log.info('Added vo ' + k.__str__() + " for " + data['source'].__str__())
                changes += 1
            for k in data['del']:
                self.sft_vo_groups.remove_vo(data['source']['name'], k['name'])
                log.info('Deleted vo ' + k.__str__() + " for " + data['source'].__str__())
                changes += 1
            if changes > 0:
                return "OK;;;Successfully saved VOs for VO group " + data['source']['name']
            else:
                return
        except:
            return "ERROR;;;Failed to save VOs for VO group " + data['source']['name']
    
    
    def listclusters(self):
        try:
            source_id = request.GET['source_id']
            target_id = request.GET['target_id']
        except:
            source_id = None;
            target_id = 'MA_sft_cluster_list';
        if target_id != 'MA_sft_cluster_list':
            raise Exception('Wrong identifier: HTTP_GET[' + target_id + ']')
        if source_id == 'MA_sft_cluster_gr_list':
            try:
                inverse = request.GET['inverse']
            except:
                inverse = None
            if inverse:
                all_clusters_list = self.sft_clusters.list_clusters()
                cluster_list_inactive = list()
                cluster_list = self.sft_cluster_groups.list_clusters(request.GET['name'])
                if not (cluster_list):
                    cluster_list = list()
                if not (all_clusters_list):
                    all_clusters_list = list()
                for cluster in all_clusters_list:
                    if not (cluster in cluster_list):
                        cluster_list_inactive.append(cluster)
                cluster_list = cluster_list_inactive
            else:
                cluster_list = self.sft_cluster_groups.list_clusters(request.GET['name'])
        elif source_id == None:
            cluster_list = self.sft_clusters.list_clusters()
        return self.__build_json__(cluster_list, CLUSTER_KEYMAP, CLUSTER_KEYMAP_ORDER, { \
                            'id_key': 'hostname', \
                            'show_keys': [ 'hostname'], \
                            })
    
    def changecluster(self):
        try:
            if request.POST['button'] == 'del':
                self.sft_clusters.remove_cluster(request.POST['hostname'])
                return "OK;;;Deleted cluster " + request.POST['hostname'] + " successfully."
            elif request.POST['button'] == 'save':
                self.sft_clusters.add_cluster(request.POST['hostname'], request.POST['alias'])
                return "OK;;;Changed cluster " + request.POST['hostname'] + " successfully."
            else:
                return "ERROR;;;Unrecognized HTTP POST request."
        except Exception, e1:
            return "ERROR;;;%r" % e1
        return "ERROR;;;Unrecognized HTTP POST request."
    
        
    def listclustergroups(self, id=None):
        cluster_gr_list = self.sft_cluster_groups.list_groups()
        if not id:
            return self.__build_json__(cluster_gr_list, CLUSTER_GR_KEYMAP, CLUSTER_GR_KEYMAP_ORDER, { \
                                'id_key': 'name', \
                                'show_keys': [ 'name'], \
                                })
        else:
            json_data = self.__build_json_parsable__(cluster_gr_list, CLUSTER_GR_KEYMAP, CLUSTER_GR_KEYMAP_ORDER, { \
                                'id_key': 'name', \
                                'show_keys': [ 'name'], \
                                })
            json_data['submembers'] = dict()
            for group in cluster_gr_list:
                cluster_list = self.sft_cluster_groups.list_clusters(group.name)
                json_data['submembers'][group.name] = self.__build_json_parsable__(cluster_list, CLUSTER_KEYMAP, CLUSTER_KEYMAP_ORDER, { \
                                    'id_key': 'hostname', \
                                    'show_keys': [ 'hostname'], \
                                    })
                json_data['id'] = id
            return json.dumps(json_data)
    
    def changeclustergroup(self):
        try:
            if request.POST['button'] == 'del':
                self.sft_cluster_groups.remove_group(request.POST['name'])
                return "OK;;;Deleted cluster group " + request.POST['name'] + " successfully."
            elif request.POST['button'] == 'save':
                self.sft_cluster_groups.create_group(request.POST['name'])
                return "OK;;;Changed cluster group " + request.POST['name'] + " successfully."
            else:
                return "ERROR;;;Unrecognized HTTP POST request."
        except Exception, e1:
            return "ERROR;;;%r" % e1
        return "ERROR;;;Unrecognized HTTP POST request."
    
    def saveclusterexchange(self):
        target_id = request.POST['target_id']
        source_id = request.POST['source_id']
        if (target_id != 'MA_sft_cluster_list' and source_id != 'MA_sft_cluster_gr_list'):
            return "ERROR;;;Unrecognized HTTP POST request."
        data = self.__parse_http_post__()
        try:
            changes = 0;
            for k in data['add']:
                log.info('Added cluster ' + k.__str__() + " for " + data['source'].__str__())
                self.sft_cluster_groups.add_cluster(data['source']['name'], k['hostname'])
                changes += 1
            for k in data['del']:
                log.info('Deleted cluster ' + k.__str__() + " for " + data['source'].__str__())
                self.sft_cluster_groups.remove_cluster(data['source']['name'], k['hostname'])
                changes += 1
            if changes > 0:
                return "OK;;;Successfully saved clusters for cluster group " + data['source']['name']
            else:
                return
        except:
            return "ERROR;;;Failed to save clusters for cluster group " + data['source']['name']
                            
    def listtests(self):
        try:
            source_id = request.GET['source_id']
            target_id = request.GET['target_id']
        except:
            source_id = None;
            target_id = 'MA_sft_test_list';
        if target_id != 'MA_sft_test_list':
            raise Exception('Wrong identifier: HTTP_GET[' + target_id + ']')
        if source_id == 'MA_sft_test_gr_list':
            try:
                inverse = request.GET['inverse']
            except:
                inverse = None
            if inverse:
                all_tests_list = self.sft_tests.list_tests()
                test_list_inactive = list()
                test_list = self.sft_test_suits.list_tests(request.GET['name'])
                if not (test_list):
                    test_list = list()
                if not (all_tests_list):
                    all_tests_list = list()
                for test in all_tests_list:
                    if not (test in test_list):
                        test_list_inactive.append(test)
                test_list = test_list_inactive
            else:
                test_list = self.sft_test_suits.list_tests(request.GET['name'])
        elif source_id == None:
            test_list = self.sft_tests.list_tests()
        return self.__build_json__(test_list, TEST_KEYMAP, TEST_KEYMAP_ORDER, { \
                            'id_key': 'name', \
                            'show_keys': [ 'name'], \
                            })
    
    def changetest(self):
        try:
            if request.POST['button'] == 'del':
                self.sft_tests.remove_test(request.POST['name'])
                return "OK;;;Deleted test " + request.POST['name'] + " successfully."
            elif request.POST['button'] == 'save':
                self.sft_tests.add_test(request.POST['name'], request.POST['xrsl'])
                return "OK;;;Changed test " + request.POST['name'] + " successfully."
            else:
                return "ERROR;;;Unrecognized HTTP POST request."
        except Exception, e1:
            return "ERROR;;;%r" % e1
        return "ERROR;;;Unrecognized HTTP POST request."
    
    def listtestsuits(self, id=None):
        test_suit_list = self.sft_test_suits.list_testsuits()
        if not id:
            return self.__build_json__(test_suit_list, TEST_SUIT_KEYMAP, TEST_SUIT_KEYMAP_ORDER, { \
                                'id_key': 'name', \
                                'show_keys': [ 'name'], \
                                })
        else:
            json_data = self.__build_json_parsable__(test_suit_list, TEST_SUIT_KEYMAP, TEST_SUIT_KEYMAP_ORDER, { \
                                'id_key': 'name', \
                                'show_keys': [ 'name'], \
                                })
            json_data['submembers'] = dict()
            for group in test_suit_list:
                test_list = self.sft_test_suits.list_tests(group.name)
                json_data['submembers'][group.name] = self.__build_json_parsable__(test_list, TEST_KEYMAP, TEST_KEYMAP_ORDER, { \
                                    'id_key': 'name', \
                                    'show_keys': [ 'name'], \
                                    })
                json_data['id'] = id
            return json.dumps(json_data)
    
    def changetestsuit(self):
        try:
            if request.POST['button'] == 'del':
                self.sft_test_suits.remove_suit(request.POST['name'])
                return "OK;;;Deleted testsuit " + request.POST['name'] + " successfully."
            elif request.POST['button'] == 'save':
                self.sft_test_suits.create_suit(request.POST['name'])
                return "OK;;;Changed testsuit " + request.POST['name'] + " successfully."
            else:
                return "ERROR;;;Unrecognized HTTP POST request."
        except Exception, e1:
            return "ERROR;;;%r" % e1
        return "ERROR;;;Unrecognized HTTP POST request."
    
    def savetestexchange(self):
        target_id = request.POST['target_id']
        source_id = request.POST['source_id']
        if (target_id != 'MA_sft_test_list' and source_id != 'MA_sft_test_gr_list'):
            return "ERROR;;;Unrecognized HTTP POST request."
        data = self.__parse_http_post__()
        try:
            changes = 0;
            for k in data['add']:
                log.info('Added test ' + k.__str__() + " for " + data['source'].__str__())
                self.sft_test_suits.add_test(data['source']['name'], k['name'])
                changes += 1
            for k in data['del']:
                log.info('Deleted test ' + k.__str__() + " for " + data['source'].__str__())
                self.sft_test_suits.remove_test(data['source']['name'], k['name'])
                changes += 1
            if changes > 0:
                return "OK;;;Successfully saved tests for test suit " + data['source']['name']
            else:
                return
        except:
            return "ERROR;;;Failed to save tests for test suit " + data['source']['name']
