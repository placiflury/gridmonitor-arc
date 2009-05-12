import logging

from gridmonitor.lib.base import *
#from gridmonitor.model.user_info import UserInfo
from user import UserController 

log = logging.getLogger(__name__)

class UserJobsController(UserController):
    
    # XXX  use user browser certificate as well
   
    def __init__(self): 
        UserController()
        c.userDN  = c.user_slcs_obj.get_dn()
 
    def index(self):
       
        
        c.title = "Monitoring System: User Jobs"
        c.menu_active = "My Jobs"
        c.heading = "Summary of Jobs submited by User"
            
        return render('/derived/user/jobs/index.html')
 
    def show(self, status):
        c.job_status = status
        c.menu_active = status
        if status != 'all':
            c.heading = "Jobs in status: '%s'" % c.job_status
            c.title = c.heading
            c.job_list = g.get_user_jobs(c.userDN,status)

        else:
            c.heading = "All of Your Jobs"
            c.title = "All of Your Jobs"
            c.job_list = g.get_user_jobs(c.userDN)
            log.debug(c.job_list)
        return render('/derived/user/jobs/show.html')
		 
