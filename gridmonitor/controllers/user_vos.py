import logging

from pylons import tmpl_context as c
from pylons.templating import render_mako as render

from gridmonitor.model.voms import VOMSConnector
from gridmonitor.model.errors.voms import VOMSException

from user import UserController

log = logging.getLogger(__name__)

class UserVosController(UserController):
    
    def __init__(self):
        UserController.__init__(self)
        try:
            self.voms = VOMSConnector()
        except VOMSException, e:
            log.warn("Failing creating VOMSConnector with %r" % e)
            self.voms = None

    def index(self):

        c.title = "Monitoring System: User View"
        c.menu_active = "VOs"
        c.heading = "Virtual Organizations Membership"
        c.user_slcs_dn = self.user_slcs_dn
        c.user_slcs_ca = self.user_slcs_ca
        c.user_client_dn = self.user_client_dn
        c.user_client_ca = self.user_client_ca
        
        if not self.voms:
            return render('/derived/user/error/voms_error.html')

        c.vo_list = self.voms.get_vos()    
        c.voms_connector = self.voms
        return render('/derived/user/vos/index.html')
 

