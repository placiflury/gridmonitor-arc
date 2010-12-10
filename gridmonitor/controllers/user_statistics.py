import logging
from datetime import datetime
import time, calendar
from decimal import Decimal

from gridmonitor.lib.base import *
from gridmonitor.model.statistics.series import Series
from user import UserController 
from sgasaggregator.utils import helpers 
from sgasaggregator.sgascache import session as sgascache_session

log = logging.getLogger(__name__)

class UserStatisticsController(UserController):
    

    def index(self):
        
        SCALING_FACTOR = Decimal(1)/Decimal(60) # 1/60 minutes, 1/3600 hours  
        
        c.title = "Monitoring System: User Job Statistics"
        c.menu_active = "Statistics about my Jobs"
        c.heading = "Statistics about my Jobs"

        c.form_error =''
        resolution = 86400 # 1 day
        series = dict()
        
        if not request.params.has_key('start_t_str'): # DEFAULT SETTINGS
            _end_t= int(time.time())  # now
            _start_t = _end_t - 27 * 86400  # 4 weeks back (0-27 days)
            
            start_t, end_t = helpers.get_sampling_interval(_start_t,_end_t, resolution)
            
            series['A_n_jobs'] = Series('n_jobs',start_t, end_t,resolution) # A_ prefix used for sorting order
            series['B_major_page_faults'] = Series('major_page_faults',start_t, end_t, resolution)
            series['C_cpu_duration'] = Series('cpu_duration',start_t, end_t, resolution)
            series['D_wall_duration'] = Series('wall_duration',start_t, end_t, resolution)
            series['C_cpu_duration'].set_scaling_factor(SCALING_FACTOR)
            series['D_wall_duration'].set_scaling_factor(SCALING_FACTOR)
            c.n_jobs_page_faults = True
            c.cpu_wall_duration = True
        else:                                       # USER SETTINGS
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
                return render('/derived/user/statistics/form.html')

            start_t, end_t = helpers.get_sampling_interval(_start_t,_end_t, resolution)

            if request.params.has_key('n_jobs_page_faults') and resolution > 0:
                series['A_n_jobs'] = Series('n_jobs',start_t, end_t, resolution)
                series['B_major_page_faults'] = Series('major_page_faults',start_t, end_t, resolution)
                c.n_jobs_page_faults = True
            elif request.params.has_key('n_jobs_page_faults'):
                series['B_major_page_faults'] = Series('major_page_faults',start_t, end_t, resolution)
            if request.params.has_key('cpu_wall_duration'):
                series['C_cpu_duration'] = Series('cpu_duration',start_t, end_t,resolution)
                series['D_wall_duration'] = Series('wall_duration',start_t, end_t,resolution)
                series['C_cpu_duration'].set_scaling_factor(SCALING_FACTOR)
                series['D_wall_duration'].set_scaling_factor(SCALING_FACTOR)
                c.cpu_wall_duration = True
            if request.params.has_key('user_kernel_time'):
                series['E_user_time'] = Series('user_time',start_t, end_t,resolution)
                series['F_kernel_time'] = Series('kernel_time',start_t, end_t,resolution)
                series['E_user_time'].set_scaling_factor(SCALING_FACTOR)
                series['F_kernel_time'].set_scaling_factor(SCALING_FACTOR)
                c.user_kernel_time = True
            if request.params.has_key('table_only'):
                c.table_only = True  
      
        c.end_t_str_max = time.strftime("%d.%m.%Y", time.gmtime())
        c.start_t_str = time.strftime("%d.%m.%Y", time.gmtime(start_t))        
        c.end_t_str = time.strftime("%d.%m.%Y", time.gmtime(end_t - 86400))   # hack to avoid increasing date 
                                                                            # upon form resubmission
        
        if session.has_key('user_slcs_obj'):
            user_slcs_obj = session['user_slcs_obj']
            slcs_dn = user_slcs_obj.get_dn()
            for acrec in  helpers.get_user_acrecords(slcs_dn, _start_t, _end_t, resolution):
                t_epoch = acrec.t_epoch
                for k in series.keys():
                    k_ = k[2:] # removing sorting prefix
                    series[k].add_sample(t_epoch, eval('acrec.%s' % k_))
        
        if session.has_key('user_client_dn'):
            browser_dn = session['user_client_dn']
            for acrec in  helpers.get_user_acrecords(browser_dn, _start_t, _end_t, resolution):
                t_epoch = acrec.t_epoch
                log.debug("start_t=%d, end_t=%d got record at epoch %d " % (_start_t, _end_t,t_epoch))
                for k in series.keys():
                    k_ = k[2:] # removing sorting prefix
                    series[k].add_sample(t_epoch, eval('acrec.%s' % k_))
       
 
        
        c.series = series
        c.resolution = resolution
        
        if c.table_only:
            c.start_t_epoch = start_t 
            c.end_t_epoch  = end_t
            return render('/derived/user/statistics/form.html')
        else:
            start_tp = start_t # plot start time
            end_tp = end_t     # plot end time

            n_samples = (end_t  - start_t)/ resolution 
            n_padding = (28 - n_samples % 28) % 28
            c.samples = n_samples + n_padding 
            log.debug("n_samples: %d, n_padding:%d" % (n_samples, n_padding))
         
            if n_padding > 0:
                # let's pad at both sites, if end_t < t_now
                t_now = int(time.time())
                n_right = 0
                if end_t < t_now:
                    pad_start_t, pad_end_t = helpers.get_sampling_interval(end_t, t_now, resolution) 
                    n_right = (pad_end_t - pad_start_t) / resolution 
            
                if n_right >= (n_padding/2):
                    n_samples_right = n_padding/2
                else:
                    n_samples_right = n_right
                
                n_samples_left = n_padding - n_samples_right


                start_tp = start_t -  n_samples_left * resolution
                end_tp =  end_t +  n_samples_right  * resolution 
                # markers for plot (chm)
                c.start_chm = n_samples_left 
                c.end_chm = n_samples_left +  n_samples + 1 # +1 for display
                log.debug("Padding samples left %d samples right %d" % (n_samples_left, n_samples_right))

            
            # shift ref-dates to 23:59:59 time of day, thus adding (resolution - 1)
            ref_start_t = start_tp + resolution  - 1
            ref_end_t = end_tp + resolution - 1
            ref_dates = range(ref_start_t, ref_end_t, resolution)
            log.debug("ref dates: %r " % ref_dates)
            log.debug("start_tp %s  end_tp %s  " % (datetime.utcfromtimestamp(start_tp), 
                datetime.utcfromtimestamp(end_tp)))
                
            if c.n_jobs_page_faults:
                c.n_job_series = series['A_n_jobs'].get_series2str(ref_dates)
                c.major_page_faults_series = series['B_major_page_faults'].get_series2str(ref_dates)
            if c.cpu_wall_duration:
                c.cpu_duration_series = series['C_cpu_duration'].get_series2str(ref_dates)
                c.wall_duration_series = series['D_wall_duration'].get_series2str(ref_dates)
            if c.user_kernel_time:
                c.user_time_series = series['E_user_time'].get_series2str(ref_dates)
                c.kernel_time_series = series['F_kernel_time'].get_series2str(ref_dates)
            
            slice_size = (end_tp - start_tp)/4.0
            log.debug("Plot slice size %0.2f" % slice_size)
            d0 = datetime.utcfromtimestamp(start_tp)
            d1 = datetime.utcfromtimestamp(start_tp + slice_size)
            d2 = datetime.utcfromtimestamp(start_tp + 2 * slice_size)
            d3 = datetime.utcfromtimestamp(start_tp + 3 * slice_size)
            d4 = datetime.utcfromtimestamp(end_tp)
            c.dates = '%d/%d/%d|%d/%d/%d|%d/%d/%d|%d/%d/%d|%d/%d/%d' % \
                (d0.day, d0.month, d0.year%100, 
                d1.day, d1.month, d1.year%100,
                d2.day, d2.month, d2.year%100,
                d3.day, d3.month, d3.year%100, 
                d4.day, d4.month, d4.year%100)

        return render('/derived/user/statistics/form.html')



    def test(self):
        c.title = "Selection of statistics."
        c.menu_active = "Statistics about my Jobs"

        return render('/derived/user/statistics/form.html')

