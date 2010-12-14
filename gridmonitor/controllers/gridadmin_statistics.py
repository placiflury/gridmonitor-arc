import logging
import time

from decimal import Decimal
from sqlalchemy import and_
import calendar

from gridmonitor.lib.base import *
from gridadmin import GridadminController

from gridmonitor.model.statistics.series import Series
from sgasaggregator.sgascache import session as sgascache_session
from sgasaggregator.sgascache import ag_schema
from sgasaggregator.utils import helpers

log = logging.getLogger(__name__)

class GridadminStatisticsController(GridadminController):
    
    def index(self):
        c.title = "Monitoring System: VO/Grid Admin Statistics"
        c.menu_active = "Grid Statistics"
        c.heading = "VO/Grid Statistics"
        """
        query = meta.Session.query(ng_schema.Cluster)
        c.dbclusters = query.filter_by(status='active').all()
        c.blacklisted = meta.Session.query(ng_schema.Grisblacklist).all()
        c.giises = meta.Session.query(ng_schema.Giis).all()
        """

        return render('/derived/gridadmin/statistics/index.html')

    def sgas(self):
        """ display statistics from SGAS accouting records """

        SCALING_FACTOR = Decimal(1)/Decimal(3600) # 1/60 minutes, 1/3600 hours  
        
        c.title = "Monitoring System: VO/Grid Admin Statistics -- Usage Tables --"
        c.menu_active = "VO/Cluster Usage"
        
        resolution = 86400
        tot_n_jobs = 0 
        tot_wall = 0
        
        if not request.params.has_key('start_t_str'): # setting defaults
            _end_t= int(time.time())  # now
            _start_t = _end_t - 27 * 86400  # 4 weeks back
        else: 
            start_t_str = request.params['start_t_str'] 
            end_t_str = request.params['end_t_str'] 
            resolution = int(request.params['resolution'])
            log.debug('From %s to  %s at %d resolution' % (start_t_str, end_t_str, resolution))
            try:
                _start_t = calendar.timegm(time.strptime(start_t_str,'%d.%m.%Y'))
                _end_t = calendar.timegm(time.strptime(end_t_str,'%d.%m.%Y'))
                if _end_t < _start_t:
                    t = _end_t
                    _end_t = _start_t
                    _start_t = t
            except:
                c.form_error = "Please enter dates in 'dd.mm.yyyy' format"
                return render('/derived/gridadmin/statistics/form.html')
      
 
        start_t, end_t = helpers.get_sampling_interval(_start_t,_end_t, resolution)
        
        c.resolution = resolution
        c.end_t_str_max = time.strftime("%d.%m.%Y", time.gmtime())
        c.start_t_str = time.strftime("%d.%m.%Y", time.gmtime(start_t))        
        c.end_t_str = time.strftime("%d.%m.%Y", time.gmtime(end_t - 86400))   # hack to avoid increasing date 
                                                                            # upon form resubmission
        
        c.heading = "VO and cluster usage numbers from (%s - %s)" % (c.start_t_str, c.end_t_str)
        
        # plot or tables
        if request.params.has_key('plotORtable') and request.params['plotORtable'] == 'plot':
            c.table = False
            c.plot = True
            # get VO names
            series = dict()
            vos = list()
            for arec in sgascache_session.Session.query(ag_schema.Vo.vo_name).distinct():
                vos.append(arec.vo_name)
            
            for vo in vos:
                if not vo:
                    vo_name = ' -- No VO --'
                else:
                    vo_name = vo

                series[vo_name] = dict()
                series[vo_name]['n_jobs'] = Series('n_jobs', start_t, end_t, resolution)
                series[vo_name]['wall_duration'] = Series('wall_duration', start_t, end_t, resolution)
           
                for rec in sgascache_session.Session.query(ag_schema.Vo).filter(and_(
                    ag_schema.Vo.t_epoch >= start_t,
                    ag_schema.Vo.t_epoch < end_t,
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
                series[vo]['wall_duration'].set_scaling_factor(SCALING_FACTOR)
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
            
            return render('/derived/gridadmin/statistics/form.html')

        else:
            c.table = True
            c.plot =  False
        
            # get VO names and VO time series -> VO aggregate records
            vos = list()
            vo_series = dict()

            for arec in sgascache_session.Session.query(ag_schema.Vo.vo_name).distinct():
                vos.append(arec.vo_name)

            for vo in vos:
                vo_series[vo] = dict()
                vo_series[vo]['n_jobs'] = Series('n_jobs', start_t, end_t, resolution)
                vo_series[vo]['wall_duration'] = Series('wall_duration', start_t, end_t, resolution)
                vo_series[vo]['wall_duration'].set_scaling_factor(SCALING_FACTOR)
           
                for rec in sgascache_session.Session.query(ag_schema.Vo).filter(and_(
                    ag_schema.Vo.t_epoch >= start_t,
                    ag_schema.Vo.t_epoch < end_t,
                    ag_schema.Vo.vo_name == vo,
                    ag_schema.Vo.resolution == resolution)):
                    vo_series[vo]['n_jobs'].add_sample(rec.t_epoch, rec.n_jobs)
                    vo_series[vo]['wall_duration'].add_sample(rec.t_epoch, rec.wall_duration)
                    tot_n_jobs += rec.n_jobs
                    tot_wall += rec.wall_duration

            # get cluster names and cluster series -> machine aggregate records
            cluster_series = dict()
            for cluster in c.cluster_menu:
                hostname = cluster[1].split('/')[-1]
                cluster_series[hostname] = dict()
                cluster_series[hostname]['n_jobs'] = \
                        Series('n_jobs', start_t, end_t, resolution)
                cluster_series[hostname]['wall_duration'] = \
                        Series('wall_duration', start_t, end_t, resolution)
                cluster_series[hostname]['wall_duration'].set_scaling_factor(SCALING_FACTOR)

                for rec in sgascache_session.Session.query(ag_schema.Machine).filter(and_(
                    ag_schema.Machine.t_epoch >= start_t,
                    ag_schema.Machine.t_epoch < end_t,
                    ag_schema.Machine.machine_name == hostname,
                    ag_schema.Machine.resolution == resolution)):

                    cluster_series[hostname]['n_jobs'].add_sample(rec.t_epoch, rec.n_jobs)
                    cluster_series[hostname]['wall_duration'].add_sample(rec.t_epoch, rec.wall_duration)

            # get VO *and* cluster time series -> VoMachine aggregate records
            vo_cluster_series = dict() 
            c.cluster_map = dict()

            for cluster in c.cluster_menu:
                hostname = cluster[1].split('/')[-1]
                display_name = cluster[0]
                c.cluster_map[hostname] = display_name
            
                vo_cluster_series[hostname] = dict()

                for vo in vos:
                    vo_cluster_series[hostname][vo] = dict()
                    vo_cluster_series[hostname][vo] = dict()
                    vo_cluster_series[hostname][vo]['n_jobs'] = \
                        Series('n_jobs', start_t, end_t, resolution)
                    vo_cluster_series[hostname][vo]['wall_duration'] = \
                        Series('wall_duration', start_t, end_t, resolution)
                    vo_cluster_series[hostname][vo]['wall_duration'].set_scaling_factor(SCALING_FACTOR)

                    for rec in sgascache_session.Session.query(ag_schema.VoMachine).filter(and_(
                        ag_schema.VoMachine.t_epoch >= start_t,
                        ag_schema.VoMachine.t_epoch < end_t,
                        ag_schema.VoMachine.vo_name == vo,
                        ag_schema.VoMachine.machine_name == hostname,
                        ag_schema.VoMachine.resolution == resolution)):
                   
                        vo_cluster_series[hostname][vo]['n_jobs'].add_sample(rec.t_epoch, rec.n_jobs)
                        vo_cluster_series[hostname][vo]['wall_duration'].add_sample(rec.t_epoch, rec.wall_duration)

           

            c.tot_n_jobs = tot_n_jobs
            c.tot_wall = tot_wall * SCALING_FACTOR
            c.vo_series = vo_series
            c.cluster_series = cluster_series
            c.vo_cluster_series = vo_cluster_series

            return render('/derived/gridadmin/statistics/form.html')
        
    def rrd(self):
        c.title = "Monitoring System: VO/Grid Admin Statistics -- RRD PLOTS -- "
        c.menu_active = "RRD Plots"
        c.heading = "RRD plots of Grid Usage "
        return render('/derived/gridadmin/statistics/rrd.html')
