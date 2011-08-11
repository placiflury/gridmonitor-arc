import logging

from pylons import tmpl_context as c
from pylons import app_globals as g
import gridmonitor.lib.helpers as h


from gridmonitor.lib.base import BaseController, render
from gridmonitor.controllers.cluster import ClusterController

log = logging.getLogger(__name__)

class PublicSummaryController(BaseController):
    """ Controller to populate the public summary
        web page(s)
    """

    def index(self):

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
        return render('/base/public.html')

