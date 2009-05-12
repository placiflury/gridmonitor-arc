class StatsApi:
    
    VALID_TYPES = ['grid','cluster','queue']

    def __init__(self,name,type):
        """ name -- name of container, e.g. cluster_name, queue_name
            type -- container type must be member of VALID_TYPES.
        """
        pass

    def get_name(self):
        """ returns name of container"""
        pass

    def get_type(self):
        """ returns type of container."""
        pass

    def get_children(self):
        """ returns list of children/sub-containers. The items of the list are
            as well NGStats objects.
        """
        pass

    def add_child(self):
        """ adding a child (i.e subcontainer) NGStats object. For a NGStats
            container that collects statistics of a a cluster (type= cluster), the
            children typically are the cluster's queues. For each queue you add 
            a NGStats object of type=queue to the cluster_obj. (just a tree).
        """
    
    def set_attribute(self,attribute_name,attribute_value):
        pass
    
    def get_attribute_names(self):
        """ returns list with names of attributes
            of the container. """
        pass

    def get_attribute(self,name):
        """ returns attribute value """
        pass

