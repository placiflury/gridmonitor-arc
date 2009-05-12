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
    map.connect('user/statistics/:action', controller='user_statistics')
    
    # mocking sites
    map.connect('siteadmin',controller='siteadmin_overview')
    map.connect('siteadmin/overview/:action', controller='siteadmin_overview')
    map.connect('siteadmin/vos/:action', controller='siteadmin_vos')
    map.connect('siteadmin/testjobs/:action', controller='siteadmin_testjobs')
    map.connect('siteadmin/testjobs/:action/:suit', controller='siteadmin_testjobs')
    map.connect('siteadmin/statistics/:action', controller='siteadmin_statistics')







    # CUSTOM ROUTES HERE
    map.connect(':controller/:action/:id')
    map.connect('*url', controller='template', action='view')

    return map
