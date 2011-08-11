import logging
import time
import calendar
from datetime import datetime

from decimal import Decimal
from sqlalchemy import and_

from pylons import tmpl_context as c
from pylons import request
from pylons.templating import render_mako as render
import gridmonitor.lib.helpers as h
from gridmonitor.lib import charts_table

from gridadmin import GridadminController


from gridmonitor.model.statistics.series import Series

from sgasaggregator.sgascache import session as sgascache_session
from sgasaggregator.sgascache import ag_schema
from sgasaggregator.utils import helpers

log = logging.getLogger(__name__)

class GridadminStatisticsController(GridadminController):

    NO_VO = 'No_VO' # string to use if no VO info required but not available
    
    def index(self):
        c.title = "Monitoring System: VO/Grid Admin Statistics"
        c.menu_active = "Grid Statistics"
        c.heading = "VO/Grid Statistics"
        
        return render('/derived/gridadmin/statistics/index.html')


    def vo(self, ctype = None):
        """ display accounting data per VO """
        
        c.title = "Monitoring System VO Usage Statistics"
        c.menu_active = "VO Usage"
        c.form_error = None
      
        c.plots = True  # XXX maybe obsolete in final implementation
        c.table = False
        
        resolution = 86400
 
        if not self.authorized:
            return render('/derived/gridadmin/error/access_denied.html')

        if not request.params.has_key('start_t_str'): # setting defaults
            _end_t = int(time.time())  # now
            _start_t = _end_t - 28 * 86400  # 4 weeks back (including ending day)
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
                return render('/derived/gridadmin/statistics/vo_form.html')
 
        start_t, end_t = helpers.get_sampling_interval(_start_t, _end_t, resolution) # incl. ending day
        
        c.resolution = resolution
        c.end_t_str_max = time.strftime("%d.%m.%Y", time.gmtime())
        c.start_t_str = time.strftime("%d.%m.%Y", time.gmtime(start_t))        
        c.end_t_str = time.strftime("%d.%m.%Y", time.gmtime(end_t))  
        
        c.heading = "VO usage numbers from (%s - %s)" % (c.start_t_str, c.end_t_str)


        # vars for column/bar/area plots
        vo_matrix_jobs = []
        vo_matrix_wall = []
        key_order = ['utctime']
        _schema = dict(utctime=('UTC Time', 'string'))


        # vars  for pie-chart plots
        pie_key_order =['vo_name','sum']
        pie_schema = dict(vo_name = ('VO name','string'), sum = ('Sum','number'))
        vo_sum_jobs = []
        vo_sum_wall = []

        _vos = helpers.get_vo_names()
        for vo in _vos:
            if not vo:
                vo = GridadminStatisticsController.NO_VO
            key_order.append(vo)
            _schema[vo]=(vo,'number')


        # init column containers
        ts = range(start_t + resolution - 1, end_t + resolution - 1, resolution)
        for t in ts:
            _row = [None] * (len(_vos) + 1) # init 
            _row[0] = datetime.utcfromtimestamp(t + resolution).strftime("%d/%m/%Y")
            vo_matrix_jobs.append(_row)
            vo_matrix_wall.append(_row[:])

        # populate matrix
        j = 1
        for vo in _vos:
            _vo_sum_jobs = 0
            _vo_sum_wall = 0
            for rec in helpers.get_vo_acrecords(vo, start_t, end_t, resolution):
                i = ts.index(rec.t_epoch)
                vo_matrix_jobs[i][j] = rec.n_jobs
                vo_matrix_wall[i][j] = int(rec.wall_duration)/3600 # hours

                _vo_sum_jobs += rec.n_jobs
                _vo_sum_wall += rec.wall_duration

            vo_sum_jobs.append([vo,_vo_sum_jobs])
            vo_sum_wall.append([vo, int(_vo_sum_wall)/3600])

            j += 1

        # XXX error handling (i.e. catch exepctions etc.))
        dt_jobs = charts_table.DataTable(_schema, key_order)
        dt_wall = charts_table.DataTable(_schema, key_order)

        for row in vo_matrix_jobs:
            dt_jobs.add_row(row)

        for row in vo_matrix_wall:
            dt_wall.add_row(row)

        dt_sum_jobs = charts_table.DataTable(pie_schema, pie_key_order)
        dt_sum_wall = charts_table.DataTable(pie_schema, pie_key_order)

        for row in vo_sum_jobs:
            dt_sum_jobs.add_row(row)
        for row in vo_sum_wall:
            dt_sum_wall.add_row(row)


        if ctype == 'column_jobs':
            return dt_jobs.get_json()
        if ctype == 'column_wall':
            return dt_wall.get_json()
        if ctype == 'pie_jobs':
            return dt_sum_jobs.get_json()
        if ctype == 'pie_wall':
            return dt_sum_wall.get_json()

        
        c.json_vo_jobs = dt_jobs.get_json()
        c.json_vo_wall = dt_wall.get_json()
        c.json_sum_jobs = dt_sum_jobs.get_json()
        c.json_sum_wall = dt_sum_wall.get_json()
        c.key_order = key_order
            
        return render('/derived/gridadmin/statistics/vo_form.html')
 


    def sgas(self):
        """ display statistics from SGAS accouting records """

        SCALING_FACTOR = Decimal(1)/Decimal(3600) # 1/60 minutes, 1/3600 hours  
        
        c.title = "Monitoring System: VO/Grid Admin Statistics -- Usage Tables --"
        c.menu_active = "Usage Tables"
        c.form_error = None
       
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
