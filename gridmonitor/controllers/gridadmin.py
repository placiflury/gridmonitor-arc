import logging
from pylons import session
from pylons import config
from pylons import tmpl_context as c
from pylons import app_globals as g
from pylons.templating import render_mako as render

import gridmonitor.lib.helpers as h
from gridmonitor.lib.base import BaseController

from gridmonitor.model.acl import meta, handler
from sft.utils import helpers as helpers


from gridmonitor.controllers.user import UserController

log = logging.getLogger(__name__)

class GridadminController(BaseController):
    
    def __init__(self):

        BaseController.__init__(self)

        self.admin = None
        self.authorized = False

        self.__before__() # call base class for authentication info
        c.user_name = session['user_name']
        c.user_surname = session['user_surname']
        
        if session.has_key('user_unique_id'):
            user_unique_id = session['user_unique_id']
            db_session = meta.Session()
            admins_pool = handler.AdminsPool(db_session)
        
            sites = admins_pool.list_admin_sites(user_unique_id)
            if sites:  # XXX we may want to extend this in the future
                self.authorized = True 
            
            
        nagios_server = config['nagios']
        if nagios_server == 'localhost':
            nagios_server_url = '/nagios'
        else:
            nagios_server_url = 'http://' + nagios_server + '/nagios'
        

        # build up menu (dynamic part)
        c.cluster_menu = list()
        vo_menu = list()
        c.no_queue_clusters = list()    

        clusters = g.get_clusters()
        
        for cluster_hostname, cluster_obj in clusters.items():
            cluster_queues = list()
            vo_cluster_queues = list()
            cluster_display_name = cluster_obj.get_alias() 
           
            log.debug("Added cluster '%s'(%s) to menu list" % \
                (cluster_display_name,cluster_hostname))
            cluster_path = '/gridadmin/clusters/show/' + cluster_hostname
            vo_path = '/gridadmin/vos/show/' + cluster_hostname
            
            queues_names = g.get_cluster_queues_names(cluster_hostname)
            if not queues_names:
                log.debug("Cluster has no queue") 
                cluster_queues = [(UserController.NO_QUEUE_FOUND, cluster_path)]
                vo_cluster_queues = [(UserController.NO_QUEUE_FOUND, cluster_path)]
                c.no_queue_clusters.append((cluster_display_name, cluster_hostname))
            else:    
                for name  in queues_names:
                    log.debug("Got queue '%s'" % name) 
                    cluster_queues.append((name, cluster_path + '/' + h.str_cannonize(name)))
                    vo_cluster_queues.append((name, vo_path + '/' + h.str_cannonize(name)))
            c.cluster_menu.append((cluster_display_name, cluster_path, cluster_queues))
            vo_menu.append((cluster_display_name, vo_path))


        log.debug("finished building up cluster menu...\n %r" % c.cluster_menu)
 

        # static menu information
        overview = [('Nagios Plugins', '/gridadmin/overview/nagios')]
       
        infosys_intervals = [('last 24 hours', '/gridadmin/infosys/show/h24'),
                    ('last week', '/gridadmin/infosys/show/w1'),
                    ('last year', '/gridadmin/infosys/show/y1')]
        
        statistics_menu = [('VO Usage', '/gridadmin/statistics/vo'),
            ('Clusters Usage ', '/gridadmin/statistics/cluster'),
            ('Cluster-VO Usage ', '/gridadmin/statistics/cluster_vos'),
            ('RRD Plots', '/gridadmin/statistics/rrd')]
        
        sfts = list()
        for sft_name in  helpers.get_all_sft_names():
            show_path = '/gridadmin/sfts/show/' + sft_name
            details = '/gridadmin/sfts/show_details/' + sft_name
            sfts.append((sft_name, show_path, [('details', details)]))

        c.top_nav = session['top_nav_bar']
        c.menu = [('Overview', '/gridadmin/overview', overview),
                ('Clusters','/gridadmin/clusters', c.cluster_menu),
                ('GRIS/GIIS', '/gridadmin/infosys', infosys_intervals)]
        
        if self.authorized:
            c.menu.append(('Grid Statistics', '/gridadmin/statistics', statistics_menu))
        c.menu.append(('SFTs', '/gridadmin/sfts', sfts))
        c.menu.append(('SFTs User', '/gridadmin/sfts/user_mgnt'))
        c.menu.append(('Nagios', nagios_server_url))

        c.top_nav_active = "VO/Grid Admin"

    def index(self):
        c.title = "Monitoring System: VO/Grid Admin View"
        c.menu_active = "Overview"
        return render('/base/gridadmin.html')
