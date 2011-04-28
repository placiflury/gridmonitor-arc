import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from gridmonitor.lib.base import BaseController, render

log = logging.getLogger(__name__)

class PtestController(BaseController):
    
    def __init__(self):
        BaseController.__init__(self) 
       
        c.heading="fiif" 
        c.menu = [('Overview', '/help')]
        c.top_nav= session['top_nav_bar']
        c.top_nav_active="Help"

    def index(self):
        # Return a rendered template
        #return render('/ptest.mako')
        # or, return a response
        #return 'Hello World'
        
        c.title = "Monitoring System: User View"
        c.menu_active = "Overview"
        
        c.crumbs = ["User"]	# not implemented...
        return render('/derived/help/index.html')
