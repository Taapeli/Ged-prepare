'''
Created on 22.11.2016

@author: jm
'''

import re

_NONAME = 'N'            # Marker for missing name part
_CHGTAG = "NOTE orig_"   # Comment: original format

_UNNAMED = ['nimetön', 'tuntematon', 'N.N.']
_PATRONYME = ['poika', 'p.', 'sson', 'ss.', 's.',
             'tytär', 'dotter', 'dr.', ]
_VON = ['von', 'af', 'de la', 'de']
_LYH = ['os.', 'o.s.', 'ent.','e.']
_SURN = {'os.':'MARR', 'o.s.':'MARR', 'ent.':'PREV', 'e.':'PREV', '/':'AKA', ',':'AKA'}


class PersonName(object):
    '''
    Stores and fixes Gedcom individual name information.

    Methods:
    __init__(...)    An object instance is greated using '1 NAME' tag row
    add(...)         Other, higher level rows are added
    lines()        Returns the list of Gedgom lines fixed
    
    The fixes are don mostly from '1 NAME givn/surn/spfx' row.
    If NAME has significant changes, the original value is also written to 'NOTE orig_'
    
    1. A patronyme in givn part is moved to spfx part and a new SPFX row is created, if needed
    1.1. If a line '2 NSFX Joonaanpoika' exists and has patronyme, the tag must be changes to 'NSFX'
    
    2. A missing givn or surn is replaced with noname mark 'N'
    
    3. ...
    
    '''

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
        self.rows = []
        if tag != 'NAME':
            raise AttributeError('Need NAME tag for init PersonName')
           
        # 1) Full name processing
        #    The parts like 'givn/surn/spfx' will be isolated and analyzed
    
        self.name = value
        s1 = value.find('/')
        s2 = value.rfind('/')
        if s1 >= 0 and s2 >= 0 and s1 != s2:     
            # Contains '/Surname/' or '/Surname1/Surname2/' etc
            self.givn = value[:s1]
            self.surn = value[s1+1:s2]
            self.spfx = value[s2+1:]
            
            # 1.1) GIVN given name part
            
            if (self.givn):
                self.givn = self.givn.rstrip()
                gnames = self.givn.split()
                #print('# {}: {!r} TÄSSÄ'.format(path, gnames))
                
                # 1.1a) Find if last givn is actually a patronyme; move it to spfx 
                
                if (len(gnames) > 0):
                    nm = gnames[-1]
                    if self._match_patronyme(nm) != None:
                        # print('# {}: {} | {!r} | {!r}'.format(path, gnames, self.surn, self.spfx))
                        self.spfx = nm
                        self.givn = ' '.join(gnames[0:-1])
                        gnames = self.givn.split()
                        self.new_spfx_row = self._format_row(level+1, 'SPFX', nm)
                
                # 1.1b) Set call name, if one of given names are marked with '*'

                for nm in gnames:
                    # Name has a star '*'
                    if nm.endswith('*'):
                        # Remove star
                        nm = nm[:-1]
                        self.givn = ''.join(self.givn.split(sep='*', maxsplit=1))
                        self.call = nm
                    # Name in parentehsins "(Jussi)"
                    elif re.match(r"\(.*\)", nm) != None:
                        # Remove parenthesis
                        self.call = nm[1:-1]
                        # Given names without call name
                        self.givn = re.sub(r"\(.*\) *", "", self.givn).rstrip()
            else:
                self.givn = _NONAME
            
            # 1.2) SURN Surname part
            
            # Parse "Aho os. Mattila", "Suname1/Surname2", "Aho e. Mattila os. Laine" etc
            # TODO: must fix surnames!

            n = 0
            nm_next = ""
            surnames = re.sub(r' */ *', ' / ', self.surn)   # "/" as separator symbol
            for nm in surnames.split():
                typ = self._match_surn_sep(nm)
                if typ != None:
                    # "Nm_left os. Nm" --> "2 NAME Name"; "3 TYPE MARR"
                    self._append_row(level, 'NAME', nm)
                    self._append_row(level + 1, 'TYPE', typ)
                    n = n+1
                    nm_next = "{} {}={!r} ".format(nm_next, typ,nm)
                else:
                    # Simple name "Nm" --> "2 NAME Nm"
                    self._append_row(level, 'NAME', nm)
            if n > 0:
                print ("# {!r} surnames {!r}".format(value, nm))                           


            # 1.3) SPFX Suffix part
            
            self.name = "{}/{}/{}".format(self.givn, self.surn, self.spfx).rstrip()
            self._append_row(level, tag, self.name)
           
            # Compare the name parts from NAME tag to this got here
            if re.sub(r' ', '', value) != re.sub(r' ', '', self.name):
                print ("{} {!r} changed to {!r}".format(path, value, self.name))           
                self._append_row(level + 1, "{}{}".format(_CHGTAG, tag), value)
        else:
            print ("{} missing /SURNAME/ in {!r}".format(path, value))         

 
    def add(self, path, level, tag, value):
        ''' Adds arguments of a gedcom line as a new row of NAME group

        Arguments example:
            path='@I0001@.NAME'
            level=2
            tag='GIVN'
            value='GIVN Brita Kristiina/'
        '''
        if tag == 'GIVN' and hasattr(self, 'givn'): 
            self._append_row(level, tag, self.givn)
            # If call name has been stored, put it here
            if hasattr(self, 'call'):
                print ("# _CALL {!r} for {!r}".format(self.call, self.name))
                self._append_row(level, '_CALL', self.call)
        
        elif tag == 'SURN' and hasattr(self, 'surn'):
            self._append_row(level, tag, self.surn)
        
        elif tag == 'SPFX' and hasattr(self, 'spfx'):
            self._append_row(level, tag, self.spfx)
        
        elif tag == 'NSFX' and hasattr(self, 'spfx') and self.spfx != '':
            if self._match_patronyme(value) != None:
                # Now patronyme is defined twice; abandon this
                pass
        
        elif tag == '_CALL':    # So called call name
            self.call = value
            self._append_row(level, tag, self.call)
        
        else: # all others like 'TYPE', 'NOTE', 'SOUR', ...
            self._append_row(level, tag, value)


    def lines(self):
        ''' Returns the stored rows associated to this person name
        '''
        if hasattr(self, 'new_spfx_row'):
            self.rows.append(self.new_spfx_row)
        return self.rows
        
# Local functions -------------
        
    def _format_row(self, level, tag, value):
        ''' Builds a gedcom row '''
        return("{} {} {}".format(level, tag, str.strip(value)))


    def _append_row(self, level, tag, value):
        ''' Stores the row to name group '''
        self.rows.append(self._format_row(level, tag, value))


    def _match_patronyme(self, nm):
        '''Returns patronyme suffix, if matches, else None'''
        for suff in _PATRONYME:
            if nm.endswith(suff):
                return suff
        return None

    def _match_surn_sep(self, nm):
        '''Returns separator type, if nm matches any of them, else None'''
        if nm in _SURN:
            return _SURN[nm]
        else:
            return None

