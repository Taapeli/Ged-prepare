'''
Created on 22.11.2016

@author: jm
'''

import re

class PersonName(object):
    '''
    Contains Gedcom individual name information from tags:
    - NAME typically 'givn/surn/spfx'
    - GIVN
    - SURN
    - SPFX
    - _CALL
    '''
    NONAME = 'N'            # Marker for missing name part
    CHGTAG = "NOTE orig_"   # Comment: original format
    
    RE_UNNAMED = ['nimetön', 'tuntematon', 'N.N.']
    RE_PATRON = ['poika', 'p.', 'sson', 'ss.', 's.',
                 'tytär', 'dotter', 'dr.', ]
    RE_VON = ['von', 'af', 'de la', 'de']
    RE_LYH = ['os.', 'o.s.', 'ent.','e.']
    RE_SURN = {'os.':'MARR', 'o.s.':'MARR', 'ent.':'BORN', 'e.':'BORN'}

    def __init__(self):
        # Create a new instance
        #print ("# person_name.__init__()")           
        self.rows = []


    def __str__(self):
        return "PersonName({})".format(self.get_name())

    def appendRow(self, level, tag, value):
        # Store a new row
        self.rows.append("{} {} {}".format(level, tag, str.strip(value)))


    def add(self, path, level, tag, value):
        ''' Processes arguments of a gedcom line.
            Returns True, while the path is one of name definitions
        Arguments example:
            path='@I0001@.NAME'
            level=2
            tag='NAME'
            value='Antti /Puuhaara/'
        '''
        #TODO: Can not process '1 NAME Catharina (Caisa)/Riihiaho/Riihinen/'
        if tag == 'NAME':
           
            # 1) Full name processing
            #    The parts like 'givn/surn/spfx' will be isolated and analyzed
        
            self.name = value
            parts = self.name.split('/')
            if len(parts) == 3:     # Contains '/Surname/'
                self.givn, self.surn, self.spfx = parts
                
                # 1.1) GIVN given name part
                
                if (self.givn):
                    self.givn = self.givn.rstrip()
                    gnames = self.givn.split()
                    
                    # 1.1a) Find id last givn is actually a patronyme; move it to spfx 
                    
                    if (len(gnames) > 0):
                        nm = gnames[-1]
                        for suff in self.RE_PATRON:
                            if nm.endswith(suff):
                                # print('# {}: {} | {!r} | {!r}'.format(path, gnames, self.surn, self.spfx))
                                self.spfx = nm
                                self.givn = ' '.join(gnames[0:-1])
                                gnames = self.givn.split()
                                #TODO: store new spfx as a SPFX line
                                break
                    
                    # 1.1b) Set call name, if one of given names are marked with '*'

                    for nm in gnames:
                        # Name has a star '*'
                        if nm.endswith('*'):
                            # Remove star
                            nm = nm[:-1]
                            self.givn = ''.join(self.givn.split(sep='*', maxsplit=1))
                            self.call = nm
                        # Name in parentehsins "(Jussi)"
                        elif re.match("\(.*\)", nm) != None:
                            # Remove parenthesis
                            self.call = nm[1:-1]
                            # Given names without call name
                            self.givn = re.sub("\(.*\) *", "", self.givn).rstrip()
                else:
                    self.givn = self.NONAME
                
                # 1.2) SURN Surname part
                
                # 1.3) SPFX Suffix part
                
                self.name = "{} /{}/ {}".format(self.givn, self.surn, self.spfx).rstrip()
                self.appendRow(level, tag, self.name)
               
                # Compare the name parts from NAME tag to this got here
                if str.strip(value) != self.name:
                    print ("{} value {!r} changed to {!r}".format(path, value, self.name))           
                    self.appendRow(level + 1, "{}{}".format(self.CHGTAG, tag), value)
            return True
    
        elif tag == 'GIVN':
            if hasattr(self, 'givn'):   #TODO: Why not? 
                self.appendRow(level, tag, self.givn)
            # If call name has been stored, put it here
            if hasattr(self, 'call'):
                print ("# _CALL {!r} for {!r}".format(self.call, self.name))
                self.appendRow(level, '_CALL', self.call)
            return True
        
        elif tag == 'SURN':
            self.appendRow(level, tag, self.surn)
            return True
        
        elif tag == 'SPFX':
            self.appendRow(level, tag, self.spfx)
            return True
        
        elif tag == '_CALL':    # So called call name
            self.call = value
            self.appendRow(level, tag, self.call)
            return True
        
        else: # like 'TYPE', 'NOTE', 'SOUR', ...
            self.appendRow(level, tag, value)
            return True


    def lines(self):
        # Return stored rows associated to this person name
        return self.rows


if __name__ == "__main__":
    myname = PersonName()
    myname.add('@I0001@.NAME', 'NAME', "Antti /Puuhaara/")
    print ("-->" + myname.get_name())
    myname = PersonName()
    myname.add('@I0002@.NAME', 'NAME', "Hello World")
    print ("-->" + myname.get_name())
    myname = PersonName()
    myname.add('@I0003@.NAME', 'NAME', "Anders (Antti) Juhonpoika /Puuhaara/")
    print ("-->" + myname.get_name())
