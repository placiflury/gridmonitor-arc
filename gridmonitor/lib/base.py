"""The base Controller API

Provides the BaseController class for subclassing, and other objects
utilized by Controllers.
"""
import logging

from pylons import config,  request, session
from pylons.controllers import WSGIController
from pylons.templating import render_mako as render

from  pylons import app_globals as g

from hashlib import md5

from gridmonitor.lib.slcs import SLCS
import gridmonitor.lib.helpers as h
from gridmonitor.model.nagios import meta as nagios_meta
from gridmonitor.model.acl import meta as acl_meta
from gridmonitor.model.acl import handler
from sft.db import sft_meta


log = logging.getLogger(__name__)

class BaseController(WSGIController):

    requires_authN = True 
    requires_authZ = False

    def __before__(self):
        """ Try to get user identity (weak authN), which is basically
            given by his/her browser certificate and/or which is 
            given by  the certificate his/her online CA would have
            generated given the Shibboleth attributes the user presented.
            (notice, the shibboleth way is currently customized for the 
            Swiss AAI Federation only)"""

        if self.requires_authN and ('authenticated' not in session):

            user_name = 'Guest'
            user_surname = '' 
            home_org = None
            unique_id = None

            # 1. check whether Shibboleth enabled
            if request.environ.has_key(config['shib_given_name']):
                """
                user_name = unicode(request.environ[config['shib_given_name']], 'utf-8')
                user_surname = unicode(request.environ[config['shib_surname']], 'utf-8')
                home_org = unicode(request.environ[config['shib_home_org']], "utf-8")
                unique_id = unicode(request.environ[config['shib_unique_id']], "utf-8")
                """
                user_name = request.environ[config['shib_given_name']]
                user_surname = request.environ[config['shib_surname']]
                home_org = request.environ[config['shib_home_org']]
                unique_id = request.environ[config['shib_unique_id']]
                
                session['user_home_org'] = home_org
                session['user_unique_id'] = unique_id
                
                # online CA enabled (XXX currently only SWISS SLCS CA supported)
                if config['slcs_enabled'] in ['True', 'true']: # 
                    user_slcs_obj = SLCS(home_org, user_name, user_surname, unique_id)
                    session['user_slcs_obj'] = user_slcs_obj

            else: # go for browser certificate
                
                if request.environ.has_key('SSL_CLIENT_S_DN_CN'): #generating a unique_id 
                    #name = unicode(request.environ['SSL_CLIENT_S_DN_CN'], 'iso-8859-1')
                    name = request.environ['SSL_CLIENT_S_DN_CN']
                    if name:
                        name = name.strip().split()
                        if len(name) > 1: 
                            user_name = name[0]   # we drop other names
                            user_surname = name[-1]
                        else:
                            user_name = name
                    
                    
                if request.environ.has_key('SSL_CLIENT_S_DN_0'):
                    #org  = unicode(request.environ['SSL_CLIENT_S_DN_O'],'iso-8859-1')
                    org  = request.environ['SSL_CLIENT_S_DN_O']
                    if org:
                        session['user_home_org'] = org.strip()
            
                if request.environ.has_key('SSL_CLIENT_S_DN'): #generating a unique_id 
                    """
                    dn = unicode(request.environ['SSL_CLIENT_S_DN'],'iso-8859-1')
                    ca = unicode(request.environ['SSL_CLIENT_I_DN'],'iso-8859-1')
                    """
                    dn = request.environ['SSL_CLIENT_S_DN']
                    ca = request.environ['SSL_CLIENT_I_DN']
                    if dn and ca:
                        unique_id = md5(dn + ca).hexdigest()
                        session['user_unique_id'] = unique_id 

            session['user_name'] = user_name
            session['user_surname'] = user_surname
            
            
            # 2. get browser certificate details
            if request.environ.has_key('SSL_CLIENT_S_DN'):
                #user_client_dn = unicode(request.environ['SSL_CLIENT_S_DN'].strip(),'iso-8859-1')
                user_client_dn = request.environ['SSL_CLIENT_S_DN'].strip()
                # if emailaddress= within DN -> fix it
                cand = user_client_dn.split("emailAddress=")
                if len(cand) > 1:
                    session['user_client_dn'] = cand[0] + "Email=" + cand[1]
                else:
                    session['user_client_dn'] = user_client_dn

                session['user_client_ca'] = request.environ['SSL_CLIENT_I_DN'].strip()

            log.info("User %s authenticated" % session['user_name'])
            session['authenticated'] = True

            # 3. set navigation bar 
            session['top_nav_bar'] = self.__get_top_nav(unique_id)
            session.save()
            

    def __get_top_nav(self, unique_id=None):
        """ creates top navigation bar based on user's access permissions. """

        if not unique_id:
            return [('User','/user'),
                    ('VO/Grid Admin','/gridadmin'),
                    ('Help','/help')]

        monadmin_flag = False
        top_nav = [('User','/user')]
        
        db_session = acl_meta.Session()
        admins_pool = handler.AdminsPool(db_session)
        admin = admins_pool.show_admin(unique_id)        
        if admin: # siteadmin top bar 
            top_nav.append(('Site Admin','/siteadmin'))
            top_nav.append(('VO/Grid Admin', '/gridadmin'))
            for site in admin.sites:
                if site.name == 'GridMonitor' and site.alias == 'not_a_real_site':
                    top_nav.append(('Monitor Admin', '/monadmin'))
                    monadmin_flag = True
                    break
            if not monadmin_flag:
                for service in admin.services:
                    if service.name in ['ACL','SFT'] and service.site_name == 'GridMonitor': 
                        top_nav.append(('Monitor Admin', '/monadmin'))
                        break
        else:
            top_nav.append(('VO/Grid Admin', '/gridadmin'))
        top_nav.append(('Help','/help'))
            
        return top_nav
        
        


    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        try:
            return WSGIController.__call__(self, environ, start_response)
        finally: # make sure scoped sessions get removed...
            nagios_meta.Session.remove()
            acl_meta.Session.remove()
            sft_meta.Session.remove()
            

# Include the '_' function in the public names
__all__ = [__name for __name in locals().keys() if not __name.startswith('_') \
           or __name == '_']
