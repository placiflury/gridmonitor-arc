import logging

from gridmonitor.lib.base import *
from user import UserController 

log = logging.getLogger(__name__)

class UserJobsController(UserController):
    
    # XXX  logging
   
    JOB_STATES = ['FINISHED','FAILED','KILLED','DELETED', 'INLRMS: R',
            'FETCHED'] # FETCHED state is a meta-state for FINISHED_FETCHED etc..

    def __init__(self): 
        UserController()
    
    def index(self):
        
        c.title = "Monitoring System: User Jobs"
        c.menu_active = "My Jobs"
        c.heading = "Information about User Jobs"
         
        
        slcs_dn = c.user_slcs_obj.get_dn()
        browser_dn = c.user_client_dn

        all_jobs = g.get_user_jobs(slcs_dn) + g.get_user_jobs(browser_dn)
        allowed_clusters = g.data_handler.get_user_clusters(slcs_dn) + \
                g.data_handler.get_user_clusters(browser_dn)
        
        allowed_clusters = {}
        allowed_clusters[slcs_dn] = g.data_handler.get_user_clusters(slcs_dn)
        allowed_clusters[browser_dn] = g.data_handler.get_user_clusters(browser_dn)

        # settings for creation of cluster-jobs table
        c.max_tot_jobs = 0
        cluster_bag = dict()
        sum_jobs_allowed_clusters = 0

        for cluster_name in allowed_clusters[slcs_dn] + allowed_clusters[browser_dn]: 
            if cluster_bag.has_key(cluster_name):
                continue
            cluster_bag[cluster_name] = dict()
            
            sum_state_jobs = 0
            for state in UserJobsController.JOB_STATES:
                num = g.data_handler.get_num_user_jobs(slcs_dn,cluster_hostname=cluster_name,status=state) + \
                    g.data_handler.get_num_user_jobs(browser_dn,cluster_hostname=cluster_name,status=state)
                cluster_bag[cluster_name][state] = num
                sum_state_jobs += num
            
            orphaned = g.data_handler.get_num_user_jobs(slcs_dn,cluster_hostname=cluster_name,status='orphaned') + \
                g.data_handler.get_num_user_jobs(browser_dn,cluster_hostname=cluster_name,status='orphaned')
            cluster_bag[cluster_name]['orphaned'] = orphaned
          
            total = g.data_handler.get_num_user_jobs(slcs_dn,cluster_hostname=cluster_name) + \
                    g.data_handler.get_num_user_jobs(browser_dn, cluster_hostname=cluster_name)
            if c.max_tot_jobs < total:
                c.max_tot_jobs = total
            
            cluster_bag[cluster_name]['other'] = total - sum_state_jobs - orphaned
            cluster_bag[cluster_name]['total'] = total
            sum_jobs_allowed_clusters += total
        

        # Fetch number of jobs of clusters that are not anymore listed 
        num_all_user_jobs = g.data_handler.get_num_user_jobs(slcs_dn) + \
                            g.data_handler.get_num_user_jobs(browser_dn)

        if sum_jobs_allowed_clusters != num_all_user_jobs: # there are more orphaned 
            orphaned = num_all_user_jobs - sum_jobs_allowed_clusters
            cluster_bag['DOWN_CLUSTERS'] = dict()
            cluster_bag['DOWN_CLUSTERS']['other'] = 0 
            for state in UserJobsController.JOB_STATES:
                cluster_bag['DOWN_CLUSTERS'][state] = 0 
            cluster_bag['DOWN_CLUSTERS']['orphaned'] = orphaned # XXX list cluster names instead
            cluster_bag['DOWN_CLUSTERS']['total'] = orphaned 
            if c.max_tot_jobs < orphaned:
                c.max_tot_jobs = orphaned
         
        c.cluster_bag = cluster_bag            

        # setting for populating the cluster chart 
        c.cluster_bar_chxl= None       # label
        cluster_bar_chd=list()    # data
        
        mtj_s = str(c.max_tot_jobs)
        mtj_s2 = str(c.max_tot_jobs/2)

        c.cluster_bar_chxl="0:|0|%s|%s|1:|0|%s|%s|2:" % (mtj_s2,mtj_s,mtj_s2,mtj_s)
        
        ckeys = cluster_bag.keys()
        ckeys.reverse()
        for cluster_name in ckeys:
            c.cluster_bar_chxl+= "|" + cluster_name
            cluster_bar_chd.append(c.cluster_bag[cluster_name]['total'])

        cluster_bar_chd.reverse()
        c.cluster_bar_chd="t:%s" % (h.list2string(cluster_bar_chd))
       
        # setting for user jobs  bar chart
        c.job_stat_summary=[0,0,0,0,0,0,0,0,0]  # finished, failed, killed, deleted,fetched,running,other,orphan,total
        
        for cluster in c.cluster_bag.values():
            c.job_stat_summary[0] += cluster['FINISHED']
            c.job_stat_summary[1] += cluster['FAILED']
            c.job_stat_summary[2] += cluster['KILLED']
            c.job_stat_summary[3] += cluster['DELETED']
            c.job_stat_summary[4] += cluster['FETCHED']
            c.job_stat_summary[5] += cluster['INLRMS: R']
            c.job_stat_summary[6] += cluster['other']
            c.job_stat_summary[7] += cluster['orphaned']
            c.job_stat_summary[8] += cluster['total']
        
        c.max_status_value = max(c.job_stat_summary[:-1])
        c.job_bar_chd="t:%s" % (h.list2string(c.job_stat_summary[:-1]))

        return render('/derived/user/jobs/index.html')
 
    def show(self, status):
        
        slcs_dn = c.user_slcs_obj.get_dn()
        browser_dn = c.user_client_dn
        c.job_list = list()  # double list        

        c.job_status = status
        c.menu_active = status
        if status != 'all':
            if status == 'orphaned':
                c.heading = "Orphaned Jobs"
                c.title = "Orphaned Jobs"
            else:
                c.heading = "Jobs in status: '%s'" % c.job_status
                c.title = c.heading
            jl = g.get_user_jobs(slcs_dn,status)
            c.job_list.append(jl)
            if browser_dn:
                jl = g.get_user_jobs(browser_dn,status)
                c.job_list.append(jl)
        else:
            c.heading = "All of Your Jobs"
            c.title = "All of Your Jobs"
            jl = g.get_user_jobs(slcs_dn)
            c.job_list.append(jl)
            if browser_dn:
                jl=g.get_user_jobs(browser_dn)
                c.job_list.append(jl)
            
            log.debug(c.job_list)
        return render('/derived/user/jobs/show.html')
		 
