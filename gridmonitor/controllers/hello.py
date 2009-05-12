import logging

from gridmonitor.lib.base import *

log = logging.getLogger(__name__)

class HelloController(BaseController):

    def index(self):
        # Return a rendered template
        #   return render('/some/template.mako')
        # or, Return a response
        log.debug("....XXXXX HI THEREE!!!")
        return 'Hello World'
