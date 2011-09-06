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
        c.down_time_items = get_nagios_scheduleddowntime_items()

        # MY JOBS SUMMARY
        num_finished = 0
        num_failed = 0
        num_killed = 0
        num_deleted = 0
        num_fetched = 0
        num_orphaned = 0
        num_tot_slcs = 0
        num_tot_browser = 0
        
        c.job_state_distribution = dict(FINISHED = 0,
                            FAILED = 0,
                            KILLED = 0,
                            DELETED = 0,
                            FETCHED = 0,
                            other = 0, 
                            orphaned = 0)

        if session.has_key('user_slcs_obj'):
            user_slcs_obj = session['user_slcs_obj']
            slcs_dn = user_slcs_obj.get_dn()
            num_finished = g.data_handler.get_num_user_jobs(slcs_dn, status = 'FINISHED')
            num_failed = g.data_handler.get_num_user_jobs(slcs_dn, status = 'FAILED') 
            num_killed = g.data_handler.get_num_user_jobs(slcs_dn, status = 'KILLED') 
            num_deleted = g.data_handler.get_num_user_jobs(slcs_dn, status = 'DELETED') 
            num_fetched = g.data_handler.get_num_user_jobs(slcs_dn, status = 'FETCHED') 
            num_orphaned = g.data_handler.get_num_user_jobs(slcs_dn, status = 'orphaned')
            num_tot_slcs = g.data_handler.get_num_user_jobs(slcs_dn) 


        if session.has_key('user_client_dn'):
            browser_dn = session['user_client_dn']
            num_finished += g.data_handler.get_num_user_jobs(browser_dn, status = 'FINISHED')
            num_failed += g.data_handler.get_num_user_jobs(browser_dn, status = 'FAILED') 
            num_killed += g.data_handler.get_num_user_jobs(browser_dn, status = 'KILLED')
            num_deleted += g.data_handler.get_num_user_jobs(browser_dn, status = 'DELETED')
            num_fetched += g.data_handler.get_num_user_jobs(browser_dn, status = 'FETCHED')
            num_orphaned += g.data_handler.get_num_user_jobs(browser_dn, status = 'orphaned')
            num_tot_browser = g.data_handler.get_num_user_jobs(browser_dn)

        c.job_state_distribution['FINISHED'] = num_finished
        c.job_state_distribution['FAILED'] = num_failed
        c.job_state_distribution['KILLED'] = num_killed
        c.job_state_distribution['DELETED'] = num_deleted
        c.job_state_distribution['FETCHED'] = num_fetched
        c.job_state_distribution['orphaned'] = num_orphaned

        num_other = num_tot_slcs + num_tot_browser - num_finished -\
                num_killed - num_deleted - num_orphaned - num_failed - num_fetched

        c.job_state_distribution['other'] = num_other

        # GRID LOAD + max load cluster + min load cluster
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
	 
