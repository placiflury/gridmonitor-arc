import logging

from gridmonitor.lib.base import *
from gridadmin import GridadminController
"""
from gridmonitor.model.giisdb import meta
from gridmonitor.model.giisdb import ng_schema
"""
log = logging.getLogger(__name__)

class GridadminStatisticsController(GridadminController):
    """
    Beware, this class is not using the API interface and is
    as such not 'portable'. XXX -> extend api? 
    """
    def index(self):
        c.title = "Monitoring System: VO/Grid Admin Statistics"
        c.menu_active = "Grid Statistics"
        c.heading = "VO/Grid Statistics"
        """
        query = meta.Session.query(ng_schema.Cluster)
        c.dbclusters = query.filter_by(status='active').all()
        c.blacklisted = meta.Session.query(ng_schema.Grisblacklist).all()
        c.giises = meta.Session.query(ng_schema.Giis).all()
        """

        return render('/derived/gridadmin/statistics/index.html')
