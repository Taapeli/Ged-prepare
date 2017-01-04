'''
Created on 22.11.2016

@author: jm
'''

class PersonName(object):
    '''
    Contains Gedcom individual name information from tags:
    - NAME typically 'givn/surn/spfx'
    - GIVN
    - SURN
    - SPFX
    - _CALL
    '''
    NONAME = 'N'   # Marker for missing name part
    CHGTAG = "NOTE orig_"

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
        if tag == 'NAME':
            #  Processes the value of NAME tag and tries to parse it to givn, surn, spfx fields
            self.name = value
            parts = self.name.split('/')
            if len(parts) == 3:     # Contains '/Surname/'
                self.givn, self.surn, self.spfx = parts
                
                # 1. Process given name field
                
                if (self.givn):
                    self.givn = self.givn.rstrip()
                    gnames = self.givn.split()
                    
                    # 1a) Set patronymes to spfx 
                    
                    if (len(gnames) > 0) & \
                       ((gnames[-1].endswith('poika') | (gnames[-1].endswith('tytär')))):
                        # print('# {}: {} | {!r} | {!r}'.format(path, gnames, self.surn, self.spfx))
                        self.spfx = gnames[-1]
                        self.givn = ' '.join(gnames[0:-1])
                        #TODO: store new spfx as a SPFX line
                    
                    # 1b) Set call name, if one of given names are marked with '*'
                    #TODO:
                    for nm in gnames:
                        if nm.endswith('*'):
                            # Remove star
                            nm = nm[:-1]
                            self.givn = ''.join(self.givn.split(sep='*', maxsplit=1))
                            # Set _CALL line
                            self.call = nm
                            # The Call name output is delayed after GIVN
                            print ("## _CALL {!r} for {!r}".format(self.call, self.name))

                else:
                    self.givn = self.NONAME
                self.name = "{} /{}/ {}".format(self.givn, self.surn, self.spfx).rstrip()
                self.appendRow(level, tag, self.name)
               
                # Compare the name parts from NAME tag to this got here
                if str.strip(value) != self.name:
                    print ("## {} value {!r} changed to {!r}".format(tag, value, self.name))           
                    self.appendRow(level + 1, "{}{}".format(self.CHGTAG, tag), value)
            return True
    
        elif tag == 'GIVN':
            self.appendRow(level, tag, self.givn)
            # If call name has been stored, put it here
            if hasattr(self, 'call'):
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
