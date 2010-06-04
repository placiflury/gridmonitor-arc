import logging

from gridmonitor.lib.base import *
from siteadmin import SiteadminController 

log = logging.getLogger(__name__)

class SiteadminStatisticsController(SiteadminController):
    
    def index(self):
	
	c.title = "Monitoring System: Site Admin Statistics"
	c.menu_active = "Site Statistics"
	c.heading = "Site Statistics"
        
	return render('/derived/siteadmin/statistics/index.html')
 
	 
