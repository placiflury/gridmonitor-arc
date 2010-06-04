"""Pylons environment configuration"""
import os

from pylons import config

import gridmonitor.lib.app_globals as app_globals
import gridmonitor.lib.helpers
from gridmonitor.config.routing import make_map

from sqlalchemy import engine_from_config
from gridmonitor.model.nagios import init_model 
from gridmonitor.model.acl import init_acl_model 
from gridmonitor.model.giisdb import init_giisdb_model 
from gridmonitor.model.sft import init_sft_model


def load_environment(global_conf, app_conf):
    """Configure the Pylons environment via the ``pylons.config``
    object
    """
    # Pylons paths
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = dict(root=root,
                 controllers=os.path.join(root, 'controllers'),
                 static_files=os.path.join(root, 'public'),
                 templates=[os.path.join(root, 'templates')])

    # Initialize config with the basic options
    config.init_app(global_conf, app_conf, package='gridmonitor',
                    template_engine='mako', paths=paths)

    config['routes.map'] = make_map()
    config['pylons.g'] = app_globals.Globals()
    config['pylons.h'] = gridmonitor.lib.helpers

    # Customize templating options via this variable
    tmpl_options = config['buffet.template_options']

    # CONFIGURATION OPTIONS HERE (note: all config options will override
    # any Pylons config options)
    nagios_engine = engine_from_config(config, 'sqlalchemy_nagios.')
    init_model(nagios_engine)
    acl_engine = engine_from_config(config, 'sqlalchemy_acl.')
    init_acl_model(acl_engine)
    
    handler_type = config['data_handler_type'].lower().strip()
    if handler_type in ['giisdb','giis_handler']:
        giisdb_engine = engine_from_config(config,'sqlalchemy_giisdb.')
        init_giisdb_model(giisdb_engine)

    sft_engine = engine_from_config(config, 'sqlalchemy_sft.')
    init_sft_model(sft_engine)


