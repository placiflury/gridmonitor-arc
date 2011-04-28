import logging
from pylons import tmpl_context as c
from pylons.templating import render_mako as render

from siteadmin import SiteadminController 

log = logging.getLogger(__name__)

class SiteadminTestjobsController(SiteadminController):
    
    def index(self):
	
	c.title = "Monitoring System: Site Admin Test Jobs"
	c.menu_active = "Test Jobs"
	c.heading = "Test Jobs"
        
	return render('/derived/siteadmin/testjobs/index.html')

    def test(self, suit): 
	c.title = "Test job suit %s" % suit
	c.menu_active = suit
	c.heading = "Test Suit to execute"
	
	return render('/derived/siteadmin/testjobs/index.html')
	
	 
