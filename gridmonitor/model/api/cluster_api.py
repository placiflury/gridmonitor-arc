"""
minimal set of fuct that a cluster object needs to implement
"""

class ClusterApi:

    def get_name():
        """ Return name of cluster front-end node. Most likely 
            it's the hostname of the cluster front-end.
            The name of the cluster must be unique.
        """
        return None

    def get_alias():
        """ return  (an) alias name for the cluster """
        return None

    def get_attribute_names(self):
        """ returns list with names of all (variables) attributes
            of the cluster. """
        return []

    def get_attribute_values(self, attribute_name):
        return [] 

