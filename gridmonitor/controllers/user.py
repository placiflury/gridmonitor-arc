import logging

from gridmonitor.lib.base import *
from gridmonitor.lib.slcs import SLCS

log = logging.getLogger(__name__)

class UserController(BaseController):
    
    NO_QUEUE_FOUND = 'NO_QUEUE'     # Tag to denote that no queue name was found 
    def __init__(self):

        # info about user
        c.user_name = request.environ[config['shib_given_name']]
        c.user_surname = request.environ[config['shib_surname']]
        home_org = request.environ[config['shib_home_org']]
        unique_id = request.environ[config['shib_unique_id']]

        if request.environ.has_key('SSL_CLIENT_S_DN'):
            user_client_dn = request.environ['SSL_CLIENT_S_DN'].strip()
            # if emailaddress= within DN -> fix it
            cand = user_client_dn.split("emailAddress=")
            if len(cand) >1:
                c.user_client_dn = cand[0] + "Email=" + cand[1]
            else:
                c.user_client_dn = user_client_dn
            
            c.user_client_ca = request.environ['SSL_CLIENT_I_DN'].strip()
        else:
            c.user_client_dn = None
            c.user_client_ca = None
       
        c.user_slcs_obj = SLCS(home_org,c.user_name,c.user_surname,unique_id)  
        log.debug("Browser certificate DN: %s." %(c.user_client_dn))
        log.debug("SHIB ID: name '%s', surname '%s', unique ID '%s'." %(c.user_name,c.user_surname,unique_id))
        # --end 

    
        # build up menu (dynamic part)
        c.cluster_menu = list()
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
            else:    
                for name  in queues_names:
                    log.debug("Got queue '%s'" % name) 
                    cluster_queues.append((name, cluster_path + '/' + h.str_cannonize(name)))
            c.cluster_menu.append((cluster_display_name,cluster_path, cluster_queues))
        log.debug("finished building up cluster menu...\n %r" % c.cluster_menu)
 
       # build up menu (static part)
        job_states = ('all', 'ACCEPTED','PREPARED', 'INLRMS','FINISHED','FAILED','KILLED','DELETED','orphans')
        jobs = list()
        for state in job_states:
          jobs.append((state,'/user/jobs/show/%s' % state))		
        
        overview = [('Core Services','/user/overview/core'),
            ('Reports','/user/overview/reports')]

        c.top_nav= [('User','/user'),
            ('Site Admin', '/siteadmin'),
            ('VO/Grid Admin', '/voadmin'),
            ('Help','/help')]
       
        # XXX nagios and support links should be read from config file and not be hardcoded.
        ## besides, if none exists, they should not even be listed in the menu 
        c.menu = [('Overview', '/user/overview/', overview),
                ('VOs','/user/vos'),
                ('Clusters', '/user/clusters', c.cluster_menu),
                ('My Jobs', '/user/jobs', jobs), 
                ('My Statistics', '/user/statistics'),
            ('Nagios','/nagios'),
            ('Submit a Ticket','http://rt.smscg.ch'), 
            ('Links','/user')]

        c.top_nav_active="User"
    

    def index(self):
	
	c.title = "Monitoring System: User View"
	c.menu_active = "Overview"
    # XXX -crumbs to be implemented
	c.crumbs=["User"]	
        
	return render('/base/user.html')
  
