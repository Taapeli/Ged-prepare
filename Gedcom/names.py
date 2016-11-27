'''
Created on 26.11.2016

@author: jm
'''

from classes.person_name import PersonName

def add_args(parser):
    pass

def initialize(args):
    global pname
    pname = None
    pass

def phase1(args,line,path,tag,value):
    '''
    Function phase1 is called once for each line in the input GEDCOM file. 
    It if be used to collect and store information about the GEDCOM 
    to be used in the subsequent phases.
    
    Example:
        args=Namespace(display_changes=False, dryrun=True, encoding='utf-8', input_gedcom='../mun-testi.ged', transform='names') 
        line='1 NAME Antti /Puuhaara/', 
        path='@I0001@.NAME' 
        tag='NAME' 
        value='Antti /Puuhaara/'

    '''
    global pname
    if line.startswith("1 NAME"):  # @indi@.NAME Antti /Puuhaara/
        pname = PersonName()
        print ('# / {}'.format(path))
        
    if pname:
        if pname.add(path, tag, value):
            print("#   Add {}: {}".format(path, value))
        else:
            pname = None
            print ('# \\ {}'.format(path))
#     if path.endswith(".WIFE"):  # @fam@.WIFE @wife@
#         parts = path.split(".")
#         fam = parts[0]
#         #wives[fam] = value
#         fams[fam].wife = value
#     if path.endswith(".MARR.DATE"):  # @fam@.MARR.DATE date
#         parts = path.split(".")
#         fam = parts[0]
#         #dates[fam] = value
#         fams[fam].date = value
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
    '''
    global pname
    
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


if __name__ == '__main__':
    pass