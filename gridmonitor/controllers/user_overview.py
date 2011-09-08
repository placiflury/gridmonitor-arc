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


        # MY JOBS INFO
        c.slcs_dn = None
        c.browser_dn = None

        if session.has_key('user_slcs_obj'):
            user_slcs_obj = session['user_slcs_obj']
            c.slcs_dn = user_slcs_obj.get_dn()
        
        if session.has_key('user_client_dn'):
            c.browser_dn = session['user_client_dn']


        # GRID LOAD + max load cluster + min load cluster => XXX dynamic!!!
        c.max_load_cluster=dict(name = None, tot_running = 0,
                tot_cpus = 0, tot_queued = 0, relative_load = -1)
        c.min_load_cluster=dict(name = None, tot_running = 0,
                tot_cpus = 0, tot_queued = 0, relative_load = -1)
        """
        Ranking of 'load' on clusters:   
            1. 'relative_load' = (#jobs_running + #jobs_queued)/# cpus  -> smaller number better
            2. on equal 'load' cluster with more cpus considered to have less effective load.
        """

        for cluster in c.cluster_menu:
            hostname = cluster[1].split('/')[-1] # stripping hostname from url
            display_name = cluster[0]
            cpus = g.get_cluster_stats(hostname,'stats_cpus')
            totaljobs = g.get_cluster_stats(hostname,'stats_totaljobs')
            usedcpus = g.get_cluster_stats(hostname,'stats_usedcpus')
            
            tot_queued = 0
            for qname in g.get_cluster_queues_names(hostname):
                gqd = g.get_queue_stats(hostname, qname, 'stats_grid_queued')
                lqd= g.get_queue_stats(hostname, qname, 'stats_local_queued')
                plrms = g.get_queue_stats(hostname, qname, 'stats_prelrms_queued')
                
                tot_queued = gqd + lqd + plrms

            # Finding max loaded cluster and min loaded cluster         
            # totaljobs ~ # jobs_running + # jobs_queued
            if cpus > 0:
                if totaljobs == 0: # little trick to favor large clusters over small if no jobs are around
                    tj = 0.5
                else:
                    tj = totaljobs
                tj += tot_queued
                relative_cluster_load = tj/float(cpus)
            else:
                continue

            if not c.max_load_cluster['name']:   # set both min=max load  (first cluster)
                c.max_load_cluster['name'] = display_name
                c.min_load_cluster['name'] = display_name
                c.min_load_cluster['tot_running'] = usedcpus  # instead of grid_running + running
                c.max_load_cluster['tot_running'] = usedcpus 
                c.max_load_cluster['tot_cpus'] = cpus
                c.min_load_cluster['tot_cpus'] = cpus
                c.max_load_cluster['tot_queued'] = tot_queued 
                c.min_load_cluster['tot_queued'] = tot_queued
                c.max_load_cluster['relative_load'] = relative_cluster_load
                c.min_load_cluster['relative_load'] = relative_cluster_load
            elif relative_cluster_load > c.max_load_cluster['relative_load']: 
                c.max_load_cluster['name'] = display_name
                c.max_load_cluster['tot_running'] = usedcpus 
                c.max_load_cluster['tot_cpus'] = cpus
                c.max_load_cluster['tot_queued'] = tot_queued 
                c.max_load_cluster['relative_load'] = relative_cluster_load
            elif (relative_cluster_load == c.max_load_cluster['relative_load'] ) and \
                    (cpus < c.max_load_cluster['tot_cpus']):  
                c.max_load_cluster['name'] = display_name
                c.max_load_cluster['tot_running'] = usedcpus 
                c.max_load_cluster['tot_cpus'] = cpus
                c.max_load_cluster['tot_queued'] = tot_queued 
                c.max_load_cluster['relative_load'] = relative_cluster_load
            
            if relative_cluster_load <  c.min_load_cluster['relative_load']: 
                c.min_load_cluster['name'] = display_name
                c.min_load_cluster['tot_running'] = usedcpus 
                c.min_load_cluster['tot_cpus'] = cpus
                c.min_load_cluster['tot_queued'] = tot_queued 
                c.min_load_cluster['relative_load'] = relative_cluster_load
            elif (relative_cluster_load == c.min_load_cluster['relative_load'] ) and \
                (cpus > c.min_load_cluster['tot_cpus']):  
                c.min_load_cluster['name'] = display_name
                c.min_load_cluster['tot_running'] = usedcpus 
                c.min_load_cluster['tot_cpus'] = cpus
                c.min_load_cluster['tot_queued'] = tot_queued 
                c.min_load_cluster['relative_load'] = relative_cluster_load

            
        return render('/derived/user/overview/index.html')

 
    def core(self):
        c.title = "Monitoring System: User View"
        c.menu_active="Core Services"
        c.heading = "Services Details"
        c.nagios_check_warn_days = UserOverviewController.NAGIOS_CHECK_AGE_WARN
        c.nagios_check_crit_days = UserOverviewController.NAGIOS_CHECK_AGE_CRIT
        c.status_core = h.get_nagios_host_services_from_group_tag(self.nagios_core_tag)
        c.status_ces = h.get_nagios_host_services_from_group_tag(self.nagios_ces_tag)
        return render('/derived/user/overview/core.html')
    
    def reports(self):
        c.title = "Monitoring System: User View"
        c.menu_active="Reports"
        c.heading = "Reports"
        return render('/derived/user/overview/report.html')
	 
