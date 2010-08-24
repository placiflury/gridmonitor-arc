import logging, time
from datetime import datetime

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

    series_map = {'n_jobs_page_faults': ['n_jobs','major_page_faults'], 
                    'cpu_wall_duration' : ['cpu_duration','wall_duration'], 
                    'user_kernel_time' : ['user_time', 'kernel_time'], 
                    'status' : ['status']}    



    def index(self):
        c.title = "Monitoring System: User Job Statistics"
        c.menu_active = "Statistics about my Jobs"
        c.heading = "Statistics about my Jobs"
       
        c.form_error =''

        if not request.params.has_key('start_t_str'): # setting defaults
            resolution = 86400 # 1 day
            now_epoch = int(time.time())
            secs_back = 28 * resolution  # 4 weeks
            start_t = now_epoch - (now_epoch % resolution) - secs_back
            start_t_str = time.strftime("%d.%m.%Y", time.gmtime(start_t))        
            end_t_str = time.strftime("%d.%m.%Y", time.gmtime(now_epoch))
        else: 
            start_t_str = request.params['start_t_str']
            end_t_str = request.params['end_t_str']
            log.info('%s %s' % (start_t_str, end_t_str))
            try:
                start_t = time.mktime(time.strptime(start_t_str,'%d.%m.%Y'))
                end_t = time.mktime(time.strptime(end_t_str,'%d.%m.%Y'))
            except:
                c.form_error = "Please enter dates in 'dd.mm.yyyy' format"
                return render('/derived/user/statistics/form.html')


            c.test = list()
            resolution = int(request.params['resolution'])
            c.test.append(resolution)
            if request.params.has_key('n_jobs_page_faults'):
                c.test.append('jobs')
            if request.params.has_key('cpu_wall_duration'):
                c.test.append('cpu_wall')
            if request.params.has_key('user_kernel_time'):
                c.test.append('user_kernel')
            if request.params.has_key('job_status'):
                c.test.append('status')
            
        


 
        c.end_t_str_max = time.strftime("%d.%m.%Y", time.gmtime())
        c.start_t_str = start_t_str
        c.end_t_str = end_t_str
        return render('/derived/user/statistics/form.html')


    def old_index(self):
        
        c.title = "Monitoring System: User Job Statistics"
        c.menu_active = "Statistics about my Jobs"
        c.heading = "Statistics about my Jobs"

        if not request.params.has_key('start_t_from'): # setting defaults
            resolution = 86400 # 1 day
            now_epoch = int(time.time())
            secs_back = 28 * default_resolution  # 4 weeks
            start_t = now_epoch - (now_epoch % default_resolution) - secs_back

        else: 
            t_str = request.params['start_t_from']
            if '.' in t_str:
                dates = t_str.split('.')
            elif '/' in t_str:
                dates = t_str.plit('/')
            else:
                # fall back to 
                pass        
            

        c.now_str = time.strftime("%d/%m/%Y", time.gmtime(now_epoch))        
        c.start_t_str = time.strftime("%d/%m/%Y", time.gmtime(start_t))        
        
        


        resolution= c.default_resolution        
        start_t_epoch = default_start_t

        
        slcs_dn = c.user_slcs_obj.get_dn()
        browser_dn = c.user_client_dn

 
        if slcs_dn_id:
            s_jobs = helpers.get_user_jobs(slcs_dn, start_t_epoch, end_t_epoch, resolution)
            

            for rec in s_jobs: 
                continue


            for rec in sgas_meta.Session.query(ag_schema.User).filter(and_(
                    ag_schema.User.t_epoch >= start_t_epoch,
                    ag_schema.User.g_id == slcs_dn_id, 
                    ag_schema.User.resolution == resolution_1)). \
                    all():

                    t_series[rec.t_epoch] = dict(resolution = rec.resolution,
                    n_jobs = rec.n_jobs, 
                    cpu_duration = rec.cpu_duration,
                    wall_duration = rec.wall_duration,
                    major_page_faults = rec.major_page_faults,
                    user_time = rec.user_time,
                    kernel_time = rec.kernel_time)
                    
                    if rec.major_page_faults > major_page_faults_max:
                        major_page_faults_max = rec.major_page_faults
                    if rec.n_jobs > n_jobs_max:
                        n_jobs_max = rec.n_jobs  
                    if rec.wall_duration > wall_duration_max:
                        wall_duration_max = rec.wall_duration
                    if rec.cpu_duration > cpu_duration_max:
                        cpu_duration_max = rec.cpu_duration
                    if rec.user_time > user_time_max:
                        user_time_max = rec.user_time
                    if rec.kernel_time > kernel_time_max:
                        kernel_time_max = rec.kernel_time
        

        if browser_dn_id:
            for rec in sgas_meta.Session.query(ag_schema.User).filter(and_(
                    ag_schema.User.t_epoch >= start_t_epoch,
                    ag_schema.User.g_id == browser_dn_id,
                    ag_schema.User.resolution == resolution_1)). \
                    all():
            
                    t_series[rec.t_epoch] = dict(resolution = rec.resolution,
                    n_jobs = rec.n_jobs, 
                    cpu_duration = rec.cpu_duration,
                    wall_duration = rec.wall_duration,
                    major_page_faults = rec.major_page_faults,
                    user_time = rec.user_time,
                    kernel_time = rec.kernel_time)
                    
                    if rec.major_page_faults > major_page_faults_max:
                        major_page_faults_max = rec.major_page_faults
                    if rec.n_jobs > n_jobs_max:
                        n_jobs_max = rec.n_jobs  
                    if rec.wall_duration > wall_duration_max:
                        wall_duration_max = rec.wall_duration
                    if rec.cpu_duration > cpu_duration_max:
                        cpu_duration_max = rec.cpu_duration
                    if rec.user_time > user_time_max:
                        user_time_max = rec.user_time
                    if rec.kernel_time > kernel_time_max:
                        kernel_time_max = rec.kernel_time

        # prepare data for plot
        c.n_jobs_max = n_jobs_max
        c.major_page_faults_max = major_page_faults_max
        c.cpu_duration_max = float(cpu_duration_max / 60)  # conversion in minutes
        c.wall_duration_max = float(wall_duration_max / 60)
        c.kernel_time_max = float(kernel_time_max / 60) 
        c.user_time_max = float(user_time_max / 60)
        
        # start date
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

        c.n_job_series = ''
        c.major_page_faults_series = ''
        c.cpu_series = ''
        c.wall_series = ''
        c.user_series = ''
        c.kernel_series= ''
       
        for date in xrange(start_t_epoch + resolution_1, now_epoch + resolution_1, resolution_1):
            if t_series.has_key(date):
                if c.n_job_series:
                    c.n_job_series += ',%d' % t_series[date]['n_jobs']
                    c.major_page_faults_series += ',%d' % t_series[date]['major_page_faults']
                    c.cpu_series += ',%0.2f' % (t_series[date]['cpu_duration'] / 60)
                    c.wall_series += ',%0.2f' % (t_series[date]['wall_duration'] / 60) 
                    c.user_series += ',%0.2f' % (t_series[date]['user_time'] / 60 )
                    c.kernel_series += ',%0.2f' % (t_series[date]['kernel_time'] / 60) 
            
                else:
                    c.n_job_series = '%d' % t_series[date]['n_jobs']
                    c.major_page_faults_series = '%d' % t_series[date]['major_page_faults']
                    c.cpu_series += '%0.2f' % (t_series[date]['cpu_duration'] / 60)
                    c.wall_series += '%0.2f' % (t_series[date]['wall_duration'] / 60) 
                    c.user_series += '%0.2f' % (t_series[date]['user_time'] / 60 )
                    c.kernel_series += '%0.2f' % (t_series[date]['kernel_time'] / 60)
                    
            else:
                if c.n_job_series:
                    c.n_job_series += ',_' 
                    c.major_page_faults_series += ',_'
                    c.cpu_series += ',_' 
                    c.wall_series += ',_'
                    c.user_series += ',_' 
                    c.kernel_series += ',_'
                else:
                    c.n_job_series = '_' 
                    c.major_page_faults_series = '_' 
                    c.cpu_series = '_' 
                    c.wall_series = '_'
                    c.user_series = '_' 
                    c.kernel_series = '_'


        return render('/derived/user/statistics/index.html')

    def test(self):
        c.title = "Selection of statistics."
        c.menu_active = "Statistics about my Jobs"

        return render('/derived/user/statistics/form.html')

