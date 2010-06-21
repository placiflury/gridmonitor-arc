import logging

from gridmonitor.lib.base import *
from gridmonitor.model.acl import meta
from gridmonitor.model.acl import schema 


log = logging.getLogger(__name__)

class SiteadminController(BaseController):
    
    NO_QUEUE_FOUND = 'NO_QUEUE'     # Tag to denote that no queue name was found 

    def __init__(self):
        self.admin = None
        self.access_denied = True
        self.clusters= list()  # list of hostname of clusters
        self.cores= list()  # list of hostname of non-cluster services (core services)

        # authorization and mapping
        # info about user
        unique_id = unicode(request.environ[config['shib_unique_id']], "utf-8")
        c.user_name = unicode(request.environ[config['shib_given_name']], 'utf-8')
        c.user_surname = unicode(request.environ[config['shib_surname']], 'utf-8')
        user_email = unicode(request.environ[config['shib_email']], "utf-8")
        user_home_org = unicode(request.environ[config['shib_home_org']], "utf-8")
        
        nagios_server = config['nagios']
        if nagios_server == 'localhost':
            nagios_server_url = '/nagios'
        else:
            nagios_server_url = 'http://' + nagios_server + '/nagios'

        query = meta.Session.query(schema.Admin)
        
        admin = query.filter_by(shib_unique_id=unique_id).first()
        if admin:
            self.access_denied = False
    
        if not self.access_denied: 
            for site in admin.sites:
                for service in site.services:
                    if service.type == 'cluster':
                        log.info("Access to service %s granted." % service.name)
                        self.clusters.append(service.hostname)
                    elif service.type == 'other': # XXX this might change
                        log.info("Access to service %s granted." % service.name)
                        self.cores.append(service.hostname)
            for service in admin.services:
                    if service.type == 'cluster':
                        if service.hostname not in self.clusters:
                            log.info("Access to service %s granted." % service.name)
                            self.clusters.append(service.hostname)
                    elif service.type == 'other': # XXX this might change
                        if service.hostname not in self.cores:
                            log.info("Access to service %s granted." % service.name)
                            self.cores.append(service.hostname)
                
        # static menu information
        test_jobs = [('test_suit1','/siteadmin/testjobs/test/suit1')]
        
        overview = [('My Services','/siteadmin/overview/core'),
            ('Reports','/siteadmin/overview/reports')]

        c.top_nav= [('User','/user'),
            ('Site Admin', '/siteadmin'),
            ('VO/Grid Admin', '/gridadmin'),
            ('Help','/help')]

        # dynamic menu information
        c.cluster_menu = list()
        c.no_queue_clusters = list()
        for cluster_hostname in self.clusters:
            cluster_obj = g.get_cluster(cluster_hostname)
            if not cluster_obj:
                continue
            cluster_queues = list()
            cluster_display_name = cluster_obj.get_alias()
            cluster_path = '/siteadmin/clusters/show/' + cluster_hostname
            queues_names = g.get_cluster_queues_names(cluster_hostname)
            if not queues_names:
                log.debug("Cluster has no queue")
                cluster_queues = [(SiteadminController.NO_QUEUE_FOUND,cluster_path)]
                c.no_queue_clusters.append((cluster_display_name,cluster_hostname))
            else:
                for name  in queues_names:
                    log.debug("Got queue '%s'" % name)
                    cluster_queues.append((name, cluster_path + '/' + h.str_cannonize(name)))
            c.cluster_menu.append((cluster_display_name,cluster_path, cluster_queues))
         
        c.menu = [('Overview', '/siteadmin/overview', overview),
                ('Clusters','/siteadmin/clusters', c.cluster_menu),
                ('Jobs','/siteadmin/jobs'),
                ('Users','/siteadmin/users'),
                ('Test Jobs', '/siteadmin/testjobs', test_jobs), 
                ('Site Statistics', '/siteadmin/statistics'),
                ('Nagios', nagios_server_url)]

        c.top_nav_active="Site Admin"
 
    def index(self):
        
        c.title = "Monitoring System: Site Admin View"
        c.menu_active = "Overview"
        if self.access_denied == True:
            return render('/derived/siteadmin/error/access_denied.html')        
        return render('/base/siteadmin.html')
  
