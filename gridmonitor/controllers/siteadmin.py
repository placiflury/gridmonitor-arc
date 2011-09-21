import logging
from pylons import session
from pylons import config
from pylons import tmpl_context as c
from pylons import app_globals as g
from pylons.templating import render_mako as render

import gridmonitor.lib.helpers as h
from gridmonitor.lib.base import BaseController
from gridmonitor.model.acl import meta
from gridmonitor.model.acl import schema

log = logging.getLogger(__name__)

class SiteadminController(BaseController):
    
    NO_QUEUE_FOUND = 'NO_QUEUE'     # Tag to denote that no queue name was found 

    def __init__(self):
        BaseController.__init__(self)

        self.admin = None
        self.authorized = False
        self.clusters= list()  # hostname of clusters
        self.cores= list()  # hostname of non-cluster services (core services)
        
        nagios_server = config['nagios']
        if nagios_server == 'localhost':
            nagios_server_url = '/nagios'
        else:
            nagios_server_url = 'http://' + nagios_server + '/nagios'
        
        self.__before__() # call base class for authentication info
        c.user_name = session['user_name']
        c.user_surname = session['user_surname']

        if session.has_key('user_unique_id'):
            query = meta.Session.query(schema.Admin)
            user_unique_id = session['user_unique_id']
            admin = query.filter_by(shib_unique_id=user_unique_id).first()
            if admin:
                self.authorized = True  # doesn't mean there are any resources to view though
                for site in admin.sites:
                    for service in site.services:
                        if service.type == 'CE':
                            log.info("Access to CE service %s granted." % service.hostname)
                            self.clusters.append(service.hostname.encode('utf-8'))
                        else: 
                            log.info("Access to core service %s granted." % service.hostname)
                            self.cores.append(service.hostname.encode('utf-8'))
                for service in admin.services:
                    if service.type == 'CE':
                        if service.hostname not in self.clusters:
                            log.info("Access to CE service %s granted." % service.hostname)
                            self.clusters.append(service.hostname.encode('utf-8'))
                    else:
                        if service.hostname not in self.cores:
                            log.info("Access to core service %s granted." % service.hostname)
                            self.cores.append(service.hostname.encode('utf-8'))
        

        # static menu information
        test_jobs = [('test_suit1','/siteadmin/testjobs/test/suit1')]
        
        overview = [('My Services','/siteadmin/overview/nagios'),
            ('Reports','/siteadmin/overview/reports')]
        

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
                cluster_queues = [(SiteadminController.NO_QUEUE_FOUND, cluster_path)]
                c.no_queue_clusters.append((cluster_display_name, cluster_hostname))
            else:
                for name  in queues_names:
                    log.debug("Got queue '%s'" % name)
                    cluster_queues.append((name, cluster_path + '/' + h.str_cannonize(name)))
            c.cluster_menu.append((cluster_display_name, cluster_path, cluster_queues))
         
        c.top_nav= session['top_nav_bar']
        
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
        if self.authorized == False:
            return render('/derived/siteadmin/error/access_denied.html')        
        return render('/base/siteadmin.html')
  
