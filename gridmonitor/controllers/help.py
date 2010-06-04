import logging

from gridmonitor.lib.base import *

log = logging.getLogger(__name__)

class HelpController(BaseController):

    def __init__(self):
        
        c.menu = [('Overview', '/help')]
        c.top_nav= [('User','/user'),
            ('Site Admin', '/siteadmin'),
            ('VO/Grid Admin', '/gridadmin'),
            ('Help','/help')]
        c.top_nav_active="Help"
    
    def index(self):
        c.menu_active = "Overview"
        return render('/derived/help/index.html')
