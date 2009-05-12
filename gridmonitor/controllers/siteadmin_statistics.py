import logging

from gridmonitor.lib.base import *
from siteadmin import SiteAdminController 

log = logging.getLogger(__name__)

class SiteadminStatisticsController(SiteAdminController):
    
    def index(self):
	
	c.title = "Monitoring System: Site Admin Statistics"
	c.menu_active = "Site Statistics"
	c.heading = "Site Statistics"
        
	return render('/derived/siteadmin/statistics/index.html')
 
	 
