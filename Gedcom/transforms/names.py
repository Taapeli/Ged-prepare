'''
    Processes gedcom lines trying to fix problems of individual name tags

    Input example (originally no indent):
        0 @I0149@ INDI
          1 NAME Johan Johanpoika /Sihvola/
            2 TYPE aka
            2 GIVN Johan Johanpoika
            2 SURN Sihvola
          1 NAME Johan /Johansson/
            2 GIVN Johan
            2 SURN Johansson
            2 SOUR @S0015@
              3 PAGE Aukeama 451, Kuva 289 Sihvola
              3 DATA
                4 DATE 28 JAN 2015
            3 NOTE @N0175@
          1 SEX M
            ...

    Processing:
        - When a "1 NAME" line is found, a new PersonName object is created
        - The components of "1 NAME" line are stored in that object and
          modified NAME line is written to output file
        - The following name data rows are replaced with the stored values if available
        - a new "2 _CALL" or '2 NSFX' lines may be added

Created on 26.11.2016

@author: JMä
'''

from classes.person_name import PersonName
from classes.gedcom_line import GedcomLine

def add_args(parser):
    pass

def initialize(args):
    global pname        # Active Name object
    global state        # 0 = start, 1 = indi processing, 2 = name processing
    state = 0
    pname = None


def phase3(args, gedline, f):
    '''
    Function phase3 is called once for each line in the input GEDCOM file.
    This function should produce the output GEDCOM by calling output_file.emit
    for each line in the output file.
    If an input line is not modified then emit should
    be called with the original line as the parameter.

    Arguments example:
        args=Namespace(display_changes=False, dryrun=True, encoding='utf-8', \
                       input_gedcom='../Mun-testi.ged', transform='names')
        gedline=(
            line='1 NAME Antti /Puuhaara/'
            level=1
            path='@I0001@.NAME'
            tag='NAME'
            value='Antti /Puuhaara/'
        )
        f=<__main__.Output object at 0x101960fd0>
    
    TODO: Store Names and other level +1 lines as members of Indi GedcomLine 
    '''

    global pname
    global state
    #print("# Phase3: args={!r}, line={!r}, path={!r}, tag={!r}, value={!r}, f={!r}".\
    #      format(args,line,path,tag,value,f))

    # ---- INDI automation engine for processing person data ----

    # For all states
    if gedline.level == 0:
        if gedline.value == 'INDI':  # Start new INDI
            # "0 INDI" starts a new logical record
            _T1_emit_and_start_record(gedline, f)
            state = 1
        else:
            # 0 level line ends previous logical record, if any and
            # starts a non-INDI logical record, which is emitted as is
            _T2_emit_record_and_gedline(gedline, f)
            state = 0
        return
    
    # For all but "0 INDI" lines
    if state == 0:      # Started, no active INDI
        # Lines are emitted as is
        _T3_emit_gedline(gedline, f)
        return

    if state == 1:      # INDI processing active
        if gedline.level == 1:
            if gedline.value == 'NAME':
                # Start a new PersonName in GedcomRecord
                _T4_store_name(gedline)
                state = 2
                return

            if gedline.value == 'BIRT':
                state = 3

        # Higher level lines are stored as a new members in the INDI logical record
        _T6_store_member(gedline)
        return
    
    if state == 2:      # NAME processing active in INDI
        if gedline.level == 1:
            # Level 1 lines terminate current NAME group
            if gedline.value == 'NAME':
                # Start a new PersonName in GedcomRecord
                _T4_store_name(gedline)
                state = 2
                return
            # Other level 1 lines terminate NAME and are stored as INDI members
            if gedline.value == 'BIRT':
                state = 3
            else:
                state = 1
            _T6_store_member(gedline)
        else:
            # Higher level lines are stored as a new members in the latest NAME group
            _T7_store_name_member(gedline)
        return

    if state == 3:       # BIRT processing (to find birth date) active in INDI
        if gedline.level == 2 and gedline.tag == 'DATE':
            _T5_save_date(gedline)
            state = 1
            return
        if gedline.level == 1:
            if gedline.value == 'NAME':
                # Start a new PersonName in GedcomRecord
                _T4_store_name(gedline)
                state = 2
            else:
                _T6_store_member(gedline)
                state = 1
            return
        # Level > 1, still waiting DATE
        _T6_store_member(gedline)
        return

    # ---- Automation operations ----

def _T1_emit_and_start_record(gedline, f):
    ''' Emit previous logical person record (if any) and create a new one '''
    pass

def _T2_emit_record_and_gedline(gedline, f):
    ''' Emit previous logical person record (if any) and emit line '''
    pass

def _T3_emit_gedline(gedline, f): 
    ''' Emit current line '''
    f.emit(gedline.get_line())

def _T4_store_name(gedline):
    ''' Save gedline as a new PersonName in the logical person record '''
    global pname
    pname = PersonName(gedline)

def _T5_save_date(gedline):
    ''' Pick year from gedline '''
    return gedline.get_year()

def _T6_store_member(gedline):
    ''' Save a new gedline member in the logical record '''
    pass

def _T7_store_name_member(gedline):
    ''' Save current line in pname '''
    global pname
    pname.add(gedline)
