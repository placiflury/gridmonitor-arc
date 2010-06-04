from  sqlalchemy import orm
from  gridmonitor.model.sft import sft_meta
import logging

log = logging.getLogger(__name__)

def init_sft_model(engine):
    """ Call me before using any of the tables or classes in the model """
    
    log.info("Setting up DB model for Site Functional Tests (SFTs)")
    sm = orm.sessionmaker(autoflush=True, transactional=True, bind=engine)
    sft_meta.engine = engine
    sft_meta.Session = orm.scoped_session(sm)

