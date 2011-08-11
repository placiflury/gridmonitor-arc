# time utility functions
import time
from datetime import datetime


def datetime2utcstring(dt, utc = True, strformat = None):
    """ Takes a datetime object and
        converts it to a human readeable
        time string.
        dt -- datetime object
        utc -- if true, utc time will be used,
               else local time.
        strformat -- strtime formating parameters
    """
    if not strformat:
        _format = "%d.%m.%Y - %H:%M:%S (UTC)"
    else:
        _format = strformat # no validity check!

    if not utc:
        return dt.strftime(_format)

    utc_struct_time = time.gmtime(time.mktime(dt.timetuple())) 
    utc_dt = datetime.fromtimestamp(time.mktime(utc_struct_time))
    return utc_dt.strftime(_format)
