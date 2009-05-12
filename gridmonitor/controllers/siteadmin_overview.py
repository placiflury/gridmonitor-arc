import logging

from gridmonitor.lib.base import *
from siteadmin import SiteAdminController 

log = logging.getLogger(__name__)

class SiteadminOverviewController(SiteAdminController):
    
    def index(self):
	
	c.title = "Monitoring System: Site Admin View"
	c.menu_active = "Overview"
	c.heading = "Current Grid Situation"
	#c.body="<p> Summary overview on SMSCG Grid. Customized for a user.</p>"
        
	return render('/derived/siteadmin/overview/index.html')
 
    def core(self):
	c.title = "Monitoring System: Site Admin View"
	c.menu_active="Core Services"
	c.heading = "Core Services Status"
	#c.body="<p> Currently VASH behaves suspiciously.</p>"
	return render('/derived/siteadmin/overview/core.html')
    
    def reports(self):
	c.title = "Monitoring System: Site Admin View"
	c.menu_active="Reports"
	c.heading = "Reports"
	#c.body="<p> generated report about last occurrences on Grid </p>"
	return render('/derived/siteadmin/overview/report.html')
	 
