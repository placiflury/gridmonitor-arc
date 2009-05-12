#!/usr/bin/env python
"""
Class for generating DN of SLCS certificate based
on the user's Shibboleth attributes
"""

class SLCS:
    CA = "/C=CH/O=Switch - Teleinformatikdienste fuer Lehre und Forschung/CN=SWITCHslcs CA"
    
    IdP_map = { "switch.ch" : "O=Switch - Teleinformatikdienste fuer Lehre und Forschung",
                "vho-switchaai.ch" : "OU=SWITCHaai Virtual Home Organization",
                "ethz.ch" : "O=ETH Zuerich",
                "epfl.ch" : "O=Ecole polytechnique federale de Lausanne (EPFL)",
                "unibas.ch" : "O=Universitaet Basel",
                "unibe.ch" : "O=Universitaet Bern",
                "unifr.ch" : "O=Universite de Fribourg",
                "unige.ch" : "O=Universite de Geneve",
                "unil.ch" : "O=Universite de Lausanne",
                "unilu.ch" : "O=Universitaet Luzern",
                "unine.ch" : "O=Universite de Neuchatel",
                "unisg.ch" : "O=Universitaet St. Gallen",
                "unisi.ch" : "O=Universita della Svizzera Italiana",
                "unizh.ch" : "O=Universitaet Zuerich",
                "uzh.ch" : "O=Universitaet Zuerich",
                "psi.ch" : "O=Paul-Scherrer-Institut (PSI)",
                "wsl.ch" : "O=Eidg. Forschungsanstalt fuer Wald, Schnee und Landschaft (WSL)",
                "hes-so.ch": "O=Haute Ecole Specialisee de Suisse occidentale (HES-SO)"
                }
    
    SHIB_DEL = ';'  # Delimiter for multi-value Shibboleth attributes

    def __init__(self,home_org, given_name, surname, unique_id):
        """
        params: 
            home_org - user's home organization (Shibboleth value)
            give_name - Shibboleth value of user's given name
            surname  - Shibboleth value of user's family name
            unique_id - Shibboleth unique ID of user
        """
        # delimiter fo ; (multiple values) 
        self.dn = "/DC=ch/DC=switch/DC=slcs/%s/CN=%s %s %s" % \
            (self.__mapped_value(home_org),
             given_name.split(SLCS.SHIB_DEL)[0], 
             surname.split(SLCS.SHIB_DEL)[0], 
            self.__hash_value(unique_id))
         

    def get_dn(self):
        return self.dn

    def get_ca(self):
        return SLCS.CA
        
    def __java_hash_code(self, input):
        """ Emulation of Java's hashCode() method. """
        h = 0
        max_int_32 = 2**32
        
        for i in range(0,len(input)):
            tmp = (31*h)
            c = ord(input[i])
            
            if tmp > (max_int_32 - 1 - c):
                tmp = tmp % max_int_32
            h = tmp + c                   
         
        return h

    def __hash_value (self, attribute):
        """ returns a hash value of the given attribute (string)"""
        
        hash_code = self.__java_hash_code(unicode(attribute))


        hash_value = '%08X' % hash_code # better than built-in hex()
        return hash_value

    def __mapped_value(self, home_org):
        if home_org in SLCS.IdP_map.keys():
            return SLCS.IdP_map[home_org]
        else:
            raise SLCSError("The home_org '%s' is not known (no mapping found) " % home_org)


    
class SLCSError(Exception):
    """ 
    Exception raised for SLCS class errors.
    Attributes:
        expression -- input expression in which error occurred
        message -- explanation of error 
    """
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message



if __name__ == "__main__":
    import sys
    try:
        slcs = SLCS(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
        print slcs.get_dn()
    except SLCSError, e:
            print "Error: ", e.message
