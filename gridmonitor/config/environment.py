"""Pylons environment configuration"""
import os
import logging

from mako.lookup import TemplateLookup
from pylons.configuration import PylonsConfig
from pylons.error import handle_mako_error
from sqlalchemy import engine_from_config


import gridmonitor.lib.app_globals as app_globals
import gridmonitor.lib.helpers
from gridmonitor.config.routing import make_map

from gridmonitor.model.nagios import init_model 
from gridmonitor.model.acl import init_acl_model 
from sft import init_configuration
from sft.db import init_model as init_sft_model
from sgasaggregator import dbinit
from sgasaggregator.sgascache import session as sgascache_session


log = logging.getLogger(__name__)

def load_environment(global_conf, app_conf):
    config = PylonsConfig()

    # Pylons paths
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = dict(root=root,
                 controllers=os.path.join(root, 'controllers'),
                 static_files=os.path.join(root, 'public'),
                 templates=[os.path.join(root, 'templates')])

    # Initialize config with the basic options
    config.init_app(global_conf, app_conf, package='gridmonitor', paths=paths)

    config['routes.map'] = make_map(config)
    config['pylons.app_globals'] = app_globals.Globals(config)
    config['pylons.h'] = gridmonitor.lib.helpers

    # Create the Mako TemplateLookup, with the default auto-escaping
    config['pylons.app_globals'].mako_lookup = TemplateLookup(
        directories=paths['templates'],
        error_handler=handle_mako_error,
        module_directory=os.path.join(app_conf['cache_dir'], 'templates'),
        input_encoding='utf-8', default_filters=['escape'],
        imports=['from webhelpers.html import escape'])

    # Setup cache object as early as possible
    import pylons
    pylons.cache._push_object(config['pylons.app_globals'].cache)

    # CONFIGURATION OPTIONS HERE (note: all config options will override
    # any Pylons config options)

    nagios_engine = engine_from_config(config, 'sqlalchemy_nagios.')
    init_model(nagios_engine)
    log.info('Nagios DB connection initialized')
    acl_engine = engine_from_config(config, prefix='sqlalchemy_acl.', encoding='utf-8')
    init_acl_model(acl_engine)
    log.info('ACL DB connection initialized')
    handler_type = config['data_handler_type'].lower().strip()
    if handler_type in ['giisdb','giis_handler']:
        from infocache.db  import init_model as init_giisdb_model
        giisdb_engine = engine_from_config(config, prefix='sqlalchemy_giisdb.')
        init_giisdb_model(giisdb_engine)
        log.info('GIIS DB connection initialized')
    sft_engine = engine_from_config(config, prefix='sqlalchemy_sft.')
    init_sft_model(sft_engine)
    init_configuration(config['sft_config'])
    log.info('SFT DB connection initialized')
    
    sgascache_engine = engine_from_config(config, prefix='sqlalchemy_sgascache.')
    dbinit.init_model(sgascache_session, sgascache_engine)
    log.info('SGASCACHE DB connection initialized')

    return config
