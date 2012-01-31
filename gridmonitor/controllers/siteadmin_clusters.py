import logging
from pylons import tmpl_context as c
from pylons import app_globals as g
from pylons.templating import render_mako as render

import gridmonitor.lib.helpers as h


from siteadmin import SiteadminController

log = logging.getLogger(__name__)

QUEUE_NAME_LEN = 11   # default len of queue names. Names will either be padded or cut to that size

class SiteadminClustersController(SiteadminController):    

    def index(self):
        c.title = "Monitoring System: Site Admin View"
        c.menu_active = "My Clusters"
        c.heading = "Clusters  %s %s has siteadmin (view) permissions." % (c.user_name, c.user_surname)

        
        if not self.authorized:
            c.heading = "My Cluster(s)"
            return render('/derived/siteadmin/error/access_denied.html')
        
        actives = h.get_cluster_names('active')[0]
        c.siteadmin_clusters =  [ hn for hn in self.clusters if hn in actives]


        dps = {}
        for hn in c.siteadmin_clusters:
            dps[hn] = h.get_cluster_displayname(hn)

        c.display_names = dps

        return render('/derived/siteadmin/clusters/index.html')
        

    def show(self, id, queue =None):
        """id - cannonized display name of cluster"""

        c.cluster_hostname = id
        for cluster in c.cluster_menu:   #XXX rather primitive -> improve
            if id == cluster[1].split('/')[-1]:
                c.cluster_display_name = cluster[0]
                break

        c.menu_active = c.cluster_display_name

        if queue:
            c.queue_name = queue
            c.title = "Characteristics of queue '%s' on cluster '%s'" % (c.queue_name, c.cluster_display_name)
            c.queue_obj = g.get_queue(c.cluster_hostname, c.queue_name)
            if not c.queue_obj:
                # XXX -> error message
                log.warn("Info about queue '%s' of cluster '%s' not available anymore." % (id, queue))
                return render("/derived/user/clusters/index.html")
            c.heading = "Queue '%s' of cluster '%s'" % (queue, c.cluster_display_name)
            return render('/derived/user/clusters/show_queue.html')


        # else fetch cluster info
        c.cluster_obj = g.get_cluster(c.cluster_hostname)
        if not c.cluster_obj:
            # XXX -> error message
            log.warn("Info about cluster '%s' not available anymore." % id)
            return render("/derived/user/clusters/index.html")
        c.queues_names = g.get_cluster_queues_names(c.cluster_hostname)
        c.heading = " Cluster %s" % c.cluster_display_name
        c.title = "Characteristics of cluster '%s'" % (c.cluster_display_name)
        return render('/derived/user/clusters/show.html')  # we use the 'user' pages to display results.

    


