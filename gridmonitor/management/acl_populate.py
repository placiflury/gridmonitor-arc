#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module for manual population of ACL. 
"""
import sqlalchemy as sa
import sqlalchemy.orm as orm

# setting import path
#import sys
#sys.path.append( '/opt/GridMonitor') # XXX more general

from gridmonitor.model.acl.handler import * 
import gridmonitor.model.acl.meta as meta
import gridmonitor.model.acl.schema

if __name__ == '__main__':
    
    db = 'mysql://monuser:lap2ns@localhost/monitor'  # name of ACL DB
    
    engine = sa.create_engine(db)
    meta.metadata.bind = engine
    meta.metadata.create_all(checkfirst=True)
  
    Session = orm.sessionmaker(bind=engine)
    
    session = Session()
    
 
    # ADMINISTRATORS -- ADD/REMOVE
    admins = AdminsPool(session)
    admins.add_admin('828471@switch.ch', 'Usai','Alessandro','alessandro.usai@switch.ch')
    admins.add_admin('521780@switch.ch', 'Flury','Placi','placi.flury@switch.ch')
    admins.add_admin('596758@vho-switchaai.ch', 'Flury','Placi','flury@switch.ch')
    admins.add_admin('186988207178@unil.ch', 'Stockinger','Heinz','Heinz.Stockinger@unil.ch')
    admins.add_admin('jocasutt@unibe.ch','Casutt',u'Joël','joel.casutt@id.unibe.ch')
    admins.add_admin('d9a030e98708201905ee206bee9d691f@wsl.ch',u'Wüst','Thomas','thomas.wuest@wsl.ch')
    admins.add_admin('6D3130333832343601@uzh.ch','Packard','Michael','m1038246@access.uzh.ch')
    admins.add_admin('128552@epfl.ch','Jermini','Pascal','pascal.jermini@epfl.ch')
    admins.add_admin('103777@epfl.ch',u'Thiémard;Thiemard','Michela','michela.thiemard@epfl.ch')
    admins.add_admin('6D34303231303401@uzh.ch','Maffioletti','Sergio','m402104@access.uzh.ch')
    admins.add_admin('aesch@unibe.ch', 'Aeschlimann', 'Andres', 'andres.aeschlimann@id.unibe.ch')
    admins.add_admin('haug@unibe.ch','Haug','Sigve','sigve.haug@lhep.unibe.ch')
    admins.add_admin('vonbuere@unibe.ch',u'von Büren','Peter','peter.vonbueren@id.unibe.ch')
    
    sites = SitesPool(session)    
    sites.add_site('SWITCH')
    sites.add_site('UniBe')
    sites.add_site('GC3 UZH')
    sites.add_site('VITAL-IT')
    sites.add_site('WSL')
    sites.add_site('EPFL')
    sites.add_site('HESGE')
    sites.add_site('USI')
    sites.add_site('CSCS','CSCS T2')

   
    services = ServicesPool(session)
    # CE's
    services.add_service('CE','SWITCH','cluster','disir.switch.ch')
    services.add_service('CE','SWITCH','cluster','bacchus.switch.ch')
    services.add_service('CE','UniBe','cluster', 'nordugrid.unibe.ch')
    services.add_service('CE','UniBe', 'cluster','ce.lhep.unibe.ch')
    services.add_service('CE','GC3 UZH','cluster','idgc3grid01.uzh.ch')
    services.add_service('CE','GC3 UZH', 'cluster','ocikbpra.unizh.ch')
    services.add_service('CE','EPFL', 'cluster','smscg.epfl.ch')
    services.add_service('CE','VITAL-IT', 'cluster','globus.vital-it.ch')
    services.add_service('CE','WSL', 'cluster','hera.wsl.ch')
    services.add_service('CE','CSCS', 'cluster','arc01.lcg.cscs.ch')
    services.add_service('CE','CSCS', 'cluster','arc02.lcg.cscs.ch')
    services.add_service('CE','HESGE', 'cluster','arctest.hesge.ch')
    # Core Services
    services.add_service('VOMS','SWITCH','other','voms.smscg.ch')
    services.add_service('GIIS','SWITCH','other','giis.smscg.ch')
    services.add_service('VASH','SWITCH','other','vash.smscg.ch')
    services.add_service('RT','SWITCH','other','rt.smscg.ch')
    services.add_service('RT2','SWITCH','other','rt.smscg.ch')
    services.add_service('MONITOR','SWITCH','other','monitor.smscg.ch')
 
    # ACL
    sites.add_admin('SWITCH','521780@switch.ch') # placi
    sites.add_admin('SWITCH','596758@vho-switchaai.ch') # placi
    sites.add_admin('SWITCH','828471@switch.ch') # Ale
    sites.add_admin('GC3 UZH','521780@switch.ch') # placi
    sites.add_admin('UniBe','521780@switch.ch') # placi
    sites.add_admin('VITAL-IT','521780@switch.ch') # placi
    sites.add_admin('WSL','521780@switch.ch') # placi
    sites.add_admin('EPFL','521780@switch.ch') # placi
    sites.add_admin('UniBe','jocasutt@unibe.ch') # Joel
    sites.add_admin('UniBe','aesch@unibe.ch') # Res
    sites.add_admin('UniBe','vonbuere@unibe.ch') # Peter 
    sites.add_admin('UniBe','haug@unibe.ch') # Sigve
    sites.add_admin('GC3 UZH','6D34303231303401@uzh.ch') # Sergio
    sites.add_admin('GC3 UZH','6D3130333832343601@uzh.ch') # Mike
    sites.add_admin('VITAL-IT','186988207178@unil.ch') # Heinz
    sites.add_admin('WSL','d9a030e98708201905ee206bee9d691f@wsl.ch') #Thomas
    sites.add_admin('EPFL','128552@epfl.ch') # Pascal  
    sites.add_admin('EPFL','103777@epfl.ch') # Pascal  

    #services.add_admin('CE','disir.switch.ch','521780@switch.ch')
    services.add_admin('CE','arc01.lcg.cscs.ch','haug@unibe.ch') # Sigve
    services.add_admin('CE','arc02.lcg.cscs.ch','haug@unibe.ch') # Sigve

    # TESTS  
    """
    admins.add_admin('6D34303231303401@uzh.ch','Maffioletti','Sergio','m402104@access.uzh.c')
    admins.add_admin('6D34303231303401@uzh.ch','Maffioletti','Sergio','m402104@access.uzh.ch')
    
    sites.remove_site('CSCS')
    sites.add_site('CSCS','CSCS T2')
    
    admins.add_admin('fake','poi','muster','zyz@hoi.du')
    sites.add_admin('SWITCH','fake')
    services.add_admin('CE','disir.switch.ch','fake')
    admins.remove_admin('fake')

    services.remove_service('RT2','rt.smscg.ch')
    
    import gridmonitor.model.acl.schema as schema
    admin = session.query(schema.Admin).first()
    if admin:
        for site in admin.sites:
            print site.name 
            for service in site.services:
                print '\t', service.name, '(', service.type, ')', service.hostname
    """
