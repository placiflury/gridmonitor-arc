import logging

from gridmonitor.lib.base import *
from user import UserController 

log = logging.getLogger(__name__)

class UserStatisticsController(UserController):
    
    def index(self):
	
	c.title = "Monitoring System: User Statistics"
	c.menu_active = "My Statistics"
	c.heading = "My Statistics"
        
	return render('/derived/user/statistics/index.html')
 
	 
