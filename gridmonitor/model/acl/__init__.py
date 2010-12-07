from sqlalchemy import orm
import logging

import meta, schema, handler, errors  # from gridmonitor.model.acl

log = logging.getLogger(__name__)

def init_acl_model(engine):
    """Call me before using any of the tables or classes in the model."""
    log.info("Setting up ACL DB model")
    meta.engine = engine 
    meta.metadata.bind = engine
    
    sm = orm.sessionmaker(bind=engine)
    meta.Session = orm.scoped_session(sm)
    

