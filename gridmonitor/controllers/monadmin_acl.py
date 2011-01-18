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
        if self.authorized == False:
            return render('/derived/monadmin/error/access_denied.html')

        return render('/derived/monadmin/acl/admin2site.html')
    
    def site2admin(self):
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "Manage ACL"
        c.heading = "Add  Site/Service to Administrator"
        if self.authorized == False:
            return render('/derived/monadmin/error/access_denied.html')
        
        return render('/derived/monadmin/acl/site2admin.html')

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
