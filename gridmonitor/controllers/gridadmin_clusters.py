import logging
from pylons import config
from pylons import tmpl_context as c
from pylons import app_globals as g
from pylons.templating import render_mako as render

import gridmonitor.lib.helpers as h

from gridadmin import GridadminController
from gridmonitor.controllers.cluster import ClusterController


log = logging.getLogger(__name__)


class GridadminClustersController(GridadminController):    

    def index(self):
        c.title = 'GridMonitor: Site Admin View. Resources of %s' % config['gridname']
        c.menu_active = "Grid Clusters"
        c.heading = '%s  Resources (Overview)' % config['gridname']

        clusters = g.get_clusters()

        c.clusters_meta = {}
        for hostname, cl_obj in clusters.items():
            c.clusters_meta[hostname] = {}
            for key in ClusterController.CLUSTER_META:
                values = cl_obj.get_attribute_values(key)
                if values:
                    c.clusters_meta[hostname][key] = values[0]
        
        active_clusters = h.get_cluster_names('active')[0]
        inactive_clusters = h.get_cluster_names('inactive')[0]
        scheddown_clusters = h.get_cluster_names('downtime')[0]
        
        all_clusters = []
        for cl in active_clusters + inactive_clusters + scheddown_clusters:
            if cl not in all_clusters:
                all_clusters.append(cl)

        all_clusters.sort()
        c.all_clusters = all_clusters
        
        
        return render('/derived/gridadmin/clusters/index.html')


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

    


