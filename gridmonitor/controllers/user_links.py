import logging

from pylons import tmpl_context as c
from pylons.templating import render_mako as render

from user import UserController

log = logging.getLogger(__name__)

class UserLinksController(UserController):
    
    def __init__(self):
        UserController.__init__(self)

    def index(self):

        c.title = "Link Collection"
        c.menu_active = "Links"
        c.heading = "Link Collection"
        return render('/derived/user/links.html')
 
	 
