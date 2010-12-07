import sqlalchemy as sa
from sqlalchemy.orm import mapper, relationship

import meta

"""
The ACL database is used to protect some parts of the GridMonitor portal
from unauthorized access. 
If has primarily been designed for a Shibboleth environment (thus the 
naming of the table entries); this doesn't mean that the tables must 
be populated with Shibboleth entries. 
"""


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
    hostname: DNS entry where service is hosted // primary key
    site_name: name of site
    type: current values [CE | VOMS| VASH|...] -> used to build up cluster-list in controllers
    alias: an alias (optional) e.g. an DNS alias
"""
t_service = sa.Table("service", meta.metadata,
        sa.Column("name", sa.types.VARCHAR(128), primary_key=True, nullable=False),
        sa.Column("hostname", sa.types.VARCHAR(128), primary_key=True, nullable=False),
        sa.Column("site_name", None, sa.ForeignKey("site.name"), nullable=False),        
        sa.Column("type", sa.types.VARCHAR(64), nullable=False),
        sa.Column("alias", sa.types.VARCHAR(128))
)

t_admin = sa.Table("admin", meta.metadata,
        sa.Column("shib_unique_id", sa.types.VARCHAR(255), primary_key=True, nullable=False),
        sa.Column("shib_surname", sa.types.VARCHAR(255), nullable=False),
        sa.Column("shib_given_name", sa.types.VARCHAR(255), nullable=False),
        sa.Column("shib_email", sa.types.VARCHAR(255), nullable=False))

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

    
    def __init__(self, name, site_name, type,
        hostname, alias = None):    
     
        self.name = name
        self.hostname = hostname
        self.site_name = site_name
        self.type = type
        self.alias = alias
        
class Admin(object):

    def __init__(self, unique_id,
       surname,
       given_name,
       email):
        self.shib_unique_id = unique_id
        self.shib_surname = surname
        self.shib_given_name = given_name
        self.shib_email = email

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
        admins = relationship(Admin,
        secondary = t_site_acl,
        primaryjoin = t_site.c.name == t_site_acl.c.site_name,
        secondaryjoin = t_site_acl.c.admin_id == t_admin.c.shib_unique_id,
         backref='sites'),
        services = relationship(Service, backref='site'))
)

mapper(Service, t_service,
        properties = dict(
        admins = relationship(Admin,
        secondary = t_service_acl,
        primaryjoin = sa.and_(t_service.c.name == t_service_acl.c.service_name,
            t_service.c.hostname == t_service_acl.c.hostname),
        secondaryjoin = t_service_acl.c.admin_id == t_admin.c.shib_unique_id,
        backref = 'services'))
)
