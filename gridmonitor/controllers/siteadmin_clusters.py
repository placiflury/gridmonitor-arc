import logging
from gridmonitor.lib.base import *
from siteadmin import SiteadminController

log = logging.getLogger(__name__)

QUEUE_NAME_LEN=11   # default len of queue names. Names will either be padded or cut to that size

class SiteadminClustersController(SiteadminController):    

    def index(self):
        c.title = "Monitoring System: Site Admin View"
        c.menu_active = "Your Cluster(s)"
        c.heading = "Your Cluster(s)"  
        
        if not self.authorized:
            c.heading= "Your Cluster(s)"
            return render('/derived/siteadmin/error/access_denied.html')
        
        # vars for cluster and queue bar charts
        c.cl_bar_chart = list()  # [(displayname,grid_running,running,cpu),...]
        c.cl_qbar_chart = dict() # {displayname : (chart_data,)}
        c.cl_detailstats = dict() # {displayname: {q_name:(grid_running,running,gridqd,localqd,plrmsqd)},..}
        
        for cluster in c.cluster_menu:
            hostname = cluster[1].split('/')[-1] # stripping hostname from url
            display_name = cluster[0]
            c.cl_detailstats[display_name]=dict()

            cpus = g.get_cluster_stats(hostname,'stats_cpus')

            # populate cluster bar-chart and statistics for cluster 'detail' displaying
            grid_running = g.get_cluster_stats(hostname,'stats_grid_running')
            running = g.get_cluster_stats(hostname,'stats_running')
            totaljobs = g.get_cluster_stats(hostname,'stats_totaljobs')
            usedcpus = g.get_cluster_stats(hostname,'stats_usedcpus')
            c.cl_bar_chart.append((display_name,grid_running,running,cpus,totaljobs,usedcpus))

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
                    gqd = g.get_queue_stats(hostname,qname,'stats_grid_queued')
                    lqd= g.get_queue_stats(hostname,qname,'stats_local_queued')
                    plrms = g.get_queue_stats(hostname,qname,'stats_prelrms_queued')
                    run = g.get_queue_stats(hostname,qname,'stats_running')
                    grun = g.get_queue_stats(hostname,qname,'stats_grid_running')

                    grid_queued.append(gqd)
                    local_queued.append(lqd)

                    prelrms_queued.append(plrms)

                    c.cl_detailstats[display_name][qname]=(grun,run,gqd,lqd,plrms)

                    qlen = len(qname)
                    if qlen <= QUEUE_NAME_LEN:
                        pass
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
                chart_scaling= c1+c2+c3
                c.cl_qbar_chart[display_name]=(chart_data,chart_scaling,chart_xlabels,len(queues_names))

        return render('/derived/siteadmin/clusters/index.html')

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
                log.warn("Info about queue '%s' of cluster '%s' not available anymore." % (id,queue))
                return render("/derived/user/clusters/index.html")
            c.heading = "Queue '%s' of cluster '%s'" % (queue,c.cluster_display_name)
            return render('/derived/user/clusters/show_queue.html')


        # else fetch cluster info
        c.cluster_obj = g.get_cluster(c.cluster_hostname)
        if not c.cluster_obj:
            # XXX -> error message
            log.warn("Info about cluster '%s' not available anymore." % id)
            return render("/derived/user/clusters/index.html")
        c.queues_names = g.get_cluster_queues_names(c.cluster_hostname)
        c.heading = " Cluster %s" % c.cluster_display_name
        c.title = "Characteristics of cluster '%s'" % (c.cluster_display_name)
        return render('/derived/user/clusters/show.html')  # we use the 'user' pages to display results.

    


