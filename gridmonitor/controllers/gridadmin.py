from sft.db import sft_meta
from sft.db import sft_schema

from gridmonitor.lib.base import *
from gridmonitor.model.acl import *
from gridmonitor.controllers.user import UserController

log = logging.getLogger(__name__)

class GridadminController(BaseController):
    
    def __init__(self):
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
           
            log.debug("Added cluster '%s'(%s) to menu list" % (cluster_display_name,cluster_hostname))
            cluster_path = '/gridadmin/clusters/show/' + cluster_hostname
            vo_path = '/gridadmin/vos/show/' + cluster_hostname
            
            queues_names = g.get_cluster_queues_names(cluster_hostname)
            if not queues_names:
                log.debug("Cluster has no queue") 
                cluster_queues = [(UserController.NO_QUEUE_FOUND,cluster_path)]
                vo_cluster_queues = [(UserController.NO_QUEUE_FOUND,cluster_path)]
                c.no_queue_clusters.append((cluster_display_name,cluster_hostname))
            else:    
                for name  in queues_names:
                    log.debug("Got queue '%s'" % name) 
                    cluster_queues.append((name, cluster_path + '/' + h.str_cannonize(name)))
                    vo_cluster_queues.append((name, vo_path + '/' + h.str_cannonize(name)))
            c.cluster_menu.append((cluster_display_name,cluster_path, cluster_queues))
            vo_menu.append((cluster_display_name, vo_path))


        log.debug("finished building up cluster menu...\n %r" % c.cluster_menu)
 

        # static menu information
        overview = [('Reports','/gridadmin/overview/reports')]
       
        infosys_intervals = [('last 24 hours', '/gridadmin/infosys/show/h24'),
                    ('last week', '/gridadmin/infosys/show/w1'),
                    ('last year', '/gridadmin/infosys/show/y1')]
        
        statistics_menu =[('RRD Plots', '/gridadmin/statistics/rrd'),
            ('Usage Tables', '/gridadmin/statistics/sgas')]
        
        sfts = list()
        for sft in  sft_meta.Session.query(sft_schema.SFTTest).all():
            sft_name = sft.name
            show_path = '/gridadmin/sfts/show/' + sft_name
            details = '/gridadmin/sfts/show_details/' + sft_name
            sfts.append((sft_name, show_path, [('details',details)]))

        c.top_nav= session['top_nav_bar']
        c.menu = [('Overview', '/gridadmin/overview', overview),
                ('Clusters','/gridadmin/clusters', c.cluster_menu),
                ('GRIS/GIIS', '/gridadmin/infosys', infosys_intervals)]
        
        if self.authorized:
                c.menu.append(('Grid Statistics', '/gridadmin/statistics', statistics_menu))
        c.menu.append(('SFTs', '/gridadmin/sfts', sfts))
        c.menu.append(('SFTs User', '/gridadmin/sfts/user_mgnt'))
        c.menu.append(('Nagios', nagios_server_url))

        c.top_nav_active="VO/Grid Admin"

    def index(self):
        c.title = "Monitoring System: VO/Grid Admin View"
        c.menu_active = "Overview"
        return render('/base/gridadmin.html')
