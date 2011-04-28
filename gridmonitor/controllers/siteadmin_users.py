import logging
from pylons import tmpl_context as c
from pylons import app_globals as g
from pylons.templating import render_mako as render


from siteadmin import SiteadminController



log = logging.getLogger(__name__)

class SiteadminUsersController(SiteadminController):    

    def index(self):
        c.title = "Monitoring System: Site Admin View"
        c.menu_active = "Users"
        c.heading = "Users allowed on your cluster(s)"  # default
        
            
        # XXX support multiple clusters, now we just take first if there is any
        
        if not self.authorized:
            c.heading = "Nothing to View"
            return render('/derived/siteadmin/error/access_denied.html')
        

        c.clusters_bag = dict()

        handler = g.get_data_handler()
        
        for cluster_hostname in self.clusters: 
            cluster_obj = g.get_cluster(cluster_hostname)
            if not cluster_obj:
                continue
            c.clusters_bag[cluster_hostname] = list()
            
            cluster_allowed_users = handler.get_cluster_users(cluster_hostname)
            # remove duplicates due to 'emailAddress='
            for user in cluster_allowed_users: 
                if user.find('emailAddress=') >=0:
                    continue
                c.clusters_bag[cluster_hostname].append(user)    
        return render('/derived/siteadmin/users/index.html')

