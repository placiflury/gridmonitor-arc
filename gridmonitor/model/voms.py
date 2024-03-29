# query voms server for 
import logging, sys, os.path
from pylons import config
from os import environ
from gridmonitor.model.errors.voms import * 

log = logging.getLogger(__name__)


class VOMSConnector:
    """
    Connector to the VOMS server's wsdl/soap interface.
 
    VOMS Admin interface must be patched, so it does not exit
    upon a connection error (e.g. SSL error), but that it throws 
    an execption instead that can be caught.
    """

    def __init__(self, user_dn=None, ca=None):

        self.grid_security_path = None
        self.voms_servers = {}  # {vo: server_dns}
        self.voms_opts ={}
        self.voms_opts['vo'] = None
        self.voms_opts['port'] = 8443
        self.voms_opts['user_cert'] = '/etc/grid-security/hostcert.pem'
        self.voms_opts['user_key'] = '/etc/grid-security/hostkey.pem'

        self.user_dn = user_dn
        self.ca = ca
        self.__read_config()
        if self.__env_ok():
            log.debug("Basic environment for accessing VOMS servers looks ok.")
            self.__setup_identity()
        else:
            raise VOMS_ENV_ERROR("Environment Errror","Environment for accessing remote VOMS is faulty.")

    def __read_config(self):
        voms_raw = config['voms']
        if voms_raw:
            for voms in  voms_raw.split(','):
                server = voms.split(':')[0] 
                log.debug("VOMS server %s" % server)
                tail = voms.split(':')[1]
                for vo in tail.split('|'):
                    log.debug(" with VO: %s" % vo)
                    self.voms_servers[vo] = server.strip()  

    def __env_ok(self):
        """
        check whether environment is set up properly
        
        returns: 1 everything is fine
                0  something is missing or wrong
        """
        missing = {}
        log.debug("Checking environment...")

        self.grid_security_path = config['grid_security_path']
        if not self.grid_security_path:
             self.grid_security_path = environ.get("GRID_SECURITY_PATH", "/etc/grid-security");

        if not os.path.exists(self.grid_security_path):
            missing["GRID_SECURITY_PATH"] = self.grid_security_path

        self.glite_location = config['glite_location']

        if not self.glite_location:
            self.glite_location = environ.get("GLITE_LOCATION", "/opt/glite");
        if not os.path.exists(self.glite_location):
            missing["GLITE_LOCATION"] = self.glite_location

        if missing:
            for i in missing.keys():
                log.error( "Please set environment '$%s=%s' correctly or specify it in your pylons deployment file."\
                 % (i, missing[i]))
            return 0

        log.debug("Checking installation of security trust achors...")

        certdir = os.path.join(self.grid_security_path, "certificates")
        vomsdir = os.path.join(self.grid_security_path, "vomsdir")

        if not os.path.exists(certdir):
            log.error("Security anchor '%s' not installed (aborting)" % cerdir)
            return 0

        cert_location_default = os.path.join(self.grid_security_path, "hostcert.pem")

        cert_location = os.environ.get("X509_USER_CERT", cert_location_default)
        if not os.path.exists(cert_location):
            missing["X509_USER_CERT"] = cert_location

        if missing:
            for i in missing.keys():
                log.error("Please set environment '$%s=%s' correctly or specify it in your pylons deployment file.."\
                 % (i, missing[i]))
            return 0
        return 1

    def __setup_identity(self):
        
        hostkey = "/etc/grid-security/hostkey.pem"
        hostcert ="/etc/grid-security/hostcert.pem"

        user_id = os.geteuid()

        log.debug("Check whether user (%d) has credentials for accessing VOMS." % user_id)

        if os.path.exists(hostkey) and os.path.exists(hostcert):
            st = os.stat(hostkey)

        if st.st_uid == user_id:
            self.voms_opts['user_cert'] = hostcert
            self.voms_opts['user_key'] = hostkey
            log.debug("Using hostcertificate to connect to VOMSes")

        else:
            log.info("Hostkey '%s' not owned by process. Trying alternative certificates." % hostkey)
            ## look for a proxy
            proxy_fname = "/tmp/x509up_u%d" % user_id
            if os.path.exists(proxy_fname):
                log.debug("using proxy file found in %s" % proxy_fname)
                self.voms_opts['user_cert'] = proxy_fname
                self.voms_opts['user_key'] = proxy_fname


            ## look for a proxy in X509_USER_PROXY env variable
            elif os.environ.has_key("X509_USER_PROXY"):
                log.debug("using user credentials found in %s" % os.environ['X509_USER_PROXY'])
                self.voms_opts['user_cert'] = os.environ['X509_USER_PROXY']
                self.voms_opts['user_key'] = os.environ['X509_USER_PROXY']

            ## use common certificate
            elif os.environ.has_key("X509_USER_CERT"):
                log.debug("using user X509 certificate")
                self.voms_opts['user_cert'] = os.environ['X509_USER_CERT']
                self.voms_opts['user_key'] = os.environ['X509_USER_KEY']
            else:
                log.error("No (proxy) certificate found for accessing VOMS.")
                raise VOMS_ENV_ERROR("Environment Errror","No (proxy) certificate foud for accessing VOMS.")
   
    def get_voms_admin_proxy(self,vo):
        """ 
        returns communication endpoint (stub) to voms server 
        or None if communication endpoint not working
        """
        admin_module_path = os.path.join(self.glite_location,"share","voms-admin","client")
        sys.path.append(admin_module_path)
        from VOMSAdmin import VOMSCommands
    
        if self.voms_opts['vo'] == vo:
            pass
        else:
            self.voms_opts['vo'] = vo
            self.voms_opts['host'] = self.voms_servers[vo]

        admin_proxy = VOMSCommands.VOMSAdminProxy(**self.voms_opts)
        return admin_proxy
    
    def listUserGroups(self,vo):
        """ 
        returns all groups of user known by this VO 
        """
        try:
            admin = self.get_voms_admin_proxy(vo)
            return admin.admin.listUserGroups(self.user_dn, self.ca)
        except:
            return [] 


    def listUsers(self,vo):
        """
        returns all users of VO
        """
        try:
            admin = self.get_voms_admin_proxy(vo)
            return admin.listUsers()
        except:
            return [] 

 
    def listUserRoles(self,vo):
        """ 
        returns all roles of user known by this VO 
        """
        try: 
            admin = self.get_voms_admin_proxy(vo)
            return admin.admin.listUserRoles(self.user_dn, self.ca)
        except:
            return []

    def listUserAttributes(self,vo):
        """
        returns list of 'generic' attributes for this user and vo 
        """
        try:
            admin = self.get_voms_admin_proxy(vo)
            return admin.attributes.listUserAttributes(self.user_dn, self.ca)
        except:
            return []

    def get_vos(self):
        """ returns list of VO names that can be queried """
        return self.voms_servers.keys()

    def reset_dn_ca(self,user_dn,ca):
        self.user_dn = user_dn
        self.ca = ca
