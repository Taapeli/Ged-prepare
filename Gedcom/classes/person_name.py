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
        

    def get_lines(self):
        ''' Returns the stored rows associated to this person name in this order 
            (if exists)
        
            n NAME <NAME_PERSONAL>
            +1 NPFX <NAME_PIECE_PREFIX>
            +1 GIVN <NAME_PIECE_GIVEN>
            +1 NICK <NAME_PIECE_NICKNAME>
            +1 SPFX <NAME_PIECE_SURNAME_PREFIX
            +1 SURN <NAME_PIECE_SURNAME>
            +1 NSFX <NAME_PIECE_SUFFIX>
            +1 _CALL <the call name defined by ourserlves>
            +1 <<SOURCE_CITATION>>
            +1 <<NOTE_STRUCTURE>>
        '''
        def _fetch_person_name(gedline): 
            ''' Analyze the given PersonName and return NAME and TYPE rows.
                The rules about patronymes should be applied here
            '''
            ret = []
            ''' 1.1) GIVN given name part'''
            self._process_givn(gedline)
            ''' 1.2) nsfx Suffix part: nothing to do?'''
            pass
            ''' 1.3) SURN Surname part: pick each surname'''
            self._process_surn(gedline)
    
            # Write NAME line 
            self.name = "{}/{}/{}".format(gedline.givn, gedline.surn, gedline.nsfx).rstrip()
            gl = GedcomLine(gedline.level, gedline.tag, self.name)
            gl.value = self.name
            ret.append(gl) 
            
            # Compare the name parts from NAME tag to this got here 
            if re.sub(r' ', '', gl.value) != re.sub(r' ', '', self.name): 
                print ("{} {!r:>36} ––> {!r}".format(gedline.path, 
                       gl.value, self.name))
                nt = GedcomLine(gedline.level, 
                                "NOTE", 
                                "{}{} {}".format(_CHGTAG, gedline.tag, gedline.value))          
                ret.append(nt)

            return ret


#         def _put(gedline):
#             ''' Store rows SURN with TYPE, if defined '''
#             # TODO: Nimen tyyppi puuttuu
#             if gedline.surn != '':
#                 self._append_gedline(gedline.level, 'SURN', gedline.surn)
#                 
#                 if name_type != '':
#                     self._append_gedline(gedline.level + 2, 'TYPE', name_type)
#                     #_note = "{} {}({})".format(_note, name, name_type)

#         def find_w_path(self, tag):
#             '''Returns those gedcom lines in NAME structure, witch have with 
#                given <path>.<tag> .
#                For example path "@I0002@.NAME.GIVN" should return 
#                both "2 GIVN" and "3 SOUR"
#             '''
#             ret = []
#             search_path = self.path + '.' + tag
#             for i in self.rows:
#                 if i.path.startswith(search_path):
#                     ret.append(i)
#             return ret

        ''' The original NAME line is not written out but the NAMEs which
            are picked out by surn part of NAME
        '''
        orows = []
        for i in range(len(self.rows)-1, 0, -1):
            if type(self.rows[i]) == PersonName:
                # Pick NAME, NOTEn TYPE from this PersonName
                #TODO: TYPE ei ole talletettu
                if x in _fetch_person_name(gedline):
                    orows.append(x)
                # The associated rows line SURN, GIVN ...
                for j in range(len(self.rows)):
                    if type(self.rows[j]) == GedcomLine:
                       orows.append(self.rows[j])

#         # First NAME line
#         orows = [str(self)]
#         for tag in [ "NPFX", "GIVN", "NICK", "SPFX", "SURN", "NSFX", "_CALL" ]:
#             for gl in find_w_path(self, tag):
#                 #TODO: pitäisi huomioida NAME-riville tehdyt muutokset
#                 #TODO: toistuvat tagin yhdistettävä: tyhjä tai samanlainen hylätään,
#                 #      muuten huomautus
#                 orows.append(str(gl))
        return orows


    # ---- Local functions ----
    
    def _process_givn(self, gedline):
        ''' Process given name part of NAME record '''

        def _match_patronyme(self, nm):
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
            #print('# {}: {!r} TÄSSÄ'.format(path, gnames))
            
            # 1.1a) Find if last givn is actually a patronyme; move it to nsfx 
            
            if (len(gnames) > 0):
                nm = gnames[-1]
                if self._match_patronyme(nm) != None:
                    # print('# {}: {} | {!r} | {!r}'.format(path, gnames, self.surn, self.nsfx))
                    self.nsfx = nm
                    self.givn = ' '.join(gnames[0:-1])
                    gnames = self.givn.split()
                    self._append_gedline(gedline.level+1, 'NSFX', nm)
            
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
        self._append_gedline(gedline.level+1, 'GIVN', self.givn)
        if hasattr(self, 'call_name'):
            self._append_gedline(gedline.level+1, '_CALL', self.call_name)


    def _process_surn(self, gedline):
        ''' Process surname part of NAME record and return a list of PersonNames,
            which are generated from each surname mentioned

        Examples:
            "Aho os. Mattila"          => PersonName[0]="Aho"
                                          PersonName[1]="Mattila" TYPE="MARR"
            "Surname1/Surname2"        => PersonName[0]="Surname1"
                                          PersonName[1]="Surname2" TYPE="AKA"
            "Aho e. Mattila os. Laine" => PersonName[0]="Aho"
                                          PersonName[1]="Mattila" TYPE="PREV"
                                          PersonName[2]="Laine" TYP="MARR"

        TODO: Pitäisi käsitellä pilkuin erotetut sukunimet Gedcom 5.5:n mukaisesti
              (kuten '/')
        TODO: Pikutetuista nimistä ensimmäinen on virallinen, muuta AKA
        '''

        #     start of _process_surn():

        if not (type(gedline) is PersonName or type(gedline) is GedcomLine):
            raise RuntimeError("GedcomLine or PersonName argument expected")

        if gedline.value == '': #op_2 No surname
            return
        state = 0
        oper = ''
        name = ''

        # pick "/" or "," as separator symbol
        surnames = re.sub(r' *[/,] *', ' , ', self.surn)   
        
        ''' Surnames processor automation rules
        
        # !state \ input !! delim !! name  !! end
        # |--------------++-------++-------++--------
        # | 0  "Started" || -     || 1,op1 || 3,op3
        # | 1  "name"    || 2,op3 || 1,op4 || 3,op5
        # | 2  "delim"   || -     || 1,op6 || -
        # | 3  "end"     || -     || -     || -
        # | -  "error"   || 
        #TODO: Each '-' should cause an error!
         For example rule "2,op3" means operation op3 and new state 2.
        '''
        for nm in surnames.split():
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




    def _format_row(self, level, tag, value):
        ''' Builds a gedcom row '''
        return("{} {} {}".format(level, tag, str.strip(value)))


#     def _append_gedline(self, level, tag, value):
#         ''' Stores the row as a GedcomLine so that previous values are replaces and 
#             right order is preserved.
#             1. Inset NAME row on the top
#             2. Is the same path is found in self.rows[x]?
#                2.1 Yes: if self.rows(x) has an empty value
#                    3.1 Replace the row with given data
#                    3.2 Else if there is a different self.rows(x).value: 
#                        append a new row 
#                2.2 No: append the row
#         '''
#         gl = GedcomLine(self._format_row(level, tag, value))
#         gl.set_path(level, tag) # Turha???
#         if tag == "NAME":
#             # 1. Add NAME row to the top
#             print("#1.  row(0) <– {} ({!r})".format(gl.path, gl.value), 
#                   file=stderr)
#             self.rows = [gl] + self.rows
#             return
# 
#         for x in range(len(self.rows)):
#             if self.rows[x].path == gl.path:
#                 # 2.1 The same path found in rows(x)
#                 v = self.rows[x].value
#                 print("#2.1 row({}) ({!r}) <– {} ({!r})".format(x, v, 
#                       gl.path, gl.value), file=stderr)
#                 self.rows[x] = gl
#                 if v != "":
#                     # 3.1 Replace curent row
#                     print("#3.1 row({}) ({!r}) <– {} ({!r})".format(x, v, gl.path,
#                           gl.value), file=stderr)
#                     self.rows[x] = gl
#                     return
#                 else:
#                     if v != value:
#                         # 3.2 Previous value is different: 
#                         #     f.ex. there are multiple SURN tags for a name
#                         print("#3.2 row({}) ({!r}) <= {} ({!r})".format(len(self.rows), 
#                                     v, gl.path, gl.value), file=stderr)
#                         self.rows.append(gl)
#                         return
# 
#         # 2.2 Path not found            
#         print("#2.2 row({}) <= {} ({!r})".format(len(self.rows), gl.path, gl.value), 
#               file=stderr)
#         self.rows.append(gl)
