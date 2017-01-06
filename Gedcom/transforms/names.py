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
        - The components of "1 NAME" line are stored and
          modified NAME line is written out
        - The following level 2 name data (GIVN, SURN, NICK, SPFX) are replaced with the stored values if available
        - a new "2 _CALL" line shall be added (call name)

    TODO: 
        - The SPFX line does not print to output file

Created on 26.11.2016

@author: JMä
'''

from classes.person_name import PersonName

def add_args(parser):
    pass

def initialize(args):
    global pname        # Active Name object
    global state        # 0 = start, 1 = indi processing, 2 = name processing
    state = 0
    pname = None

# Process automation operations
#
def create_name_group():
    # Create new PersonName
    global pname

    pname = PersonName()
    
def add_to_name_group(path, level, tag, value):
    # Save current line in pname
    global pname

    pname.add(path, level, tag, value)
    
def emit_name_group(f):
    # Print the lines of pname to output file
    global pname

    if type(pname) is PersonName:
        # Name group ended; Emit previous pname rows
        for row in pname.lines():
            f.emit(row)
        pname = None

# ------------------------------


def phase3(args,line,level,path,tag,value,f):
    '''
    Function phase3 is called once for each line in the input GEDCOM file.
    This function should produce the output GEDCOM by calling output_file.emit
    for each line in the output file.
    If an input line is not modified then emit should
    be called with the original line as the parameter.

    Arguments example:
        args=Namespace(display_changes=False, dryrun=True, encoding='utf-8', \
             input_gedcom='../Mun-testi.ged', transform='names')
        line='1 NAME Antti /Puuhaara/'
        level=1
        path='@I0001@.NAME'
        tag='NAME'
        value='Antti /Puuhaara/'
        f=<__main__.Output object at 0x101960fd0>
    '''

    global pname
    global state
    #print("# Phase3: args={!r}, line={!r}, path={!r}, tag={!r}, value={!r}, f={!r}".\
    #      format(args,line,path,tag,value,f))

    # Process automation engine

    if state == 0:      # Start, no active INDI
        # The lines are written to output file
        f.emit(line)
        if level == 0 and value == 'INDI':
            state = 1
        return

    if state == 1:      # INDI processing active
        if level == 0:
            # End of this individual
            f.emit(line)
            state = 0
            return

        if level == 1 and tag == 'NAME':    # line like '1 NAME Maija Liisa* /Nieminen/'
            # Start of first name definition
            create_name_group()
            add_to_name_group(path, level, tag, value)
            state = 2
            return

        # Other INDI lines are written to output file
        f.emit(line)
        return
    
    if state == 2:      # NAME processing active
        if level == 0:
            # End of Name and Indi group
            emit_name_group(f)
            if value == 'INDI':
                state = 1
            else:
                state = 0
            f.emit(line)
        else:
            if level > 1:
                # Lines in Name group
                add_to_name_group(path, level, tag, value)
            else:
                # Level 1, end of Name group
                emit_name_group(f)
                if tag == 'NAME':
                    create_name_group()
                    add_to_name_group(path, level, tag, value)
                else:
                    state = 1
                    f.emit(line)
        return
