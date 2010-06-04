import logging

from gridmonitor.lib.base import *
from user import UserController

log = logging.getLogger(__name__)

class UserTicketsController(UserController):
    
    def index(self):
        c.title = "Monitoring System: User View"
        c.menu_active = "Got a Problem?"
        c.heading = "Got a Problem with the Grid or any of its Applications?"
        
        return render('/derived/user/tickets/index.html')


