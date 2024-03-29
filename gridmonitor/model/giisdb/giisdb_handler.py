"""
Handler for reading Grid Information System data that is stored 
in a (local) db.
"""
__author__ = "Placi Flury grid@switch.ch"
__date__ = "19.04.2011"
__version__ = "0.3"

import logging
import cPickle
from gridmonitor.model.api.handler_api import HandlerApi
from infocache.db import meta, schema
from sqlalchemy import and_  as AND


class GiisDbHandler(HandlerApi):

    def __init__(self):
        self.log = logging.getLogger(__name__)

    def get_clusters(self, start_t = None, end_t = None):
        """ Returns dictionary of clusters, where the key is 
            the cluster hostname (which is/must be unique) and the value
            is a cluster object that implements the cluster api.
            The returned dictionary may be empty.
        """
        cls = dict()
        query = meta.Session.query(schema.NGCluster)
        dbclusters = query.filter_by(status='active').all()
        self.log.debug("Found %d active clusters." % (len(dbclusters)))
        for cluster in dbclusters:
            cls[cluster.hostname] = cluster
        return cls 

    def get_cluster_queues(self, cluster_hostname, start_t=None, end_t = None):
        """ Returns dictionary of queue objects for given clusters, where
            the keys are the queue names. The queue 
            objects implement the queue qpi. The dictionary  may be empty.
            
            cluster_hostname     -  DN of cluster
            start_t     -  valid from time starting at start_t
            end_t       -  valid until time end_t
        """
        qs = dict()
        query = meta.Session.query(schema.NGQueue)
        for queue in query.filter_by(hostname = cluster_hostname, status = 'active').all():
            qs[queue.get_name()] = queue
        return qs
        
    def get_cluster_jobs(self, cluster_hostname, start_t=None, end_t = None):
        """ Returns list of jobs on cluster. The jobs object implement the 
            job api. List may be empty.
            
            cluster_hostname     -  DN of cluster
            start_t     -  valid from time starting at start_t
            end_t       -  valid until time end_t
        """
        # XXX implement start_t and end_t
        query = meta.Session.query(schema.NGJob)
        jobs = query.filter_by(cluster_name = cluster_hostname).all()
        return jobs
        

    def get_cluster_users(self, cluster_hostname, start_t=None, end_t = None):
        """ Returns list of users (DNs) of allowed on cluster. 
            
            cluster_hostname     -  DN of cluster
            start_t     -  valid from time starting at start_t
            end_t       -  valid until time end_t
        """
        query = meta.Session.query(schema.UserAccess)
        users = query.filter_by(hostname = cluster_hostname).all()
        ulist = list() 
        for u in users:
            ulist.append(u.user)

        return ulist

    def get_user_clusters(self, user_dn, start_t=None, end_t = None):
        """ Returns list of cluster hostnames users is allowed on.
            
            user_dn     -  DN of user (like in certificate)
            start_t     -  valid from time starting at start_t
            end_t       -  valid until time end_t
        """
        query = meta.Session.query(schema.UserAccess)
        clusters = query.filter_by(user = user_dn).all()
        cls = list()
    
        for cluster in clusters:
            if cluster.hostname not in cls:
                cls.append(cluster.hostname)
        return cls


    def get_user_queues(self, user_dn, cluster_hostname, start_t, end_t):
        """ Returns list of queue objects to which user is allowed on.
            The queue objects implement the queue api.
            
            user_dn     -  DN of user (like in certificate)
            cluster_hostname -  DNS of cluster
            start_t     -  valid from time starting at start_t
            end_t       -  valid until time end_t
        """
        query = meta.Session.query(schema.UserAccess)
        return query.filter_by(user = user_dn, hostname = cluster_hostname).all()
        """
        qs=list()
        for q in queues:
            qs.append(q.queuename)
        return qs
        """

    def get_user_jobs(self, user_dn, status=None, start_t = None, end_t=None):
        """ 
        special job status 'orphaned' must be supported. Orphans are jobs
        jobs that got executed on a queue the user can't access anymore.
        """
        query = meta.Session.query(schema.NGJob)
        query = query.outerjoin('access')
       
        if status == 'orphaned':
            query = query.filter(AND(schema.NGJob.global_owner==user_dn, 
            schema.UserAccess.user == None))
            orphaned = query.all()
            self.log.debug("Found %d orphaned" % len(orphaned))
            return orphaned
        elif status == 'INLRMS':
            jobs=query.filter(AND(schema.UserAccess.user != None,
                schema.NGJob.global_owner == user_dn,
                schema.NGJob.status.like('%INLRMS%'))).all()
        elif status == 'FETCHED':
            jobs=query.filter(AND(schema.UserAccess.user != None,
                schema.NGJob.global_owner == user_dn, 
                schema.NGJob.status.like('%FETCHED%'))).all()
        elif status:
            jobs = query.filter(AND(schema.UserAccess.user != None, 
                schema.NGJob.global_owner==user_dn, 
                schema.NGJob.status==status)).all()
        else:
            jobs = query.filter(AND(schema.NGJob.global_owner == user_dn)).all()

        self.log.debug("Found %d non-orphaned jobs" % len(jobs))
        return jobs

    def get_num_user_jobs(self,user_dn, cluster_hostname=None, status=None, start_t = None, end_t=None):
        """ 
        Returns the number of jobs for user.
        special job status 'orphaned' must be supported. Orphans are jobs
        jobs that got executed on a queue the user can't access anymore.
        """
        query = meta.Session.query(schema.NGJob)
        query = query.outerjoin('access')
      
        if not cluster_hostname: 
            if status == 'orphaned':
                query = query.filter(AND(schema.NGJob.global_owner == user_dn, 
                schema.UserAccess.user == None))
                norphaned = query.count()
                return norphaned
            elif status == 'INLRMS':
                njobs=query.filter(AND(schema.UserAccess.user != None,
                    schema.NGJob.global_owner == user_dn,
                    schema.NGJob.status.like('%INLRMS%'))).count()
            elif status == 'FETCHED':
                njobs=query.filter(AND(schema.UserAccess.user != None,
                    schema.NGJob.global_owner == user_dn,
                    schema.NGJob.status.like('%FETCHED%'))).count()
            elif status:
                njobs = query.filter(AND(schema.UserAccess.user != None, 
                    schema.NGJob.global_owner == user_dn,
                    schema.NGJob.status == status)).count()
            else:
                njobs = query.filter(AND(schema.NGJob.global_owner == user_dn)).count()

            return njobs
        else:
            if status == 'orphaned':
                query = query.filter(AND(schema.NGJob.cluster_name == cluster_hostname, 
                    schema.NGJob.global_owner == user_dn, 
                    schema.UserAccess.user == None))
                norphaned = query.count()
                return norphaned
            elif status == 'INLRMS':
                njobs=query.filter(AND(schema.NGJob.cluster_name == cluster_hostname, 
                        schema.UserAccess.user != None,
                        schema.NGJob.global_owner == user_dn,
                        schema.NGJob.status.like('%INLRMS%'))).count()
            elif status == 'FETCHED':
                njobs=query.filter(AND(schema.NGJob.cluster_name == cluster_hostname, 
                    schema.UserAccess.user != None,
                    schema.NGJob.global_owner == user_dn,
                    schema.NGJob.status.like('%FETCHED%'))).count()
            elif status:
                njobs = query.filter(AND(schema.NGJob.cluster_name == cluster_hostname,
                    schema.UserAccess.user != None, 
                    schema.NGJob.global_owner == user_dn, 
                    schema.NGJob.status==status)).count()
            else:
                njobs = query.filter(AND(schema.NGJob.cluster_name == cluster_hostname, 
                    schema.NGJob.global_owner == user_dn)).count()
            return njobs
            

    def refresh(self):
        """ refreshing everything. May throw HandlerExceptions."""
        pass

    def refresh_clusters(self):
        pass

    def refresh_queues(self,cluster_hostname):
        pass

    def refresh_queue(self,cluster_hostname, queue_name):
        pass

    def refresh_jobs(self,cluster_hostname):
        pass

    def refresh_user_jobs(self, user_dn):
        pass

    def get_grid_stats(self):
        """ returns either statistics object that implements the StatsApi, or None.
            Calling the get_type() method return 'grid'.
        """
        query = meta.Session.query(schema.GridStats)
        stats = query.first()
        if stats:
            return cPickle.loads(stats.pickle_object)
        return None

    def get_cluster_stats(self, cluster_hostname):
        """ returns either statistics object that implements the StatsApi, or None.
            Calling the get_type() method return 'cluster'.
        """
        grid_stats = self.get_grid_stats()
        if grid_stats:
            cluster_stats = grid_stats.get_children()
            for cluster_stat in cluster_stats:
                if cluster_stat.get_name() == cluster_hostname:
                    return cluster_stat
        return None


    def get_queue_stats(self,cluster_hostname,queue_name):
        """ returns either statistics object that implements the StatsApi, or None.
            Calling the get_type() method return 'queue'.
        """
        cluster_stats = self.get_cluster_stats(cluster_hostname)
        if cluster_stats:
            queue_stats_list = cluster_stats.get_children()
            for queue_stat in queue_stats_list:
                if queue_stat.get_name() == queue_name:
                    return queue_stat

    def get_user_stats(self,user_dn):
        # XXX 
        pass


