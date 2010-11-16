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
        c.slsc_dn = None
        c.user_client_dn = None
        
        if not self.voms:
            return render('/derived/user/error/voms_error.html')
 
        if session.has_key('user_slcs_obj'):
            user_slcs_obj = session['user_slcs_obj']
            c.slcs_dn = user_slcs_obj.get_dn()
            c.slcs_ca = user_slcs_obj.get_ca()

        if session.has_key('user_client_dn'):
            browser_dn = session['user_client_dn']
            c.user_client_dn = browser_dn
            if session.has_key('user_client_ca'):
                browser_dn = session['user_client_ca']
                c.user_client_ca = browser_dn

        c.vo_list = self.voms.get_vos()    
        c.voms_connector = self.voms
        return render('/derived/user/vos/index.html')
 
	 
