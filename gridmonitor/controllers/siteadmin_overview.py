import logging
from pylons import config
from pylons import tmpl_context as c
from pylons.templating import render_mako as render

import gridmonitor.lib.helpers as h

from siteadmin import SiteadminController

from gridmonitor.lib.nagios_utils import get_nagios_scheduleddowntime_items


log = logging.getLogger(__name__)

class SiteadminOverviewController(SiteadminController):    

    def __init__(self):
        SiteadminController.__init__(self)
        self.nagios_ces_tag = config['nagios_ces']   # Grid computing elements  (defined by nagios hostgroup alias)
        self.nagios_core_tag = config['nagios_core']   # Grid computing elements  (defined by nagios hostgroup alias)
    
    def index(self):
        c.title = "Monitoring System: Site Admin View"
        c.menu_active = "Overview"
        c.heading = "<span class='warn_status'> You are not authorized to view content of this page.</span>"  # default
        
        if not self.authorized:
            c.heading= "Site Overview"
            return render('/derived/siteadmin/error/access_denied.html')

        c.heading = "Tactical Overview on Your Services"

        c.site_cores = self.cores
        c.site_ces = self.clusters


        # XXX FIX BELOW THINGS
        
        c.now_scheduled_down = h.get_cluster_names('downtime')[0]

        # DOWNTIME INFO        
        dti = {} 
        for ditem in get_nagios_scheduleddowntime_items():
            hostname = ditem.generic_object.name1
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

        return render('/derived/siteadmin/overview/index.html')

    def nagios(self):
        c.title = "Monitoring System: User View"
        c.menu_active = "Nagios Plugins"
        c.heading = "Details about Nagios Plugins"
    
        return render('/derived/user/overview/nagios.html')
    
    def reports(self):
        c.title = "Monitoring System: User View"
        c.menu_active = "Reports"
        c.heading = "Reports"
        return render('/derived/user/overview/report.html')
	 
