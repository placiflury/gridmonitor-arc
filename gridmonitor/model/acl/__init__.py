from sqlalchemy import orm
import logging
from gridmonitor.model.acl import meta

log = logging.getLogger(__name__)

def init_acl_model(engine):
    """Call me before using any of the tables or classes in the model."""
    log.info("Setting up ACL DB model")
    sm = orm.sessionmaker(autoflush=False, transactional=False, bind=engine)

    meta.engine = engine
    meta.Session = orm.scoped_session(sm)
    

