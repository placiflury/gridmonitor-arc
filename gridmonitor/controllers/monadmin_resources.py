import logging
from gridmonitor.lib.base import *
from monadmin import MonadminController

log = logging.getLogger(__name__)

class MonadminResourcesController(MonadminController):    
    
    def index(self):
        
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "Manage Resources"
        c.heading = "Listing Administrators and Resources"  # default
        # XXX fill in logic

        return render('/derived/monadmin/resources/index.html')
        

    def admins(self):
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "Manage Resources"
        c.heading = "Manage Administrators of Grid Sites and Grid Services"
        
        # XXX fill in logic

        return render('/derived/monadmin/resources/admin.html')
    
    def site_services(self):
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "Manage Resources"
        c.heading = "Manage Grid Sites and Services"


        # XXX fill in logic

        return render('/derived/monadmin/resources/site_services.html')
        

