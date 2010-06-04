import logging
from pylons import config
from gridmonitor.lib.base import *
from gridmonitor.model.voms import VOMSConnector
from gridmonitor.model.errors.voms import *
from user import UserController 

log = logging.getLogger(__name__)

class UserLinksController(UserController):
    
    def __init__(self):
        UserController()

    def index(self):

        c.title = "Link Collection"
        c.menu_active = "Links"
        c.heading = "Link Collection"
        return render('/derived/user/links.html')
 
	 
