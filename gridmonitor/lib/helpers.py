"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to both as 'h'.
"""
import logging
import urllib, datetime

from webhelpers import *
from gridmonitor.model.nagios import meta
from gridmonitor.model.nagios import hosttables
from gridmonitor.model.nagios import servicetables
from gridmonitor.model.nagios import scheduleddowntimes
from routes.util import url_for # used in subsequent modules, don't remove



log = logging.getLogger(__name__)

def get_nagios_host_services_from_group_tag(tag):
    """ 
    pass tag of nagios host group you would like to fetch
    returns list 
    XXX error handling 
    """ 
    res = []
     
    query = meta.Session.query(hosttables.HostGroup)
    nagios_hgroup = query.filter_by(alias=tag).first()
    nagios__hgroup_members = None
    if nagios_hgroup:
        nagios_hgroup_members = nagios_hgroup.members
        log.debug("Found Nagios group %s (%d members)" % (tag,len(nagios_hgroup_members)))
    else:
        log.warn("No members of the nagios '%s' group found in mysql's ndoutils db." % tag)

    for mem in nagios_hgroup_members:
        d={}
        host_object_id = mem.host_object_id
        alias = mem.host.alias
        display_name = mem.host.display_name
        d['alias'] = alias
        d['display_name'] = display_name
        d['hoststatus_object'] = mem.host.status[0]  # 1-1 mapping expected 
        query = meta.Session.query(servicetables.Service)
        d['services_q'] = query.filter(servicetables.Service.host_object_id == host_object_id).all()
        res.append(d)

    return res

def get_nagios_scheduleddowntime_items():
    """
    returns host/services downtime object
    """
    query = meta.Session.query(scheduleddowntimes.ScheduledDownTime)
    scheduleditems = query.all()

    if scheduleditems:
        return scheduleditems
    return None

             
def is_epoch_time(sqldatetime):
    """
    sqldatetime is of sqlalchemy.types.DateType
    """
    if sqldatetime == datetime.datetime(1970,1,1,1):
        return True
    return False 

def get_sqldatetime_age(sqldatetime):
    """
    sqldatetime is of sqlalchemy.types.DateType
    returns datetime.timedelta object with time difference 
    from sqldatetime to current time (now).
    """ 
    return datetime.datetime.now() - sqldatetime


def str_cannonize(str):
   """ Input string with spaces and/or mixed upper and lower 
       characters will be converted to a cannonical form, 
       i.e. all to lowercase and spaces replaced by a '_'.

       Return  new cannonical string
   """
   if not str:
	return None

   tmp = str.split()  # intention is to replace multiple whitespaces by a single '_'
   new_str = ""
   for i in range(0,len(tmp) -1):
      	new_str += tmp[i] + "_"
	
   new_str += tmp[-1]  
   return new_str


def link(url, label=None):
    """ return link termed 'label' or if no label has been specified,
        the link will be named after the url.
    """
    if label:
        return "<a href=\"%s\">%s</a>" % (url,label)
    else:
        return "<a href=\"%s\">%s</a>" % (url,url)
        
	
   
def format_environ(environ):
    result = []
    keys = environ.keys()
    keys.sort()
    for key in keys:
        result.append("%s: %r" %(key,environ[key]))
    return '\n'.join(result)   
 
def list2string(l):
    """ returns a comma-separated string of the list items."""
    res = ''
    if type(l) == list:
        for item in l:
            if not res:
                res = str(item)
            else:
                res = res + "," + str(item) 
    return res

def quote_plus(str):
    return urllib.quote_plus(str) 

def unquote_plus(str):
    return urllib.unquote_plus(str)

 
def filter_unicode_accentued_string(ucode):
    """
    Converts unicode to Latin-1 and converts accentued chars into their unaccentued equivalent
      
    192 => 'A', 193 => 'A', 194 => 'A', 195 => 'A', 196 => 'Ae', 197 => 'A',
    198 => 'AE', 199 => 'C', 200 => 'E', 201 => 'E', 202 => 'E', 203 => 'E',
    204 => 'I', 205 => 'I', 206 => 'I', 207 => 'I', 209 => 'N', 210 => 'O',
    211 => 'O', 212 => 'O', 213 => 'O', 214 => 'Oe', 216 => 'O', 217 => 'U',
    218 => 'U', 219 => 'U', 220 => 'Ue', 221 => 'Y', 223 => 'ss', 224 => 'a',
    225 => 'a', 226 => 'a', 227 => 'a', 228 => 'ae', 229 => 'a', 230 => 'ae',
    231 => 'c', 232 => 'e', 233 => 'e', 234 => 'e', 235 => 'e', 236 => 'i',
    237 => 'i', 238 => 'i', 239 => 'i', 241 => 'n', 242 => 'o', 243 => 'o',
    244 => 'o', 245 => 'o', 246 => 'oe', 248 => 'o', 249 => 'u', 250 => 'u',
    251 => 'u', 252 => 'ue', 253 => 'y', 255 => 'y'
    """
    if not ucode:
        return None

    str= ''
    for c in ucode.encode('Latin-1'):
        code = ord(c)
        if code in [192,193,194,195,197]:
            str+='A'
        elif code == 196:
            str+='Ae'
        elif code == 198:
            str+='AE'
        elif code == 199:
            str+='C'
        elif code in [200,201,202,203]:
            str+='E'
        elif code in [204,205,206,207]:
            str+='I'
        elif code == 209:
            str+='N'
        elif code in [210,211,212,213,216]:
            str+='O'
        elif code == 214:
            str+='Oe'
        elif code in [217,218,219]:
            str+='U'
        elif code == 220:
            str+='Ue'
        elif code == 221:
            str+='Y'
        elif code == 223:
            str+='ss'
        elif code in [224,225,226,227,229]:
            str+='a'
        elif code in [228,230]:
            str+='ae'
        elif code == 231:
            str+='c'
        elif code in [232,233,234,235]:
            str+='e'
        elif code in [236,237,238,239]:
            str+='i'
        elif code == 241:
            str+='n'
        elif code in [242,243,244,245,248]:
            str+='o'
        elif code == 246:
            str+='oe'
        elif code in [249,250,251]:
            str+='u'
        elif code == 252:
            str+='ue'
        elif code in [253,255]:
            str+='y'
        else:
            str+=c 
    return str
