import sqlalchemy as sa
from sqlalchemy import orm

from gridmonitor.model.nagios import meta

def init_model(engine):
    """Call me before using any of the tables or classes in the model."""
    meta.engine = engine
    sm = orm.sessionmaker(bind=engine)
    meta.Session = orm.scoped_session(sm)
    

