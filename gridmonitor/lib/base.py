"""The base Controller API

Provides the BaseController class for subclassing, and other objects
utilized by Controllers.
"""
from pylons import c, cache, config, g, request, response, session
from pylons.controllers import WSGIController
from pylons.controllers.util import abort, etag_cache, redirect_to
from pylons.decorators import jsonify, validate
from pylons.i18n import _, ungettext, N_
from pylons.templating import render

from hashlib import md5

import gridmonitor.lib.helpers as h
import gridmonitor.model as model
from gridmonitor.model.nagios import meta as nagios_meta
from gridmonitor.model.acl import meta as acl_meta
from sft.db import sft_meta


import logging

log = logging.getLogger(__name__)


class BaseController(WSGIController):

    requires_authN = True 

    def __before__(self):
        """ Try to get user identity (weak authN), which is basically
            given by his/her browser certificate and/or which is 
            given by  the certificate his/her online CA would have
            generated given the Shibboleth attributes the user presented.
            (notice, the shibboleth way is currently customized for the 
            Swiss AAI Federation only)"""

        if self.requires_authN and ('authenticated' not in session):

            user_name = 'Guest'
            user_surname ='' 
            home_org = None
            unique_id = None

            # 1. check whether Shibboleth enabled
            if request.environ.has_key('shib_given_name'):
                user_name = unicode(request.environ[config['shib_given_name']], 'utf-8')
                user_surname = unicode(request.environ[config['shib_surname']], 'utf-8')
                home_org = unicode(request.environ[config['shib_home_org']], "utf-8")
                unique_id = unicode(request.environ[config['shib_unique_id']], "utf-8")
                
                session['user_home_org'] = home_org
                session['user_unique_id'] = unique_id
                
                # online CA enabled (XXX currently only SWISS SLCS CA supported)
                if config['slcs_enabled'] in ['True','true']: # 
                    user_slcs_obj = SLCS(home_org, user_name,user_surname,unique_id)
                    session['user_slcs_obj'] = user_slcs_obj

            else: # go for browser certificate
                
                if request.environ.has_key('SSL_CLIENT_S_DN_CN'): #generating a unique_id 
                    name = unicode(request.environ['SSL_CLIENT_S_DN_CN'], 'iso-8859-1')
                    if name:
                        name = name.strip().split()
                        if len(name) > 1: 
                            user_name = name[0]   # we drop other names
                            user_surname = name[-1]
                        else:
                            user_name = name
                    
                    
                if request.environ.has_key('SSL_CLIENT_S_DN_0'):
                    org  = unicode(request.environ['SSL_CLIENT_S_DN_O'],'iso-8859-1')
                    if org:
                        session['user_home_org'] = org.strip()
            
                if request.environ.has_key('SSL_CLIENT_S_DN'): #generating a unique_id 
                    dn = unicode(request.environ['SSL_CLIENT_S_DN'],'iso-8859-1')
                    ca = unicode(request.environ['SSL_CLIENT_I_DN'],'iso-8859-1')
                    if dn and ca:
                        session['user_unique_id'] = md5(dn + ca).hexdigest()

            session['user_name'] = user_name
            session['user_surname'] = user_surname
            
            
            # 2. get browser certificate details
            if request.environ.has_key('SSL_CLIENT_S_DN'):
                user_client_dn = unicode(request.environ['SSL_CLIENT_S_DN'].strip(),'iso-8859-1')
                # if emailaddress= within DN -> fix it
                cand = user_client_dn.split("emailAddress=")
                if len(cand) > 1:
                    session['user_client_dn'] = cand[0] + "Email=" + cand[1]
                else:
                    session['user_client_dn'] = user_client_dn

                session['user_client_ca'] = request.environ['SSL_CLIENT_I_DN'].strip()

            session['authenticated'] = True
            session.save()

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
