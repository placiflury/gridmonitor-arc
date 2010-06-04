import sqlalchemy as sa
from sqlalchemy.orm import mapper, relation
from gridmonitor.model.acl import meta

"""
site table:
    name: name of the site
    alias: alias for site name (optional)
"""
t_site = sa.Table("site", meta.metadata,
        sa.Column("name", sa.types.VARCHAR(128), primary_key=True),
        sa.Column("alias", sa.types.VARCHAR(128))
)

"""
service table:
    name: e.g. cluster name, VOMS, VASH, etc. // primary key
    hostname: dns entry where service is hosted // primary key
    site_name: name of site
    type: current values [cluster|other]
    alias: an alias (optional)
"""
t_service = sa.Table("service", meta.metadata,
        sa.Column("name", sa.types.VARCHAR(128), primary_key=True),
        sa.Column("hostname", sa.types.VARCHAR(128), primary_key=True),
        sa.Column("site_name", None, sa.ForeignKey("site.name"), nullable=False),        
        sa.Column("type", sa.types.VARCHAR(64), nullable=False),
        sa.Column("alias", sa.types.VARCHAR(128))
)

t_admin = sa.Table("admin", meta.metadata,
        sa.Column("shib_unique_id", sa.types.VARCHAR(255), primary_key=True),
        sa.Column("shib_surname", sa.types.VARCHAR(255), nullable=False),
        sa.Column("shib_given_name", sa.types.VARCHAR(255), nullable=False),
        sa.Column("shib_email", sa.types.VARCHAR(255), nullable=False),
        sa.Column("shib_affiliation", sa.types.VARCHAR(255)),
        sa.Column("shib_homeorg", sa.types.VARCHAR(255))
)

t_service_acl = sa.Table("service_acl", meta.metadata,
        sa.Column("id", sa.types.Integer, primary_key=True),
        sa.Column("service_name", None, sa.ForeignKey("service.name")),
        sa.Column("hostname", None, sa.ForeignKey("service.hostname")),
        sa.Column("admin_id", None, sa.ForeignKey("admin.shib_unique_id"))        
)

t_site_acl = sa.Table("site_acl", meta.metadata,
        sa.Column("id", sa.types.Integer, primary_key=True),
        sa.Column("site_name", None, sa.ForeignKey("site.name")),
        sa.Column("admin_id", None, sa.ForeignKey("admin.shib_unique_id"))        
)

class Site(object):

    def __init__(self, name, alias=None):
        self.name = name
        self.alias = alias

class Service(object):

    VALID_TYPES = ['cluster','other']
    
    def __init__(self, name, site_name, type,
        hostname, alias = None):    
        
        if type not in Service.VALID_TYPES:
            # XXX raising exception instead
            type = 'other'
        self.name = name
        self.hostname = hostname
        self.site_name = site_name
        self.type = type
        self.alias = alias
        
class Admin(object):

    def __init__(self, shib_unique_id,
        shib_surname,
        shib_given_name,
        shib_email,
        shib_affiliation = None,
        shib_homeorg = None):
        
        self.shib_unique_id = shib_unique_id
        self.shib_surname = shib_surname
        self.shib_given_name = shib_given_name
        self.shib_email = shib_email
        self.shib_affiliation = shib_affiliation 
        self.shib_homeorg = shib_homeorg

class SiteACL(object):
    pass

class ServiceACL(object):
    pass 

# 1:1 mappings
mapper(Admin, t_admin)
mapper(SiteACL, t_site_acl)
mapper(ServiceACL, t_service_acl)

# N:M mappings
mapper(Site, t_site,
    properties = dict(
        admins = relation(Admin,
        secondary = t_site_acl,
        primaryjoin = t_site.c.name == t_site_acl.c.site_name,
        secondaryjoin = t_site_acl.c.admin_id == t_admin.c.shib_unique_id,
         backref='sites'),
        services = relation(Service, backref='site'))
)

mapper(Service, t_service,
        properties = dict(
        admins = relation(Admin,
        secondary = t_service_acl,
        primaryjoin = sa.and_(t_service.c.name == t_service_acl.c.service_name,
            t_service.c.hostname == t_service_acl.c.hostname),
        secondaryjoin = t_service_acl.c.admin_id == t_admin.c.shib_unique_id,
        backref = 'services'))
)
