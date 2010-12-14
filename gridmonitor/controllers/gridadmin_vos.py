import logging
import time

from sqlalchemy import and_
from decimal import Decimal

from gridmonitor.lib.base import *
from gridadmin import GridadminController

from gridmonitor.model.statistics.series import Series

from sgasaggregator.sgascache import session as sgascache_session
from sgasaggregator.sgascache import ag_schema
from sgasaggregator.utils import helpers

log = logging.getLogger(__name__)

class GridadminVosController(GridadminController):

    def index(self):
	
        c.title = "Monitoring System: VO/Grid Admin VOs"
        c.menu_active = "VO Usage"
        c.heading = "Current VO Usage Pattern for Grid"


        resolution = 86400
        series = dict()

        # XXX allow more resolutions
        # and allow for several days  
        
        
        _end_t= int(time.time())  # now
        _start_t = _end_t - resolution  
            
        start_t_epoch, end_t_epoch = helpers.get_sampling_interval(_start_t,_end_t, resolution)

        start_t_str = time.strftime("%d.%m.%Y", time.gmtime(start_t_epoch))
        end_t_str = time.strftime("%d.%m.%Y", time.gmtime(end_t_epoch))

        log.debug("VO usage statistics from %s to %s (UTC)" % (start_t_str, end_t_str))

        # get VO names
        vos = list()
        for arec in sgascache_session.Session.query(ag_schema.Vo.vo_name).distinct():
            vos.append(arec.vo_name)

        
        for vo in vos:
            if not vo:
                vo_name = ' -- No VO --'
            else:
                vo_name = vo

            series[vo_name] = dict()
            series[vo_name]['n_jobs'] = Series('n_jobs', start_t_epoch, end_t_epoch, resolution)
            series[vo_name]['wall_duration'] = Series('wall_duration', start_t_epoch, end_t_epoch, resolution)
       
            for rec in sgascache_session.Session.query(ag_schema.Vo).filter(and_(
                ag_schema.Vo.t_epoch >= start_t_epoch,
                ag_schema.Vo.t_epoch < end_t_epoch,
                ag_schema.Vo.vo_name == vo,
                ag_schema.Vo.resolution == resolution)):
           
                series[vo_name]['n_jobs'].add_sample(rec.t_epoch, rec.n_jobs)
                series[vo_name]['wall_duration'].add_sample(rec.t_epoch, rec.wall_duration)
 
        # preparing data for plot 
        walltime_data = list()
        jobs_data = list()
        vo_labels = ''
        walltime_max = 0
        job_max = 0
        c.num_vos = len(series.keys())
        
        for vo in series.keys():
            njob = series[vo]['n_jobs'].get_sum()    
            series[vo]['wall_duration'].set_scaling_factor(Decimal(1)/Decimal(60))
            wall = series[vo]['wall_duration'].get_sum()
            
            if walltime_max < wall:
                walltime_max = wall
            if job_max < njob:
                job_max = njob
            walltime_data.append(wall)
            jobs_data.append(njob)

            vo_labels+="|"
            vo_labels += vo
        
        c.vo_labels = vo_labels
        walltime_data.reverse()
        c.walltime_data = h.list2string(walltime_data)
        c.walltime_max = float(walltime_max)
        jobs_data.reverse()
        c.jobs_data = h.list2string(jobs_data)
        c.job_max = float(job_max)
        
                        
        return render('/derived/gridadmin/vos/index.html')

    def show(self, hostname):

        c.title = "Monitoring System: VO/Grid Admin VOs"

        cluster_hostname = hostname
        for cluster in c.cluster_menu:   #XXX rather primitive -> improve
            if hostname == cluster[1].split('/')[-1]:
                c.cluster_display_name = cluster[0]
                break

        c.menu_active=c.cluster_display_name
        
        resolution = 86400
        series = dict()
        
        _end_t= int(time.time())  # now
        _start_t = _end_t - resolution  
            
        start_t_epoch, end_t_epoch = helpers.get_sampling_interval(_start_t,_end_t, resolution)

        start_t_str = time.strftime("%d.%m.%Y", time.gmtime(start_t_epoch))
        end_t_str = time.strftime("%d.%m.%Y", time.gmtime(end_t_epoch))
        
        # get VO names
        vos = list()
        for arec in sgascache_session.Session.query(ag_schema.Vo.vo_name).distinct():
            vos.append(arec.vo_name)

        
        for vo in vos:
            if not vo:
                vo_name = ' -- No VO --'
            else:
                vo_name = vo
        
            series[vo_name] = dict()
            series[vo_name]['n_jobs'] = Series('n_jobs', start_t_epoch, end_t_epoch, resolution)
            series[vo_name]['wall_duration'] = Series('wall_duration', start_t_epoch, end_t_epoch, resolution)
       
            for rec in sgascache_session.Session.query(ag_schema.VoMachine).filter(and_(
                ag_schema.VoMachine.t_epoch >= start_t_epoch,
                ag_schema.VoMachine.t_epoch < end_t_epoch,
                ag_schema.VoMachine.vo_name == vo,
                ag_schema.VoMachine.machine_name == hostname,
                ag_schema.VoMachine.resolution == resolution)):
           
                series[vo_name]['n_jobs'].add_sample(rec.t_epoch, rec.n_jobs)
                series[vo_name]['wall_duration'].add_sample(rec.t_epoch, rec.wall_duration)
 
        # preparing data for plot 
        walltime_data = list()
        jobs_data = list()
        vo_labels = ''
        walltime_max = 0
        job_max = 0
        c.num_vos = len(series.keys())
        
        for vo in series.keys():
            njob = series[vo]['n_jobs'].get_sum()    
            series[vo]['wall_duration'].set_scaling_factor(Decimal(1)/Decimal(60))
            wall = series[vo]['wall_duration'].get_sum()
            
            if walltime_max < wall:
                walltime_max = wall
            if job_max < njob:
                job_max = njob
            walltime_data.append(wall)
            jobs_data.append(njob)

            vo_labels+="|"
            vo_labels += vo
        
        c.vo_labels = vo_labels
        walltime_data.reverse()
        c.walltime_data = h.list2string(walltime_data)
        c.walltime_max = float(walltime_max)
        jobs_data.reverse()
        c.jobs_data = h.list2string(jobs_data)
        c.job_max = float(job_max)
        
        c.heading = "Current VO Usage Pattern for cluster %s" % c.cluster_display_name
        
        return render('/derived/gridadmin/vos/show.html')
