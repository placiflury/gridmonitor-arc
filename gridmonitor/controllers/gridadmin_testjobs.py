import logging

from gridmonitor.lib.base import *
from gridadmin import GridadminController

log = logging.getLogger(__name__)

class GridadminTestjobsController(GridadminController):


    def index(self):
        c.title = "Monitoring System: VO/Grid Admin Test Jobs"
        c.menu_active = "Test Jobs"
        c.heading = "Test Jobs"
        return render ('/derived/gridadmin/testjobs/form.html')

    def form(self):
        self.index()
    
    def submit(self):
        try:
            c.tmp = request.params.getall('testsuit1')
            
        except:
            c.tmp = 'no test jobs selected'
        return render('/derived/gridadmin/testjobs/test.html')


    def test(self, suit): 
        c.title = "Test job suit %s" % suit
        c.menu_active = suit
        c.heading = "Test Suit to execute"
        
        return render('/derived/gridadmin/testjobs/index.html')


