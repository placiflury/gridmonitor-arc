import logging
import time

from sqlalchemy import and_
from decimal import Decimal

from gridmonitor.lib.base import *
from gridadmin import GridadminController

from gridmonitor.model.statistics.series import Series

from sgas.db import sgas_meta
from sgas.db import ag_schema # schema of tables of aggregated usage record 
from sgas.db import sgas_schema  # original SGAS schema
from sgas.utils import helpers

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


        resolution = 86400
        series = dict()

        # XXX allow more resolutions
        # and allow for several days  
        now = int(time.time())
        start_t_epoch = now - (now % resolution)
        end_t_epoch = now
        
        start_t_str = time.strftime("%d.%m.%Y", time.gmtime(start_t_epoch))
        end_t_str = time.strftime("%d.%m.%Y", time.gmtime(now))

        log.debug("VO usage statistics from %s to %s (UTC)" % (start_t_str, end_t_str))
        
        for vo in  sgas_meta.Session.query(ag_schema.ReducedVoInfo).all():
            if not vo.vo_name:
                vo_name = '-- no VO --'
            else:
                vo_name = vo.vo_name
            series[vo_name] = dict()
            series[vo_name]['n_jobs'] = Series('n_jobs', start_t_epoch, end_t_epoch, resolution)
            series[vo_name]['wall_duration'] = Series('wall_duration', start_t_epoch, end_t_epoch, resolution)
       
            vo_id = vo.id
            for rec in sgas_meta.Session.query(ag_schema.Vo).filter(and_(
                ag_schema.Vo.t_epoch >= start_t_epoch,
                ag_schema.Vo.t_epoch < end_t_epoch,
                ag_schema.Vo.vo_id == vo_id,
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

        # XXX allow more resolutions
        # and allow for several days  
        now = int(time.time())
        start_t_epoch = now - (now % resolution)
        end_t_epoch = now
        
        start_t_str = time.strftime("%d.%m.%Y", time.gmtime(start_t_epoch))
        end_t_str = time.strftime("%d.%m.%Y", time.gmtime(now))

        log.debug("VO usage statistics from %s to %s (UTC) for %s" % (start_t_str, end_t_str, hostname))

        m_id = helpers.get_cluster_id(hostname)
        
        for vo in  sgas_meta.Session.query(ag_schema.ReducedVoInfo).all():
            if not vo.vo_name:
                vo_name = '-- no VO --'
            else:
                vo_name = vo.vo_name
            series[vo_name] = dict()
            series[vo_name]['n_jobs'] = Series('n_jobs', start_t_epoch, end_t_epoch, resolution)
            series[vo_name]['wall_duration'] = Series('wall_duration', start_t_epoch, end_t_epoch, resolution)
       
            vo_id = vo.id
            for rec in sgas_meta.Session.query(ag_schema.VoMachine).filter(and_(
                ag_schema.VoMachine.t_epoch >= start_t_epoch,
                ag_schema.VoMachine.t_epoch < end_t_epoch,
                ag_schema.VoMachine.vo_id == vo_id,
                ag_schema.VoMachine.m_id == m_id,
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
