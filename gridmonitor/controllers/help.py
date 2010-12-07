import logging

from gridmonitor.lib.base import *

log = logging.getLogger(__name__)

class HelpController(BaseController):

    def __init__(self):
        
        c.menu = [('Overview', '/help')]
        c.top_nav= session['top_nav_bar']
        c.top_nav_active="Help"
    
    def index(self):
        c.menu_active = "Overview"
        return render('/derived/help/index.html')
