import logging
from datetime import datetime
from pylons import session
from pylons import config 
from pylons import tmpl_context as c
from pylons import app_globals as g
from pylons.templating import render_mako as render

import gridmonitor.lib.helpers as h
from gridmonitor.lib.nagios_utils import get_nagios_scheduleddowntime_items


from user import UserController

log = logging.getLogger(__name__)

class UserOverviewController(UserController):

    def __init__(self):
        UserController.__init__(self)
        
    def index(self):
        c.title = "Monitoring System: User View"
        c.menu_active = "Overview"
        c.heading = "Welcome  %s %s" % (c.user_name, c.user_surname)

        c.now_scheduled_down = h.get_cluster_names('downtime')

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
            # the very same scheduled downtime (which is necessarily true...)
            dti[hostname]['start_t'] = ditem.scheduled_start_time
            dti[hostname]['end_t'] = ditem.scheduled_end_time
            dti[hostname]['reason'] = ditem.comment_data
        
        c.down_time_items  = dti
            
        return render('/derived/user/overview/index.html')

 
    def nagios(self):
        c.title = "Monitoring System: User View"
        c.menu_active="Nagios Plugins"
        c.heading = "Details about Nagios Plugins"
    
        return render('/derived/user/overview/nagios.html')
    
    def reports(self):
        c.title = "Monitoring System: User View"
        c.menu_active="Reports"
        c.heading = "Reports"
        return render('/derived/user/overview/report.html')
	 
