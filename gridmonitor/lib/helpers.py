"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to both as 'h'.
"""
from webhelpers import *

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
    
        
