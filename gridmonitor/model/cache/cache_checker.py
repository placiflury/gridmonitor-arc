from __future__ import with_statement # enables with statement for python 2.5
import os, os.path
import logging
from threading import Thread, Lock, activeCount
import time 

__author__="Placi Flury placi.flury@switch.ch"
__date__="16.11.2009"
__version__="0.2"

# last modification (16.11.2009) added optional name to observer registration 

class CacheModifyChecker(Thread):

    observers = []
    observer_names = []
    lock = Lock()

    def __init__(self,cache_file,check_interval=60):
        """ cache_file file to check on changes. Checks
            are done every check_interval seconds (default=60).
        """
        Thread.__init__(self)
        self.cache = cache_file
        self.log = logging.getLogger(__name__)
        if type(check_interval == int) or type(check_interval) == float:
            self.log.info("Checking interval set to %r secs" % check_interval) 
            self.check_interval =float(check_interval)
        else:
            self.log.error("Invalid checking interval %r. Setting it to 60 secs instead." % check_interval)
            self.check_interval=float(20)
        self.last_status = None

    def check(self):
        status = None
        if os.path.exists(self.cache) and os.path.isfile(self.cache):
            status = os.stat(self.cache)[-1]  # keep last change's epoch time          
            self.log.debug("status: %r", status)

        if status != self.last_status:
            self.log.info("File '%s' changed." % self.cache)
            self.last_status = status
            self.notify()
    
    def register_observer(self,observer,name=None):
        with CacheModifyChecker.lock:
            if name:
                if name in CacheModifyChecker.observer_names:
                    self.log.info("%s is already registered" % observer)
                else:
                    CacheModifyChecker.observer_names.append(name)
                    self.log.info("Registering %s" % observer)
                    CacheModifyChecker.observers.append(observer)
            elif observer not in CacheModifyChecker.observers:
                self.log.info("Registering %s" % observer)
                CacheModifyChecker.observers.append(observer)

    def unregister_observer(self,observer):
        if observer in CacheModifyChecker.observers:
            with CacheModifyChecker.lock:
                self.log.info("Unregistering %s" % observer)
                CacheModifyChecker.observers.remove(observer)
                CacheModifyChecker.obeserver_names.remove(observer.name)

    def notify(self):
        for observer in CacheModifyChecker.observers:
            with CacheModifyChecker.lock:
                self.log.debug("notifying %s" % observer)
                observer.notify()
    
    def run(self):
        while 1:
            self.check()
            self.log.debug("taking a nap...")
            time.sleep(self.check_interval)
            if not CacheModifyChecker.observers:
                self.log.info("Stopping cache checker...")
                break
