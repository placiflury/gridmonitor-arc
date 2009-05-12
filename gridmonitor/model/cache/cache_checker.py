import os, os.path
import logging
from threading import Thread
import time 

class CacheModifyChecker(Thread):

    _observers = []

    def __init__(self,cache_file,check_interval=20):
        """ cache_file file to check on changes. Checks
            are done every check_interval seconds (default=20).
         """
        Thread.__init__(self)
        self.cache = cache_file
        self.log = logging.getLogger(__name__)
        if type(check_interval == int) or type(check_interval) == float:
            self.log.info("Checking interval set to %r secs" % check_interval) 
            self.check_interval =float(check_interval)
        else:
            self.log.error("Inalid checking interval %r. Settint it to 20 secs instead." % check_interval)
            self.check_interval=float(20)
        self.last_status = None

    def check(self):
        status = None
        if os.path.exists(self.cache) and os.path.isfile(self.cache):
            status = os.stat(self.cache)[-1]  # keep last change's epoch time          
            self.log.debug("status: %r", status)

        if status != self.last_status:
            self.log.debug("Cache file status changed.")
            self.last_status = status
            self.notify()
    
    def register_observer(self,observer):
        if observer not in self._observers:
            self.log.info("Registring %s" % observer)
            self._observers.append(observer)
 
    def unregister_observer(self,observer):
        if observer in self._observers:
            self.log.info("Unregistring %s" % observer)
            self._observers.remove(observer)

    def notify(self):
        for observer in self._observers:
            observer.notify()

    def run(self):
        while 1:
            self.check()
            self.log.debug("taking a nap...")
            time.sleep(self.check_interval)
            if not self._observers:
                break
        self.log.info("Stopping cache checke...")
