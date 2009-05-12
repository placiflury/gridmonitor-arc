import logging

from gridmonitor.lib.base import *
from user import UserController 

log = logging.getLogger(__name__)

QUEUE_NAME_LEN=11   # default len of queue names. Names will either be padded or cut to that size

class UserClustersController(UserController):
    
    def index(self):
        c.title = "Monitoring System: User View - Clusters"
        c.menu_active = "Clusters"
        c.heading = "Grid Clusters"
        
        c.tot_cpus = g.get_grid_stats('stats_cpus')
        c.max_cpus=0   # holds values of biggest cluster -> required for generator of chart
        
        # vars for 3D pie chart 
        c.cl_pie_chart_labels = None
        c.cl_pie_chart_data = None
        
        # vars for cluster and queue bar charts
        c.cl_bar_chart = list()  # [(displayname,grid_running,running,cpu),...]
        c.cl_qbar_chart = dict() # {displayname : (chart_data,)}

        for cluster in c.cluster_menu:
            hostname = cluster[1].split('/')[-1] # stripping hostname from url
            display_name = cluster[0]
            cpus = g.get_cluster_stats(hostname,'stats_cpus')
            log.debug("Found for cluster %s (%s)  %d cpus" % (display_name, hostname,cpus))
            if c.max_cpus < cpus:
                c.max_cpus = cpus
            
            # populate pie-chart 
            if not c.cl_pie_chart_labels:
                c.cl_pie_chart_labels = display_name
                c.cl_pie_chart_data = "t:%s" % str(cpus)
            else:
                c.cl_pie_chart_labels += "|%s" % display_name
                c.cl_pie_chart_data += ",%s" % str(cpus)

            # populate cluster bar-chart
            grid_running = g.get_cluster_stats(hostname,'stats_grid_running')
            running = g.get_cluster_stats(hostname,'stats_running')
            c.cl_bar_chart.append((display_name,grid_running,running,cpus))
            
            # populate queue bar-chart(s)
            queues_names = g.get_cluster_queues_names(hostname)
            # handle case of no queues 
            if not queues_names:
                c.cl_qbar_chart[hostname]=(None,None,None,0)
            else:
                grid_queued = list()
                local_queued = list()
                prelrms_queued = list()
                chart_xlabels="1:|gridqueued|localqueued|lrmsqueued|2:"
                for qname in queues_names:
                    log.debug("We go here 4")
                    grid_queued.append(g.get_queue_stats(hostname,qname,'stats_grid_queued'))
                    local_queued.append(g.get_queue_stats(hostname,qname,'stats_local_queued'))
                    prelrms_queued.append(g.get_queue_stats(hostname,qname,'stats_prelrms_queued'))
                    
                    # padding queue name
                    qlen = len(qname)
                    if qlen == QUEUE_NAME_LEN:
                        pass
                    elif qlen < QUEUE_NAME_LEN:
                        # XXX google chart ignores my padding ;-(
                        pass
                        """
                        pad = QUEUE_NAME_LEN - qlen
                        qname = '&#8287;' + '+' * pad + qname  # the + will be url encoded as a space
                        """
                    else: # too long
                        qname = qname[:QUEUE_NAME_LEN-3] + "..." 
                    chart_xlabels+= "|"+qname
                
                grid_queued.reverse()
                local_queued.reverse()
                prelrms_queued.reverse()

                chart_data="t:%s|%s|%s" % (h.list2string(grid_queued),h.list2string(local_queued),h.list2string(prelrms_queued))
                c1 = max(grid_queued)
                c2 = max(local_queued)
                c3 = max(prelrms_queued)
                chart_scaling= max(c1,c2,c3)
                
                c.cl_qbar_chart[display_name]=(chart_data,chart_scaling,chart_xlabels,len(queues_names))
            
        return render('/derived/user/clusters/index.html')

 
    def show(self, id, queue =None):
        """id - cannonized display name of cluster"""
        
        c.cluster_hostname = id
        for cluster in c.cluster_menu:   #XXX rather primitive -> improve
            if id == cluster[1].split('/')[-1]:
                c.cluster_display_name = cluster[0]
                break

        c.menu_active = c.cluster_display_name
        
        if queue:
            c.queue_name = queue
            c.title = "Characteristics of queue '%s' on cluster '%s'" % (c.queue_name, c.cluster_display_name)
            c.queue_obj = g.get_queue(c.cluster_hostname, c.queue_name)
            if not c.queue_obj:
                # XXX -> error message
                pass
            c.heading = "Queue '%s' of cluster '%s'" % (queue,c.cluster_display_name)
            return render('/derived/user/clusters/show_queue.html')

      
        # else fetch cluster info
        c.cluster_obj = g.get_cluster(c.cluster_hostname)
        c.heading = " Cluster %s" % c.cluster_display_name
        c.title = "Characteristics of cluster '%s'" % (c.cluster_display_name)
        return render('/derived/user/clusters/show.html')
		 
