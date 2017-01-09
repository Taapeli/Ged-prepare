'''
Created on 22.11.2016

@author: jm
'''

import re

class PersonName(object):
    '''
    Stores and fixes Gedcom individual name information.

    Methods:
    __init__(...)    An object instance is greated using '1 NAME' tag row
    add(...)         Other, higher level rows are added
    lines()        Returns the list of Gedgom lines fixed
    
    The fixes are don mostly from '1 NAME givn/surn/spfx' row:
    1. A patronyme in givn part is moved to spfx part and a new SPFX row is created, if needed
    2. A missing givn or surn is replaced with noname mark 'N'
    3. ...
    '''
    _NONAME = 'N'            # Marker for missing name part
    _CHGTAG = "NOTE orig_"   # Comment: original format
    
    _UNNAMED = ['nimetön', 'tuntematon', 'N.N.']
    _PATRONYME = ['poika', 'p.', 'sson', 'ss.', 's.',
                 'tytär', 'dotter', 'dr.', ]
    _VON = ['von', 'af', 'de la', 'de']
    _LYH = ['os.', 'o.s.', 'ent.','e.']
    _SURN = {'os.':'MARR', 'o.s.':'MARR', 'ent.':'BORN', 'e.':'BORN'}


    def __str__(self):
        return "PersonName({})".format(self.name)


    def __init__(self, path, level, tag, value):
        ''' Creates a new instance on person name definition.
            The arguments must be from a NAME gedcom line.

        Arguments example:
            path='@I0001@.NAME'
            level=2
            tag='NAME'
            value='Antti /Puuhaara/'
        '''
        #TODO: Can not process '1 NAME Catharina (Caisa)/Riihiaho/Riihinen/'
        
        self.rows = []

        if tag != 'NAME':
            raise AttributeError('Need NAME tag for init PersonName')
           
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
                #print('# {}: {!r} TÄSSÄ'.format(path, gnames))
                
                # 1.1a) Find if last givn is actually a patronyme; move it to spfx 
                
                if (len(gnames) > 0):
                    nm = gnames[-1]
                    for suff in self._PATRONYME:
                        if nm.endswith(suff):
                            # print('# {}: {} | {!r} | {!r}'.format(path, gnames, self.surn, self.spfx))
                            self.spfx = nm
                            self.givn = ' '.join(gnames[0:-1])
                            gnames = self.givn.split()
                            self.new_spfx_row = self._format_row(level+1, 'SPFX', nm)
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
                self.givn = self._NONAME
            
            # 1.2) SURN Surname part
            
            # 1.3) SPFX Suffix part
            
            self.name = "{}/{}/{}".format(self.givn, self.surn, self.spfx).rstrip()
            self._append_row(level, tag, self.name)
           
            # Compare the name parts from NAME tag to this got here
            if re.sub(r' ', '', value) != re.sub(r' ', '', self.name):
                print ("{} value {!r} changed to {!r}".format(path, value, self.name))           
                self._append_row(level + 1, "{}{}".format(self._CHGTAG, tag), value)
        elif len(parts) > 3:
            print ("{} complicated {!r} NOT CHANGED".format(path, value))           

 
    def add(self, path, level, tag, value):
        ''' Adds arguments of a gedcom line as a new row of NAME group

        Arguments example:
            path='@I0001@.NAME'
            level=2
            tag='GIVN'
            value='GIVN Brita Kristiina/'
        '''
        if tag == 'GIVN' and hasattr(self, 'givn'):   #TODO: Why not? 
            self._append_row(level, tag, self.givn)
            # If call name has been stored, put it here
            if hasattr(self, 'call'):
                print ("# _CALL {!r} for {!r}".format(self.call, self.name))
                self._append_row(level, '_CALL', self.call)
        
        elif tag == 'SURN' and hasattr(self, 'surn'):
            self._append_row(level, tag, self.surn)
        
        elif tag == 'SPFX' and hasattr(self, 'spfx'):
            self._append_row(level, tag, self.spfx)
            return True
        
        elif tag == '_CALL':    # So called call name
            self.call = value
            self._append_row(level, tag, self.call)
        
        else: # like 'TYPE', 'NOTE', 'SOUR', ...
            self._append_row(level, tag, value)


    def lines(self):
        ''' Returns the stored rows associated to this person name
        '''
        if hasattr(self, 'new_spfx_row'):
            self.rows.append(self.new_spfx_row)
        return self.rows
        
# Local functions -------------
        
    def _format_row(self, level, tag, value):
        # Builds a gedcom row 
        return("{} {} {}".format(level, tag, str.strip(value)))


    def _append_row(self, level, tag, value):
        # Stores the row to name group
        self.rows.append(self._format_row(level, tag, value))




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
