import logging

from gridmonitor.lib.base import *
from gridmonitor.lib.slcs import SLCS

log = logging.getLogger(__name__)

class UserController(BaseController):
    
    NO_QUEUE_FOUND = 'NO_QUEUE'     # Tag to denote that no queue name was found 


    def __init__(self):
        
        # build up menu (dynamic part)
        c.cluster_menu = list()
        c.no_queue_clusters = list()    

        clusters = g.get_clusters()
        
        for cluster_hostname, cluster_obj in clusters.items():
            cluster_queues = list()
            cluster_display_name = cluster_obj.get_alias() 
           
            log.debug("Added cluster '%s'(%s) to menu list" % (cluster_display_name,cluster_hostname))

            cluster_path = '/user/clusters/show/' + cluster_hostname
            queues_names = g.get_cluster_queues_names(cluster_hostname)
            if not queues_names:
                log.debug("Cluster has no queue") 
                cluster_queues = [(UserController.NO_QUEUE_FOUND,cluster_path)]
                c.no_queue_clusters.append((cluster_display_name,cluster_hostname))
            else:    
                for name  in queues_names:
                    log.debug("Got queue '%s'" % name) 
                    cluster_queues.append((name, cluster_path + '/' + h.str_cannonize(name)))
            c.cluster_menu.append((cluster_display_name,cluster_path, cluster_queues))
        log.debug("finished building up cluster menu...\n %r" % c.cluster_menu)
 
       # build up menu (static part)
        job_states = ('all', 'ACCEPTED','PREPARED', 'INLRMS','FINISHED',
            'FAILED','KILLED','DELETED','FETCHED','orphaned') # FETCHED is a meta-state
        jobs = list()
        for state in job_states:
          jobs.append((state,'/user/jobs/show/%s' % state))		
        
        overview = [('Core Services','/user/overview/core'),
            ('Reports','/user/overview/reports')]

        c.top_nav= [('User','/user'),
            ('Site Admin', '/siteadmin'),
            ('VO/Grid Admin', '/gridadmin'),
            ('Help','/help')]
       
        # XXX nagios and support links should be read from config file and not be hardcoded.
        ## besides, if none exists, they should not even be listed in the menu 
        c.menu = [('Overview', '/user/overview/', overview),
                ('VOs','/user/vos'),
                ('Clusters', '/user/clusters', c.cluster_menu),
                ('My Jobs', '/user/jobs', jobs), 
                ('My Statistics', '/user/statistics'),
                ('Got a Problem?','/user/tickets'), 
                ('Links','/user/links')]

        c.top_nav_active="User"
        
        # the __before__ method only gets called after instatiation of class
        # we need to call it immediately
        self.__before__() # base class
        c.user_name = session['user_name']
        c.user_surname = session['user_surname']

    def index(self):
        c.title = "Monitoring System: User View"
        c.menu_active = "Overview"
        # XXX -crumbs to be implemented
        c.crumbs=["User"]	
        

        return render('/base/user.html')
