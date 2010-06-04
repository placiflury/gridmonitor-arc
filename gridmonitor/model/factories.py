"""
Factories for instantiation of data model classes based
on configuration settings. 

"""
__author__="Placi Flury placi.flury@switch.ch"
__date__="28.01.2009"
__version__="0.1"

from pylons import config
import logging


log = logging.getLogger(__name__)

class DataHandlerFactory:
    """ Factory for instantiation of a DataHandler class object. 
        The DataHandler queries the Grid Information System
        for current status in the grid. Each DataHandler has
        to implement the DataModelInterface.  
        
    """

    def get_handler(self):

        handler_type = config['data_handler_type'].lower().strip() 
        
        if handler_type in ['infocache','cache','cache_handler']:
            log.info("going for Cache Handler")
            from gridmonitor.model.cache.cache_handler import CacheHandler
            return CacheHandler()  
        elif handler_type in ['giisdb','giis_hanlder']:
            log.info("going for GiisDB Handler")
            from gridmonitor.model.giisdb.giisdb_handler import GiisDbHandler
            return GiisDbHandler()
        else:
            # XXX throw exception
            # handler_type not known
            return None
