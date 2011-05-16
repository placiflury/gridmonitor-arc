import logging
from pylons import session
from pylons import tmpl_context as c
from pylons import app_globals as g
from pylons.templating import render_mako as render

import gridmonitor.lib.helpers as h

from user import UserController

log = logging.getLogger(__name__)

QUEUE_NAME_LEN=11   # default len of queue names. Names will either be padded or cut to that size

class UserClustersController(UserController):
    
    def __init__(self): 
        UserController.__init__(self)
        c.user_slcs_dn = None       
        c.user_client_dn = None
        
        if session.has_key('user_slcs_obj'):
            user_slcs_obj = session['user_slcs_obj']
            c.user_slcs_dn = user_slcs_obj.get_dn()

        if session.has_key('user_client_dn'):
            c.user_client_dn = session['user_client_dn']

    def index(self):
        c.title = "Monitoring System: User View - Clusters"
        c.menu_active = "Clusters"
        c.heading = "Grid Clusters for %s %s" % (c.user_name, c.user_surname)
       
        
        c.allowed_clusters = {}
        c.allowed_clusters[c.user_slcs_dn] = g.data_handler.get_user_clusters(c.user_slcs_dn)
        c.allowed_clusters[c.user_client_dn] = g.data_handler.get_user_clusters(c.user_client_dn)
        c.allowed_clusters['slcs_browser'] =  [sc for sc in c.allowed_clusters[c.user_slcs_dn] \
            for bc in c.allowed_clusters[c.user_client_dn] if sc==bc] # list comprehension
                        
        
        c.tot_cpus = g.get_grid_stats('stats_cpus')
        c.max_cpus=0   # holds values of biggest cluster -> required for generator of chart
        
        # vars for 3D pie charts -> we'll create one for ALL clusters, and one for SLCS and Browser DN access 
        c.cl_pie_chart_labels = dict()
        c.cl_pie_chart_labels['all'] = dict()
        c.cl_pie_chart_labels[c.user_slcs_dn] = dict()
        c.cl_pie_chart_labels[c.user_client_dn] = dict()
        c.cl_pie_chart_data = dict()
        c.cl_pie_chart_data['all'] = dict()
        c.cl_pie_chart_data[c.user_slcs_dn] = dict()
        c.cl_pie_chart_data[c.user_client_dn] = dict()
        
        # vars for cluster and queue bar charts
        c.cl_bar_chart = list()  # [(displayname,grid_running,running,cpu),...]
        c.cl_qbar_chart = dict() # {displayname : (chart_data,)}
        c.cl_detailstats = dict() # {displayname: {q_name:(grid_running,running,gridqd,localqd,plrmsqd)},..}

        for cluster in c.cluster_menu:
            hostname = cluster[1].split('/')[-1] # stripping hostname from url
            display_name = cluster[0]
            c.cl_detailstats[display_name]=dict()

            cpus = g.get_cluster_stats(hostname,'stats_cpus') 
            if cpus == 0: # if queue info did not contain num of cpus we take cluster info
                cpus=g.get_cluster_stats(hostname,'stats_totalcpus')

            log.debug("Found for cluster %s (%s)  %d cpus" % (display_name, hostname,cpus))
            if c.max_cpus < cpus:
                c.max_cpus = cpus
           
            _cpus = abs(cpus) # avoid to be screwed by negative numbers 
            # populate pie-charts
            if hostname in c.allowed_clusters[c.user_slcs_dn]:
                if not c.cl_pie_chart_labels[c.user_slcs_dn]:
                    c.cl_pie_chart_labels[c.user_slcs_dn] = display_name
                    c.cl_pie_chart_data[c.user_slcs_dn] = "t:%s" % str(_cpus)
                else:
                    c.cl_pie_chart_labels[c.user_slcs_dn] += "|%s" % display_name
                    c.cl_pie_chart_data[c.user_slcs_dn] += ",%s" % str(_cpus)
            if hostname in c.allowed_clusters[c.user_client_dn]:
                if not c.cl_pie_chart_labels[c.user_client_dn]:
                    c.cl_pie_chart_labels[c.user_client_dn] = display_name
                    c.cl_pie_chart_data[c.user_client_dn] = "t:%s" % str(_cpus)
                else:
                    c.cl_pie_chart_labels[c.user_client_dn] += "|%s" % display_name
                    c.cl_pie_chart_data[c.user_client_dn] += ",%s" % str(_cpus)
            if not c.cl_pie_chart_labels['all']:
                c.cl_pie_chart_labels['all'] = display_name
                c.cl_pie_chart_data['all'] = "t:%s" % str(_cpus)
            else:
                c.cl_pie_chart_labels['all'] += "|%s" % display_name
                c.cl_pie_chart_data['all'] += ",%s" % str(_cpus)
                
         

            # populate cluster bar-chart and statistics for cluster 'detail' displaying
            grid_running = g.get_cluster_stats(hostname,'stats_grid_running')
            running = g.get_cluster_stats(hostname,'stats_running')
            totaljobs = g.get_cluster_stats(hostname,'stats_totaljobs')
            usedcpus = g.get_cluster_stats(hostname,'stats_usedcpus')
            c.cl_bar_chart.append((display_name,grid_running,running,cpus,totaljobs,usedcpus,hostname))
            
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
                chart_scaling= c1+c2+c3
                
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
        return render('/derived/user/clusters/show.html')
		 
