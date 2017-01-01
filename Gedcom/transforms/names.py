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
        - The SPFX line does not  print to output file
        - CALL names are not processed

Created on 26.11.2016

@author: JMä
'''

from classes.person_name import PersonName

def add_args(parser):
    pass

def initialize(args):
    global pname        # Active Name object
    global isIndi       # True, when processing an Individual

    pname = None
    isIndi = False
    pass

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
        line='1 NAME Antti /Puuhaara/',
        path='@I0001@.NAME'
        tag='NAME'
        value='Antti /Puuhaara/'
        f=<__main__.Output object at 0x101960fd0>

    '''

    global pname
    global isIndi

    #print("# Phase3: args={!r},line={!r},path={!r},tag={!r},value={!r},f={!r}".format(args,line,path,tag,value,f))
    level = line[:1]

#  0. if 0 INDI:
#   Set isIndi=True if a person data block starts

    if level == "0":
        # Is this a line like "0 @I0008@ INDI"?
        isIndi = (value == "INDI")
        # Emit any level 0 line
        f.emit(line)
        return
    if isIndi == False:
        # Emit any line outside person data blocks
        f.emit(line)
        return

# 1. if isIndi: # A Person line

#    1.1 if 1 NAME: # A new name definetion
#        emit (pname.rows()) # if exists
#        new pname()

    if line.startswith("1 NAME"):  # @indi@.NAME Antti /Puuhaara/
        # Check, if previous 1 NAME group has to be completed
        if type(pname) is PersonName:
            # Yes, emit the previous name
            for row in pname.get_rows():
                f.emit(row)

        pname = PersonName()

    if type(pname) is PersonName:

#    1.2 else if pname.add(line): 
#        add() returns True, if line is still part of person name description
#        The stored value is converted when added to person name group

        if pname.add(path, line[:1], tag, value):
            #print("#   ++ {}: {}".format(path, value))
            pass

#    1.3 else: # All names are processed
#        emit all stored rows, clear pname and emit current row

        else:
            for row in pname.get_rows():
                f.emit(row)
            pname = None
            print ('# \\ {}'.format(path))
            f.emit(line)

# 2. else: # Other line, not in any person name group
#    emit (line)

    else:
        f.emit(line)
