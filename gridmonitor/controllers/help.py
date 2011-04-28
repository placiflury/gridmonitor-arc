import logging
from pylons import tmpl_context as c
from pylons.templating import render_mako as render
from pylons import session

from gridmonitor.lib.base import BaseController
log = logging.getLogger(__name__)

class HelpController(BaseController):

    def __init__(self):
        BaseController.__init__(self)        
        c.menu = [('Overview', '/help')]
        c.top_nav= session['top_nav_bar']
        c.top_nav_active="Help"
    
    def index(self):
        c.title = "GridMonitor Help"
        c.heading = "Help"
        c.menu_active = "Overview"
        return render('/derived/help/index.html')
