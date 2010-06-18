import logging

from gridmonitor.lib.base import *
from gridadmin import GridadminController

from infocache.db import meta
from infocache.db import ng_schema

log = logging.getLogger(__name__)

class GridadminInfosysController(GridadminController):
    """
    Beware, this class is not using the API interface and is
    as such not 'portable'. XXX -> extend api? 
    """
    def __init__(self):
        GridadminController()
        query = meta.Session.query(ng_schema.Cluster)
        #c.dbclusters = query.filter_by(status='active').all()
        c.dbclusters = query.all()
        c.blacklisted = meta.Session.query(ng_schema.Grisblacklist).all()
        c.giises = meta.Session.query(ng_schema.Giis).all()
        c.title = "Monitoring System -- Infosys (GRIS/GIIS) Statistics --"
        
        # get some query time
        if c.giises:
            c.query_time = c.giises[0].db_lastmodified
        elif c.dbclusters:
            c.query_time = c.dbclusters[0].db_lastmodified
        else:
            c.query_time = 'UNKNOWN' 

    def index(self):

        c.menu_active = "GRIS/GIIS"
        c.heading = "Information System Details"
        c.suffix= None 
        
        query = meta.Session.query(ng_schema.Cluster)
        c.db_inactive_clusters = query.filter_by(status='inactive').all()
        return render('/derived/gridadmin/infosys/index.html')

    
    def show(self,arg):
        interval = arg
        if not interval:
            c.menu_active = "GRIS/GIIS"
            c.heading = "Statistics about the Grid Information System (GRIS/GIIS)"
            c.suffix = None
        elif interval == 'w1':
            c.menu_active = "last week"
            c.suffix= '_w1.png'
            c.heading = "Statistics about the Grid Information System (GRIS/GIIS) of current week."
        elif interval == 'y1':
            c.menu_active = "last year"
            c.suffix= '_y1.png'
            c.heading = "Statistics about the Grid Information System (GRIS/GIIS) of current  year."
        else:
            c.menu_active = "last 6 hours"
            c.suffix= '_h6.png'
            c.heading = "Statistics about the Grid Information System (GRIS/GIIS) of last 6 hours."
            
        return render('/derived/gridadmin/infosys/index.html')
    
    def show_all(self, arg):
        """ Shows all available plots for specified cluster. Mostly 
            used for displaying history of 'inactive' clusters. 
        """
        c.cluster_name = arg
        c.heading = "Statistics about %s (GRIS/GIIS)" % c.cluster_name
        return render('/derived/gridadmin/infosys/details.html')
            
