import logging
import json
import urllib

from pylons import app_globals as g
from pylons import session
from pylons import request

import gridmonitor.lib.helpers as h
from gridmonitor.lib.base import BaseController
from gridmonitor.lib.charts_table import DataTable
from gridmonitor.model.api.job_api import JobApi


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
 
    def _get_json_params(self):
        """ extracts json parameters from 
            request (used to get params sent
            by ajax)
        """

        md = request.params  # UnicodeMultiDict
        # convert to simple dict
        params = {}
        for k in md.keys():
            if k[-2:] == '[]': # got list 
                params[k[:-2]] = md.getall(k)
            else:
                params[k] = md.get(k)

        log.debug("Got following json params: >%s<" % params)
        return params

    

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
                nrun = g.data_handler.get_num_user_jobs(dn, cluster, status = 'INLRMS:R')
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


    def get_ucj_states(self, arg1 = None, arg2 = None):
        """
            User-Cluster-Job states.
            
            returns json object with corresponding states for each cluster for
                    given user and cluster_list.

            arg1 - dn of the user (must be double url encoded!!), if no dn is given
                 the session 'dns' will be used 
            arg2 - selector for clusters that should be considered. Not yet impl. i.e.
                 now all clusters get selected (default).
        """
        dn = arg1
        # tag = arg2

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
                            ucj2[host][k] += ucj1[host][k]
                        ucj2[host]['total'] += ucj1[host]['total']
                    else:
                        for k in JobsController.JOB_STATES:
                            ucj2[host][k] = ucj1[host][k]
                        ucj2[host]['total'] = ucj1[host]['total']
                
            else:
                if ucj1:
                    return json.dumps(ucj1)

            return json.dumps(ucj2)

    def gc_ucj_states(self, arg1 = None, arg2 = None):
        """
            User-Cluster-Job states.
            
            Returns a json string that can be passed
            unmodified to the google charts API. 
            
            arg1 - dn of the user 
            arg2 - selector for clusters that should be considered. Not yet impl. i.e.
                   now all clusters get selected (default).

        """

        dn = arg1
        tag = arg2

        key_order = ['cluster', 'fin', 'fail', 'kil', 'del', 'ftchd', 'run', 'other', 'orph']
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

        ucj = json.loads(self.get_ucj_states(dn, tag))

        clusters = ucj.keys()
        clusters.sort()

        for cl in clusters:
            if cl != 'summary':
                dt.add_row(cl, ucj[cl]['FINISHED'], \
                    ucj[cl]['FAILED'],\
                    ucj[cl]['KILLED'],\
                    ucj[cl]['DELETED'],\
                    ucj[cl]['FETCHED'],\
                    ucj[cl]['RUN'],\
                    ucj[cl]['other'],\
                    ucj[cl]['orphaned'])
        
        return dt.get_json()


    def get_cuj_states(self, arg1):
        """
        Cluster-User_jobs states.
        
        arg1 -  hostname of the cluster
        
        Returns a json object with the all users and their
        jobs represented.
        """

        hostname = arg1

        orphaned = False   # flag
        ret = {}            
        
        if hostname not in h.get_cluster_names('active')[0]: # all jobs orphaned
            orphaned = True


        for job in g.data_handler.get_cluster_jobs(hostname):
            _user = job.get_globalowner()
            _status = job.get_status()
            
            if _user not in ret.keys():
                ret[_user] =  dict(FINISHED = 0,
                                    FAILED = 0,
                                    KILLED = 0,
                                    DELETED = 0,
                                    FETCHED = 0,
                                    RUN = 0,
                                    orphaned = 0,
                                    other = 0,
                                    total = 0)
        
            if orphaned:
                ret[_user]['orphaned'] += 1
                ret[_user]['total'] += 1
                continue
            
            if _status in ['FINISHED', 'FAILED', 'KILLED']:
                ret[_user][_status] += 1
            elif _status == 'INLRMS:R':
                ret[_user]['RUN'] += 1
            elif _status in JobApi.JOB_STATES_DEL:
                ret[_user]['DELETED']  += 1 
            elif _status in JobApi.JOB_STATES_FETCHED:
                ret[_user]['FETCHED']  += 1 
            else:
                ret[_user]['other']  += 1 

            ret[_user]['total'] += 1
            
        # check whether any of the users has not anymore
        # access to the cluster -> if so orphan all his/her jobs
       
        for user in ret.keys():
            user_allowed_clusters = g.data_handler.get_user_clusters(user)
            if hostname not in user_allowed_clusters:
                ret[user]['orphaned'] = ret[user]['FINISHED'] + \
                    ret[user]['FAILED'] + \
                    ret[user]['KILLED'] + \
                    ret[user]['RUN'] + \
                    ret[user]['other']
                
                ret[user]['FINISHED']  = 0
                ret[user]['FAILED'] = 0
                ret[user]['KILLED'] = 0
                ret[user]['RUN']  = 0
                ret[user]['other'] = 0

 
        return json.dumps(ret)
    
    def gc_cuj_states(self, arg1):
        """
            Cluster-User-Job states.
            
            Returns a json string that can be passed
            unmodified to the google charts API. 
            
            arg1 -  hostname of the cluster
        """

        hostname = arg1

        key_order = ['user', 'fin', 'fail', 'kil', 'del', 'ftchd', 'run', 'other', 'orph']
        description = {'user': ('User','string'),
                    'fin': ('FINISHED', 'number'),
                    'fail': ('FAILED', 'number'),
                    'kil': ('KILLED', 'number'),
                    'del': ('DELETED', 'number'),
                    'ftchd': ('FETCHED', 'number'),
                    'run': ('Running','number'),
                    'other': ('Other state', 'number'),
                    'orph': ('Orphaned', 'number')}

        dt = DataTable(description, key_order)


        cuj = json.loads(self.get_cuj_states(hostname))

        users = cuj.keys()
        # users.sort()

        for user in users:
            _usr = user.split('/CN=')[1] 
            dt.add_row(_usr, cuj[user]['FINISHED'], \
                cuj[user]['FAILED'],\
                cuj[user]['KILLED'],\
                cuj[user]['DELETED'],\
                cuj[user]['FETCHED'],\
                cuj[user]['RUN'],\
                cuj[user]['other'],\
                cuj[user]['orphaned'])
        
        return dt.get_json() 



    def get_cj_states(self, arg1 = None):
        """
            Cluster-Job states.
            
            param: arg1 - list of hostnames of the cluster front-end
                                if no list is passed, hostnames of considered clusters
                                expected to be passed via  http POST

            returns a json dictionary with corresponding states for each cluster 

        """

        cluster_list = arg1

        if  not cluster_list:
            args = self._get_json_params()
            cluster_list = args['hostlist']
        ret = {}
        sum_cluster_jobs = 0
        
        ret['summary'] = dict(total = 0)
        for k in JobsController.JOB_STATES:
            ret['summary'][k] = 0

        for cluster in cluster_list:
            nfin = nfld = nkil = ndel = nftchd = nrun = 0
            norphaned = nother = ntot = 0
            
            active_clusters = h.get_cluster_names('active')[0]

            cjobs = g.data_handler.get_cluster_jobs(cluster)
            if cluster not in active_clusters: # all orphaned
                norphaned = len(cjobs)
                ret[cluster] = dict(FINISHED = nfin,
                                    FAILED = nfld,
                                    KILLED = nkil,
                                    DELETED = ndel,
                                    FETCHED = nftchd,
                                    RUN = nrun,
                                    orphaned = norphaned,
                                    other = nother,
                                    total = norphaned)
                ret['summary']['orphaned'] += norphaned
                continue                
            
            allowed_users = g.data_handler.get_cluster_users(cluster)
        
            for job in cjobs:
                _status = job.get_status()
                _dn = job.get_globalowner()
           
                if job.get_globalowner() not in allowed_users:
                    norphaned += 1
                elif _status == 'FINISHED':
                    nfin += 1 
                elif _status == 'FAILED':
                    nfld += 1 
                elif _status == 'KILLED':
                    nkil += 1 
                elif _status == 'INLRMS:R':
                    nrun += 1 
                elif _status in JobApi.JOB_STATES_DEL:
                    ndel += 1 
                elif _status in JobApi.JOB_STATES_FETCHED:
                    nftchd += 1 
                else:
                    nother += 1 
            
                ntot += 1

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
        
        return json.dumps(ret)


    def gc_cj_states(self):
        """ 
            Cluster-Job-states.
            
            Returns a json string that can be passed
            unmodified to the google charts API. 
            
            cluster_list -- list of hostnames of considered clusters
                             passed in by http POST
        """
        args = self._get_json_params()
        cluster_list = args['hostlist']
        
        log.debug("Got cluster_list %r" % cluster_list) 

        key_order = ['cluster', 'fin', 'fail', 'kil', 'del', 'ftchd', 'run', 'other', 'orph']
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

        cj = json.loads(self.get_cj_states(cluster_list))

        cluster_list.sort()

        for _cl in cluster_list:
            cl = _cl.encode('utf-8')
            dt.add_row(cl, cj[cl]['FINISHED'], \
                cj[cl]['FAILED'],\
                cj[cl]['KILLED'],\
                cj[cl]['DELETED'],\
                cj[cl]['FETCHED'],\
                cj[cl]['RUN'],\
                cj[cl]['other'],\
                cj[cl]['orphaned'])
        

        # add summary (if more then one cluster)
        if len(cluster_list) > 1:
            cl = 'summary'
            dt.add_row(cl, cj[cl]['FINISHED'], \
                cj[cl]['FAILED'],\
                cj[cl]['KILLED'],\
                cj[cl]['DELETED'],\
                cj[cl]['FETCHED'],\
                cj[cl]['RUN'],\
                cj[cl]['other'],\
                cj[cl]['orphaned'])

        return dt.get_json()
