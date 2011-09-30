import logging
import json

from pylons import tmpl_context as c
from pylons.templating import render_mako as render

import gridmonitor.lib.helpers as h

from siteadmin import SiteadminController

log = logging.getLogger(__name__)

class SiteadminJobsController(SiteadminController):    


    def index(self):
        c.title = "Monitoring System: Site Admin View"
        c.menu_active = "Jobs"
        c.heading = "Jobs/Users on Your Cluster(s)"  # default
 
        if not self.authorized:
            c.heading = "Nothing to View"  # default
            return render('/derived/siteadmin/error/access_denied.html')

        actives = h.get_cluster_names('active')[0]
    
        c.siteadmin_clusters =  [ hn for hn in self.clusters if hn in actives]


        
        return render('/derived/siteadmin/jobs/index.html')

