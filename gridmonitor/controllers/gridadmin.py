import logging

from gridmonitor.lib.base import *
from gridmonitor.model.sft import sft_meta
from gridmonitor.model.sft import sft_schema
from gridmonitor.lib.slcs import SLCS

log = logging.getLogger(__name__)

class GridadminController(BaseController):
    
    def __init__(self):

        # authorization and mapping
        # info about user  XXX finish ACL implementation 
        unique_id = unicode(request.environ[config['shib_unique_id']], "utf-8")
        c.user_name = unicode(request.environ[config['shib_given_name']], 'utf-8')
        c.user_surname = unicode(request.environ[config['shib_surname']], 'utf-8')
        user_email = unicode(request.environ[config['shib_email']], "utf-8")
        user_home_org = unicode(request.environ[config['shib_home_org']], "utf-8")
        
        if request.environ.has_key('SSL_CLIENT_S_DN'):
            c.user_client_dn = unicode(request.environ['SSL_CLIENT_S_DN'].strip(),'ISO-8859-1')

        user_slcs_obj = SLCS(user_home_org,c.user_name,c.user_surname,unique_id)  
        c.user_slcs_dn = user_slcs_obj.get_dn()

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
            vo_menu.append((cluster_display_name, vo_path, vo_cluster_queues))
        log.debug("finished building up cluster menu...\n %r" % c.cluster_menu)
 

        # static menu information
        overview = [('Reports','/gridadmin/overview/reports')]
       
        infosys_intervals = [('last 6 hours', '/gridadmin/infosys/show/h6'),
                    ('last week', '/gridadmin/infosys/show/w1'),
                    ('last year', '/gridadmin/infosys/show/y1')]
        
        sfts = list()
        for sft in  sft_meta.Session.query(sft_schema.SFTTest).all():
            sft_name = sft.name
            show_path = '/gridadmin/sfts/show/' + sft_name
            details = '/gridadmin/sfts/show_details/' + sft_name
            sfts.append((sft_name, show_path, [('details',details)]))

        
        c.top_nav= [('User','/user'),
            ('Site Admin', '/siteadmin'),
            ('VO/Grid Admin', '/gridadmin'),
            ('Help','/help')]
         
        c.menu = [('Overview', '/gridadmin/overview', overview),
                ('Clusters','/gridadmin/clusters', c.cluster_menu),
                ('GRIS/GIIS', '/gridadmin/infosys', infosys_intervals),
                ('VO Usage', '/gridadmin/vos', vo_menu),
                ('Grid Statistics', '/gridadmin/statistics'),
                ('SFTs', '/gridadmin/sfts', sfts),
                ('SFTs User', '/gridadmin/sfts/user_mgnt'),
                ('Nagios', '/nagios')]

        c.top_nav_active="VO/Grid Admin"

    def index(self):
        c.title = "Monitoring System: VO/Grid Admin View"
        c.menu_active = "Overview"
        return render('/base/gridadmin.html')
