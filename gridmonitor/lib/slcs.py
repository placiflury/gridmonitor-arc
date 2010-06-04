#!/usr/bin/env python
"""
Class for generating DN of SLCS certificate based
on the user's Shibboleth attributes

SWITCHaai specific
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
                "wsl.ch" : "O=Eidg. Forschungsanstalt fuer Wald Schnee und Landschaft (WSL)",
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

        home= self.__mapped_value(home_org)
        gname= given_name.split(SLCS.SHIB_DEL)[0]
        sname = surname.split(SLCS.SHIB_DEL)[0]
        

        # delimiter fo ; (multiple values) 
        self.dn = "/DC=ch/DC=switch/DC=slcs/%s/CN=%s %s %s" % \
            (home,
            self.filter_unicode_accentued_string(gname), 
            self.filter_unicode_accentued_string(sname), 
            self.__hash_value(unique_id))
         

    def get_dn(self):
        return self.dn

    def get_ca(self):
        return SLCS.CA
	
    def filter_unicode_accentued_string(self, ucode):
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
            elif code in [246]:
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
        # XXX fix it 
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
        homeorg= unicode(sys.argv[1],'utf-8')
        given_name = unicode(sys.argv[2],'utf-8')
        surname = unicode(sys.argv[3],'utf-8')
        uniqueid = unicode(sys.argv[4],'utf-8')
        slcs = SLCS(homeorg, given_name, surname, uniqueid)
        print slcs.get_dn()
    except SLCSError, e:
            print "Error: ", e.message
