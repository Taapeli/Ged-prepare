'''
Created on 22.11.2016

@author: jm
'''

import re
from sys import stderr
from classes.gedcom_line import GedcomLine

_NONAME = 'N'            # Marker for missing name part
_CHGTAG = "NOTE orig_"   # Comment: original format

_UNNAMED = ['nimetön', 'tuntematon', 'N.N.', '?']
_PATRONYME = ['poika', 'p.', 'sson', 'ss.', 's.',
             'tytär', 'dotter', 'dr.', ]
_SURN = {'os.':'MARR', 'o.s.':'MARR', 'ent.':'PREV', 'e.':'PREV', '/':'AKA', ',':'AKA'}
_VON = ['von', 'af', 'de la', 'de']
_BABY = {"vauva":"U", "poikavauvai":"M", "tyttövauva":"F", 
         "poikalapsi":"M", "tyttölapsi":"F", "lapsi":"U"}
#TODO: Lyhenteet myös ruotsiksi


class PersonName(object):
    '''
    Stores and fixes Gedcom individual name information.

    Methods:
    __init__(...)    Create an PersonName instance from a '1 NAME' tag row
    add_line(...)    Add an associated row (with a higher level number)
    set_attr(...)    Set rule for patronymes
    get_lines()      Returns the list of Gedgom get_lines fixed
    
    The main source of information is the '1 NAME givn/surn/nsfx' row.
    If NAME has significant changes, the original value is also written to 
    'NOTE orig_'
    
    1. A patronyme in givn part is moved to nsfx part and a new NSFX row is created,
       if needed
    
    2. A missing givn or surn is replaced with noname mark 'N'
    
    3. ...
    '''

    def __str__(self):
        return "{} NAME {}".format(self.level, self.name)


    def __init__(self, gedline):
        ''' Creates a new instance on person name definition.
            The arguments must be a NAME gedcom line.
        '''
#       Example: GedLine{
#         path='@I0001@.NAME'
#         level=2
#         tag='NAME'
#         value='Anders (Antti)/Puuhaara e. Träskalle/' }

        if gedline.tag != 'NAME':
            raise AttributeError('Needs a NAME row for PersonName.init()')
        # GedcomLines associated to this PersonName
        self.rows = []

        self.level = gedline.level
        self.path = gedline.path
        self.tag = gedline.tag
        self.name = gedline.value

        ''' 1) Full name processing
               The parts like 'givn/surn/nsfx' will be isolated and analyzed
        '''
        # Split 'ginv/surn/nsfx' from NAME line
        s1 = gedline.value.find('/')
        s2 = gedline.value.rfind('/')
        if s1 >= 0 and s2 >= 0 and s1 != s2:     
            # Contains '.../Surname/...' or '.../Surname1/Surname2/...' etc
            self.givn = gedline.value[:s1]
            self.surn = gedline.value[s1+1:s2]
            self.nsfx = gedline.value[s2+1:]
            

    def add_line(self, gedline):
        ''' Adds a new, higher level row to person name structure

        Arguments example:
            path='@I0002@.NAME'
            level=2
            tag='GIVN'
            value='GIVN Brita Kristiina/'
        '''
        if not type(gedline) is GedcomLine:
            raise RuntimeError("GedcomLine argument expected")

        # A ready made GedcomLine
        self.rows.append(gedline)
        

#     def get_lines(self):
#         ''' Returns the stored rows associated to this person name in this order 
#             (if exists)
#         
# #             n NAME <NAME_PERSONAL>
# #             +1 NPFX <NAME_PIECE_PREFIX>
# #             +1 GIVN <NAME_PIECE_GIVEN>
# #             +1 NICK <NAME_PIECE_NICKNAME>
# #             +1 SPFX <NAME_PIECE_SURNAME_PREFIX
# #             +1 SURN <NAME_PIECE_SURNAME>
# #             +1 NSFX <NAME_PIECE_SUFFIX>
# #             +1 _CALL <the call name defined by ourserlves>
# #             +1 <<SOURCE_CITATION>>
# #             +1 <<NOTE_STRUCTURE>>
#         '''
#         ''' The original NAME line is not written out but the NAMEs which
#             are picked out by surn part of NAME
#         '''
#         orows = []
#         for i in range(len(self.rows)-1, 0, -1):
#             if type(self.rows[i]) == PersonName:
#                 # Pick NAME, NOTEn TYPE from this PersonName
#                 #TODO: TYPE ei ole talletettu
#                 for x in self.get_person_rows(self):
#                     orows.append(x)
#                 # The associated rows line SURN, GIVN ...
#                 for obj in self.rows:
#                     if type(obj) == GedcomLine:
#                         orows.append(obj)
#         return orows


    def get_person_rows(self): 
        ''' Analyze the given PersonName and return GedcomLines:
            first NAME and then associated rows.
            The rules about patronymes and merging original and generated values should be applied here
        '''
        ''' 1.1) GIVN given name part '''
        self._evaluate_givn(self)
        ''' 1.2) nsfx Suffix part: nothing to do? '''
        pass
        ''' 1.3) SURN Surname part: pick each surname
                 Returns NAME, GIVN, SURN, NSFX rows and their associated lines (like SOUR)
        '''
        ret = self._evaluate_surn(self)


        
        # Compare the name parts from NAME tag to this got here 
        if re.sub(r' ', '', gl.value) != re.sub(r' ', '', self.name): 
            print ("{} {!r:>36} ––> {!r}".format(self.path, 
                                                 gl.value, self.name))
            nt = GedcomLine(self._format_row(self.level, 
                            "NOTE", 
                            "{}{} {}".format(_CHGTAG, self.tag, self.value)))    
            ret.append(nt)
        return ret


    # ---- Local functions ----
    
    def _evaluate_givn(self, gedline):
        ''' Process given name part of NAME record '''

        def _match_patronyme(nm):
            '''Returns patronyme suffix, if matches, else None'''
            for suff in _PATRONYME:
                if nm.endswith(suff):
                    return suff
            return None


        if not (type(gedline) is PersonName or type(gedline) is GedcomLine):
            raise RuntimeError("GedcomLine or PersonName argument expected, got {!r}".format(type(gedline)))

        if self.givn:
            self.givn = self.givn.rstrip()
            gnames = self.givn.split()
            
            # 1.1a) Find if last givn is actually a patronyme; mark it as new nsfx 
            
            if (len(gnames) > 0):
                nm = gnames[-1]
                if _match_patronyme(nm) != None:
                    self.nsfx_new = nm
                    self.givn = ' '.join(gnames[0:-1])
                    gnames = self.givn.split()
            
            # 1.1b) Set call name, if one of given names are marked with '*'
    
            for nm in gnames:
                # Name has a star '*'
                if nm.endswith('*'):
                    # Remove star
                    nm = nm[:-1]
                    self.givn = ''.join(self.givn.split(sep='*', maxsplit=1))
                    self.call_name = nm
                # Name in parentehsins "(Jussi)"
                elif re.match(r"\(.*\)", nm) != None:
                    # Remove parenthesis
                    self.call_name = nm[1:-1]
                    # Given names without call name
                    self.givn = re.sub(r"\(.*\) *", "", self.givn).rstrip()
        else:
            self.givn = _NONAME


    def _evaluate_surn(self, gedline):
        ''' Process surname part of NAME record and return a list of PersonNames,
            which are generated from each surname mentioned

        Examples:
            "Mattila"                  => PersonName[0]="Mattila"
            "Frisk os. Mattila"        => PersonName[0]="Mattila"
                                          PersonName[1]="Frisk" TYPE="MARR"
            "Surname1/Surname2"        => PersonName[0]="Surname1"
                                          PersonName[1]="Surname2" TYPE="AKA"
            "Reipas e. Frisk os. Laine"=> PersonName[0]="Laine"
                                          PersonName[1]="Frisk" TYP="MARR"
                                          PersonName[2]="Reipas" TYPE="CHANGED"
            "Lehti os. Lampi e. Damm"  => PersonName[0]="Damm"
                                          PersonName[1]="Lampi" TYP="CHANGED"
                                          PersonName[2]="Lehti" TYPE="MARR"
        '''
        def put_person(name, name_type):
            ''' Return each PersonName instance '''
            # Store rows SURN with TYPE, if defined
            ret = []
            if name != '':
                # Write NAME line 
                self.name = "{}/{}/{}".format(self.givn, self.surn, self.nsfx).rstrip() 
                self._append_gedline(gedline.level, gedline.tag, self.name) 
                self.value = self.name
                self._append_gedline(gedline.level+1, 'SURN', name)
                if name_type != '':
                    self._append_gedline(gedline.level + 2, 'TYPE', name_type)
                    #_note = "{} {}({})".format(_note, name, name_type)
            ''' Generate GIVN, _CALL and SURN lines '''
            #TODO: Nämä rivit yhdistettävä olemassa oleviin
            gl = GedcomLine(self._format_row(self.level+1, 'GIVN', self.givn))
            self.rows.append(gl)
            if hasattr(self, 'call_name'):
                gl = GedcomLine(self._format_row(self.level+1, '_CALL', self.call_name))
                self.rows.append(gl)
            # Get associated rows
            for gl in self.rows:
                print("#person+ row <– {} ({!r})".format(gl.path, gl.value), 
                      file=stderr)
                ret.append(gl)
            return ret
       
        if not (type(gedline) is PersonName or type(gedline) is GedcomLine):
            raise RuntimeError("GedcomLine or PersonName argument expected")

        if gedline.name == '': #op_2 No surname
            return
        state = 0
        oper = ''
        name = ''
        # The PersonName, where other attributes will be applied
        current = self
        # convert "/" and "," to separator symbol ","
        surnames = re.sub(r' *[/,] *', ' , ', self.surn).split()
        
        ''' This surnames automate reads surnames and separators from right to left
            and writes PersonNames to self.rows(?)
        
            !state \ input !! delim ! name  ! end
            |--------------++-------+-------+--------
            | 0 "Started"  || -     | 1,op1 | 3,op3
            | 1 "name"     || 2,op3 | 1,op2 | 3,op4
            | 2 "delim"    || -     | 1,op1 | -
            | 3 "end"      || -     | -     | -
            | - "error"    || 
        #TODO: Each '-' should cause an error!
         For example rule "2,op3" means operation op3 and new state 2.
             op1: save name=nm
             op2: concatenate a two part name
             op3: write PersonName(name), TYPE=oper[delim]
             op4: write last PersonName(name), TYPE=oper[delim]
        '''

        for nm in reversed(surnames):
            if state == 0:          # Start state
                #op_1 Only name expected.
                name = nm
                state = 1
            elif state == 1:        # Possible separator state / 
                                    # left side name has been stored
                # Name or separator expected
                # If name, concatenate to the left side name, else store the
                # separator type
                if nm in _SURN:
                    #op_3: A separator 'os.', ... found: 
                    #      Create PersonName rows with the left side name and it's type
                    put_person(name, oper)
                    oper = _SURN[nm]
                    state = 2
                else:
                    #op_2: Another name found
                    name = name + ' ' + nm
                    #_note = "{} {!r}".format(_note, name)

        #op_4: End: output the previous name and it's type
        put_person(name, oper)
        # The last name is the one used
        self.surn = name


    def _format_row(self, level, tag, value):
        ''' Builds a gedcom row '''
        return("{} {} {}".format(level, tag, str.strip(value)))


    def _append_gedline(self, level, tag, value):
        ''' Stores the row as a GedcomLine so that previous values are replaced and 
            right order is preserved.
            1. Inset NAME row on the top
            2. Is the same path is found in self.rows[x]?
               2.1 Yes: if self.rows(x) has an empty value
                   3.1 Replace the row with given data
                   3.2 Else if there is a different self.rows(x).value: 
                       append a new row 
               2.2 No: append the row
        '''
        gl = GedcomLine(self._format_row(level, tag, value))
        gl.set_path(level, tag) # Turha???
        if tag == "NAME":
            # Write NAME line 
            self.name = "{}/{}/{}".format(self.givn, self.surn, self.nsfx).rstrip()
            gl = GedcomLine(self._format_row(level, tag, value))
            gl.value = self.name
            print("#person  row <– {} ({!r})".format(gl.path, gl.value), 
                  file=stderr)
            self.rows.append(gl)
            # A new patronyme?
            if hasattr(self, 'nsfx_new'):
                self._append_gedline(self.level+1, 'NSFX', self.nsfx_new)
            return
 
        for x in range(len(self.rows)):
            if self.rows[x].path == gl.path:
                # 2.1 The same path found in rows(x)
                v = self.rows[x].value
                print("#person 2.1 row({}) ({!r}) <– {} ({!r})".format(x, v, 
                      gl.path, gl.value), file=stderr)
                self.rows[x] = gl
                if v != "":
                    # 3.1 Replace curent row
                    print("#person 3.1 row({}) ({!r}) <– {} ({!r})".format(x, v, gl.path,
                          gl.value), file=stderr)
                    self.rows[x] = gl
                    return
                else:
                    if v != value:
                        # 3.2 Previous value is different: 
                        #     f.ex. there are multiple SURN tags for a name
                        print("#person 3.2 row({}) ({!r}) <= {} ({!r})".format(len(self.rows), 
                                    v, gl.path, gl.value), file=stderr)
                        self.rows.append(gl)
                        return
 
        # 2.2 Path not found            
        print("#person 2.2 row({}) <= {} ({!r})".format(len(self.rows), gl.path, gl.value), 
              file=stderr)
        self.rows.append(gl)
