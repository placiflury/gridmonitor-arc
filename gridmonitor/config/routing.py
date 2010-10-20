"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from pylons import config
from routes import Mapper

def make_map():
    """Create, configure and return the routes Mapper"""
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('error/:action/:id', controller='error')

    map.connect('',controller='user_overview')
    map.connect('user',controller='user_overview')
    map.connect('user/overview/:action', controller='user_overview')
    map.connect('user/vos/:action', controller='user_vos')
    map.connect('user/clusters/:action', controller='user_clusters')
    map.connect('user/clusters/:action/:id', controller='user_clusters')
    map.connect('user/clusters/:action/:id/:queue', controller='user_clusters')
    map.connect('user/jobs/:action', controller='user_jobs')
    map.connect('user/jobs/:action/:status', controller='user_jobs')
    map.connect('user/jobdetails/:dn/:jobid',controller='user_job_details')
    map.connect('user/statistics/:action', controller='user_statistics')
    map.connect('user/tickets', controller='user_tickets')
    map.connect('user/links', controller='user_links')
    
    # site admin
    map.connect('siteadmin',controller='siteadmin_overview')
    map.connect('siteadmin/overview/:action', controller='siteadmin_overview')
    map.connect('siteadmin/clusters/:action', controller='siteadmin_clusters')
    map.connect('siteadmin/clusters/:action/:id', controller='siteadmin_clusters')
    map.connect('siteadmin/clusters/:action/:id/:queue', controller='siteadmin_clusters')
    map.connect('siteadmin/jobs/:action', controller='siteadmin_jobs')
    map.connect('siteadmin/users/:action', controller='siteadmin_users')
    map.connect('siteadmin/testjobs/:action', controller='siteadmin_testjobs')
    map.connect('siteadmin/testjobs/:action/:suit', controller='siteadmin_testjobs')
    map.connect('siteadmin/statistics/:action', controller='siteadmin_statistics')
    map.connect('siteadmin/newadmin/:action', controller='siteadmin_newadmin')
    
    # grid admin
    map.connect('gridadmin',controller='gridadmin_overview')
    map.connect('gridadmin/overview/:action', controller='gridadmin_overview')
    map.connect('gridadmin/clusters/:action', controller='gridadmin_clusters')
    map.connect('gridadmin/clusters/:action/:id', controller='gridadmin_clusters')
    map.connect('gridadmin/clusters/:action/:id/:queue', controller='gridadmin_clusters')
    map.connect('gridadmin/vos/:action', controller='gridadmin_vos')
    map.connect('gridadmin/vos/:action/:id', controller='gridadmin_vos')
    map.connect('gridadmin/vos/:action/:id/:queue', controller='gridadmin_vos')
    map.connect('gridadmin/sfts/:action', controller='gridadmin_sfts')
    map.connect('gridadmin/sfts/:action/:name', controller='gridadmin_sfts')
    map.connect('gridadmin/sfts/:action/:name/:cluster_name', controller='gridadmin_sfts')
    map.connect('gridadmin/statistics/:action', controller='gridadmin_statistics')
    map.connect('gridadmin/infosys/:action', controller='gridadmin_infosys')
    map.connect('gridadmin/infosys/:action/:arg', controller='gridadmin_infosys')
    map.connect('gridadmin/plot/:action/:type/:name', controller='gridadmin_plot')

    # help 
    map.connect('help',controller='help')







    # CUSTOM ROUTES HERE
    map.connect(':controller/:action/:id')
    map.connect('*url', controller='template', action='view')

    return map
