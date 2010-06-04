from sqlalchemy import orm
from gridmonitor.model.giisdb import meta
import logging

log = logging.getLogger(__name__)

def init_giisdb_model(engine):
    """ Called before using any of the tables or classes in the model."""

    log.info("Setting up GIIS DB model")

    sm = orm.sessionmaker(autoflush=False,transactional=False,bind=engine)
    meta.engine = engine
    meta.Session = orm.scoped_session(sm)
