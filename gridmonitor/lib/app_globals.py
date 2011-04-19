"""The application's Globals object"""
import logging
import sys
import time

from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

from gridmonitor.model.factories import DataHandlerFactory
from gridmonitor.model.errors.handler import * 
from gridmonitor.model.errors.voms import * 

class Globals(object):
    """Globals acts as a container for objects available throughout the
    life of the application
    """
    
    NUM_TRIES = 5
    SLEEP_TIME = 5  # in secs

    def __init__(self, config):
        """One instance of Globals is created during application
        initialization and is available during requests via the 'g'
        variable:
        XXX: since multiple instances of apache (may) get spawned, each instance
        will create it's own Globals object. ;-(
        --> BEWARE: the time it takes for the __init__ is  critical for user perception on performance. 
        """
        self.log = logging.getLogger(__name__)
        self.cache = CacheManager(**parse_cache_config_options(config))

        self.data_handler = None
        for i in xrange(0, Globals.NUM_TRIES): 
            try:
                self.log.info("Starting GridMonitor by getting handler...")  
                self.data_handler = DataHandlerFactory().get_handler(config)
                self.log.debug("...got data handler")
                break
            except HandlerException, e:
                self.log.info("Handler might not exist yet. Let's try again...")
                time.sleep(Globals.SLEEP_TIME)
            except Exception, e:
                self.log.error("Handler exception: '%r'" % e)
                sys.exit(1)  # XXX display a website with more info about error instead?
        if not self.data_handler:
            self.log.error("Stop trying to get handler.")
            sys.exit(1)

    
    def __del__(self):
        del(self.data_handler)

    def get_data_handler(self):
        """ return data handler """
        return self.data_handler

    def get_clusters(self):
        return self.data_handler.get_clusters()
    
    def get_cluster(self, hostname):
        clusters = self.get_clusters()
        if clusters.has_key(hostname):
            return clusters[hostname]
        return None
    
    def get_cluster_queues(self,cluster_hostname):
        return self.data_handler.get_cluster_queues(cluster_hostname)
    
    def get_cluster_queues_names(self,cluster_hostname):
        queue_dict = self.data_handler.get_cluster_queues(cluster_hostname)
        return queue_dict.keys()

    def get_queue(self,cluster_hostname,queue_name):
        queues = self.get_cluster_queues(cluster_hostname)
        if queues.has_key(queue_name):
            return queues[queue_name]
        return None   

    def get_user_jobs(self,userDN, status=None):
        return self.data_handler.get_user_jobs(userDN,status)

    # STATISTICS
    def get_grid_stats(self,stats_variable):
        """ return value of statistical variable for the entire grid. If
            statistical variable does not exists or hasn't been set, it 
            will return 0.
        """
        grid_stats= self.data_handler.get_grid_stats()
        name = config[stats_variable].strip()
        val = grid_stats.get_attribute(name)
        self.log.debug("Grid statistics: '%s=%r'" % (name,val))
        if val == None:
            return 0
        return val
    
    def get_cluster_stats(self,cluster_hostname,stats_variable):
        """ return value of statistical variable for given cluster. If
            statistical variable does not exists or hasn't been set, it 
            will return 0.
        """
        cluster_stats= self.data_handler.get_cluster_stats(cluster_hostname)
        if not cluster_stats:  return 0
        name = config[stats_variable].strip()
        val = cluster_stats.get_attribute(name)
        self.log.debug("Cluster statistics: '%s=%r'" % (name,val))
        if val == None:
            return 0
        return val


    def get_queue_stats(self,cluster_hostname,queue_name,stats_variable):
        """ return value of statistical variable for given cluster-queue. If
            statistical variable does not exists or hasn't been set, it 
            will return 0.
        """
        queue_stats = self.data_handler.get_queue_stats(cluster_hostname,queue_name)
        if not queue_stats: return 0
        name = config[stats_variable].strip()
        val = queue_stats.get_attribute(name)
        self.log.debug("Queue statistics: '%s=%r'" % (name,val))
        if val == None:
            return 0
        return val 
    


