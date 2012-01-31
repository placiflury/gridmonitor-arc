import logging
from pylons import config
from pylons import tmpl_context as c
from pylons.templating import render_mako as render

import gridmonitor.lib.helpers as h
from gridmonitor.lib.nagios_utils import get_nagios_scheduleddowntime_items

from siteadmin import SiteadminController


log = logging.getLogger(__name__)

class SiteadminOverviewController(SiteadminController):    

    def __init__(self):
        SiteadminController.__init__(self)
        self.nagios_ces_tag = config['nagios_ces']   # Grid computing elements  (defined by nagios hostgroup alias)
        self.nagios_core_tag = config['nagios_core']   # Grid computing elements  (defined by nagios hostgroup alias)
    
    def index(self):
        c.title = "Monitoring System: Site Admin View"
        c.menu_active = "Overview"
        c.heading = "<span class='warn_status'> You are not authorized to view the content of this page.</span>"  # default
        
        if not self.authorized:
            c.heading = "Site Overview"
            return render('/derived/siteadmin/error/access_denied.html')

        c.heading = "Tactical Overview on Your Services"

        c.site_cores = self.cores
        c.site_ces = self.clusters

        c.now_scheduled_down = h.get_cluster_names('downtime')[0]

        # DOWNTIME INFO        
        dti = {} 
        for ditem in get_nagios_scheduleddowntime_items():
            hostname = ditem.generic_object.name1
            if hostname in self.cores or hostname in self.clusters:
                if not dti.has_key(hostname):
                    dti[hostname] = {'services' : []}
                if ditem.generic_object.name2:
                    service = ditem.generic_object.name2
                    dti[hostname]['services'].append(service)
                # notice, we assume that all services of the host have
                # the very same scheduled downtime (which is not necessarily true...)
                dti[hostname]['start_t'] = ditem.scheduled_start_time
                dti[hostname]['end_t'] = ditem.scheduled_end_time
                dti[hostname]['reason'] = ditem.comment_data
        
        c.down_time_items  = dti


        actives = h.get_cluster_names('active')[0]
        cld = {}
    

        c.no_info_clusters =  []
        for hostname in self.clusters:
            if hostname in actives:
                cld[hostname] = h.get_cluster_details(hostname)
            # else: -> report cluster is not 'known' despite been in the ACL
            else:
                c.no_info_clusters.append(hostname)

        c.clusters_details = cld

        #XXX  most recent SFT results 
        #XXX jobs/VO (?)


        return render('/derived/siteadmin/overview/index.html')

    def nagios(self):
        c.title = "Monitoring System: Site Admin View"
        c.menu_active = "Nagios Plugins"
        c.heading = "Nagios Plugins Output for Your Services"
        c.site_cores = self.cores
        c.site_ces = self.clusters
    
        return render('/derived/siteadmin/overview/nagios.html')
    
    def reports(self):
        c.title = "Monitoring System: User View"
        c.menu_active = "Reports"
        c.heading = "Reports"
        return render('/derived/user/overview/report.html')
	 
