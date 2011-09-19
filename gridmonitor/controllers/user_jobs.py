import logging
import json
from pylons import session
from pylons import tmpl_context as c
from pylons import app_globals as g
from pylons.templating import render_mako as render

from user import UserController
from jobs import JobsController 

log = logging.getLogger(__name__)

class UserJobsController(UserController):
    
    
    def index(self):
        
        c.title = "Monitoring System: User Jobs"
        c.menu_active = "My Jobs"
        c.heading = "Information about User Jobs"

        jc = JobsController()
         
        c.jobs_states =  json.loads(jc.get_ucj_states())

        if c.jobs_states['summary']['orphaned'] > 0:
            c.orphaned = True
        else:
            c.orphaned = False

        return render('/derived/user/jobs/index.html')
 
    def show(self, status):
         
        c.user_slcs_dn = None       
        c.user_client_dn = None
        
        if session.has_key('user_slcs_obj'):
            user_slcs_obj = session['user_slcs_obj']
            c.user_slcs_dn = user_slcs_obj.get_dn()
            c.user_slcs_ca = user_slcs_obj.get_ca()

        if session.has_key('user_client_dn'):
            c.user_client_dn = session['user_client_dn']
            if session.has_key('user_client_ca'):
                c.user_client_ca = session['user_client_ca']
        
        c.job_list = list()  # double list        

        c.job_status = status
        c.menu_active = status
        
        if status != 'all':
            if status == 'orphaned':
                c.heading = "Orphaned Jobs"
                c.title = "Orphaned Jobs"
            else:
                c.heading = "Jobs in status: '%s'" % c.job_status
                c.title = c.heading
            jl = g.get_user_jobs(c.user_slcs_dn, status)
            c.job_list.append(jl)
            if c.user_client_dn:
                jl = g.get_user_jobs(c.user_client_dn, status)
                c.job_list.append(jl)
        else:
            c.heading = "All of Your Jobs"
            c.title = "All of Your Jobs"
            jl = g.get_user_jobs(c.user_slcs_dn)
            c.job_list.append(jl)
            if c.user_client_dn:
                jl = g.get_user_jobs(c.user_client_dn)
                c.job_list.append(jl)
            
            log.debug(c.job_list)
        return render('/derived/user/jobs/show.html')
		 
