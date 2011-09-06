import logging
import json

from pylons import config
from pylons import app_globals as g

from gridmonitor.lib.base import BaseController
import gridmonitor.lib.helpers as h

from gridmonitor.lib.charts_table import DataTable
from gridmonitor.lib.nagios_utils import get_nagios_summary, get_hostnames_from_group_tag

log = logging.getLogger(__name__)

class GridController(BaseController):
    

    def get_nagios_cores_stats(self):
        """
        Returns status information about 
        the plugins of the nagios core services, which 
        were grouped by nagios by the the configuration
        tag 'nagios_core'.
        
        returns a json (dictionary) object
        """
        tag = config['nagios_core']
        core_hosts = get_hostnames_from_group_tag(tag)
        return json.dumps(get_nagios_summary(core_hosts, dates2utc = True))
    
    def get_nagios_ces_stats(self):
        """
        Returns status information about the nagiosplugins of the
        computing elements (CE) , which 
        were grouped by nagios by the the configuration
        tag 'nagios_ces'.
        
        returns a json (dictionary) object
        """
        tag = config['nagios_ces']
        core_hosts = get_hostnames_from_group_tag(tag)
        return json.dumps(get_nagios_summary(core_hosts, dates2utc = True))



    def get_grid_load(self):
        """ returns the current load statistics
            of entire grid as a json object.
        """
        obj = {}
        obj['grid_running'] =  g.get_grid_stats('stats_grid_running')
        obj['running'] = g.get_grid_stats('stats_running')
        obj['totaljobs'] = g.get_grid_stats('stats_totaljobs')
        obj['usedcpus'] = g.get_grid_stats('stats_usedcpus')
        obj['totalcpus'] = g.get_grid_stats('stats_totalcpus')
        
        obj['grid_queued'] = g.get_grid_stats('stats_grid_queued')
        obj['local_queued'] = g.get_grid_stats('stats_local_queued')
        obj['prelrms_queued'] = g.get_grid_stats('stats_prelrms_queued')

        # get number of active clusters
        cl_list = h.get_cluster_names('active')[0]
        if cl_list: 
            obj['num_clusters'] = len(cl_list)
        else:
            obj['num_clusters'] = 0

        return json.dumps(obj)


    def gc_cpu_load(self):
        """ Returns a json string that can be passed
            unmodified to the google charts API. 

        """

        key_order = ['gridrun', 'run','cpus']
        description = { 'gridrun': ('Grid Running', 'number'),
                    'run': ('Running','number'),
                    'cpus': ('Avail. Cores', 'number')}


        dt = DataTable(description, key_order)

        gridrun =  g.get_grid_stats('stats_grid_running')
        run = g.get_grid_stats('stats_running') 
        cpus = g.get_grid_stats('stats_cpus')

       
        dt.add_row( gridrun, abs(run - gridrun), abs(cpus - run))
        
        return dt.get_json()

    def gc_queue_load(self):
        """ Returns a json string with queue load 
            of specified cluster (by hostname), which
            can be passed to the google charts API.

        """
        key_order = ['gridqueued', 'localqueued','lrmsqueued']

        description = {'gridqueued' : ('Grid Queued', 'number'),
                        'localqueued' : ('Local Queued', 'number'),
                        'lrmsqueued' : ('Pre-LRMS Queued', 'number')}

        dt = DataTable(description, key_order)
        gridq = g.get_grid_stats('stats_grid_queued')
        locq = g.get_grid_stats('stats_local_queued')
        lrmsq = g.get_grid_stats('stats_prelrms_queued')

        dt.add_row(abs(gridq), abs(locq), abs(lrmsq))
        
        return dt.get_json()





