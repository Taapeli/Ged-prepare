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
             'tytär', 't.', 'dotter', 'dr.', ]
_SURN = {'os.':'avionimi', 'o.s.':'avionimi', 'ent.':'entinen', 'e.':'entinen', '/':'AKA', ',':'AKA'}
_VON = ['von', 'af', 'de la', 'de']
_BABY = {"vauva":"U", "poikavauva":"M", "tyttövauva":"F", 
         "poikalapsi":"M", "tyttölapsi":"F", "lapsi":"U"}
#TODO: Lyhenteet myös ruotsiksi

DEBUG=False
def debug(s):
    if DEBUG:
        print (s, file=stderr)


class PersonName(GedcomLine):
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

#     def __str__(self):
#         return "{} NAME {}".format(self.level, self.value)


    def __init__(self, gedline):
        ''' Creates a new instance on person name definition.
            The arguments must be a NAME gedcom line.
        '''
#       Example: GedLine{
#         path='@I0001@.NAME'
#         level=2
#         tag='NAME'
#         value='Anders (Antti)/Puuhaara e. Träskalle/' }

        self.rows = []
        if type(gedline) == GedcomLine:
            tup = (gedline.level, gedline.tag, gedline.value)
        else:
            tup = gedline
        GedcomLine.__init__(self, tup)


    def add_line(self, gedline):
        ''' Adds a new, descendant row with higher level number to person name structure

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


    def get_person_rows(self): 
        ''' Analyze this NAME and return it's GedcomLines:
            first NAME and then the descendant rows in the level hierarchy.
            The rules about merging original and generated values should be applied here
        '''
        ''' 1) Full name parts like 'givn/surn/nsfx' will be isolated and analyzed '''
        # Split 'ginv/surn/nsfx' from NAME line
        s1 = self.value.find('/')
        s2 = self.value.rfind('/')
        if s1 >= 0 and s2 >= 0 and s1 != s2:     
            # Contains '.../Surname/...' or even '.../Surname1/Surname2/...' etc
            self.givn = self.value[:s1].rstrip()
            self.surn = self.value[s1+1:s2]
            self.nsfx = self.value[s2+1:]
        else:
            self.givn = ''
            self.surn = self.value
            self.nsfx = ''
            
        ''' 1.1) GIVN given name part rules '''
        self._evaluate_givn()
        ''' 1.2) nsfx Suffix part: nothing to do? '''
        pass
        ''' 1.3) SURN Surname part: pick each surname as a new PersonName
                 Creates NAME, GIVN, SURN, NSFX rows and their associated lines into self.rows
        '''
        ret = []    # List of merged lines
        for pn in self._extract_surnames():
            debug('#' + str(pn))
            # Merge original and new rows
            self._create_gedcom_rows(pn)
            # Collect merged rows
            ret.extend(pn.rows)
        return ret

    # ---- Local functions ----
    
    def _evaluate_givn(self):
        ''' Process given name part of NAME record '''

        def _match_patronyme(nm):
            '''Returns patronyme suffix, if matches, else None'''
            for suff in _PATRONYME:
                if nm.endswith(suff):
                    return suff
            return None


        if self.givn:
            gnames = self.givn.split()
            
            # 1.1a) Find if last givn is actually a patronyme; mark it as new nsfx 
            
            if (len(gnames) > 0):
                nm = gnames[-1]
                if _match_patronyme(nm) != None:
                    self.nsfx_orig = self.nsfx
                    self.nsfx = nm
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


    def _extract_surnames(self):
        ''' Process surname part of NAME record and return a list of PersonNames,
            which are generated from each surname mentioned
        Examples:
            "Mattila"                  => PersonName[0]="givn/Mattila/"
            "Frisk os. Mattila"        => PersonName[0]="givn/Mattila/"
                                          PersonName[1]="givn/Frisk/" TYPE="avionimi"
            "Surname1/Surname2"        => PersonName[0]="givn/Surname1/"
                                          PersonName[1]="givn/Surname2/" TYPE="tunnettu myös"
            "Reipas e. Frisk os. Laine"=> PersonName[0]="givn/Laine/"
                                          PersonName[1]="givn/Frisk/" TYP="avionimi"
                                          PersonName[2]="givn/Reipas/" TYPE="otettu nimi"
            "Lehti os. Lampi e. Damm"  => PersonName[0]="givn/Damm/"
                                          PersonName[1]="givn/Lampi/" TYP="otettu nimi"
                                          PersonName[2]="givn/Lehti/" TYPE="avionimi"
        '''

        if self.value == '':
            return None
        ret = []
        for nm, name_type in self._get_surname_list():
            #TODO: nsfx_new käsittelemättä
            name = '{}/{}/{}'.format(self.givn, nm, self.nsfx)
            pn = PersonName((self.level, 'NAME', name))
            pn.surn = nm
            pn.givn = self.givn
            pn.nsfx = self.nsfx
            if hasattr(self,'nsfx_org'):
                pn.nsfx_orig = self.nsfx_orig
            if hasattr(self,'call_name'):
                pn.call_name = self.call_name
            if name_type:
                pn.set_attr('TYPE', name_type)
#             self._put_person(nm, name_type)
            ret.append(pn)
        return ret


    def _get_surname_list(self):
        ''' Returns a list of {name:type} pairs parsed from self.surn '''
        
        # convert "/" and "," to a single separator symbol " , "
        surnames = re.sub(r' *[/,] *', ' , ', self.surn).split()
        ret = []
        # Following surnames automate reads surnames and separators from right to left
        # and writes PersonNames to self.rows(?) '''
        #
        #    !state \ input !! delim ! name  ! end
        #    |--------------++-------+-------+--------
        #    | 0 "Started"  || -     | 1,op1 | -
        #    | 1 "name"     || 2,op2 | 1,op3 | 3,op4
        #    | 2 "delim"    || -     | 1,op1 | -
        #    | 3 "end"      || -     | -     | -
        #    | - "error"    || 
        ##TODO: Each '-' should cause an error!
        #    For example rule "2,op3" means operation op3 and new state 2.
        #        op1: save name=nm, clear oper
        #        op2: return { PersonName(name): oper[delim] }
        #        op3: concatenate a two part name
        #        op4: return { PersonName(name): oper[delim] }

        state = 0
#         orig_name = ""
        for nm in reversed(surnames):
            if state == 0 or state == 3:        # Start state
                #op1 Only name expected
                name = nm
                oper = ''
                state = 1
            elif state == 1 or state == 2:      # Possible separator state / 
                                                # left side name has been stored
                if nm in _SURN:
                    #op2: A separator 'os.', ... found: 
                    #      Create PersonName rows with the left side name and it's type
                    ret.append((name, oper))
                    name = ''
                    oper = _SURN[nm]
                    state = 2
                else:
                    #op3: Another name found
                    name = str.rstrip(nm + ' ' + name)

        #op4: End: output the last name and it's type
        ret.append((name, oper))
        return ret


    def _format_row(self, level, tag, value):
        ''' Builds a gedcom row '''
        return("{} {} {}".format(level, tag, str.strip(value)))


    def _create_gedcom_rows(self, pn):
        ''' Stores the given PersonName as GedcomLines so that previous values of pn.rows are merged.
            This is important, as original lines may have descentants like SOUR, which must be kept
            in place.
            1. Inset NAME row on the top
            2. Loop trough original GedcomLines self.rows 
               2.1 If tag GIVN, SURN or NSFX is found, update/report the pn.row
               2.2 Else copy self.row the to pn.rows
            3. Create new pn.rows, if any of GIVN, SURN or NSFX is not used
        '''

        def i_tag(tag):
            ''' Is this one of my unused tags? Return corresponding value or None '''
            for i in range(len(my_tags)):
                if my_tags[i][0] == r.tag:
                    # Remove used tag and return it's value
                    ret = my_tags[i][1]
                    del my_tags[i]
                    return ret
            return None
        
        def report_change(tag, value, new_value):
            ''' Report a report_change value for a tag '''
            pn.rows.append(GedcomLine((self.level+1, _CHGTAG + tag, value)))
            if self.path.endswith(tag):
                path = self.path
            else:
                path = "{}.{}".format(self.path, tag)
            print ("{} {!r:>36} ––> {!r}".format(path, value, new_value))
            
        my_tags = [['NAME', pn.value], ['GIVN', pn.givn], ['SURN', pn.surn], \
                   ['NSFX', pn.nsfx], ['TYPE', pn.get_attr('TYPE')]]
        if hasattr(pn, 'call_name'):
            my_tags.append(['_CALL', pn.call_name])
#             print('{} on {!r}'.format(pn.givn, pn.call_name))

        # 1. The first row is the PersonName (inherited class from GedcomLine)
        orig_rows = [self]
        orig_rows.extend(self.rows)
        # For name comparison
        name_self = re.sub(r' ', '', self.value)

        # 2. r = original onput gedcom self.row 
        for r in orig_rows:
            # 2.1 Is there a new value for this line
            new_value = i_tag(r.tag)
            if new_value:
#                 if r.value != new_value:
#                     debug("#{:>36} repl row[{}] {} {!r}<–{!r}".\
#                           format(r.path, len(pn.rows), r.tag, r.value, new_value))
#                 else:
#                     debug("#{:>36} keep row[{}] {} {!r}".\
#                           format(r.path, len(pn.rows), r.tag, new_value))
                pn.rows.append(GedcomLine((r.level, r.tag, new_value)))
                # Show NAME differences 
                if r.tag == 'NAME' and pn.value != name_self: 
                    report_change(r.tag, self.value, new_value)
#                     print ("{} {!r:>36} ––> {!r}".format(self.path, self.value, new_value))
#                     pn.rows.append(GedcomLine((self.level+1, _CHGTAG + self.tag, self.value)))
                if r.tag == 'NSFX' and hasattr(self, 'nsfx_orig'):
                    report_change(r.tag, self.value, self.nsfx_orig)
#                     print ("{} {!r:>36} ––> {!r}".format(self.path, self.nsfx_orig, self.value))
#                     pn.rows.append(GedcomLine((self.level+1, _CHGTAG + self.tag, self.value)))
                continue
            # 2.2 Only append to pn.row
            debug("#{:>36} add  row[{}] {} {!r}".\
                  format(r.path, len(pn.rows), r.tag, r.value))
            pn.rows.append(GedcomLine((r.level, r.tag, r.value)))

        # 3 Create new rows for unused tags
        for tag, value in my_tags:
            if value:
                displ_path = "{},{}".format(self.path, tag)
                debug("#{:>36} new  row[{}] {} {!r}".\
                      format(displ_path, len(pn.rows), tag, value))
                pn.rows.append(GedcomLine((pn.level + 1, tag, value)))
                if tag == 'NSFX' and hasattr(self, 'nsfx_orig'):
                    report_change(tag, self.nsfx_orig, self.nsfx)
#                     print ("{} {!r:>36} ––> {!r}".format(self.path, self.nsfx_orig, self.value))
#                     pn.rows.append(GedcomLine((self.level+1, _CHGTAG + self.tag, self.value)))
