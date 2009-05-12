import logging

from gridmonitor.lib.base import *
from user import UserController 
from pylons import config, request

log = logging.getLogger(__name__)

class UserOverviewController(UserController):
    
    def index(self):
        c.title = "Monitoring System: User View"
        c.menu_active = "Overview"
        c.heading = "Welcome  %s %s" % (c.user_name,c.user_surname)
        return render('/derived/user/overview/index.html')

 
    def core(self):
        c.title = "Monitoring System: User View"
        c.menu_active="Core Services"
        c.heading = "Core Services Status"
        return render('/derived/user/overview/core.html')
    
    def reports(self):
        c.title = "Monitoring System: User View"
        c.menu_active="Reports"
        c.heading = "Reports"
        return render('/derived/user/overview/report.html')
	 
