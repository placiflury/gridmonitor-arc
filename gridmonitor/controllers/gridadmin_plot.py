import logging
from gridmonitor.lib.base import *
from gridadmin import GridadminController



class GridadminPlotController(GridadminController):    
    """ Grid administrator plot controller """

    def show(self, type = 'load', name = 'Grid'):
        c.title = "Monitoring System: VO/Grid Admin View - RRD PLOTS"
        c.menu_active = "Overview"
       
        c.heading, c.plot_names = h.get_plot_selection(type,name) 
        
        return render('/derived/gridadmin/plot/show.html')	 
