import logging
from pylons import config
from pylons import tmpl_context as c
from pylons.templating import render_mako as render

import gridmonitor.lib.helpers as h
from gridmonitor.lib.nagios_utils import get_nagios_scheduleddowntime_items
from gridadmin import GridadminController

from infocache.db import meta, schema # XXX not clean -> move to API

log = logging.getLogger(__name__)

class GridadminOverviewController(GridadminController):    
    """ Grid administrator overview controller """

    def __init__(self):
        GridadminController.__init__(self)
        self.nagios_core_tag = config['nagios_core'] # core services (defined by nagios hostgroup alias)
        self.nagios_ces_tag = config['nagios_ces']   # Grid computing elements  (defined by nagios hostgroup alias)
    
    def index(self):
        c.title = "Monitoring System: VO/Grid Admin View"
        c.menu_active = "Overview"
        
        c.heading = "Tactical Overview on Grid Services"
       

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

        # inactive COMPUTING ELEMENTS 

        c.db_inactive_clusters = h.get_cluster_names('inactive')


        # GETTING GIIS-LIST
        c.giises = meta.Session.query(schema.GiisMeta).all()
        
        return render('/derived/gridadmin/overview/index.html')
    
    def nagios(self):
        c.title = "Monitoring System: Site Admin View"
        c.menu_active = "Nagios Plugins"
        c.heading = "Details about Nagios Plugins"
        
        return render('/derived/user/overview/nagios.html')

    def reports(self):
        c.title = "Monitoring System: VO/Grid Admin View"
        c.menu_active = "Reports"
        c.heading = "Reports"
        return render('/derived/gridadmin/overview/report.html')	 
