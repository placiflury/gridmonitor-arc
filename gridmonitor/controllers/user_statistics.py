import logging
import time
import calendar

from pylons import tmpl_context as c
from pylons.templating import render_mako as render
from pylons import request

from user import UserController
from sgasaggregator.utils import helpers 

log = logging.getLogger(__name__)

class UserStatisticsController(UserController):
    

    def __init__(self):
        
        UserController.__init__(self)

        _secs_res = 86400
   
        c.form_error = None
        if not request.params.has_key('start_t_str'): # setting defaults
            _end_t = int(time.time())  # now
            _start_t = _end_t - 28 * 86400  # 4 weeks back (including endding day)
        else: 
            start_t_str = request.params['start_t_str'] 
            end_t_str = request.params['end_t_str'] 
            log.debug('From %s to  %s at %d resolution' % (start_t_str, end_t_str, _secs_res))
            try:
                _start_t = calendar.timegm(time.strptime(start_t_str,'%d.%m.%Y'))
                _end_t = calendar.timegm(time.strptime(end_t_str,'%d.%m.%Y'))
                if _end_t < _start_t:
                    t = _end_t
                    _end_t = _start_t
                    _start_t = t
            except:
                c.form_error = "Please enter dates in 'dd.mm.yyyy' format"
     
        start_t, end_t = helpers.get_sampling_interval(_start_t, _end_t, _secs_res) # incl. endding day
        
        c.resolution = 'day'
        c.end_t_str_max = time.strftime("%d.%m.%Y", time.gmtime())
        c.start_t_str = time.strftime("%d.%m.%Y", time.gmtime(start_t))        
        c.end_t_str = time.strftime("%d.%m.%Y", time.gmtime(end_t))  
        
    
    def index(self):
        c.title = "Monitoring System: VO/Grid User Statistics"
        c.menu_active = "My Statistics"
        c.heading = "My Usage Statistics"
        
        return render('/derived/user/statistics/index.html')
    

