import logging
import time
import calendar


from pylons import tmpl_context as c
from pylons import request
from pylons.templating import render_mako as render

from siteadmin import SiteadminController
from sgasaggregator.utils import helpers

log = logging.getLogger(__name__)

class SiteadminStatisticsController(SiteadminController):


    def __init__(self):
        
        SiteadminController.__init__(self)

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
        c.title = "Monitoring System: Cluster and VO Usage Statistics"
        c.menu_active = "Site Statistics"
        c.heading = "Statistics of Clusters  %s %s has siteadmin (view) permissions." % (c.user_name, c.user_surname)
        
        if not self.authorized:
            return render('/derived/siteadmin/error/access_denied.html')

        c.cluster_names = self.clusters
        c.cluster_names.sort()
            
        return render('/derived/siteadmin/statistics/cluster_vo_stats.html')
    
    def cluster_vos(self):
        """ 
            display accounting data per cluster 
            XXX - not yet added to menue -> wait for further menus items
        """
        
        c.title = "Monitoring System: Cluster and VO Usage Statistics"
        c.menu_active = "Site Statistics"
        c.heading = "Statistics of Cluster VO Usage"
        
        if not self.authorized:
            return render('/derived/siteadmin/error/access_denied.html')

        c.cluster_names = self.clusters
        c.cluster_names.sort()
            
        return render('/derived/siteadmin/statistics/cluster_vo_stats.html')
 
