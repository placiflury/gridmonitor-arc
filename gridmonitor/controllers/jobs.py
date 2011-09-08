import logging
import json
import urllib

from pylons import app_globals as g
from pylons import session

from gridmonitor.lib.base import BaseController
from gridmonitor.lib.charts_table import DataTable

log = logging.getLogger(__name__)

class JobsController(BaseController):
    
    """ This controller doesn't serve a web page of
        the GridMonitor application. It does instead
        provide json query urls to populate data/plots
    """

    JOB_STATES = ['FINISHED', 
            'KILLED',
            'FAILED',
            'DELETED',
            'FETCHED',
            'RUN',
            'orphaned',
            'other']

    def _get_ucj_states(self, dn, cluster_list = None):
        """
            returns a dictionary with corresponding states for each cluster for
                    given user and cluster_list.

            dn - dn of the user 
            cluster_list - list of hostname of the cluster front-end, if no cluster list
                            has been given, we take all clusters user is allowd on
        """

        dn = urllib.unquote_plus(dn)
        log.debug("Creating job summary for  DN >%s<" % dn)

        ret = {}

        if not cluster_list:
            clist = g.data_handler.get_user_clusters(dn)
        else:
            clist = cluster_list

        sum_cluster_jobs = 0


        ret['summary'] = dict(total = 0)
        for k in JobsController.JOB_STATES:
                ret['summary'][k] = 0

        for cluster in clist:
            if not ret.has_key(cluster):
                nfin = g.data_handler.get_num_user_jobs(dn, cluster , status = 'FINISHED')
                nfld = g.data_handler.get_num_user_jobs(dn, cluster, status = 'FAILED') 
                nkil = g.data_handler.get_num_user_jobs(dn, cluster, status = 'KILLED') 
                ndel = g.data_handler.get_num_user_jobs(dn, cluster, status = 'DELETED') 
                nftchd = g.data_handler.get_num_user_jobs(dn, cluster, status = 'FETCHED') 
                nrun = g.data_handler.get_num_user_jobs(dn, cluster, status = 'INLRMS: R')
                norphaned = g.data_handler.get_num_user_jobs(dn, cluster, status = 'orphaned')
                ntot  = g.data_handler.get_num_user_jobs(dn, cluster) 
                nother = ntot - nfin - nfld - nkil - ndel - nftchd - norphaned -nrun
                
                ret[cluster] = dict(FINISHED = nfin,
                                    FAILED = nfld,
                                    KILLED = nkil,
                                    DELETED = ndel,
                                    FETCHED = nftchd,
                                    RUN = nrun,
                                    orphaned = norphaned,
                                    other = nother,
                                    total = ntot)

                ret['summary']['FINISHED'] += nfin
                ret['summary']['FAILED'] += nfld
                ret['summary']['KILLED'] += nkil
                ret['summary']['DELETED'] += ndel
                ret['summary']['FETCHED'] += nftchd
                ret['summary']['RUN'] += nrun
                ret['summary']['orphaned'] += norphaned
                ret['summary']['other'] += nother


                sum_cluster_jobs += ntot

        ret['summary']['total'] = sum_cluster_jobs
        
        # final check for orphaned jobs of clusters which are down or not reacheable
        if not cluster_list:
            sum_grid_jobs = g.data_handler.get_num_user_jobs(dn)
            dorph = sum_grid_jobs - sum_cluster_jobs

            if dorph != 0:
                ret['DOWN_CLUSTERS'] = dict(total = dorph)
                for k in JobsController.JOB_STATES:
                    ret['DOWN_CLUSTERS'][k] = 0
            
                ret['DOWN_CLUSTERS']['orphaned'] = dorph
                ret['summary']['orphaned'] += dorph

        return ret


    def get_ucj_states(self, dn = None, tag = None):
        """
            returns json object with corresponding states for each cluster for
                    given user and cluster_list.

            dn - dn of the user (must be double url encoded!!), if no dn is given
                 the session 'dns' will be used 
            tag - selector for clusters that should be considered. Not yet impl. i.e.
                rith now all clusters get selected (default).
        """


        if dn:
            return json.dumps(self._get_ucj_states(dn))
        else:
            ucj1 = None
            ucj2 = None

            if session.has_key('user_slcs_obj'):
                user_slcs_obj = session['user_slcs_obj']
                ucj1 = self._get_ucj_states(user_slcs_obj.get_dn())

            if session.has_key('user_client_dn'):
                browser_dn = session['user_client_dn']
                ucj2 = self._get_ucj_states(browser_dn)
            
            if ucj1 and ucj2:
                for host in ucj1.keys(): # summary is also included
                    if ucj2.has_key(host):
                        for k in JobsController.JOB_STATES:
                            ret[host][k] += ucj[host][k]
                        ucj2[host]['total'] += ucj1[host]['total']
                    else:
                        for k in JobsController.JOB_STATES:
                            ret[host][k] = ucj[host][k]
                        ucj2[host]['total'] = ucj1[host]['total']
                
            else:
                if ucj1:
                    return json.dumps(ucj1)

            return json.dumps(ucj2)

    def gc_ucj_states(self, dn, tag = None):
        """ Returns a json string that can be passed
            unmodified to the google charts API. 
            
            dn - dn of the user (must be double url encoded!!)
            tag - selector for clusters that should be considered. Not yet impl. i.e.
                rith now all clusters get selected (default).

        """
        key_order = ['cluster', 'fin', 'fail', 'kil', 'del','ftchd', 'run','other','orph']
        description = {'cluster': ('Cluster','string'),
                    'fin': ('FINISHED', 'number'),
                    'fail': ('FAILED', 'number'),
                    'kil': ('KILLED', 'number'),
                    'del': ('DELETED', 'number'),
                    'ftchd': ('FETCHED', 'number'),
                    'run': ('Running','number'),
                    'other': ('Other state', 'number'),
                    'orph': ('Orphaned', 'number')}

        dt = DataTable(description, key_order)

        ucj = self._get_ucj_states(dn, tag)

        clusters = ucj.keys()
        clusters.sort()

        for cl in clusters:
            dt.add_row(cl, ucj[cl]['FINISHED'], \
                ucj[cl]['FAILED'],\
                ucj[cl]['KILLED'],\
                ucj[cl]['DELETED'],\
                ucj[cl]['FETCHED'],\
                ucj[cl]['RUN'],\
                ucj[cl]['other'],\
                ucj[cl]['orphaned'])
        
        return dt.get_json()



    def cluster_summary(self, cluster):
        """
            cluster - hostname of cluster front-end
            XXX not yet implemented
        """
        pass 

    def status_summary(self, state):
        """
            state - job state
            
            XXX not yet implemented
        """
        pass 
