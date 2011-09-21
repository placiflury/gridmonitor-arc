import logging
import json

from pylons import config
from pylons import request
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


    def get_nagios_stats(self):
        """
        Should allow to get nagios info for specifies 'hostlist[]', 
        which is passed by a POST request

        returns a json (dictionary) object
        """
        ddict = request.POST # doubleDict
        hlist = ddict.getall('hostlist[]') # XXX why did it got the '[]' suffix ???

        return json.dumps(get_nagios_summary(hlist, dates2utc = True))



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




    def get_min_max_clusters(self):
        """ returns a json string with info about the 
            cluster with the maximal and the cluster 
            with the minimal load on the grid.
        """

        max_load_cluster=dict(name = None, cname = None,  tot_running = 0,
                tot_cpus = 0, tot_queued = 0, relative_load = -1)
        min_load_cluster=dict(name = None, cname = None, tot_running = 0,
                tot_cpus = 0, tot_queued = 0, relative_load = -1)


        hosts, meta = h.get_cluster_names('active')
        
        for hostname in hosts:

            if meta[hostname]['alias']:
                display_name = meta[hostname]['alias']
            else:
                display_name = hostname

            cname = h.str_cannonize(display_name)

            cpus = g.get_cluster_stats(hostname,'stats_cpus')
            totaljobs = g.get_cluster_stats(hostname,'stats_totaljobs')
            usedcpus = g.get_cluster_stats(hostname,'stats_usedcpus')

            tot_queued = 0
            for qname in g.get_cluster_queues_names(hostname):
                gqd = g.get_queue_stats(hostname, qname, 'stats_grid_queued')
                lqd= g.get_queue_stats(hostname, qname, 'stats_local_queued')
                plrms = g.get_queue_stats(hostname, qname, 'stats_prelrms_queued')

                tot_queued = gqd + lqd + plrms

            # Finding max loaded cluster and min loaded cluster         
            # totaljobs ~ # jobs_running + # jobs_queued
            if cpus > 0:
                if totaljobs == 0: # little trick to favor large clusters over small if no jobs are around
                    tj = 0.5
                else:
                    tj = totaljobs
                tj += tot_queued
                relative_cluster_load = tj/float(cpus)
            else:
                continue
        
            if not max_load_cluster['name']:   # set both min=max load  (first cluster)
                max_load_cluster['name'] = display_name
                min_load_cluster['name'] = display_name
                max_load_cluster['cname'] = cname
                min_load_cluster['cname'] = cname
                min_load_cluster['tot_running'] = usedcpus  # instead of grid_running + running
                max_load_cluster['tot_running'] = usedcpus
                max_load_cluster['tot_cpus'] = cpus
                min_load_cluster['tot_cpus'] = cpus
                max_load_cluster['tot_queued'] = tot_queued
                min_load_cluster['tot_queued'] = tot_queued
                max_load_cluster['relative_load'] = relative_cluster_load
                min_load_cluster['relative_load'] = relative_cluster_load
            elif relative_cluster_load > max_load_cluster['relative_load']:
                max_load_cluster['name'] = display_name
                max_load_cluster['cname'] = cname
                max_load_cluster['tot_running'] = usedcpus
                max_load_cluster['tot_cpus'] = cpus
                max_load_cluster['tot_queued'] = tot_queued
                max_load_cluster['relative_load'] = relative_cluster_load
            elif (relative_cluster_load == max_load_cluster['relative_load'] ) and \
                    (cpus < max_load_cluster['tot_cpus']):
                max_load_cluster['name'] = display_name
                max_load_cluster['cname'] = cname
                max_load_cluster['tot_running'] = usedcpus
                max_load_cluster['tot_cpus'] = cpus
                max_load_cluster['tot_queued'] = tot_queued
                max_load_cluster['relative_load'] = relative_cluster_load

            if relative_cluster_load <  min_load_cluster['relative_load']:
                min_load_cluster['name'] = display_name
                min_load_cluster['cname'] = cname
                min_load_cluster['tot_running'] = usedcpus
                min_load_cluster['tot_cpus'] = cpus
                min_load_cluster['tot_queued'] = tot_queued
                min_load_cluster['relative_load'] = relative_cluster_load
            elif (relative_cluster_load == min_load_cluster['relative_load'] ) and \
                (cpus > min_load_cluster['tot_cpus']):
                min_load_cluster['name'] = display_name
                min_load_cluster['cname'] = cname
                min_load_cluster['tot_running'] = usedcpus
                min_load_cluster['tot_cpus'] = cpus
                min_load_cluster['tot_queued'] = tot_queued
                min_load_cluster['relative_load'] = relative_cluster_load

        min_max_cl = dict(min_load_cluster = min_load_cluster, max_load_cluster = max_load_cluster)
        
        return json.dumps(min_max_cl)
        




