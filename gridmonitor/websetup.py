"""Setup the GridMonitor application"""
import logging

from paste.deploy import appconfig

from gridmonitor.config.environment import load_environment

from sft.db import sft_meta
from gridmonitor.model.acl import meta as acl_meta

log = logging.getLogger(__name__)

def setup_config(command, filename, section, vars):
    """Place any commands to setup gridmonitor here"""
    conf = appconfig('config:' + filename)
    load_environment(conf.global_conf, conf.local_conf)
    
    # Load (create)  the models
    acl_meta.metadata.create_all(bind=acl_meta.engine)
    sft_meta.metadata.create_all(bind=sft_meta.engine)
