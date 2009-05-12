"""
minimal set of fuct that a job object needs to implement
"""

class JobApi:

    def get_jobname(self):
        """ returns job name """
        return None

    def get_globalid(self):
        """ returns global job id """
        pass

    def get_globalowner(self):
        pass

    def get_status(self):
        pass

    def get_exitcode(self):
        pass

    def get_cluster_name(self):
        pass

    def get_queue_name(self):
        pass
    
    def get_attribute_names(self):
        """ returns list with names of all (variables) attributes
            of the job. """
        return []

    def get_attribute_values(self, attribute_name):
        return [] 

