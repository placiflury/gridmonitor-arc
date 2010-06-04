#!/usr/bin/env python
##############################################################################
# Copyright (c) 2008, SMSCG - Swiss Multi Science Computing Grid.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the University of California, Berkeley nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE REGENTS AND CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# $Id$
################################################################################
"""
Interface (API) to data model of the Grid-Monitoring tool. The interface should
allow to either access to a database and/or directly to e.g. the information 
system of the Grid middleware. 

"""
__author__="Placi Flury placi.flury@switch.ch"
__date__="14.04.2009"
__version__="0.1.1"


class HandlerApi:
    """ Interface to data model used by the Grid Monitoring tool. """

    def __init__(self):
        """ May throw HandlerExeptions. """
        pass
            
    def get_clusters(self,start_t=None, end_t = None):
        """ Returns dictionary of clusters, where the key is 
            the cluster hostname (which is/must be unique) and the value
            is a cluster object that implements the cluster api.
            The returned dictionary may be empty.
        """
        pass
     

    def get_cluster_queues(self, cluster_hostname, start_t=None, end_t = None):
        """ Returns dictionary of queue objects for given clusters, where
            the keys are the queue names. The queue 
            objects implement the queue qpi. The dictionary  may be empty.
            
            cluster_hostname     -  DN of cluster
            start_t     -  valid from time starting at start_t
            end_t       -  valid until time end_t
        """
        pass

    def get_cluster_jobs(self, cluster_hostname, start_t=None, end_t = None):
        """ Returns list of jobs on cluster. The jobs object implement the 
            job api. List may be empty.
            
            cluster_hostname     -  DN of cluster
            start_t     -  valid from time starting at start_t
            end_t       -  valid until time end_t
        """
        pass
    
    def get_cluster_users(self, cluster_hostname, start_t=None, end_t = None):
        """ Returns list of users (DNs) of allowed on cluster. 
            
            cluster_hostname     -  DN of cluster
            start_t     -  valid from time starting at start_t
            end_t       -  valid until time end_t
        """
        pass


    def get_user_clusters(self,user_dn,start_t=None, end_t = None):
        """ Returns list of cluster hostnames users is allowed on.
            
            user_dn     -  DN of user (like in certificate)
            start_t     -  valid from time starting at start_t
            end_t       -  valid until time end_t
        """
        pass 
    
    def get_user_queues(self,user_dn, cluster_hostname,start_t,end_t):
        """ Returns list of queue objects to which user is grated access.
            The queue objects implement the queue api.
            
            user_dn     -  DN of user (like in certificate)
            cluster_hostname -  DNS of cluster
            start_t     -  valid from time starting at start_t
            end_t       -  valid until time end_t
        """
        pass

    def get_user_jobs(self,user_dn, status=None, start_t = None, end_t=None):
        """ 
        special job status 'orphans' must be supported. Orphans are jobs
        jobs that got executed on a queue the user can't access anymore.
        """
        pass
    
    def get_num_user_jobs(self,user_dn, cluster_hostname=None, status=None, start_t = None, end_t=None):
        """ 
        Returns only the number of jobs for user. 
        special job status 'orphans' must be supported. Orphans are jobs
        jobs that got executed on a queue the user can't access anymore.
        """
        pass

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
        pass

    def get_cluster_stats(self,cluster_hostname):
        """ returns either statistics object that implements the StatsApi, or None.
            Calling the get_type() method return 'cluster'.
        """
        pass

    def get_queue_stats(self,cluster_hostname,queue_name):
        """ returns either statistics object that implements the StatsApi, or None.
            Calling the get_type() method return 'queue'.
        """
        pass

    def get_user_stats(self,user_dn):
        pass
