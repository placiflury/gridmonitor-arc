"""
minimal set of fuct that a queue object needs to implement
"""

class QueueApi:

    def get_name(self):
        """ returns queue name """
        return None

    def get_cname(self):
        """ returns a 'cannonical' representation of the
            name of the queue. The cannonical name must 
            be allowed to be used within a URL.
        """
        return None

    def get_attribute_names(self):
        """ returns list with names of all (variables) attributes
            of the queue. """
        return []

    def get_attribute_values(self, attribute_name):
        return [] 

