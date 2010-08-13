import logging, time
from datetime import datetime

from gridmonitor.lib.base import *
from siteadmin import SiteadminController 

from sqlalchemy import and_
from sgas.db import sgas_meta
from sgas.db import ag_schema # schema of tables of aggregated usage record 
from sgas.db import sgas_schema  # original SGAS schema


log = logging.getLogger(__name__)

class SiteadminStatisticsController(SiteadminController):
    
    def index(self):

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
        sum_n_jobs= dict() 
        major_page_faults_max = dict()
        sum_major_page_faults = dict()
        cpu_duration_max = dict()
        sum_cpu_duration = dict()
        wall_duration_max = dict()
        sum_wall_duration = dict()
        user_time_max = dict()
        sum_user_time = dict()
        kernel_time_max = dict()
        sum_kernel_time = dict()
        
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
          
            
 
            if not n_jobs_max.has_key(cluster_name):
                n_jobs_max[cluster_name] = rec.n_jobs
                major_page_faults_max[cluster_name] = rec.major_page_faults
                wall_duration_max[cluster_name] = rec.wall_duration
                cpu_duration_max[cluster_name] = rec.cpu_duration
                user_time_max[cluster_name] = rec.user_time
                kernel_time_max[cluster_name] = rec.kernel_time
                continue 
        
            if rec.major_page_faults > major_page_faults_max[cluster_name]:
                major_page_faults_max[cluster_name] = rec.major_page_faults
            if rec.n_jobs > n_jobs_max[cluster_name]:
                n_jobs_max[cluster_name] = rec.n_jobs
            if rec.wall_duration > wall_duration_max[cluster_name]:
                wall_duration_max[cluster_name] = rec.wall_duration
            if rec.cpu_duration > cpu_duration_max[cluster_name]:
                cpu_duration_max[cluster_name] = rec.cpu_duration
            if rec.user_time > user_time_max[cluster_name]:
                user_time_max[cluster_name] = rec.user_time
            if rec.kernel_time > kernel_time_max[cluster_name]:
                kernel_time_max[cluster_name] = rec.kernel_time
            
        
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
