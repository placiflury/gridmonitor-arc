"""
Implementation of the cache api. Is used to access the cache in read
only mode. 
"""
__author__="Placi Flury placi.flury@switch.ch"
__date__="22.04.2009"
__version__="0.1"

import logging, os.path
import shelve
from gridmonitor.model.cache.api.cache import Cache
from gridmonitor.model.cache.errors.cache import * 


class CacheReader(Cache):

    def __init__(self,dbfile):
        self.log = logging.getLogger(__name__)
        self.dbfile = dbfile

    def get_handle(self):
        if os.path.exists(self.dbfile) and os.path.isfile(self.dbfile):
            try:
                dbase = shelve.open(self.dbfile, 'r') # read only
                self.log.debug("Accessing cache/shelve '%s'" % self.dbfile)
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

