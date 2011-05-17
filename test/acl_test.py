#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test tool for ACL 
"""
import ConfigParser
import os.path

import sqlalchemy as sa
import sqlalchemy.orm as orm 

import sys


def list_admins(admins):   
    """ listing GridMonitor administrators """
    for admin in admins.list_admins():
        print " - unique_id=%s, surname=%s, given_name=%s, email=%s " % \
            (admin.shib_unique_id, admin.shib_surname, admin.shib_given_name, admin.shib_email)
    print '\n' 


def list_admin_sites(admins, uid):
    print "Sites of admin: %s" % uid
    for site in admins.list_admin_sites(uid):
        print '\t ', site.name

def list_admin_services(admins, uid):
    print "Services of admin: %s" % uid
    for svc in admins.list_admin_services(uid):
        print '\t ',  svc.name, svc.hostname, svc.type, svc.alias

def remove_admin(admins, unique_id):
    """ removing administrator from GridMonitor """

    if unique_id: 
        try:
            admins.remove_admin(unique_id) 
            print '...successfully removed user'
        except:
            print 'Error: could not remove admin'


def add_site(sites, name, alias):
    """ Adding a site """
    
    sites.add_site(name, alias)
    
    site_name = name.strip()
    site = sites.show_site(name)
    if not site:
        print 'insertion of site has failed'

    assert site.name == site_name, "inserted site name was not stripped: >%s< vs >%s<" % (site.name, site_name)
    if alias:
        assert site.alias == alias.strip(), "inserted site name was not stripped" 

def list_sites(sites):
    for site in sites.list_sites():
        print site.name, site.alias
    
def list_services(sites, site_name):
    for service in sites.list_services(site_name):
        print service.name, service.site_name, service.hostname, service.type


if __name__ == '__main__':
    
    from gridmonitor.model.acl.handler import * 
    from gridmonitor.model.acl import meta
    from logging.config import fileConfig
    
    cfg = '/opt/smscg/monitor/deploy.ini'   # GridMonitor configuration file
    fileConfig(cfg)

    if not os.path.exists(cfg):
        print "Error: path to '%s' doesn't exist! Please try again." % cfg
        sys.exit(1)
    if not os.path.isfile(cfg):
        print "Error: '%s' is not a file! Please try again." % cfg
        sys.exit(1)

    parser = ConfigParser.ConfigParser()
    parser.read(cfg)
    db = parser.get('app:main','sqlalchemy_acl.url').strip()
    valid_service_types = parser.get('app:main','acl_service_types').strip()
   
    print "Got db config '%s' from configuration file." % db  
    try:
        engine = sa.create_engine(db)
        meta.metadata.bind = engine
        meta.metadata.create_all(checkfirst=True)
      
        Session = orm.sessionmaker(bind=engine)
        session = Session()
    except Exception, e:
        print '\nError while creating engine: %r' % e
        sys.exit(1)


    # XXX start tests 

    # testing admins
    # add, update, show, list, list_sites, list_services, remove admin
    
    admins = AdminsPool(session)
    sites = SitesPool(session)
    services = ServicesPool(session)
    
    unique_ids = ['id1', '\t id2', '     id3 ', u'id4 ']
    surnames = ['flury', '\t tschopp', '     aesch ', u'usai  ']
    given_names = ['placi', '\t valery','   res ', u'ale  ']
    emails = ['placi@flury\n', '\t valery@tschopp','  res@aesch ', u'ale@usai   ']

    _sites = [ ('switchi', None),
            (' uzh    ', '    uniz    '),
            ('\tunibe\n', ' '),
            (u'epfl  ','EPFL')]

    _services = [ ('serv1', 'switchi ', 'CE', 'jp.test.ch', 'ali1'),
                ('  serv2   ', '    uzh', ' CE', '   ocikbr.test.ch ', None),
                ('serv3   ', '  unibe\t', 'VASH', ' ub.test.ch ', ' ' ),
                ('\tserv4   ', 'epfl', 'VOMS', ' ep.test.ch ', 'ali2')]

    
    # are things cleaned up?
    for uid in unique_ids:
        admins.remove_admin(uid) 
        admin = admins.show_admin(uid)
        if admin:
            print 'Error, admin %s has not been removed' % uid

    for name, alias in _sites:
        sites.remove_site(name)

    # ADMINS
    # add admins
    print "=> Adding admins <="
    for n in xrange(0, len(unique_ids)):
        admins.add_admin(unique_ids[n],
            surnames[n], 
            given_names[n],
            emails[n])

    # show admins
    print "=> Showing added admins <="
    for n in xrange(0, len(unique_ids)):
        admin = admins.show_admin(unique_ids[n])
        if not admin:
            print 'Error, admin %s was not inserted/could not be found.' % unique_ids[n]
    
        _uid = unique_ids[n].strip()
        _sn = surnames[n].strip() 
        _gn = given_names[n].strip()
        _em = emails[n].strip()
           
        assert admin.shib_unique_id == _uid, 'uids are not identical >%s< != >%s<' % (admin.shib_unique_id, _uid)
        assert admin.shib_surname == _sn, 'surnames are not identical'
        assert admin.shib_given_name == _gn, 'given names  are not identical'
        assert admin.shib_email == _em, 'emails are not identical'

    # update admins
    print "=> Updating admin %s <=" % unique_ids[0]

    _uid = unique_ids[0].strip()
    _surname = surnames[0] + 'up   '
    _given_name = given_names[0] + 'up '
    _email = emails[0] + 'up '

    _sn = _surname.strip() 
    _gn = _given_name.strip()
    _em = _email.strip()

    admins.update_admin(unique_ids[0], 
        _surname, _given_name, _email)

    # check update
    print "=> Checking updated amdin <="
    admin = admins.show_admin(unique_ids[0])
    assert admin.shib_unique_id == _uid, 'uids are not identical'
    assert admin.shib_surname == _sn, 'surnames are not identical'
    assert admin.shib_given_name == _gn, 'given names  are not identical'
    assert admin.shib_email == _em, 'emails are not identical'


    # listing admin
    list_admins(admins)
    
    # listing admin sites
    for uid in unique_ids:
        list_admin_sites(admins, uid)
    # listing admin services
    for uid in unique_ids:
        list_admin_services(admins, uid)


    # SITES
    
    # add sites
    print "=> Adding sites <="
    for name, alias in _sites:
        add_site(sites, name, alias)
    
    # list sites
    for site in sites.list_sites():
        print '\t', site.name, site.alias
        assert site.name == site.name.strip(), 'site name got not stripped properly'
        if site.alias:
            assert site.alias == site.alias.strip(), 'site alias got not stripped properly' 

    # list services
    for name, alias in _sites:
        print "=> listing services of site: %s <=" % name
        list_services(sites, name)

    # adding admins to site
    print "=> Adding admins to sites <="
    for uid in unique_ids:
        for name, alias in _sites:
            sites.add_admin(name,uid)
    
    # listing admin sites
    for uid in unique_ids:
        list_admin_sites(admins, uid)

    # listing site admins
    for name, alias in _sites:
        n = len(sites.list_admins(name))
        assert n == len(unique_ids), 'number of admins is not correct'


    # SERVICES

    print "=> Adding services <="
    for na, si, tp, host, alias in _services:
        services.add_service(na, si, tp, host, alias)

    # show services 
    print "=> Listing services <="
    for sv in services.list_services():
        print '\t', sv.name, sv.hostname, sv.site_name, sv.type, sv.alias

    for na, si, tp, host, alias in _services:
        sv = services.show_service(host)
        assert sv.name == sv.name.strip(), '%s was not stripped' % sv.name
        assert sv.hostname == sv.hostname.strip(), '%s was not stripped' % sv.hostname
        assert sv.site_name == sv.site_name.strip(), '%s was not stripped' % sv.site_name
    
    for name, alias in _sites:
        print "=> listing services of site: %s <=" % name
        list_services(sites, name)

    # listing admin services
    for uid in unique_ids:
        list_admin_services(admins, uid)
     
   
    # remove admin (from site) -> check if also removed from service

    ruid = unique_ids[0]
    print 'removing admin %s' % ruid
    admins.remove_admin(ruid)
    na = _services[0][0]
    host = _services[0][3]
    for admin in services.list_admins(na, host):
        print 'got admin %s' % admin.shib_given_name.strip()
        assert admin.shib_unique_id != ruid, 'removed admin still exists for services'
            
     
     


    # CLEAN UP 
    for uid in unique_ids:
        admins.remove_admin(uid) 
        admin = admins.show_admin(uid)
        if admin:
            print 'Error, admin %s has not been removed' % uid

    for name, alias in _sites:
        sites.remove_site(name)
   
    print "=> Listing services after clean-up <="
    for sv in services.list_services():
        print '\t', sv.name, sv.hostname, sv.site_name, sv.type, sv.alias


    print '=> cleaned up <=' 
    list_admins(admins)

    session.close()
        
