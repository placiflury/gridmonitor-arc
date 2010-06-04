import logging

from gridmonitor.lib.base import *
from gridadmin import GridadminController

log = logging.getLogger(__name__)

class GridadminVosController(GridadminController):
    def __compare(self,a,b):
        if len(a) > len(b):
            return 1
        elif len(a) < len(b):
            return -1
        else:
            return 0

    def index(self):
	
        c.title = "Monitoring System: VO/Grid Admin VOs"
        c.menu_active = "VO Usage"
        c.heading = "Current VO Usage Pattern for Grid"
        
        walltime_data = list()
        jobs_data = list()
        vo_labels = ''

        grid_vo_usage = g.get_grid_stats('stats_vo_usage')
        vos = grid_vo_usage.keys()
        vos.sort(self.__compare)
        walltime_max =0
        job_max = 0
        for vo in vos:
            wall = grid_vo_usage[vo]['walltime']
            njob = grid_vo_usage[vo]['num_jobs']    
            if walltime_max < wall:
                walltime_max = wall
            if job_max < njob:
                job_max = njob
            walltime_data.append(wall)
            jobs_data.append(njob)

            vol = eval(vo)            
            vo_labels+="|"
            for v in vol:
                vo_labels += v+'&nbsp;' 
                        
        c.num_vos = len(vos)             
        c.vo_labels = vo_labels
        walltime_data.reverse()
        c.walltime_data = h.list2string(walltime_data)
        c.walltime_max = walltime_max
        jobs_data.reverse()
        c.jobs_data = h.list2string(jobs_data)
        c.job_max = job_max
        
        return render('/derived/gridadmin/vos/index.html')

    def show(self,id, queue = None):
        """ XXX remove duplicate code... """

        c.title = "Monitoring System: VO/Grid Admin VOs"

        cluster_hostname = id
        for cluster in c.cluster_menu:   #XXX rather primitive -> improve
            if id == cluster[1].split('/')[-1]:
                c.cluster_display_name = cluster[0]
                break
        c.menu_active=c.cluster_display_name
        c.queue = None
        
        # prepare data for charts        
        walltime_data = list()
        jobs_data = list()
        vo_labels = ''
        
        # let's sort things 
        if queue:
            cq_vo_usage = g.get_queue_stats(cluster_hostname, queue, 'stats_vo_usage')
            c.queue = queue
            c.heading = "Current VO Usage Pattern for queue %s of cluster %s " \
                 % (queue, c.cluster_display_name)
        else:
            cq_vo_usage = g.get_cluster_stats(cluster_hostname,'stats_vo_usage')
            c.heading = "Current VO Usage Pattern for cluster %s" % c.cluster_display_name
        
        vos = cq_vo_usage.keys()

        vos.sort(self.__compare)
        walltime_max =0
        job_max = 0
        for vo in vos:
            njob = cq_vo_usage[vo]['num_jobs'] 
            wall= cq_vo_usage[vo]['walltime']
            if walltime_max < wall:
                walltime_max = wall
            if job_max < njob:
                job_max = njob
            walltime_data.append(wall)
            jobs_data.append(njob)

            vol = eval(vo)            
            vo_labels+="|"
            for v in vol:
                vo_labels += v+'&nbsp;' 
                        
        c.num_vos = len(vos)             
        c.vo_labels = vo_labels
        walltime_data.reverse()
        c.walltime_data = h.list2string(walltime_data)
        c.walltime_max = walltime_max
        jobs_data.reverse()
        c.jobs_data = h.list2string(jobs_data)
        c.job_max = job_max
        
        return render('/derived/gridadmin/vos/show.html')
