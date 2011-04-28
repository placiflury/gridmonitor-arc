import logging
from pylons import config
from pylons import tmpl_context as c
from pylons.templating import render_mako as render

import gridmonitor.lib.helpers as h

from siteadmin import SiteadminController
from user_overview import UserOverviewController

log = logging.getLogger(__name__)

class SiteadminOverviewController(SiteadminController):    

    def __init__(self):
        SiteadminController.__init__(self)
        self.nagios_ces_tag = config['nagios_ces']   # Grid computing elements  (defined by nagios hostgroup alias)
        self.nagios_core_tag = config['nagios_core']   # Grid computing elements  (defined by nagios hostgroup alias)
    
    def index(self):
        c.title = "Monitoring System: Site Admin View"
        c.menu_active = "Overview"
        c.heading = "Nothing to View"  # default
        
        if not self.authorized:
            c.heading= "Site Overview"
            return render('/derived/siteadmin/error/access_denied.html')
        
        c.heading = "Tactical Overview on Your Services"
        
        # find core services admin has rigths to view
        all_cores = h.get_nagios_host_services_from_group_tag(self.nagios_core_tag)
        missing_cores = [ x for x in self.cores]  # copy
        c.core_stats_summary={0:0, 1:0, 2:0, 3:0} # 0 -- OK, 1 -- WARN, 2 -- CRITICAL, 3 -- UNKNOWN
        c.core_hosts_down=0
        c.cores_admin=False
        for core in all_cores:
            if (core['alias'] in self.cores) or (core['display_name'] in self.cores):
                c.cores_admin = True
                if core['hoststatus_object'].current_state != 0: 
                    c.core_hosts_down += 1
                    continue
                core_name = core['display_name']
                core_name2 =core['alias']
                for service in core['services_q']:
                    if service.status:
                        if h.is_epoch_time(service.status[0].last_check):  # UNKNOWN STATE
                            c.core_stats_summary[3] = c.core_stats_summary[3] + 1
                        else:
                            record_age = h.get_sqldatetime_age(service.status[0].last_check).days
                            if record_age  >= UserOverviewController.NAGIOS_CHECK_AGE_CRIT:
                                c.core_stats_summary[2] = c.core_stats_summary[2] + 1
                            elif record_age >= UserOverviewController.NAGIOS_CHECK_AGE_WARN:
                                c.core_stats_summary[1] = c.core_stats_summary[1] + 1
                            else:
                                state = service.status[0].current_state
                                c.core_stats_summary[state] = c.core_stats_summary[state] + 1
        
                for n in range(0, missing_cores.count(core_name)):  # removing from missing list
                    missing_cores.remove(core_name)
                for n in range(0, missing_cores.count(core_name2)):  # removing from missing list
                    missing_cores.remove(core_name2)
        
        c.missing_cores = missing_cores
       

        # find ce record of cluster admin has rights to view
        all_ces = h.get_nagios_host_services_from_group_tag(self.nagios_ces_tag)
        admin_ces = dict()
        missing_clusters = [ x for x in self.clusters]  # copy
        c.ces_stats_summary={0:0,1:0,2:0,3:0}
        c.ce_hosts_down=0
        c.ce_admin=False
        for ce in all_ces:
            if (ce['alias'] in self.clusters) or (ce['display_name'] in self.clusters):
                c.ce_admin=True
                if ce['hoststatus_object'].current_state != 0: 
                    c.ce_hosts_down +=1
                    continue
                cluster_name = ce['display_name']
                cluster_name2 =ce['alias']
                admin_ces[cluster_name] = dict() 
                for service in ce['services_q']:
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
                        if service.display_name.lower() in ['supported vos','grid pool accounts']:
                            admin_ces[cluster_name][service.display_name] = dict()
                            admin_ces[cluster_name][service.display_name]['current_state'] = service.status[0].current_state 
                            admin_ces[cluster_name][service.display_name]['output'] = service.status[0].output
                            admin_ces[cluster_name][service.display_name]['perfdata'] = service.status[0].perfdata
        
                for n in range(0, missing_clusters.count(cluster_name)):  # removing from missing list
                    missing_clusters.remove(cluster_name)
                for n in range(0, missing_clusters.count(cluster_name2)):  # removing from missing list
                    missing_clusters.remove(cluster_name2)
        
        c.admin_ces = admin_ces 
        c.missing_clusters = missing_clusters
        
        
        return render('/derived/siteadmin/overview/index.html')

    def core(self):
        c.title = "Monitoring System: Site Admin View"
        c.menu_active="My Services"
        c.heading = "My Services Status"
        
        c.nagios_check_warn_days = UserOverviewController.NAGIOS_CHECK_AGE_WARN
        c.nagios_check_crit_days = UserOverviewController.NAGIOS_CHECK_AGE_CRIT
        all_core= h.get_nagios_host_services_from_group_tag(self.nagios_core_tag)
        all_ces= h.get_nagios_host_services_from_group_tag(self.nagios_ces_tag)
        # pick out those user has admin rights on
        c.status_core =[]
        for co in all_core:
            if (co['alias'] in self.cores) or (co['display_name'] in self.cores):
                c.status_core.append(co)

        c.status_ces =[]
        for ce in all_ces:
            if (ce['alias'] in self.clusters) or (ce['display_name'] in self.clusters):
                c.status_ces.append(ce)

        return render('/derived/user/overview/core.html')
                    
            

    def reports(self):
        c.title = "Monitoring System: Site Admin View"
        c.menu_active="Reports"
        c.heading = "Reports"
        return render('/derived/siteadmin/overview/report.html')	 
