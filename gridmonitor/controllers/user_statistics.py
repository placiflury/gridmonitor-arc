import logging, time
from datetime import datetime

from gridmonitor.lib.base import *
from user import UserController 

from sqlalchemy import and_ 
from sgas.db import sgas_meta
from sgas.db import ag_schema # schema of tables of aggregated usage record 
from sgas.db import sgas_schema  # original SGAS schema

log = logging.getLogger(__name__)

class UserStatisticsController(UserController):
    
    def index(self):
        c.title = "Monitoring System: User Job  Statistics"
        c.menu_active = "My Statistics"
        c.heading = "My Job Statistics"

        slcs_dn_id = None
        browser_dn_id = None
        resolution_1 = 86400  # XXX read from config 

        # get all job records of user (for browser and SLCS cert)

        slcs_dn = c.user_slcs_obj.get_dn()
        rec = sgas_meta.Session.query(sgas_schema.GlobalUserName). \
            filter_by(global_user_name=slcs_dn).first()

        if rec:
            slcs_dn_id = rec.id

        browser_dn = c.user_client_dn

        rec  = sgas_meta.Session.query(sgas_schema.GlobalUserName). \
            filter_by(global_user_name=browser_dn).first()

        if rec:
            browser_dn_id = rec.id
       
       
        # fetching records four weeks back
        now_epoch = int(time.time())
        secs_back = 86400 * 28
        start_t_epoch = now_epoch - (now_epoch % resolution_1) - secs_back


        t_series = dict() # [time : {values}]     
        n_jobs_max = 0
        major_page_faults_max = 0       
        cpu_duration_max = 0
        wall_duration_max = 0
        user_time_max = 0
        kernel_time_max = 0
 
        if slcs_dn_id:
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
        c.cpu_duration_max = cpu_duration_max / 60  # conversion in minutes
        c.wall_duration_max = wall_duration_max / 60
        c.kernel_time_max = kernel_time_max / 60 
        c.user_time_max = user_time_max / 60
        
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
                    c.n_job_series += ',%s' % t_series[date]['n_jobs']
                    c.major_page_faults_series += ',%s' % t_series[date]['major_page_faults']
                    c.cpu_series += ',%s' % (t_series[date]['cpu_duration'] / 60)
                    c.wall_series += ',%s' % (t_series[date]['wall_duration'] / 60) 
                    c.user_series += ',%s' % (t_series[date]['user_time'] / 60 )
                    c.kernel_series += ',%s' % (t_series[date]['kernel_time'] / 60) 
            
                else:
                    c.n_job_series = '%s' % t_series[date]['n_jobs']
                    c.major_page_faults_series = '%s' % t_series[date]['major_page_faults']
                    c.cpu_series += '%s' % (t_series[date]['cpu_duration'] / 60)
                    c.wall_series += '%s' % (t_series[date]['wall_duration'] / 60) 
                    c.user_series += '%s' % (t_series[date]['user_time'] / 60 )
                    c.kernel_series += '%s' % (t_series[date]['kernel_time'] / 60)
                    
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
