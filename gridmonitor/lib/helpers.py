"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to both as 'h'.
"""
import logging

import urllib

from datetime import datetime

from webhelpers.html.tags import link_to
from routes.util import url_for # used in subsequent modules, don't remove

# XXX use API def instead
from infocache.db import meta as info_meta
from infocache.db import schema as info_schema


from nagios_utils import get_nagios_scheduleddowntime_items

log = logging.getLogger(__name__)

def get_cluster_names(state):
    """ returns list of hostnames of clusters in given state and 
                optionally metadata dictionary 

        Valid states are:
        inactive -- inactive cluster(s), that is the information system has
                    lost track of cluster(s) *and* cluster did not schedule
                    a downtime
        downtime -- a downtime has been scheduled for cluster(s) (active now!!)
        active -- active cluster (no downtime and not inactive)

        Notice, higher level logic shall deal with intersection of 
                cluster states e.g. inactive + scheduled downtime state
    """
        
    hostnames = []
    metadata = {}
    
    if state in ['inactive', 'active']:
        down_clusters = get_cluster_names('downtime')[0]
        for cl in info_meta.Session.query(info_schema.NGCluster).filter_by(status = state).all():
            if (cl.hostname not in down_clusters):
                hostnames.append(cl.hostname)
                metadata[cl.hostname] = dict(alias = cl.alias, db_lastmodified = cl.db_lastmodified)
    elif state == 'downtime':
        now_scheduled_down = []
        for it in get_nagios_scheduleddowntime_items(currently_down = True):
            hostname = it.generic_object.name1
            if (hostname not in hostnames):
                metadata[hostname] = dict( start_t = it.scheduled_start_time, \
                        end_t = it.scheduled_end_time)
                hostnames.append(hostname)
        

    log.debug("clusters (state: %s)  %r " % (state, hostnames))
    hostnames.sort()
    return hostnames, metadata
             


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
        return link_to(label, url)
    else:
        return link_to(url, url)
        
   
def format_environ(environ):
    result = []
    keys = environ.keys()
    keys.sort()
    for key in keys:
        result.append("%s: %r" %(key, environ[key]))
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
        if code in [192, 193, 194, 195, 197]:
            str += 'A'
        elif code == 196:
            str += 'Ae'
        elif code == 198:
            str += 'AE'
        elif code == 199:
            str += 'C'
        elif code in [200, 201, 202, 203]:
            str += 'E'
        elif code in [204, 205, 206, 207]:
            str += 'I'
        elif code == 209:
            str += 'N'
        elif code in [210, 211, 212, 213, 216]:
            str += 'O'
        elif code == 214:
            str += 'Oe'
        elif code in [217, 218, 219]:
            str += 'U'
        elif code == 220:
            str += 'Ue'
        elif code == 221:
            str += 'Y'
        elif code == 223:
            str += 'ss'
        elif code in [224, 225, 226, 227, 229]:
            str += 'a'
        elif code in [228, 230]:
            str += 'ae'
        elif code == 231:
            str += 'c'
        elif code in [232, 233, 234, 235]:
            str += 'e'
        elif code in [236, 237, 238, 239]:
            str += 'i'
        elif code == 241:
            str += 'n'
        elif code in [242, 243, 244, 245, 248]:
            str += 'o'
        elif code == 246:
            str += 'oe'
        elif code in [249, 250, 251]:
            str += 'u'
        elif code == 252:
            str += 'ue'
        elif code in [253, 255]:
            str += 'y'
        else:
            str += c 
    return str
