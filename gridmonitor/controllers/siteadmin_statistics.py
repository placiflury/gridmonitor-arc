import logging
from datetime import datetime
import time, calendar
from decimal import Decimal

from gridmonitor.lib.base import *
from gridmonitor.model.statistics.series import Series
from siteadmin import SiteadminController 

from sqlalchemy import and_
from sgas.db import sgas_meta
from sgas.db import ag_schema # schema of tables of aggregated usage record 
from sgas.db import sgas_schema  # original SGAS schema
from sgas.utils import helpers 


log = logging.getLogger(__name__)

class SiteadminStatisticsController(SiteadminController):
    
    def index(self):

        c.title = "Monitoring System: Site Admin Statistics"
        c.menu_active = "Site Statistics"
        c.heading = "Site Statistics"
        
        c.form_error =''
        resolution = 86400
        
        series = dict()

        if not request.params.has_key('start_t_str'): # setting defaults
            now = int(time.time())
            secs_back = 28 * resolution  # 4 weeks
            start_t = now - (now % resolution) - secs_back
            end_t = now
            start_t_str = time.strftime("%d.%m.%Y", time.gmtime(start_t))        
            end_t_str = time.strftime("%d.%m.%Y", time.gmtime(now))
            for cluster in self.clusters:
                series[cluster] = dict()
                series[cluster]['n_jobs'] = Series('n_jobs',start_t, end_t,resolution)
                series[cluster]['major_page_faults'] = Series('major_page_faults',start_t, end_t,resolution)
                series[cluster]['cpu_duration'] = Series('cpu_duration',start_t, end_t,resolution)
                series[cluster]['wall_duration'] = Series('wall_duration',start_t, end_t,resolution)
            c.n_jobs_page_faults = True
            c.cpu_wall_duration = True
        else: 
            start_t_str = request.params['start_t_str'] 
            end_t_str = request.params['end_t_str'] 
            log.info('%s %s' % (start_t_str, end_t_str))
            try:
                start_t = calendar.timegm(time.strptime(start_t_str,'%d.%m.%Y'))
                end_t = calendar.timegm(time.strptime(end_t_str,'%d.%m.%Y'))
                if end_t < start_t:
                    t = end_t
                    end_t = start_t
                    start_t = t
                elif end_t == start_t: # same day
                    start_t = end_t - resolution
            except:
                c.form_error = "Please enter dates in 'dd.mm.yyyy' format"
                return render('/derived/siteadmin/statistics/form.html')

            resolution = int(request.params['resolution'])

            for cluster in self.clusters:
                series[cluster] = dict()
                if request.params.has_key('n_jobs_page_faults') and resolution > 0:
                    series[cluster]['n_jobs'] = Series('n_jobs',start_t, end_t,resolution)
                    series[cluster]['major_page_faults'] = \
                        Series('major_page_faults',start_t, end_t,resolution)
                    c.n_jobs_page_faults = True
                elif request.params.has_key('n_jobs_page_faults'):
                    series[cluster]['major_page_faults'] = \
                        Series('major_page_faults',start_t, end_t,resolution)
                if request.params.has_key('cpu_wall_duration'):
                    series[cluster]['cpu_duration'] = Series('cpu_duration',start_t, end_t,resolution)
                    series[cluster]['wall_duration'] = Series('wall_duration',start_t, end_t,resolution)
                    c.cpu_wall_duration = True
                if request.params.has_key('user_kernel_time'):
                    series[cluster]['user_time'] = Series('user_time',start_t, end_t,resolution)
                    series[cluster]['kernel_tiem'] = Series('kernel_time',start_t, end_t,resolution)
                    c.user_kernel_time = True
            if request.params.has_key('plot_table'):
                c.plot_table = True  
       
        t_ref = None # for resolutions > 86440 we need to callibrate time series

        for cluster in self.clusters:
            for acrec in  helpers.get_cluster_acrecords(cluster, start_t, end_t, resolution):
                if resolution == 0: # convert datetime to epoch time
                    t_epoch = time.mktime(acrec.end_time.timetuple()) + \
                    acrec.end_time.microsecond/1000000.0 - time.timezone
                else:
                    t_epoch = acrec.t_epoch
                    t_ref = t_epoch
                for k in series[cluster].keys():
                    series[cluster][k].add_sample(t_epoch, eval('acrec.%s' % k))

        c.end_t_str_max = time.strftime("%d.%m.%Y", time.gmtime())
        c.start_t_str = start_t_str
        c.end_t_str = end_t_str
        
        start_tp = start_t
        end_tp = end_t 
        
        if c.plot_table or resolution == 0:
            # XXX to do 
            log.info("XXX, only tables or original resolution")
            return render('/derived/siteadmin/statistics/form.html')
            
        else:
            n_samples = (end_t - start_t)/ resolution
            n_padding = (28 - n_samples % 28) % 28
            c.samples = n_samples + n_padding 
        
            if n_padding > 0:
                t_now = time.time()
                n_samples_right = int(t_now - end_t) / resolution
                if n_samples_right > n_padding:
                    n_samples_right = n_padding
                    start_tp = start_t
                else:
                    n_samples_left = n_padding - n_samples_right
                    start_tp = start_t - (n_samples_left) * resolution
                end_tp = end_t + (n_samples_right) * resolution
                # markers for plot (chm)
                c.start_chm = n_samples_left
                c.end_chm = n_samples_left +  n_samples
                log.debug("Dummy samples left %0.2f samples right %0.2f" % (n_samples_left, n_samples_right))

            if (resolution > 86400) and t_ref: # callibration
                t_offset = (t_ref - start_tp) % resolution
                start_tp += t_offset
                end_tp += t_offset
            
            ref_dates = range(start_tp, end_tp, resolution)
            
            minutes = Decimal(1)/Decimal(6)
        
            c.n_job_series= dict()
            c.major_page_faults_series= dict()
            c.cpu_duration_series = dict()
            c.wall_duration_series = dict()
            c.user_time_series = dict()
            c.kernel_time_series = dict()
            
            for cluster in self.clusters:
                if c.n_jobs_page_faults and resolution > 0:
                    c.n_job_series[cluster] = series[cluster]['n_jobs'].get_series2str(ref_dates)
                if c.n_jobs_page_faults:
                    c.major_page_faults_series[cluster] = \
                        series[cluster]['major_page_faults'].get_series2str(ref_dates)
                if c.cpu_wall_duration:
                        series[cluster]['cpu_duration'].set_scaling_factor(minutes)
                        series[cluster]['wall_duration'].set_scaling_factor(minutes)
                        c.cpu_duration_series[cluster] = \
                            series[cluster]['cpu_duration'].get_series2str(ref_dates)
                        c.wall_duration_series[cluster] = \
                            series[cluster]['wall_duration'].get_series2str(ref_dates)
                if c.user_kernel_time:
                    series[cluster]['user_time'].set_scaling_factor(minutes)
                    series[cluster]['kernel_time'].set_scaling_factor(minutes)
                    c.user_time_series[cluster] = series[cluster]['user_time'].get_series2str(ref_dates)
                    c.kernel_time_series[cluster] = series[cluster]['kernel_time'].get_series2str(ref_dates)
            
            slice_size = (end_tp - start_tp)/4
            d0 = datetime.utcfromtimestamp(start_tp)
            d1 = datetime.utcfromtimestamp(start_tp + slice_size)
            d2 = datetime.utcfromtimestamp(start_tp + 2 * slice_size)
            d3 = datetime.utcfromtimestamp(start_tp + 3 * slice_size)
            d4 = datetime.utcfromtimestamp(end_t)
            c.dates = '%d/%d/%d|%d/%d/%d|%d/%d/%d|%d/%d/%d|%d/%d/%d' % \
                (d0.day,d0.month, d0.year%100, 
                d1.day, d1.month, d1.year%100,
                d2.day, d2.month, d2.year%100,
                d3.day, d3.month, d3.year%100, 
                d4.day, d4.month, d4.year%100)

        c.clusters = self.clusters
        c.series = series
        c.resolution = resolution
        return render('/derived/siteadmin/statistics/form.html')

 
    def old_index(self):

        c.title = "Monitoring System: Site Admin Statistics"
        c.menu_active = "Site Statistics"
        c.heading = "Site Statistics"
        
        resolution_1 = 86400  # XXX read from config 
        
        # fetching records four weeks back
        now_epoch = int(time.time())
        secs_back = 86400 * 28
        start_t_epoch = now_epoch - (now_epoch % resolution_1) - secs_back
        
        cluster_db_ids = dict()
        for cluster_hostname in self.clusters: 
            rec = sgas_meta.Session.query(sgas_schema.MachineName). \
                filter_by(machine_name = cluster_hostname).first()
            if rec:
                cluster_db_ids[rec.id] = cluster_hostname
      
        log.debug('Feched following cluster maps (SGAS) %r' % cluster_db_ids) 

        t_series = dict() # [time : {cluster_name: {values}}]     
        n_jobs_max = dict()
        major_page_faults_max = dict()
        cpu_duration_max = dict()
        wall_duration_max = dict()
        user_time_max = dict()
        kernel_time_max = dict()

        # query all machines and not only those of site (minimize # of queries) 
        for rec in sgas_meta.Session.query(ag_schema.Machine).filter(and_(
            ag_schema.Machine.t_epoch >= start_t_epoch,
            ag_schema.Machine.resolution == resolution_1)).all():
            
            if not cluster_db_ids.has_key(rec.m_id):
                continue

            cluster_name= cluster_db_ids[rec.m_id]
            stats = dict(resolution = rec.resolution,
                    n_jobs = rec.n_jobs,
                    cpu_duration = rec.cpu_duration,
                    wall_duration = rec.wall_duration,
                    major_page_faults = rec.major_page_faults,
                    user_time = rec.user_time,
                    kernel_time = rec.kernel_time)

            if not t_series.has_key(rec.t_epoch):
                t_series[rec.t_epoch] = {cluster_name : stats}
            else:
                t_series[rec.t_epoch][cluster_name] = stats

            n_jobs_max[cluster_name]            = max(n_jobs_max.get(cluster_name), rec.n_jobs)
            major_page_faults_max[cluster_name] = max(major_page_faults_max.get(cluster_name), rec.major_page_faults)
            wall_duration_max[cluster_name]     = max(wall_duration_max.get(cluster_name), rec.wall_duration)
            cpu_duration_max[cluster_name]      = max(cpu_duration_max.get(cluster_name), rec.cpu_duration)
            user_time_max[cluster_name]         = max(user_time_max.get(cluster_name), rec.user_time)
            kernel_time_max[cluster_name]       = max(kernel_time_max.get(cluster_name), rec.kernel_time)


        # preparations for plots

        c.n_jobs_max = n_jobs_max
        c.major_page_faults_max = major_page_faults_max
        c.cpu_duration_max = dict()
        for k,v in cpu_duration_max.items():
            c.cpu_duration_max[k] = float(v/60)
        c.wall_duration_max = dict()
        for k,v in wall_duration_max.items():
            c.wall_duration_max[k] = float(v/60)
        c.user_time_max = dict()
        for k,v in user_time_max.items():
            c.user_time_max[k] = float(v/60)

        c.kernel_time_max = dict()
        for k,v in kernel_time_max.items():
            c.kernel_time_max[k] = float(v/60)

        # dates
        w4 = datetime.utcfromtimestamp(start_t_epoch)
        w3 = datetime.utcfromtimestamp(start_t_epoch + 604800) # 1 week in secs
        w2 = datetime.utcfromtimestamp(start_t_epoch + 1209600) # 2 weeks in secs
        w1 = datetime.utcfromtimestamp(start_t_epoch + 1814400) # 3 weeks in secs
        to = datetime.today()
        c.dates = '%d/%d/%d|%d/%d/%d|%d/%d/%d|%d/%d/%d|%d/%d/%d' % \
            (w4.day,w4.month, w4.year%100,
            w3.day, w3.month, w3.year%100,
            w2.day, w2.month, w2.year%100,
            w1.day, w1.month, w1.year%100,
            to.day, to.month, to.year%100)


        c.n_job_series = dict()
        c.major_page_faults_series = dict()
        c.cpu_series = dict()
        c.wall_series = dict()
        c.user_series = dict()
        c.kernel_series= dict()

        for cluster_name in cluster_db_ids.values():
            c.n_job_series[cluster_name] = ''
            c.major_page_faults_series[cluster_name] = ''
            c.cpu_series[cluster_name] = ''
            c.wall_series[cluster_name] = ''
            c.user_series[cluster_name] = ''
            c.kernel_series[cluster_name] = ''


        for date in xrange(start_t_epoch + resolution_1, now_epoch + resolution_1, resolution_1):
            for cluster_name in cluster_db_ids.values():
                if t_series.has_key(date) and t_series[date].has_key(cluster_name):
                    if c.n_job_series[cluster_name]:
                        c.n_job_series[cluster_name] += ',%d' % \
                            t_series[date][cluster_name]['n_jobs']
                        c.major_page_faults_series[cluster_name] += ',%d' % \
                             t_series[date][cluster_name]['major_page_faults']
                        c.cpu_series[cluster_name] += ',%0.2f' % \
                            (t_series[date][cluster_name]['cpu_duration'] / 60)
                        c.wall_series[cluster_name] += ',%0.2f' % \
                            (t_series[date][cluster_name]['wall_duration'] / 60)
                        c.user_series[cluster_name] += ',%0.2f' % \
                            (t_series[date][cluster_name]['user_time'] / 60 )
                        c.kernel_series[cluster_name] += ',%0.2f' % \
                            (t_series[date][cluster_name]['kernel_time'] / 60)
                    else:
                        c.n_job_series[cluster_name] += '%d' % \
                            t_series[date][cluster_name]['n_jobs']
                        c.major_page_faults_series[cluster_name] += ',%d' % \
                             t_series[date][cluster_name]['major_page_faults']
                        c.cpu_series[cluster_name] += '%0.2f' % \
                            (t_series[date][cluster_name]['cpu_duration'] / 60)
                        c.wall_series[cluster_name] += '%0.2f' % \
                            (t_series[date][cluster_name]['wall_duration'] / 60)
                        c.user_series[cluster_name] += '%0.2f' % \
                            (t_series[date][cluster_name]['user_time'] / 60 )
                        c.kernel_series[cluster_name] += '%0.2f' % \
                            (t_series[date][cluster_name]['kernel_time'] / 60)
                else:
                    if c.n_job_series[cluster_name]:
                        c.n_job_series[cluster_name] += ',_'
                        c.major_page_faults_series[cluster_name] += ',_'
                        c.cpu_series[cluster_name] += ',_'
                        c.wall_series[cluster_name] += ',_'
                        c.user_series[cluster_name] += ',_'
                        c.kernel_series[cluster_name] += ',_'
                    else:
                        c.n_job_series[cluster_name] = '_'
                        c.major_page_faults_series[cluster_name] = '_'
                        c.cpu_series[cluster_name] = '_'
                        c.wall_series[cluster_name] = '_'
                        c.user_series[cluster_name] = '_'
                        c.kernel_series[cluster_name] = '_'

            

        return render('/derived/siteadmin/statistics/index.html')
