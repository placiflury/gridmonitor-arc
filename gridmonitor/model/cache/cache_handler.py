"""
Data Handler for accessing cached data from the Grid Information System.
Currently GRIS/GIIS cached data are supported. Extension to BDII should
be possible without any changes as long as the implementation sticks to 
the APIs. 
"""
__author__="Placi Flury placi.flury@switch.ch"
__date__="16.11.2009"
__version__="0.1"

# last change -- after being notified of new cache, read it so it gets in memory

from pylons import config
import logging
import sys
from gridmonitor.model.api.handler_api import HandlerApi
import gridmonitor.model.cache.errors.cache as CACHE
import gridmonitor.model.errors.handler as HANDLER
from gridmonitor.model.cache.cache_reader import *
from gridmonitor.model.cache.cache_checker import CacheModifyChecker


class Singleton(object):
    def __new__(cls,*args,**kwargs):
        if '_inst' not in vars(cls):
            cls._inst = super(Singleton,cls).__new__(cls,*args,**kwargs)
        return cls._inst    
    

class CacheHandler(Singleton,HandlerApi):
    """
    DataHandler for accessing cached data of the grid information system 
    (e.g GRIS/GIIS, BDII).
    """

    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.cache_file = config['infocache_file'].strip()
        cache_check_interval = config['infocache_check_interval'].strip()
        unpickle_path = config['infocache_unpickle_classes'].strip()
        sys.path.append(unpickle_path)
        self.name = "cachehandler"
        self.checker = CacheModifyChecker(self.cache_file,cache_check_interval)
        self.checker.register_observer(self,self.name) 
        self.checker.start()

        self.refresh() 

    def __del__(self):
        self.checker.unregister_observer(self)
        
    def notify(self):
        self.refresh()
    
    def refresh(self):

        self.cache = CacheReader(self.cache_file)
        try:
            self.db = self.cache.get_handle() # logging done at level below 
            # XXX read it in order to get it in memory
            for k in self.db.keys():
                self.db[k]   
        except CACHE.ACCESS_ERROR, e:
            raise HANDLER.ACCESS_ERROR(e.expression, e.message)
    
            
    def get_clusters(self,start_t=None, end_t = None):
        """ start_t and end_t are currently ignored."""
        if self.db.has_key('clusters'):
            return self.db['clusters']
        return dict()
  
    def get_cluster_queues(self, cluster_hostname, start_t=None, end_t = None):
        """ start_t and end_t are currently ignored."""
        if self.db.has_key('cluster_queues'):
            if self.db['cluster_queues'].has_key(cluster_hostname):
                return self.db['cluster_queues'][cluster_hostname]
        return dict()
    
    def get_cluster_jobs(self, cluster_hostname, start_t=None, end_t = None):
        """ start_t and end_t are currently ignored."""
        if self.db.has_key('cluster_jobs'):
            if self.db['cluster_jobs'].has_key(cluster_hostname):
                return self.db['cluster_jobs'][cluster_hostname]
        return list()

    def get_cluster_users(self, cluster_hostname, start_t=None, end_t = None):
        """ start_t and end_t are currently ignored."""
        if self.db.has_key('cluster_allowed_users'):
            if self.db['cluster_allowed_users'].has_key(cluster_hostname):
                return self.db['cluster_allowed_users'][cluster_hostname]
        return list()
    

    def get_user_clusters(self,user_dn,start_t=None, end_t = None):
        """ start_t and end_t are currently ignored."""
        if self.db.has_key('user_cluster_queues'):
            if self.db['user_cluster_queues'].has_key(user_dn):
                return self.db['user_cluster_queues'][user_dn].keys()
        return list()
        
        
    def get_user_queues(self,user_dn, cluster_hostname,start_t,end_t):
        """ start_t and end_t are currently ignored."""
        if self.db.has_key('user_cluster_queues'):
            if self.db['user_cluster_queues'].has_key(user_dn):
                if  self.db['user_cluster_queues'][user_dn].has_key(cluster_hostname):
                    return self.db['user_cluster_queues'][user_dn][cluster_hostname] 
 
    def get_user_jobs(self,user_dn, status=None, start_t = None, end_t=None):
        """ start_t and end_t are currently ignored."""
        if self.db.has_key('user_jobs'):
            if self.db['user_jobs'].has_key(user_dn):
                self.log.debug("Found %d job(s) for user %s." % (len(self.db['user_jobs'][user_dn]), user_dn))
                if not status:
                    job_list = list()
                    for val_list in  self.db['user_jobs'][user_dn].values():
                        job_list += val_list
                    return job_list
                elif self.db['user_jobs'][user_dn].has_key(status):
                    return self.db['user_jobs'][user_dn][status]
        return list()


    def refresh_clusters(self):
        self.refresh()  # no selective refresh of cache available

    def refresh_queues(self,cluster_hostname):
        self.refresh() # no selective refresh of cache available

    def refresh_queues(self,cluster_hostname):
        self.refresh() # no selective refresh of cache available


    def refresh_queue(self,cluster_hostname, queue_name):
        self.refresh() # no selective refresh of cache available

    def get_grid_stats(self):
        if self.db.has_key('grid_stats'):
            return self.db['grid_stats']
        return None
 
    def get_cluster_stats(self,cluster_hostname):
        grid_stats = self.get_grid_stats()
        if grid_stats:
            cluster_stats = grid_stats.get_children()
            self.log.debug("Found %d cluster statisticss objects" % len(cluster_stats))
            for cluster_stat in cluster_stats:
                if cluster_stat.get_name() == cluster_hostname:
                    return cluster_stat
        return None

    def get_queue_stats(self,cluster_hostname,queue_name):
        cluster_stats = self.get_cluster_stats(cluster_hostname)
        if cluster_stats:
            queue_stats_list = cluster_stats.get_children()
            for queue_stat in queue_stats_list:
                if queue_stat.get_name() == queue_name:
                    return queue_stat
        return None

    def get_user_stats(self,user_dn):
        # XXX to do
        pass
        



