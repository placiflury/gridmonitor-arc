"""
Implementation of the cache api. Is used to access the cache in read
only mode. 
"""
__author__="Placi Flury placi.flury@switch.ch"
__date__="22.04.2009"
__version__="0.1"

import logging, os.path
import shelve
from cache.api.cache import Cache
from cache.errors.cache import * 


class CacheReader(Cache):

    def __init__(self,dbfile):
        self.log = logging.getLogger(__name__)
        self.dbfile = dbfile

    def get_handle(self):
        if os.path.exists(self.dbfile) and os.path.isfile(self.dbfile):
            try:
                dbase = shelve.open(self.dbfile, 'r') # read only
                self.log.info("Accessing cache/shelve '%s'" % self.dbfile)
            except Exception, e:
                self.log.error("Access of '%s' cache failed with %r" % (self.dbfile, e))
                raise ACCESS_ERROR("Access Error", "Could not access cache at '%s'." % self.dbfile)
            return dbase
        self.log.warn("Cache at '%s' does not exist" % (self.dbfile))
        raise ACCESS_ERROR("Access Error", "Cache at '%s' does not exist" % ( self.dbfile))

    def close_handle(self,handle):
        try:
            handle.close()
        except:
            pass

if __name__ == "__main__":
    """
    from api.job_api import *
    from api.queue_api import *
    from api.cluster_api import *
    """

    import os,sys
    sys.path.append("/home/flury/ch.smscg.infocache")
    from api.queue_api import * 
    from api.job_api import * 
    from api.cluster_api import * 
    from api.stats_api import * 

    def _print(d):
        if type(d) == str:
            print d
        elif type(d) == dict:
            for k in d.keys():
                print k, ' - ', _print(d[k])
        elif type(d) == list:
            for item in d:
                _print(item)
        elif isinstance(d,JobApi):
            names = d.get_attribute_names()
            for name in names:
                print '\t', name, d.get_attribute_values(name)
        elif isinstance(d,QueueApi):
            names = d.get_attribute_names()
            for name in names:
                print '\t', name, d.get_attribute_values(name)
        elif isinstance(d,ClusterApi):
            names = d.get_attribute_names()
            for name in names:
                print '\t', name, d.get_attribute_values(name)
        elif isinstance(d,StatsApi):
            names = d.get_attribute_names()
            for name in names:
                print '\t', name, d.get_attribute(name)
        else:

            print "type %s not handled" % (type(d))

    db_read = CacheReader("/home/flury/testcache")
    hd = db_read.get_handle()
    queues = hd['cluster_queues']
    for k in hd.keys():
        print "XXX" * 10, '--', k, '--','XXX' * 10
        _print(hd[k])
    
    db_read.close_handle(hd)


