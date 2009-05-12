import logging
from pylons import config
from gridmonitor.lib.base import *
from gridmonitor.model.voms import VOMSConnector
from gridmonitor.model.errors.voms import *
from user import UserController 

log = logging.getLogger(__name__)

class UserVosController(UserController):
    
    def __init__(self):
        UserController()
        try:
            self.voms = VOMSConnector()
        except VOMSException, e:
            self.voms = None

    def index(self):

        c.title = "Monitoring System: User View"
        c.menu_active = "VOs"
        c.heading = "Virtual Organizations Membership"
        
        if not self.voms:
            return render('/derived/user/error/voms_error.html')
        c.vo_list = self.voms.get_vos()    
        c.voms_connector = self.voms
        return render('/derived/user/vos/index.html')
 
	 
