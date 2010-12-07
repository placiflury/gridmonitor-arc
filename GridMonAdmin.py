#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Administration tool for the creation/deletion of the 
administrators of the GridMonitor portal. 

Terminololgy: An administrator of the GridMonitor portal 
    has the rights and responsibility to manage the ACL
    of the GridMonitor portal.

This small tool is used to create the 'super admin', i.e.
the very first admin of the portal. Subsequent editing of
the GridPortal ACLs should be done via the portal itself
(see /monadmin tab of portal)


The GridMonitor portal can be operated as an AAI (shibboleth)
service or just as a plain portal. 

In the AAI case authentication and authorization will be based
on AAI attributes. You'll be asked to provide the following 
Shibboleth attributes for creating the very first administrator:

    shib_unique_id=
    shib_surname=
    shib_given_name= 
    shib_email=
     
In case of a non-AAI GridMonitor portal you will need to provide 
the following entries to create the very first administrator:

    X509_DN = 
    X509_CA = 
    surname = 
    given_name = 
    email = 

Notice, the surname, given_name and email are fully decoupled from
the  X509 certificate (so if your cert has not any email in it, 
don't worry). 

"""
import ConfigParser
import os.path
from hashlib import md5
from socket import gethostname

import sqlalchemy as sa
import sqlalchemy.orm as orm 

import sys

def get_input(msg):
    """ Sames as raw_input + stripping of whitespaces, ' (quotes) 
        and " (double quotes) """
    raw = raw_input(msg)
    if raw:
        return raw.strip().strip("'").strip('"')
    return raw
 


def add_admin(session):
    """ Adding a super administrator. """
    
    aai = get_input("Do you have an AAI enabled GridMonitor portal[N/y]:").lower()
    if not aai or  aai != 'y':
        aai_enabled= False
    else:
        aai_enabled = True
        
    if aai_enabled:
        while True:
            unique_id =  get_input("Please enter AAI unique ID:")
            if not unique_id:
                print 'Error: unique_id is missing'
                continue
            surname =  get_input("Please enter AAI surname:")
            if not surname:
                print 'Error: surname is missing'
                continue
            given_name =  get_input("Please enter AAI given name:")
            if not given_name:
                print 'Error: given name is missing'
                continue
            email =  get_input("Please enter AAI email:")
            if not email:
                print 'Error: email is missing'
                continue
            print "You defined the following  super administrator will be entered:\n"
            print "unique_id=%s" % unique_id
            print "surname=%s" % surname
            print "given_name=%s" % given_name
            print "email=%s" % email
            
            cont = get_input("Do you want to continue[Y/n]:").lower()
            if cont and cont != 'y':
                print 'Not entering any user'
                return True
            
            break 
    else:
        while True:
            DN = get_input("Please enter user DN:")
            if not DN:
                print "Error: DN is missing"
                continue
            CA = get_input("Please enter issueing CA:")
            if not CA:
                print "Error: CA is missing"
                continue
            surname =  get_input("Please enter surname:")
            if not surname:
                print 'Error: surname is missing'
                continue
            given_name =  get_input("Please enter given name:")
            if not given_name:
                print 'Error: given name is missing'
                continue
            email =  get_input("Please enter email:")
            if not email:
                print 'Error: email is missing'
                continue
            
            print "You defined the following  super administrator will be entered:\n"
            print "DN=%s" % DN
            print "CA=%s" % CA
            print "surname=%s" % surname
            print "given_name=%s" % given_name
            print "email=%s" % email
            unique_id = md5(DN+CA).hexdigest()
            print "\n The super administrator will have the following unique_id '%s'" % unique_id

            cont = get_input("Do you want to continue[Y/n]:").lower()
            if cont and cont != 'y':
                print 'Not entering any user'
                return True
            break

    admins = AdminsPool(session)
    print 'inserting  super admin ...'
    admins.add_admin(unique_id, surname, given_name, email)
    sites = SitesPool(session)    
    sites.add_site('GridMonitor','not_a_real_site')
    hostname = gethostname()
    services = ServicesPool(session, valid_service_types)
    services.add_service('ACL','GridMonitor','MONITOR', hostname)
    services.add_service('SFT','GridMonitor','MONITOR', hostname)
    sites.add_admin('GridMonitor', unique_id) 
    print '... successfully inserted.'

    return True


def list_admins(session):   
    """ listing GridMonitor administrators """
    admins = AdminsPool(session)
    print '\n', 10 * '-', 'Listing of existing users:', 10 * '-', '\n'
    for admin in admins.list_admins():
        print " - unique_id=%s, surname=%s, given_name=%s, email=%s " % \
            (admin.shib_unique_id, admin.shib_surname, admin.shib_given_name, admin.shib_email)
    print '\n' 


def remove_admin(session):
    """ removing administrator from GridMonitor """
    cont = get_input("Do you want to remove one[Y/n]:").lower()
    if cont and cont != 'y':
        print 'Canceling...',
        return True
    
    unique_id = get_input("Please enter unique_id of user to remove:")
    admins = AdminsPool(session)

    if unique_id: # XXX one could add a check whether unique_id is a valid one
        try:
            admins.remove_admin(unique_id) 
            print '...successfully removed user'
        except:
            print 'Error: could not remove admin'

if __name__ == '__main__':
    
    from gridmonitor.model.acl.handler import * 
    from gridmonitor.model.acl import meta
    
   
    print 10* '=' + ' WELCOME TO THE ADMIN TOOL OF THE GRIDMONITOR ' + 10 * '=' + '\n'
    print '  This tool will guide you through the creation of the top '
    print '  adminstrator of the GridMonitor portal (the super admin).'
    print '  Once the super admin has been created, she/he can add  '
    print '  other (super) admins via the GridMonitor portal interface.'
    print '  We therefore recommend to use this script only for the ' 
    print '  creation of the very first admin. \n'

    cont = get_input("Do you want to continue[Y/n]:").lower()
    
    if cont and cont != 'y':
        print 'bye!'
        sys.exit(0)
  
    while True:
        config_file = '/opt/smscg/monitor/deploy.ini'   # GridMonitor configuration file
        config = get_input("Enter path to config file of GridMonitor [%s]:" % (config_file))
  
        if not config:
            cfg = config_file
        else:
            cfg = config.strip()
         
        if not os.path.exists(cfg):
            print "Error: path to '%s' doesn't exist! Please try again." % cfg
            continue
        if not os.path.isfile(cfg):
            print "Error: '%s' is not a file! Please try again." % cfg
            continue
        break

    parser = ConfigParser.ConfigParser()
    parser.read(cfg)
    parser.read(config_file)
    db = parser.get('app:main','sqlalchemy_acl.url').strip()
    valid_service_types = parser.get('app:main','acl_service_types').strip()
   
    print "Got db config '%s' from configuration file." % db  
    print "Trying to get engine to db",
    try:
        engine = sa.create_engine(db)
        meta.metadata.bind = engine
        meta.metadata.create_all(checkfirst=True)
      
        Session = orm.sessionmaker(bind=engine)
        session = Session()
    except Exception, e:
        print '\nError while creating engine: %r' % e
        sys.exit(-1)
    print '... got it'


    while True:
        action = get_input("Do you want to add or remove an admin[A(dd)/R(emove)/L(ist)/Q(uit)]:")
        
        if action.lower() == 'a': # add user
            add_admin(session)
            continue
        elif action.lower() == 'r' : # remove user
            print '\nActual users:',
            list_admins(session)
            remove_admin(session)
            print '\nNew list of users:',
            list_admins(session)
            continue
        elif action.lower() == 'l': # list users
            list_admins(session)
            continue
        elif action.lower() == 'q': # qui
            session.close()
            print 'bye!'
            break
        else:
            print "Error: '%s' isn't a valid choice" % action
        
