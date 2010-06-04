"""Setup the GridMonitor application"""
import logging

from paste.deploy import appconfig
from pylons import config

from gridmonitor.config.environment import load_environment

log = logging.getLogger(__name__)

def setup_config(command, filename, section, vars):
    """Place any commands to setup gridmonitor here"""
    conf = appconfig('config:' + filename)
    load_environment(conf.global_conf, conf.local_conf)
    
    # Load the models
    from gridmonitor.model.acl import meta
    meta.acl_metadata.bind = meta.engine
    meta.acl_metadata.create_all(checkfirst=True)
    
    from gridmonitor.model.sft import sft_meta
    sft_meta.metadata.bind = sft_meta.engine
    sft_meta.metadata.create_all(checkfirst=True)
