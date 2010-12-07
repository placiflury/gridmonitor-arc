import logging

from gridmonitor.lib.base import *
from user import UserController 
from pylons import config

log = logging.getLogger(__name__)

class UserOverviewController(UserController):

    NAGIOS_CHECK_AGE_WARN = 1 # records older than 1 day
    NAGIOS_CHECK_AGE_CRIT = 3 # records older than 3 days

    def __init__(self):
        UserController()
        self.nagios_core_tag = config['nagios_core'] # core services (defined by nagios hostgroup alias)
        self.nagios_ces_tag = config['nagios_ces']   # Grid computing elements  (defined by nagios hostgroup alias)
        
    
    def index(self):
        c.title = "Monitoring System: User View"
        c.menu_active = "Overview"
        c.heading = "Welcome  %s %s" % (c.user_name,c.user_surname)

        status_core = h.get_nagios_host_services_from_group_tag(self.nagios_core_tag)

        # CORE SERVICES
        c.core_stats_summary={0:0,1:0,2:0,3:0} # 0 -- OK, 1 -- WARN, 2 -- CRITICAL, 3 -- UNKNOWN
        c.core_hosts_down=0
        for host in status_core:
            # XXX if host down -> report
            if host['hoststatus_object'].current_state != 0: 
                c.core_hosts_down +=1
                continue
            for service in host['services_q']:
                if service.status:
                    if h.is_epoch_time(service.status[0].last_check):  # UNKNOWN STATE
                        c.core_stats_summary[3] = c.core_stats_summary[3] +1
                    else:
                        record_age = h.get_sqldatetime_age(service.status[0].last_check).days
                        if record_age  >= UserOverviewController.NAGIOS_CHECK_AGE_CRIT:
                            c.core_stats_summary[2] = c.core_stats_summary[2] +1
                        elif record_age >= UserOverviewController.NAGIOS_CHECK_AGE_WARN:
                            c.core_stats_summary[1] = c.core_stats_summary[1] +1
                        else:
                            state = service.status[0].current_state
                            c.core_stats_summary[state] = c.core_stats_summary[state] +1
        
        status_ces = h.get_nagios_host_services_from_group_tag(self.nagios_ces_tag)

        # COMPUTING ELEMENTS
        c.ces_stats_summary={0:0,1:0,2:0,3:0}
        c.ce_hosts_down=0
        for host in status_ces:
            if host['hoststatus_object'].current_state != 0: 
                c.ce_hosts_down +=1
                continue
            for service in host['services_q']:
                if service.status:
                    if h.is_epoch_time(service.status[0].last_check):  # UNKNOWN STATE
                        c.ces_stats_summary[3] = c.ces_stats_summary[3] +1
                    
                    else: 
                        record_age = h.get_sqldatetime_age(service.status[0].last_check).days
                        if record_age >= UserOverviewController.NAGIOS_CHECK_AGE_CRIT:
                            c.ces_stats_summary[2] = c.ces_stats_summary[2] +1
                        elif record_age >= UserOverviewController.NAGIOS_CHECK_AGE_WARN:
                            c.ces_stats_summary[1] = c.ces_stats_summary[1] +1
                        else:
                            state = service.status[0].current_state
                            c.ces_stats_summary[state] = c.ces_stats_summary[state] +1

        # MY JOBS SUMMARY
        num_finished = 0
        num_failed = 0
        num_killed = 0
        num_deleted = 0
        num_fetched = 0
        num_orphaned = 0
        num_tot_slcs = 0
        num_tot_browser = 0
        
        c.job_state_distribution = dict(FINISHED=0,FAILED=0,KILLED=0,DELETED=0, FETCHED=0,other=0, orphaned=0)

        if session.has_key('user_slcs_obj'):
            user_slcs_obj = session['user_slcs_obj']
            slcs_dn = user_slcs_obj.get_dn()
            num_finished = g.data_handler.get_num_user_jobs(slcs_dn, status='FINISHED')
            num_failed = g.data_handler.get_num_user_jobs(slcs_dn,status ='FAILED') 
            num_killed = g.data_handler.get_num_user_jobs(slcs_dn,status='KILLED') 
            num_deleted = g.data_handler.get_num_user_jobs(slcs_dn,status='DELETED') 
            num_fetched = g.data_handler.get_num_user_jobs(slcs_dn,status='FETCHED') 
            num_orphaned = g.data_handler.get_num_user_jobs(slcs_dn, status='orphaned')
            num_tot_slcs = g.data_handler.get_num_user_jobs(slcs_dn) 


        if session.has_key('user_client_dn'):
            browser_dn = session['user_client_dn']
            num_finished += g.data_handler.get_num_user_jobs(browser_dn, status= 'FINISHED')
            num_failed += g.data_handler.get_num_user_jobs(browser_dn, status='FAILED') 
            num_killed += g.data_handler.get_num_user_jobs(browser_dn,status='KILLED')
            num_deleted += g.data_handler.get_num_user_jobs(browser_dn, status='DELETED')
            num_fetched += g.data_handler.get_num_user_jobs(browser_dn, status='FETCHED')
            num_orphaned += g.data_handler.get_num_user_jobs(browser_dn, status='orphaned')
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
        c.max_load_cluster=dict(name=None,tot_running=0,tot_cpus=0,tot_queued=0, relative_load=-1)
        c.min_load_cluster=dict(name=None,tot_running=0,tot_cpus=0,tot_queued=0, relative_load=-1)
        """
        Ranking of 'load' on clusters:   
            1. 'relative_load' = (#jobs_running + #jobs_queued)/# cpus  -> smaller number better
            2. on equal 'load' cluster with more cpus considered to have less effective load.
        """

        c.clusters_summary = dict(totcpus =0, grid_running=0, running=0,totaljobs=0,usedcpus=0,
                grid_queued=0, local_queued=0,prelrms_queued =0, queues_running=0, queues_grid_running=0)
        for cluster in c.cluster_menu:
            hostname = cluster[1].split('/')[-1] # stripping hostname from url
            display_name = cluster[0]
            cpus = g.get_cluster_stats(hostname,'stats_cpus')
            grid_running = g.get_cluster_stats(hostname,'stats_grid_running')
            running = g.get_cluster_stats(hostname,'stats_running')
            totaljobs = g.get_cluster_stats(hostname,'stats_totaljobs')
            usedcpus = g.get_cluster_stats(hostname,'stats_usedcpus')

            c.clusters_summary['totcpus'] += cpus
            c.clusters_summary['grid_running'] += grid_running
            c.clusters_summary['running'] += running
            c.clusters_summary['totaljobs'] += totaljobs
            c.clusters_summary['usedcpus'] += usedcpus
            
            tot_queued = 0
            for qname in g.get_cluster_queues_names(hostname):
                gqd = g.get_queue_stats(hostname,qname,'stats_grid_queued')
                lqd= g.get_queue_stats(hostname,qname,'stats_local_queued')
                plrms = g.get_queue_stats(hostname,qname,'stats_prelrms_queued')
                run = g.get_queue_stats(hostname,qname,'stats_running')
                grun = g.get_queue_stats(hostname,qname,'stats_grid_running')
                
                tot_queued = gqd + lqd + plrms
 
                c.clusters_summary['grid_queued'] += gqd
                c.clusters_summary['local_queued'] += lqd
                c.clusters_summary['prelrms_queued'] += plrms
                c.clusters_summary['queues_running'] += run
                c.clusters_summary['queues_grid_running'] += grun

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
            elif (relative_cluster_load == c.max_load_cluster['relative_load'] ) and (cpus < c.max_load_cluster['tot_cpus']):  
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
            elif (relative_cluster_load == c.min_load_cluster['relative_load'] ) and (cpus > c.min_load_cluster['tot_cpus']):  
                c.min_load_cluster['name'] = display_name
                c.min_load_cluster['tot_running'] = usedcpus 
                c.min_load_cluster['tot_cpus'] = cpus
                c.min_load_cluster['tot_queued'] = tot_queued 
                c.min_load_cluster['relative_load'] = relative_cluster_load

            # CHECK FOR SCHEDULED DOWNTIMES 
            c.down_time_items = h.get_nagios_scheduleddowntime_items()
            
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
	 
