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
        #TODO
        - When a "1 NAME" line is found, a new PersonName object is created
        - The componenst of "1 NAME" line are stored and NAME line is modified
        - The following level 2 name data (GIVN, SURN, NICK, SPFX) are replaced with the stored values if available
        - a new "2 _CALL" line shall be added (call name)

Created on 26.11.2016

@author: JMä
'''

from classes.person_name import PersonName

def add_args(parser):
    pass

def initialize(args):
    global pname
    global isIndi

    pname = None
    isIndi = False
    pass

def phase1(args,line,path,tag,value):
    '''
    Function phase1 is called once for each line in the input GEDCOM file. 
    It if be used to collect and store information about the GEDCOM 
    to be used in the subsequent phases.
    
    Arguments example:
        args=Namespace(display_changes=False, dryrun=True, encoding='utf-8', input_gedcom='../mun-testi.ged', transform='names') 
        line='1 NAME Antti /Puuhaara/', 
        path='@I0001@.NAME' 
        tag='NAME' 
        value='Antti /Puuhaara/'
    '''
    global pname
    global isIndi
    
    if line.startswith("0"):
        # Is this an INDI line like "0 @I0008@ INDI"
        isIndi = (value == "INDI")
        return
    if isIndi == False:
        return
    
    if tag == "NAME":  # @indi@.NAME Antti /Puuhaara/
        pname = PersonName()
        print ('# / {}'.format(path))
        
    if pname:
        if pname.add(path, tag, value):
            print("#   ++ {}: {}".format(path, value))
        else:
            #TODO: Ei saa tuhota pname-sisltöä, se pitää tulostaa emit() 
            pname = None
            print ('# \\ {}'.format(path))
#     if path.endswith(".WIFE"):  # @fam@.WIFE @wife@
#         parts = path.split(".")
#         fam = parts[0]
#         #wives[fam] = value
#         fams[fam].wife = value
#     if path.endswith(".MARR.PLAC"):  # @fam@.MARR.PLAC place
#         parts = path.split(".")
#         fam = parts[0]
#         place = value
#         fams[fam].place = value

# def phase2(args):
#     '''
#     Function phase2 is called once after phase1 but before phase2. 
#     '''
#     for fam,faminfo in fams.items():
#         m = re.match(r"([^,]+), \(([^/]+)/([^/]+)\)",faminfo.place)
#         if m:
#             husb_place = m.group(2)+", "+m.group(1)
#             wife_place = m.group(3)+", "+m.group(1)
#             resi[faminfo.husb].append((husb_place,faminfo.date))
#             resi[faminfo.wife].append((wife_place,faminfo.date))
#             fixedfams[fam] = m.group(1)

def phase3(args,line,path,tag,value,f):
    '''
    Function phase3 is called once for each line in the input GEDCOM file. 
    It is called after phase2.
    This function should produce the output GEDCOM by calling output_file.emit
    for each line in the output file. 
    If an input line is not modified then emit should
    be called with the original line as the parameter.
    
    Arguments example: 
        args=Namespace(display_changes=False, dryrun=True, encoding='utf-8', input_gedcom='Mun-testi.ged', transform='names'),
        line='1 WIFE @I0001@',
        path='@F0001@.WIFE',
        tag='WIFE',
        value='@I0001@',
        f=<__main__.Output object at 0x101960fd0>

    '''
    global pname
    #print("# Phase3: args={!r},line={!r},path={!r},tag={!r},value={!r},f={!r}".format(args,line,path,tag,value,f))
    
    if value == "NAME":
        f.emit(pname.get_name())
#         id = line.split()[1]
#         if id in resi:
#             f.emit(line)
#             for place,date in resi[id]:
#                 f.emit("1 RESI")
#                 f.emit("2 TYPE marriage")
#                 if date: f.emit("2 DATE " + date)
#                 f.emit("2 PLAC " + place)
#             return
#     if path.endswith(".MARR.PLAC"):  # @fam@.MARR.PLAC place
#         parts = path.split(".")
#         fam = parts[0]
#         if fam in fixedfams:
#             level = line.split()[0]
#             line = level + " PLAC " + fixedfams[fam]
#         f.emit(line)
#         return
    else:
        f.emit(line)
