import logging, time
from datetime import datetime
import time, calendar
from decimal import Decimal

from gridmonitor.lib.base import *
from gridmonitor.model.statistics.series import Series
from user import UserController 

from sqlalchemy import and_ , or_
from sgas.db import sgas_meta
from sgas.db import ag_schema # schema of tables of aggregated usage record 
from sgas.db import sgas_schema  # original SGAS schema
from sgas.utils import helpers 

log = logging.getLogger(__name__)

class UserStatisticsController(UserController):


    def index(self):

        c.title = "Monitoring System: User Job Statistics"
        c.menu_active = "Statistics about my Jobs"
        c.heading = "Statistics about my Jobs"
       
        c.form_error =''
        
        resolution = 86400 # 1 day
        series = dict()

        if not request.params.has_key('start_t_str'): # setting defaults
            now = int(time.time())
            secs_back = 28 * resolution  # 4 weeks
            start_t = now - (now % resolution) - secs_back
            end_t = now
            start_t_str = time.strftime("%d.%m.%Y", time.gmtime(start_t))        
            end_t_str = time.strftime("%d.%m.%Y", time.gmtime(now))
            series['n_jobs'] = Series('n_jobs',start_t, end_t,resolution)
            series['major_page_faults'] = Series('major_page_faults',start_t, end_t,resolution)
            series['cpu_duration'] = Series('cpu_duration',start_t, end_t,resolution)
            series['wall_duration'] = Series('wall_duration',start_t, end_t,resolution)
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
            except:
                c.form_error = "Please enter dates in 'dd.mm.yyyy' format"
                return render('/derived/user/statistics/form.html')

            resolution = int(request.params['resolution'])

            if request.params.has_key('n_jobs_page_faults') and resolution > 0:
                series['n_jobs'] = Series('n_jobs',start_t, end_t,resolution)
                series['major_page_faults'] = Series('major_page_faults',start_t, end_t,resolution)
                c.n_jobs_page_faults = True
            elif request.params.has_key('n_jobs_page_faults'):
                series['major_page_faults'] = Series('major_page_faults',start_t, end_t,resolution)
            if request.params.has_key('cpu_wall_duration'):
                series['cpu_duration'] = Series('cpu_duration',start_t, end_t,resolution)
                series['wall_duration'] = Series('wall_duration',start_t, end_t,resolution)
                c.cpu_wall_duration = True
            if request.params.has_key('user_kernel_time'):
                series['user_time'] = Series('user_time',start_t, end_t,resolution)
                series['kernel_time'] = Series('kernel_time',start_t, end_t,resolution)
                c.user_kernel_time = True
            if request.params.has_key('plot_table'):
                c.plot_table = True  
        
        slcs_dn = c.user_slcs_obj.get_dn()
        browser_dn = c.user_client_dn
       
        t_ref = None # for resolutions > 86440 we need to callibrate time series
 
        if slcs_dn:
            for acrec in  helpers.get_user_acrecords(slcs_dn, start_t, end_t, resolution):
                if resolution == 0: # convert datetime to epoch time
                    t_epoch = time.mktime(acrec.end_time.timetuple()) + \
                    acrec.end_time.microsecond/1000000.0 - time.timezone
                else:
                    t_epoch = acrec.t_epoch
                    t_ref = t_epoch

                for k in series.keys():
                    series[k].add_sample(t_epoch, eval('acrec.%s' % k))

        if browser_dn:
            for acrec in  helpers.get_user_acrecords(browser_dn, start_t, end_t, resolution):
                if resolution == 0: # convert datetime to epoch time
                    t_epoch = time.mktime(acrec.end_time.timetuple()) + \
                    acrec.end_time.microsecond/1000000.0 - time.timezone
                else:
                    t_epoch = acrec.t_epoch
                    t_ref = t_epoch
                for k in series.keys():
                    series[k].add_sample(t_epoch, eval('acrec.%s' % k))
       
 
        c.end_t_str_max = time.strftime("%d.%m.%Y", time.gmtime())
        c.start_t_str = start_t_str
        c.end_t_str = end_t_str
        
        start_tp = start_t
        end_tp = end_t 
        
        if c.plot_table or resolution == 0:
            # XXX to do 
            log.info("XXX, only tables or original resolution")
            return render('/derived/user/statistics/form.html')
            
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
                
            if c.n_jobs_page_faults:
                c.n_job_series = series['n_jobs'].get_series2str(ref_dates)
                c.major_page_faults_series = series['major_page_faults'].get_series2str(ref_dates)
            if c.cpu_wall_duration:
                series['cpu_duration'].set_scaling_factor(minutes)
                series['wall_duration'].set_scaling_factor(minutes)
                c.cpu_duration_series = series['cpu_duration'].get_series2str(ref_dates)
                c.wall_duration_series = series['wall_duration'].get_series2str(ref_dates)
            if c.user_kernel_time:
                series['user_time'].set_scaling_factor(minutes)
                series['kernel_time'].set_scaling_factor(minutes)
                c.user_time_series = series['user_time'].get_series2str(ref_dates)
                c.kernel_time_series = series['kernel_time'].get_series2str(ref_dates)
            
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

        c.series = series
        c.resolution = resolution
        return render('/derived/user/statistics/form.html')



    def test(self):
        c.title = "Selection of statistics."
        c.menu_active = "Statistics about my Jobs"

        return render('/derived/user/statistics/form.html')

