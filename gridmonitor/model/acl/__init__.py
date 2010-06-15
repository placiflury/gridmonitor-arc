from sqlalchemy import orm
import logging
from gridmonitor.model.acl import meta

log = logging.getLogger(__name__)

def init_acl_model(engine):
    """Call me before using any of the tables or classes in the model."""
    log.info("Setting up ACL DB model")
    meta.engine = engine
    sm = orm.sessionmaker(bind=engine)
    meta.Session = orm.scoped_session(sm)
    

