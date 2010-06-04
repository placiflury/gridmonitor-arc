import logging

from gridmonitor.lib.base import *
from siteadmin import SiteadminController 

log = logging.getLogger(__name__)

class SiteadminVosController(SiteadminController):
    
    def index(self):
	
	c.title = "Monitoring System: Site Admin VOs"
	c.menu_active = "Site Statistics"
	c.heading = "Site Statistics"
        
	return render('/derived/siteadmin/vos/index.html')
 
	 
