'''
Created on 16.1.2017

@author: jm
'''

import re
from classes.gedcom_line import GedcomLine


class GedcomRecord(object):
    '''
    Stores a Gedcom logical record (level 0 record) with higher level lines included.

    Methods:
    __init__(...)    An object instance is created using the level 0 line
    add(...)         Other, higher level rows are added
    get_lines()      Returns an iterable containing the lines
    
    The fixes are don mostly from '1 NAME givn/surn/nsfx' row.
    If NAME has significant changes, the original value is also written to 'NOTE orig_'
    
    '''
    global _surn_lines
    

    def __str__(self):
        return "GedcomRecord({})".format(self.id)


    def __init__(self):
        ''' Creates a new instance of gedcom logical record
            which includes a group of gredcom lines starting with a level0 record.
        '''
        self.rows = []

    
    def add_line(self, gedline):
        ''' Adds a gedcom line to set
        '''

        if gedline.tag == 'NAME':
            rows.append(PersonName(gedline))
           
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

            # Write NAME line
            self.name = "{}/{}/{}".format(self.givn, self.surn, self.nsfx).rstrip()
            self._append_row(level, tag, self.name)
            # Write new SURN lines, if any
            for ln in self._surn_lines:
                self.rows.append(ln)

           
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
            #print ("{} # '{} {}'".format(path, tag, value))           
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

        TODO: Pitäisi käsitellä pilkuin erotetut sukunimet Gedcom 5.5:n mukaisesti
        '''
        #global _note
        
        def _put(name, name_type):
            ''' Store ouput rows: SURN with TYPE, if defined '''
            if name != '':
                self._surn_lines.append(self._format_row(level+1, 'SURN', name))
                if name_type != '':
                    self._surn_lines.append(self._format_row(level + 2, 'TYPE', name_type))
                    #_note = "{} {}({})".format(_note, name, name_type)


        if value == '': #op_2 No surname
            return
        state = 0
        oper = ''
        name = ''
        #_note = ''
        
        surnames = re.sub(r' */ *', ' / ', self.surn)   # pick "/" as separator symbol
        
        # Names processor automate
        for nm in surnames.split():
            if state == 0:          # Start state
                #op_1 Only name expected.
                name = nm
                state = 1
            elif state == 1:        # Possible separator state / left side name has been stored
                # Name or separator expected
                # If name, concatenate to the left side name, else store the separator type
                if nm in _SURN:
                    #op_3: A separator found: output the previous name and it's type
                    _put(name, oper)
                    oper = _SURN[nm]
                    state = 2
                else:
                    #op_4: Another name found
                    name = name + ' ' + nm
                    #_note = "{} {!r}".format(_note, name)
            else: # State = 2         Delimiter passed
                #op_6: A name expected
                name = nm

        #op_5: End: output the previous name and it's type
        _put(name, oper)
        # The last name is the one used
        self.surn = name
        #if _note != '':
        #    print ("#{} {!r} surnames{}".format(path, value, _note))                           

    
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

