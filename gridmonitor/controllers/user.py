import logging
from pylons import session
from pylons import tmpl_context as c
from pylons import app_globals as g
from pylons.templating import render_mako as render

import gridmonitor.lib.helpers as h
from gridmonitor.lib.base import BaseController

log = logging.getLogger(__name__)

class UserController(BaseController):
    
    NO_QUEUE_FOUND = 'NO_QUEUE'     # Tag to denote that no queue name was found 

    def __init__(self):
        BaseController.__init__(self)
        
        # the __before__ method only gets called after instatiation of class
        # we need to call it explicitly
        self.__before__() # base class
        c.user_name = session['user_name']
        c.user_surname = session['user_surname']
        
        # build up menu (dynamic part)
        c.cluster_menu = list()
        c.no_queue_clusters = list()    

        clusters = g.get_clusters()
        
        for cluster_hostname, cluster_obj in clusters.items():
            cluster_queues = list()
            cluster_display_name = cluster_obj.get_alias() 
           
            log.debug("Added cluster '%s'(%s) to menu list" % \
                 (cluster_display_name,cluster_hostname))

            cluster_path = '/user/clusters/show/' + cluster_hostname
            queues_names = g.get_cluster_queues_names(cluster_hostname)
            if not queues_names:
                log.debug("Cluster has no queue") 
                cluster_queues = [(UserController.NO_QUEUE_FOUND, cluster_path)]
                c.no_queue_clusters.append((cluster_display_name, cluster_hostname))
            else:    
                for name in queues_names:
                    log.debug("Got queue '%s'" % name) 
                    cluster_queues.append((name, cluster_path + '/' + h.str_cannonize(name)))
            c.cluster_menu.append((cluster_display_name, cluster_path, cluster_queues))
        log.debug("finished building up cluster menu...\n %r" % c.cluster_menu)
 
       # build up menu (static part)
        job_states = ('all', 'ACCEPTED', 'PREPARED', 'INLRMS', 'FINISHED',
            'FAILED', 'KILLED', 'DELETED', 'FETCHED', 'orphaned') # FETCHED is a meta-state

        jobs = list()
        for state in job_states:
            jobs.append((state, '/user/jobs/show/%s' % state))		
        
        overview = [('Core Services', '/user/overview/core')]

        c.top_nav = session['top_nav_bar']

       
        c.menu = [('Overview', '/user/overview', overview),
                ('VOs','/user/vos'),
                ('Clusters', '/user/clusters', c.cluster_menu),
                ('My Jobs', '/user/jobs', jobs), 
                ('My Statistics', '/user/statistics'),
                ('Got a Problem?', '/user/tickets'), 
                ('Links', '/user/links')]

        c.top_nav_active = "User"
        

    def index(self):
        c.title = "Monitoring System: User View"
        c.menu_active = "Overview"
        
        c.crumbs = ["User"]	# not implemented...
        

        return render('/base/user.html')
