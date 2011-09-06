""" Nagios utils/helpers.  """

import logging
from datetime import datetime
import gridmonitor.lib.time_utils as tu

from gridmonitor.model.nagios import meta
from gridmonitor.model.nagios import hosttables
from gridmonitor.model.nagios import servicetables
from gridmonitor.model.nagios import scheduleddowntimes



log = logging.getLogger(__name__)

NAGIOS_CHECK_AGE_WARN = 1 # records older than 1 day
NAGIOS_CHECK_AGE_CRIT = 3 # records older than 3 days



def get_hostnames_from_group_tag(tag):
    """
    pass tag of nagios host group.
    returns list of hostnames for given tag
    """

    res = []

    query = meta.Session.query(hosttables.HostGroup)
    nagios_hgroup = query.filter_by(alias=tag).first()
    nagios_hgroup_members = None
    if nagios_hgroup:
        nagios_hgroup_members = nagios_hgroup.members
        log.debug("Found Nagios group %s (%d members)" % (tag, len(nagios_hgroup_members)))
    else:
        log.warn("No members of the nagios '%s' group found in mysql's ndoutils db." % tag)

    for mem in nagios_hgroup_members:
        res.append(mem.host.display_name)        

    return res

def get_nagios_host_services_from_group_tag(tag):
    """ 
    pass tag of nagios host group you would like to fetch
    returns list 
    XXX error handling 
    """ 
    res = []
     
    query = meta.Session.query(hosttables.HostGroup)
    nagios_hgroup = query.filter_by(alias=tag).first()
    nagios_hgroup_members = None
    if nagios_hgroup:
        nagios_hgroup_members = nagios_hgroup.members
        log.debug("Found Nagios group %s (%d members)" % (tag, len(nagios_hgroup_members)))
    else:
        log.warn("No members of the nagios '%s' group found in mysql's ndoutils db." % tag)

    for mem in nagios_hgroup_members:
        d = {}
        
        d['alias'] = mem.host.alias
        d['display_name'] = mem.host.display_name
        d['hoststatus_object'] = mem.host.status[0]  # 1-1 mapping expected 
        
        query = meta.Session.query(servicetables.Service)
        d['services_q'] = query.filter(servicetables.Service.host_object_id == mem.host_object_id).all()
        
        res.append(d)

    return res

def get_nagios_service_statuses(hostname, dates2utc = False):
    """ return the Nagios statuses of all
        services of a host (and host status itself). Format dictionary with service name  as key
        and status as value.

        dates2utc -- if set to True, dates are converted to utc time strings
    """
    services = {}

    host = meta.Session.query(hosttables.Host).filter_by(display_name = hostname).first() # yes 'display_name' ...
    if host:
        host_id = host.host_object_id
        if dates2utc:
            last_check = tu.datetime2utcstring(host.status[0].last_check)
        else:
            last_check = host.status[0].last_check

        services['host ping'] = dict(status = host.status[0].current_state, 
                        output = host.status[0].output, 
                        last_check = last_check)
        for service_obj in meta.Session.query(servicetables.Service).filter_by(host_object_id = host_id).all():
            if dates2utc:
                last_check = tu.datetime2utcstring(service_obj.status[0].last_check)
            else:
                last_check = service_obj.status[0].last_check

            services[service_obj.display_name] = dict(status = service_obj.status[0].current_state, 
                output = service_obj.status[0].output,
                perfdata = service_obj.status[0].perfdata,
                last_check = last_check)

    return  services
        

def get_nagios_scheduleddowntime_items(currently_down = False):
    """
    currently_down - if true only items that are right now (time)
                    scheduled to be down will be returned.

    returns host/services downtime object
    """
    ret = []
    
    query = meta.Session.query(scheduleddowntimes.ScheduledDownTime)
    scheduleditems = query.all()

    
    if currently_down:
        for it in scheduleditems:
            start_t = it.scheduled_start_time
            end_t = it.scheduled_end_time
            if datetime.now() > start_t and datetime.now() < end_t:
                ret.append(it)
        return ret
    else:
        if scheduleditems:
            return scheduleditems
        return ret



def get_nagios_summary( hostlist, dates2utc = False):
    """ returns a nagios summary for a given hostlist 
        (list of hostname DN).
        
        Warning:  - passed list will be modified
        
        dates2utc -- if set to True, dates are converted to utc time strings
    """

    host_summary = { 'up' : [],
                    'down' : [],
                    'scheduleddown': [],
                    'unknown': [] }

    nagios_code_map = { 0: 'ok',
                        1: 'warn',
                        2: 'critical',
                        3: 'unknown'}
    
    plugins_summary = {0 :{'cnt': 0, 'hs': []},
                     1 :  {'cnt': 0, 'hs': []},
                     2 : {'cnt': 0, 'hs': []},
                     3 : {'cnt': 0, 'hs': []}} # 0 -- ok, 1 -- warn, 2 -- critical, 3 -- unknown

    host_plugins_info = {} # {hostname : {plugin_name, output, date, perfdata}} 
                            # the '.' in the hostname and the will be substituted by the '-1-' sequence. 
                            # We do this  so the json.dump can be used by javascript functions...
   
    service_name_map={} # map to get valid javascript property names from 'service names' 

    for it in  get_nagios_scheduleddowntime_items(currently_down=True):
        hostname = it.generic_object.name1
        if hostname in hostlist:
            output = 'From: %s to %s (local time)' % \
                (it.scheduled_start_time, it.scheduled_end_time)

            host_summary['scheduleddown'].append(dict(hostname = hostname,
            output = output, date = None))

            hostlist.remove(hostname) 


    for hostname in hostlist:
        _hostname = hostname.replace('.','-1-')
        host_plugins_info[_hostname] = {}

        ngs = get_nagios_service_statuses(hostname)
                    
        # get host info 
        hstatus = ngs['host ping']['status']
        output = ngs['host ping']['output']
        last_check = ngs['host ping']['last_check']
        
        if start_epoch_time(last_check): # check did never run
            hptr = host_summary['unknown']         
        elif hstatus != 0:
            hptr = host_summary['down']
        else:    
            hptr =  host_summary['up']
        
        if dates2utc:
            last_check = tu.datetime2utcstring(last_check)

        hptr.append(dict(hostname = hostname, output = output, date = last_check))

        # get host services info
        service_names = ngs.keys()
        service_names.remove('host ping')
       
        for name in service_names: 
            _name = ''
            for p in name.split():
                _name += p + '_'
            if _name not in service_name_map.keys():
                service_name_map[_name] = name
 
            last_check = ngs[name]['last_check']
            status = ngs[name]['status']
            output = ngs[name]['output']
            perfdata = ngs[name]['perfdata']
            eff_status = 'unknown'

            if start_epoch_time(last_check): 
                plugins_summary[3]['cnt'] += 1
                plugins_summary[3]['hs'].append((_hostname, _name))
                eff_status = nagios_code_map[3]
            else:
                record_age = get_sqldatetime_age(last_check).days
                if record_age  >= NAGIOS_CHECK_AGE_CRIT:
                    plugins_summary[2]['cnt'] += 1
                    plugins_summary[2]['hs'].append((_hostname, _name))
                    eff_status = nagios_code_map[2]
                elif record_age >= NAGIOS_CHECK_AGE_WARN:
                    plugins_summary[1]['cnt'] += 1
                    plugins_summary[1]['hs'].append((_hostname, _name))
                    eff_status = nagios_code_map[1]
                else:
                    plugins_summary[status]['cnt'] += 1
                    plugins_summary[status]['hs'].append((_hostname, _name))
                    eff_status = nagios_code_map[status]

            if dates2utc:
                last_check = tu.datetime2utcstring(last_check)
            
            host_plugins_info[_hostname][_name] = dict(last_check = last_check, \
                    status = eff_status, output = output, perfdata = perfdata)


    # preparing to return things
    _plugins_summary = {'ok' : plugins_summary[0], 
                    'warn' : plugins_summary[1],
                    'critical': plugins_summary[2],
                    'unknown' : plugins_summary[3]}

    return dict( host_summary = host_summary, 
                plugins_summary = _plugins_summary,
                details = host_plugins_info,
                service_name_map = service_name_map)                    


def start_epoch_time(sqldatetime):
    """
    sqldatetime is of sqlalchemy.types.DateType
    """
    if sqldatetime == datetime(1970, 1, 1, 1):
        return True
    return False 

def get_sqldatetime_age(sqldatetime):
    """
    sqldatetime is of sqlalchemy.types.DateType
    returns datetime.timedelta object with time difference 
    from sqldatetime to current time (now).
    """ 
    return datetime.now() - sqldatetime

