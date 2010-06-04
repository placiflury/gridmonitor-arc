"""
Dealing with cluster and cluster groups
"""

import logging
from sqlalchemy import orm
from gridmonitor.model.sft import sft_meta
from gridmonitor.model.sft import sft_schema as schema
class UserPool():
    
    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.log.debug("Initialization finished")
    

    def add_user(self,DN, pwd):
        user = sft_meta.Session.query(schema.User).filter_by(DN=DN).first()
        if user:
            self.log.info("User '%s' exists already" % DN)
        else:
            self.log.debug("Adding user '%s'." % DN)
            user = schema.User(DN,pwd)
            sft_meta.Session.save(user)
            sft_meta.Session.flush()
        sft_meta.Session.commit() 
        sft_meta.Session.clear() # -> make sure things get reloaded freshly


    def get_user_passwd(self,DN):
        user = sft_meta.Session.query(schema.User).filter_by(DN=DN).first()
        if user:
            try:
                passwd = user.get_passwd() 
            except Exception, e:
                passwd = None
                self.log.error("Could not fetch password of user '%s', got '%r'" 
                    % (DN,e))
            finally:
                return passwd
    
    def reset_user_passwd(self,DN,passwd):
        user = sft_meta.Session.query(schema.User).filter_by(DN=DN).first()
        if user:
            user.reset_passwd(passwd)
            sft_meta.Session.flush()
            sft_meta.Session.commit()
            sft_meta.Session.clear()

    def remove_user(self,DN):
        user = sft_meta.Session.query(schema.User).filter_by(DN=DN).first()
        if user:
            self.log.debug("Removing user '%s'." % DN)
            sft_meta.Session.delete(user)   
            sft_meta.Session.flush()
            sft_meta.Session.commit()
            sft_meta.Session.clear() # -> make sure things get reloaded freshly
    
