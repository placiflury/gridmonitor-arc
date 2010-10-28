import logging
from gridmonitor.lib.base import *
from monadmin import MonadminController

log = logging.getLogger(__name__)

class MonadminAclController(MonadminController):    
    
    def index(self):
        
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "Manage ACL"
        c.heading = "Listing current ACLs"
        # XXX fill in logic
        
        return render('/derived/monadmin/acl/index.html')
    

    def admin2site(self):
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "Manage ACL"
        c.heading = "Add  Administrator to Site/Service"


        # XXX fill in logic

        return render('/derived/monadmin/acl/admin2site.html')
    
    def site2admin(self):
        c.title = "Monitoring System: Monitor Admin View"
        c.menu_active = "Manage ACL"
        c.heading = "Add  Site/Service to Administrator"
        
        # XXX fill in logic

        return render('/derived/monadmin/acl/site2admin.html')
        

