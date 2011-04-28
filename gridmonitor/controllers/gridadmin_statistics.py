import logging
import time

from decimal import Decimal
from sqlalchemy import and_
import calendar

from pylons import tmpl_context as c
from pylons import request
from pylons.templating import render_mako as render
import gridmonitor.lib.helpers as h

from gridadmin import GridadminController


from gridmonitor.model.statistics.series import Series

from sgasaggregator.sgascache import session as sgascache_session
from sgasaggregator.sgascache import ag_schema
from sgasaggregator.utils import helpers

log = logging.getLogger(__name__)

class GridadminStatisticsController(GridadminController):

    NO_VO = '-- No VO --' # string to use if no VO info required but not available
    
    def index(self):
        c.title = "Monitoring System: VO/Grid Admin Statistics"
        c.menu_active = "Grid Statistics"
        c.heading = "VO/Grid Statistics"
        
        return render('/derived/gridadmin/statistics/index.html')

    def sgas(self):
        """ display statistics from SGAS accouting records """

        SCALING_FACTOR = Decimal(1)/Decimal(3600) # 1/60 minutes, 1/3600 hours  
        
        c.title = "Monitoring System: VO/Grid Admin Statistics -- Usage Tables --"
        c.menu_active = "VO/Cluster Usage"
       
        if not self.authorized:
            return render('/derived/gridadmin/error/access_denied.html')
 
        resolution = 86400
        tot_n_jobs = 0 
        tot_wall = 0
        
        if not request.params.has_key('start_t_str'): # setting defaults
            _end_t= int(time.time())  # now
            _start_t = _end_t - 28 * 86400  # 4 weeks back (including endding day)
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
     
        
 
        start_t, end_t = helpers.get_sampling_interval(_start_t, _end_t, resolution) # incl. endding day
        
        c.resolution = resolution
        c.end_t_str_max = time.strftime("%d.%m.%Y", time.gmtime())
        c.start_t_str = time.strftime("%d.%m.%Y", time.gmtime(start_t))        
        c.end_t_str = time.strftime("%d.%m.%Y", time.gmtime(end_t))  
        
        c.heading = "VO and cluster usage numbers from (%s - %s)" % (c.start_t_str, c.end_t_str)
        
        vo_series = dict()
        vos = list()
        for arec in sgascache_session.Session.query(ag_schema.Vo.vo_name).distinct():
            vo = arec.vo_name
            vos.append(vo)   # i.e. vo can be  NULL/None

            vo_series[vo] = dict()
            vo_series[vo]['n_jobs'] = Series('n_jobs', start_t, end_t, resolution)
            vo_series[vo]['wall_duration'] = Series('wall_duration', start_t, end_t, resolution)
       
            for rec in sgascache_session.Session.query(ag_schema.Vo).filter(and_(
                ag_schema.Vo.t_epoch >= start_t,
                ag_schema.Vo.t_epoch < end_t,
                ag_schema.Vo.vo_name == vo,
                ag_schema.Vo.resolution == resolution)):
           
                vo_series[vo]['n_jobs'].add_sample(rec.t_epoch, rec.n_jobs)
                vo_series[vo]['wall_duration'].add_sample(rec.t_epoch, rec.wall_duration)
                vo_series[vo]['wall_duration'].set_scaling_factor(SCALING_FACTOR)
                
                tot_n_jobs += rec.n_jobs
                tot_wall += rec.wall_duration
        
        cluster_series = dict()
        for arec in sgascache_session.Session.query(ag_schema.Machine.machine_name).distinct():
            hostname = arec.machine_name
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


        # plot or tables
        if request.params.has_key('plotORtable') and request.params['plotORtable'] == 'plot':
            c.table = False
            c.plot = True

            # PLOT 1 DATA: VO - plot (i.e. usage per VO)
            walltime_data = list()
            jobs_data = list()
            vo_labels = ''
            walltime_max = 0
            job_max = 0
            c.num_vos = len(vo_series.keys())
            rvos = list()
            for vo in vo_series.keys():
                njob = vo_series[vo]['n_jobs'].get_sum()    
                vo_series[vo]['wall_duration']
                wall = vo_series[vo]['wall_duration'].get_sum()
                
                if walltime_max < wall:
                    walltime_max = wall
                if job_max < njob:
                    job_max = njob
                walltime_data.append(wall)
                jobs_data.append(njob)

            # vo names must be sorted in reverse order
            rvos = vo_series.keys()
            rvos.reverse()
            for vo in rvos:
                vo_labels+="|"
                if not vo:
                    vo_labels += GridadminStatisticsController.NO_VO
                else:
                    vo_labels += vo
            
            c.vo_labels = vo_labels
            walltime_data.reverse()
            c.walltime_data = h.list2string(walltime_data)
            c.walltime_max = float(walltime_max)
            jobs_data.reverse()
            c.jobs_data = h.list2string(jobs_data)
            c.job_max = float(job_max)
           

            # PLOT 2 DATA:  cluster plot (i.e usage per cluster)
            # plot...
            # XXX if number of clusters >= 14, we going to get problems with the size of the plot
            # google charts, won't plot anymore -> break up in smaller plots

            n_clusters = len(cluster_series.keys())
            c.plot_size = 3  # we want 3 clusters per plot
            n_plots = n_clusters / c.plot_size + 1

            cl_walltime_max = 0
            cl_job_max = 0
            cl_walltime_data = [list() for x in range(0,n_plots)]
            cl_jobs_data = [list() for x in range(0, n_plots)]
            c.cl_labels = [list() for x in range(0, n_plots)]
           
            n = 0
            old_plot_num = 0
            cl_labels = ''
            for cluster in cluster_series.keys():
                njob = cluster_series[cluster]['n_jobs'].get_sum()    
                cluster_series[cluster]['wall_duration'].set_scaling_factor(SCALING_FACTOR)
                wall = cluster_series[cluster]['wall_duration'].get_sum()
                
                if cl_walltime_max < wall:
                    cl_walltime_max = wall
                if cl_job_max < njob:
                    cl_job_max = njob
               
                plot_num =  n / c.plot_size
                if old_plot_num != plot_num:
                    old_plot_num = plot_num            
                    cl_labels = ''

                cl_walltime_data[plot_num].append(wall)
                cl_jobs_data[plot_num].append(njob)
                
                cl_labels +="|"
                cl_labels += cluster
                c.cl_labels[plot_num] = cl_labels
                n += 1
                    

            c.cl_walltime_data = list()
            c.cl_jobs_data = list()

            for i in range(0,n_plots - 1):
                cl_walltime_data[i].reverse()
                c.cl_walltime_data.append(h.list2string(cl_walltime_data[i]))
                cl_jobs_data[i].reverse()
                c.cl_jobs_data.append(h.list2string(cl_jobs_data[i]))
           
            c.n_plots = n_plots 
            c.cl_job_max = float(cl_job_max)
            c.num_clusters = len(c.cluster_menu)
            c.cl_walltime_max = float(cl_walltime_max)
 
            return render('/derived/gridadmin/statistics/form.html')

        else:
            c.table = True
            c.plot =  False

            # get VO *and* cluster time series -> VoMachine aggregate records
            vo_cluster_series = dict() 
            c.cluster_map = dict()

            for cluster in c.cluster_menu:   # used for reverse mapping
                hostname = cluster[1].split('/')[-1]
                display_name = cluster[0]
                c.cluster_map[hostname] = display_name
            
            for hostname in cluster_series.keys():
                vo_cluster_series[hostname] = dict()
                for vo in vos:
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
