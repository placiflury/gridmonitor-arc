import logging

from gridmonitor.lib.base import *

log = logging.getLogger(__name__)

class SiteAdminController(BaseController):

    def __init__(self):
	# XXX read cluster-list from configuration files

	# static menu information
	test_jobs = [('test_suit1','/siteadmin/testjobs/test/suit1')]
	
	overview = [('Core Services','/siteadmin/overview/core'),
		('Reports','/siteadmin/overview/reports')]

    	c.top_nav= [('User','/user'),
		('Site Admin', '/siteadmin'),
		('VO/Grid Admin', '/voadmin'),
		('Help','/help')]
	
	c.menu = [('Overview', '/siteadmin/overview', overview),
       		('VOs','/siteadmin/vos'),
       		('Test Jobs', '/siteadmin/testjobs', test_jobs), 
       		('Site Statistics', '/siteadmin/statistics'),
		('Nagios','https://venus.switch.ch/nagios')]

    	c.top_nav_active="Site Admin"
    
   

    def index(self):
	
	c.title = "Monitoring System: Site Admin View"
	c.menu_active = "Overview"
        
	return render('/base/siteadmin.html')
  
