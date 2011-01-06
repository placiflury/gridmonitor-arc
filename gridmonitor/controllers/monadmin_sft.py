import logging
from gridmonitor.lib.base import *
from monadmin import MonadminController


log = logging.getLogger(__name__)
class MonadminSftController(MonadminController):    
    def index(self):
        
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "Manage SFT"
        c.heading = "Listing current SFTs"
        # XXX fill in logic
        
        return render('/derived/monadmin/sft/index.html')
    
    def list(self):
        
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "View SFTs (dummy)"
        c.heading = "Listing current SFTs"
        # XXX fill in logic
        
        return render('/derived/monadmin/sft/index.html')
    
    def edit(self):
        
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "Edit SFTs (dummy)"
        c.heading = "Editing current SFTs"
        # XXX fill in logic
        
        return render('/derived/monadmin/sft/index.html')

