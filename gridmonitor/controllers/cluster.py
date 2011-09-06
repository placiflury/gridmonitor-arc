import logging
import json

from datetime import datetime

from pylons import tmpl_context as c
from pylons import app_globals as g
from  gridmonitor.lib.nagios_utils import get_nagios_scheduleddowntime_items, get_nagios_service_statuses

import gridmonitor.lib.time_utils as tu

from gridmonitor.lib.base import BaseController, render
from gridmonitor.lib.charts_table import DataTable


log = logging.getLogger(__name__)

class ClusterController(BaseController):
    """ This controller doesn't serve a web page of
        the GridMonitor application. It does instead
        provide json query urls to populate data/plots
    """

    CLUSTER_META = ['alias','support','cache',
                'middlewares','cert_expiration',
                'operating_systems']
    

    CSS_STATUS_CLASS = { 0 : 'ok_status', 
                        1 : 'warn_status',
                        2 : 'error_status'}

    def get_clusters(self):
        """
            returns a json object, which is
            an array of cluster objects, each holding
            some meta-data about the clusters.
        """ 
        jclusters = {}
        
        clusters = g.get_clusters()

        for hostname, cl_obj in clusters.items():
            jclusters[hostname] = {}
            for key in ClusterController.CLUSTER_META:
                values = cl_obj.get_attribute_values(key)
                if values:
                    jclusters[hostname][key] = values[0]
        return json.dumps(jclusters)
        


    def get_cluster_meta_table(self, hostname, tag):
        """ compiles a html table (e.g. for the 'qtip'), 
            preceeded by a <h2> </h2>  with the metadata
            of the given cluster. 
            
            hostname -- name of the cluster (frontend)
            tag -- specifies which metadata to include. 
                   options are: 
                    'Nagios' - for nagios info,
                    'SFT '  - for Site functional tests info,
                    'Infosys' - for information system info.
        """

        jstatus = json.loads(self.get_cluster_meta(hostname))

        _html = '<h2> ' + tag + '</h2> \n' +  \
                '<table summary="Status Infobox">'  

 
        if tag == 'Nagios':
            if not jstatus.has_key('nagios'):
                _html += "<tr> <td colspan='2'> Cluster on (nagios) scheduled downtime </td> </tr>"
                _html += "<tr> <td> Starting:</td> <td> %s </td></tr>" % jstatus['start_t']
                _html += "<tr> <td> Ending:</td> <td> %s </td> </tr>" % jstatus['end_t']
            else:
                _nagios = jstatus['nagios']
                _keys = _nagios.keys()
                if not _keys:
                    _html += '<tr class="undef_status"> <td colspan=2> No Nagios Info available!</td></tr>' 
                else:
                    _keys.sort()
                    for k in _keys:
                        css_class = ClusterController.CSS_STATUS_CLASS[_nagios[k]['status']]
                        _html += '<tr class="%s"> <td> %s</td> <td> %s </td></tr>' % (css_class, k, _nagios[k]['output'])
        elif tag == 'SFT':
            pass
        elif tag == 'Infosys':
            if jstatus['status'] == 'Scheduled Downtime':
                _html += '<tr> <td colspan=2> Scheduled downtime! Infosys not checked.</td></tr>'
            else:
                _html += '<tr><td>Status</td> <td> %s </td> </tr>' % (jstatus['status']);
                _html += '<tr><td>Response time</td> <td> %s </td> </tr>' % (jstatus['response_time'])
                _html += '<tr><td>Processing time</td> <td> %s </td> </tr>' % (jstatus['processing_time'])
        elif tag == 'Downtime':
            _html += "<tr> <td colspan='2'> Cluster on (nagios) scheduled downtime </td> </tr>"
            _html += "<tr> <td> Starting:</td> <td> %s </td></tr>" % jstatus['start_t']
            _html += "<tr> <td> Ending:</td> <td> %s </td> </tr>" % jstatus['end_t']
        
        _html += '</table>'
        
        return _html 

    def get_cluster_meta(self, hostname):
        """ returns status of cluster as a json object"""

        jstatus = dict(hostname = hostname, 
                status = 'unknown')
        
        # nagios information 
        for it in get_nagios_scheduleddowntime_items():
            if  it.generic_object.name1 == hostname:
                start_t = it.scheduled_start_time
                end_t = it.scheduled_end_time
                if datetime.now() > start_t and datetime.now() < end_t:
                    jstatus['status'] = 'Downtime' # scheduled downtime
                    jstatus['start_t'] = tu.datetime2utcstring(start_t)
                    jstatus['end_t'] = tu.datetime2utcstring(end_t)
 
        if jstatus['status'] != 'Downtime': # get services statuses
            services = get_nagios_service_statuses(hostname, dates2utc = True)
            jstatus['nagios'] = services 
            

        # infosys information
        cluster = g.get_cluster(hostname)
        if cluster:
            jstatus['alias'] = cluster.get_alias()
            if jstatus['status'] != 'Downtime':
                metadata = cluster.get_metadata()
                jstatus['status'] = metadata.get_status()
                jstatus['processing_time'] = metadata.get_processing_time()
                jstatus['response_time'] = metadata.get_response_time()

        return json.dumps(jstatus)
         
    def get_cluster_load(self, hostname):  
        """ 
            returns the current load statistics 
            of cluster as a json object.
        """
        obj = {'cl': {}, 'q':{}}
        obj['cl']['cl_grid_running'] =  g.get_cluster_stats(hostname,'stats_grid_running')
        obj['cl']['cl_running'] = g.get_cluster_stats(hostname,'stats_running')
        obj['cl']['cl_totaljobs'] = g.get_cluster_stats(hostname,'stats_totaljobs')
        obj['cl']['cl_usedcpus'] = g.get_cluster_stats(hostname,'stats_usedcpus')
        cpus = g.get_cluster_stats(hostname,'stats_cpus')
        if cpus == 0: # if queue info did not contain num of cpus we take cluster info
            cpus = g.get_cluster_stats(hostname,'stats_totalcpus')
        
        obj['cl']['cl_totalcpus'] = cpus

        for q_name in g.get_cluster_queues_names(hostname):
            obj['q'][q_name] = {}
            obj['q'][q_name]['grid_queued'] = g.get_queue_stats(hostname,q_name,'stats_grid_queued')
            obj['q'][q_name]['local_queued'] = g.get_queue_stats(hostname,q_name,'stats_local_queued')
            obj['q'][q_name]['prelrms_queued'] = g.get_queue_stats(hostname,q_name,'stats_prelrms_queued')
            obj['q'][q_name]['running'] = g.get_queue_stats(hostname,q_name,'stats_running')
            obj['q'][q_name]['grid_running'] = g.get_queue_stats(hostname,q_name,'stats_grid_running')
            
        return json.dumps(obj)

    def gc_cpu_load(self, hostname):
        """ Returns a json string that can be passed
            unmodified to the google charts API. 

            hostname - host name of the cluster front-end.
        """
        key_order = ['cluster', 'gridrun', 'run','cpus']
        description = {'cluster': ('Cluster','string'),
                    'gridrun': ('Grid Running', 'number'),
                    'run': ('Running','number'),
                    'cpus': ('Avail. Cores', 'number')}


        dt = DataTable(description, key_order)
        cluster = g.get_cluster(hostname)
        if not cluster: 
            return 

        gridrun =  g.get_cluster_stats(hostname,'stats_grid_running')
        run = g.get_cluster_stats(hostname,'stats_running') 
        cpus = g.get_cluster_stats(hostname,'stats_cpus')

       
        dt.add_row(cluster.get_alias(), gridrun, abs(run-gridrun), abs(cpus-run))
        
        return dt.get_json()

    def gc_queue_load(self, hostname):
        """ Returns a json string with queue load 
            of specified cluster (by hostname), which
            can be passed to the google charts API.

            hostname - host name of the cluster front-end.
        """
        key_order=['queue','gridqueued', 'localqueued','lrmsqueued']

        description = {'queue': ('Queue','string'),
                        'gridqueued' : ('Grid Queued', 'number'),
                        'localqueued' : ('Local Queued', 'number'),
                        'lrmsqueued' : ('Pre-LRMS Queued', 'number')}

        dt = DataTable(description, key_order)
        no_queue_flag = True
        for q_name in g.get_cluster_queues_names(hostname):
            no_queue_flag = False
            gridq = g.get_queue_stats(hostname,q_name,'stats_grid_queued')
            locq = g.get_queue_stats(hostname,q_name,'stats_local_queued')
            lrmsq =  g.get_queue_stats(hostname,q_name,'stats_prelrms_queued')
            dt.add_row(q_name, abs(gridq), abs(locq), abs(lrmsq))
        
        if no_queue_flag:
            return 'NoQueueError'
        return dt.get_json()

    def show_rrd_plots(self, hostname):
        """ renders a page displaying the 
            load, and infosys rrd plots for the given 
            cluster (hostname).
        """

        c.cluster = hostname
        c.title = "Information for cluster: XXX"  # XXX map to cluster name (and not host name)
        return render('/base/cluster.html')

