import logging
from pylons import tmpl_context as c
from pylons import app_globals as g
from pylons.templating import render_mako as render

import gridmonitor.lib.helpers as h
from gridmonitor.model.api.job_api import JobApi

from siteadmin import SiteadminController


log = logging.getLogger(__name__)

USER_NAME_LEN = 11

class SiteadminJobsController(SiteadminController):    

    JOB_STATES = ['FINISHED','FAILED','KILLED','DELETED','INLRMS: R']

    def index(self):
        c.title = "Monitoring System: Site Admin View"
        c.menu_active = "Jobs"
        c.heading = "Jobs/Users on Your Cluster(s)"  # default
       
 
        if not self.authorized:
            c.heading = "Nothing to View"  # default
            return render('/derived/siteadmin/error/access_denied.html')

        handler = g.get_data_handler()
        
        c.clusters_bag = dict()
        for cluster_hostname in self.clusters: 
            cluster_obj = g.get_cluster(cluster_hostname)
            if not cluster_obj:
                continue
            c.clusters_bag[cluster_hostname] = dict()
            
            users_bag=dict()
            max_tot_jobs = 0
            user_list = list()

            cluster_jobs = handler.get_cluster_jobs(cluster_hostname)

            for job in cluster_jobs:
                user = job.get_globalowner()
                if user not in user_list:
                    user_list.append(user) 
                status = job.get_status()
                
                if not users_bag.has_key(user):
                    users_bag[user]=dict()
                    for state in SiteadminJobsController.JOB_STATES:
                        users_bag[user][state] = 0
                    users_bag[user]['FETCHED'] = 0
                    users_bag[user]['DELETED'] = 0
                    users_bag[user]['other'] = 0
                    users_bag[user]['total'] = 0
                
                if status in SiteadminJobsController.JOB_STATES:
                    users_bag[user][status]+=1
                elif status in JobApi.JOB_FETCHED:
                    users_bag[user]['FETCHED']+=1
                elif status in JobApi.JOB_DELETED:
                    users_bag[user]['DELETED']+=1
                else:
                    users_bag[user]['other']+=1
                users_bag[user]['total']+=1
                
                if max_tot_jobs < users_bag[user]['total']:
                    max_tot_jobs = users_bag[user]['total']
            
            c.clusters_bag[cluster_hostname]['users_bag'] = users_bag 
            c.clusters_bag[cluster_hostname]['max_tot_jobs'] = max_tot_jobs
            
            # check for orphaned jobs/users
            orphan_list = list()
            for user in user_list:
                allowed_clusters = g.data_handler.get_user_clusters(user)
                if cluster_hostname not in allowed_clusters:
                    orphan_list.append(user)

            c.clusters_bag[cluster_hostname]['orphan_list'] = orphan_list
            
            # setting for populationg the user jobs cahrt
            userjobs_bar_chxl = None  # label
            userjobs_bar_chd=list()     # data

            mtj_s = str(max_tot_jobs)
            mtj_s2 = str(max_tot_jobs/2)

            userjobs_bar_chxl="0:|0|%s|%s|1:|0|%s|%s|2:" % (mtj_s2,mtj_s,mtj_s2,mtj_s)


            ukeys = users_bag.keys()
            ukeys.reverse()
            for user in ukeys:
                user_cn = user.split("/CN=")[-1]
                # shorten user_cn if too long
                if len(user_cn) > USER_NAME_LEN:
                    user_cn = user_cn[:USER_NAME_LEN-3]+ "..."
                
                userjobs_bar_chxl+="|" + user_cn  
                userjobs_bar_chd.append(users_bag[user]['total'])
            
            userjobs_bar_chd.reverse()
            userjobs_bar_chd="t:%s" %(h.list2string(userjobs_bar_chd))
            
            c.clusters_bag[cluster_hostname]['userjobs_bar_chxl'] = userjobs_bar_chxl
            c.clusters_bag[cluster_hostname]['userjobs_bar_chd'] = userjobs_bar_chd


            # setting for populating the user jobs states  bar chart
            job_stat_summary=[0,0,0,0,0,0,0,0]  # finished, failed, killed, deleted,fetched,running,other,total


            for job in users_bag.values():
                job_stat_summary[0] += job['FINISHED']
                job_stat_summary[1] += job['FAILED']
                job_stat_summary[2] += job['KILLED']
                job_stat_summary[3] += job['DELETED']
                job_stat_summary[4] += job['FETCHED']
                job_stat_summary[5] += job['INLRMS: R']
                job_stat_summary[6] += job['other']
                job_stat_summary[7] += job['total']

            max_status_value = max(job_stat_summary[:-1])
            job_bar_chd="t:%s" % (h.list2string(job_stat_summary[:-1]))

            c.clusters_bag[cluster_hostname]['job_stat_summary'] = job_stat_summary 
            c.clusters_bag[cluster_hostname]['max_status_value'] = max_status_value
            c.clusters_bag[cluster_hostname]['job_bar_chd'] = job_bar_chd
        
        return render('/derived/siteadmin/jobs/index.html')

