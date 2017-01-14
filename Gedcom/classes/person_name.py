'''
Created on 22.11.2016

@author: jm
'''

import re

_NONAME = 'N'            # Marker for missing name part
_CHGTAG = "NOTE orig_"   # Comment: original format

_UNNAMED = ['nimetön', 'tuntematon', 'N.N.', '?']
_PATRONYME = ['poika', 'p.', 'sson', 'ss.', 's.',
             'tytär', 'dotter', 'dr.', ]
_VON = ['von', 'af', 'de la', 'de']
_LYH = ['os.', 'o.s.', 'ent.','e.']


class PersonName(object):
    '''
    Stores and fixes Gedcom individual name information.

    Methods:
    __init__(...)    An object instance is greated using '1 NAME' tag row
    add(...)         Other, higher level rows are added
    lines()        Returns the list of Gedgom lines fixed
    
    The fixes are don mostly from '1 NAME givn/surn/nsfx' row.
    If NAME has significant changes, the original value is also written to 'NOTE orig_'
    
    1. A patronyme in givn part is moved to nsfx part and a new NSFX row is created, if needed
    
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
            raise AttributeError('Needs a NAME row for PersonName.init()')
           
        # 1) Full name processing
        #    The parts like 'givn/surn/nsfx' will be isolated and analyzed
    
        self.name = value
        s1 = value.find('/')
        s2 = value.rfind('/')
        if s1 >= 0 and s2 >= 0 and s1 != s2:     
            # Contains '/Surname/' or '/Surname1/Surname2/' etc
            self.givn = value[:s1]
            self.surn = value[s1+1:s2]
            self.nsfx = value[s2+1:]
            
            # 1.1) GIVN given name part
            self._proc_givn(path, level, value)
            # 1.2) SURN Surname part
            self._proc_surn(path, level, value)
            # 1.3) nsfx Suffix part: nothing to do?
            pass

            self.name = "{}/{}/{}".format(self.givn, self.surn, self.nsfx).rstrip()
            self._append_row(level, tag, self.name)
           
            # Compare the name parts from NAME tag to this got here
            if re.sub(r' ', '', value) != re.sub(r' ', '', self.name):
                print ("{} {!r} changed to {!r}".format(path, value, self.name))           
                self._append_row(level + 1, "{}{}".format(_CHGTAG, tag), value)
        else:
            print ("{} missing /SURNAME/ in {!r}".format(path, value))         

 
    def add(self, path, level, tag, value):
        ''' Adds a new, higher level row

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

        elif tag == 'NSFX' and hasattr(self, 'nsfx'): 
            if self.nsfx != value:
                if self.nsfx == '':
                    self._append_row(level, tag, value)
                else:
                    if hasattr(self, 'new_nsfx_row') == False:
                        self._append_row(level, tag, self.nsfx)
                        print ("{} {!r} changed to {!r}".format(path, value, self.nsfx))           
                        self._append_row(level + 1, "{}{}".format(_CHGTAG, tag), value)

        elif tag == '_CALL':    # So called call name
            self.call = value
            self._append_row(level, tag, self.call)

        else: # all others like 'TYPE', 'NOTE', 'SOUR', ...
            print ("{} # '{} {}'".format(path, tag, value))           

            self._append_row(level, tag, value)


    def lines(self):
        ''' Returns the stored rows associated to this person name
        '''
        if hasattr(self, 'new_nsfx_row'):
            self.rows.append(self.new_nsfx_row)
        return self.rows


    # Local functions
    
    def _proc_givn(self, path, level, value):
        ''' Process given name part of NAME record
        '''
        if (self.givn):
            self.givn = self.givn.rstrip()
            gnames = self.givn.split()
            #print('# {}: {!r} TÄSSÄ'.format(path, gnames))
            
            # 1.1a) Find if last givn is actually a patronyme; move it to nsfx 
            
            if (len(gnames) > 0):
                nm = gnames[-1]
                if self._match_patronyme(nm) != None:
                    # print('# {}: {} | {!r} | {!r}'.format(path, gnames, self.surn, self.nsfx))
                    self.nsfx = nm
                    self.givn = ' '.join(gnames[0:-1])
                    gnames = self.givn.split()
                    self.new_nsfx_row = self._format_row(level+1, 'NSFX', nm)
            
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

    def _proc_surn(self, path, level, value):
        ''' Process surname part of NAME record

        Examples:
            "Aho os. Mattila"          => NAME="Aho"
                                          NAME="Mattila" TYPE="MARR"
            "Surname1/Surname2"        => NAME="Surname1"
                                          NAME="Surname2" TYPE="AKA"
            "Aho e. Mattila os. Laine" => NAME="Aho"
                                          NAME="Mattila" TYPE="PREV"
                                          NAME="Laine" TYP="MARR"

        TODO: Pitäisikö käsitellä pilkuin erotetut sukunimet Gedcom 5.5:n mukaisesti?
        '''
        _SURN = {'os.':'MARR', 'o.s.':'MARR', 'ent.':'PREV', 'e.':'PREV', '/':'AKA', ',':'AKA'}

        state = 0
        type_left = None
        name_left = None
        note = ''
        
        surnames = re.sub(r' */ *', ' / ', self.surn)   # "/" as separator symbol
        
        # Names processor automate
        for nm in surnames.split():
            if state == 0:          # Start state / the word on the right side of a separator
                # Only name expected. 
                # If a separator on the left, save with type found, else save without type
                if type_left != None:
                    self._append_row(level, 'NAME', name_left)
                    self._append_row(level + 1, 'TYPE', type_left)
                    note = "{} {}({})".format(note, name_left, type_left)
                    type_left = None                    
                name_left = nm
                state = 1
            else: # state = 1         Possible separator state / left side name has been stored
                # Name or separator expected
                # If name, concatenate to the left side name, else store the separator type
                if nm in _SURN:
                    type_left = _SURN[nm]
                    state = 0
                else:
                    name_left = name_left + ' ' + nm
                    note = "{} {!r}".format(note, name_left)

        if type_left != None:
            self._append_row(level, 'NAME', name_left)
            self._append_row(level + 1, 'TYPE', type_left)
            note = ''
            type_left = None                    
        if note != '':
            print ("#{} {!r} surnames{}".format(path, value, note))                           
    
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

