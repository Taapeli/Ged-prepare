#!/usr/bin/env python3

"""
Generic GEDCOM transformer 
Kari Kujansuu, 2016.

The transforms are specified by separate Python modules ("plugins") in the subdirectory "transforms".

Parameters of main():
 1. The name of the plugin. This can be the name of the Python file ("module.py")
    or just the name of the module ("module").
    In both case the .py file must be in the current directory or on the PYTHONPATH.

 2. The name of the input GEDCOM file. This is also the name of the output file.

 3. "--encoding" [optional] specifies the character encoding used to read and write
    the GEDCOM files. The default is UTF-8.

 4. "--display_changes" [optional] can be specified to allow the plugins to
    show the modification. The plugin must implement the logic to do that.

 5. "--dryrun" [optional] means that no changes are saved and the input file is not modified.

If the --dryrun parameter is not specified then the original input file is
renamed by adding a sequence number to the file name and the new version of
the file is saved with the same name as the input file. These names are displayed at the
end of the program.

A plugin may contain the following functions:

- add_args(parser)
- initialize(args)                              # Called once in the beginning of the transformation
- phase1(args,line,level,path,tag,value)        # [optional] called once per GEDCOM line
- phase2(args)                                  # [optional] called between phase1 and phase2
- phase3(args,line,level,path,tag,value,output_file)
                                                # [optional] called once per GEDCOM line

The function "add_args" is called in the beginning of the program and it allows
the plugin to add its own arguments for the program. The values of the arguments
are stored in the "args" object that is passed to the other functions.

Function "initialize" is called in the beginning of the transformation.

If function "phase1" is defined, it is called once for each line in the input GEDCOM file.
It can be used to collect information to be used in the subsequent phases.

Function "phase2" may be defined for processing all the information got from phase1
before phase3.

Function "phase3" is called once for each line in the input GEDCOM file.
This function should produce the output GEDCOM by calling output_file.emit()
for each line in the output file.
If an input line is not modified then emit should be called with the original line
as it's parameter.

The parameters of each phases:
- "args" is the object returned by ArgumentParser.parse_args.
- "gedline", a GedcomLine() object, which includes
    - "line", the original line in the input GEDCOM (unicode string)
    - "level", the level number of the line (integer)
    - "path", the current hierarchy of the GEDCOM tags, e.g @I123@.BIRT.DATE
      representing the DATE tag inside the BIRT tag for the individual @I123@.
    - "tag", the current tag (last part of path)
    - "value", the value for the current tag, e.g. a date or a name
- "output_file" is a file-like object containing the method emit(string) that is used to produce the output

"""
_VERSION="0.2"

import sys
import os
import getpass
import time
import argparse
import tempfile
from sys import stderr
import importlib

from classes.gedcom_line import GedcomLine

def numeric(s):
    return s.replace(".","").isdigit()

class Output:
    def __init__(self,args):
        self.args = args
        self.log = True
    def __enter__(self):
        args = self.args
        input_gedcom = args.input_gedcom
        if args.output_gedcom:
            self.output_filename = args.output_gedcom
        else:
            tempfile.tempdir = os.path.dirname(input_gedcom) # create tempfile in the same directory so you can rename it later
            self.tempname = tempfile.mktemp()
            self.newname = self.generate_name(input_gedcom)
            self.output_filename = self.tempname
        self.f = open(self.output_filename,"w",encoding=args.encoding)
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.f.close()
        if not self.args.dryrun:
            self.save()

    def emit(self,s):
        self.f.write(s+"\n")
        if self.log:
            self.log = False
            args = sys.argv[1:]
            self.emit("1 NOTE _TRANSFORM v.{} {}".format(_VERSION, sys.argv[0]))
            self.emit("2 CONT _COMMAND {} {}".format(os.path.basename(sys.argv[0]), " ".join(args)))
            user = getpass.getuser()
            if not user:
                user = "Unnamed"
            datestring = time.strftime("%d %b %Y %H:%M:%S", time.localtime(time.time()))
            self.emit("2 CONT _DATE {} {}".format(user, datestring))
            if self.newname:
                self.emit("2 CONT _SAVEDFILE " + self.newname)
    def save(self):
        input_gedcom = self.args.input_gedcom
        if not self.args.output_gedcom:
            os.rename(input_gedcom,self.newname)
            os.rename(self.tempname,input_gedcom)
            print("Input file renamed to '{}'".format(self.newname))
            print("New version saved as '{}'".format(input_gedcom))
        else:
            print("Output saved as '{}'".format(self.args.output_gedcom))
    def generate_name(self,name):
        i = 0
        while True:
            newname = "{}.{}".format(name,i)
            if not os.path.exists(newname): return newname
            i += 1


def read_gedcom(args):
    
    try:
        for linenum, line in enumerate(open(args.input_gedcom, encoding=args.encoding)):
            # Clean the line
            line = line[:-1]
            if line[0] == "\ufeff": 
                line = line[1:]
            # Return a gedcom line object
            gedline = GedcomLine(line, linenum)
            yield gedline

    except FileNotFoundError:
        print("Tiedostoa '{}' ei ole!".format(args.input_gedcom), file=sys.stderr)
        raise
    except Exception as err:
        print(type(err))
        print("Virhe: {0}".format(err), file=sys.stderr)


def process_gedcom(args,transformer):

    transformer.initialize(args)

    # 1st traverse
    if hasattr(transformer,"phase1"):
        for gedline in read_gedcom(args):
            transformer.phase1(args, gedline)
            #transformer.phase1(args,line,level,path,tag,value)

    # Intermediate processing of collected data
    if hasattr(transformer,"phase2"):
        transformer.phase2(args)

    # 2nd traverse "phase3"
    with Output(args) as f:
        for gedline in read_gedcom(args):
            transformer.phase3(args, gedline, f)


def get_transforms():
    # all transform modules should be .py files in the package/subdirectory "transforms"
    for name in os.listdir("transforms"):
        if name.endswith(".py") and name != "__init__.py": 
            modname = name[0:-3]
            transformer = importlib.import_module("transforms."+modname)
            doc = transformer.__doc__
            if doc:
                docline = doc.strip().splitlines()[0]
            else:
                docline = ""
            version = getattr(transformer,"version","")
            yield (modname,transformer,docline,version)


def find_transform(prefix):
    choices = []
    for modname,transformer,docline,version in get_transforms():
        if modname == prefix: return transformer
        if modname.startswith(prefix):
            choices.append((modname,transformer))
    if len(choices) == 1: return choices[0][1]
    if len(choices) > 1: 
        print("Ambiguous transform name: {}".format(prefix))
        print("Matching names: {}".format(",".join(name for name,t in choices)))
    return False


def main():
    print("\nTaapeli GEDCOM transform program A (version {})\n".format(_VERSION))
    parser = argparse.ArgumentParser()
    parser.add_argument('transform', help="Name of the transform (Python module)")
    parser.add_argument('input_gedcom', help="Name of the input GEDCOM file")
    parser.add_argument('--output_gedcom', help="Name of the output GEDCOM file; this file will be created/overwritten" )
    parser.add_argument('--display-changes', action='store_true',
                        help='Display changed rows')
    parser.add_argument('--dryrun', action='store_true',
                        help='Do not produce an output file')
    #parser.add_argument('--display-nonchanges', action='store_true',
    #                    help='Display unchanged places')
    parser.add_argument('--encoding', type=str, default="utf-8",
                        help="e.g, UTF-8, ISO8859-1")
    parser.add_argument('-l', '--list', action='store_true', help="List transforms")

    if len(sys.argv) > 1 and sys.argv[1] in ("-l","--list"):
        print("List of transforms:")
        for modname,transformer,docline,version in get_transforms():
            print("  {:20.20} {:10.10} {}".format(modname,version,docline))
        return

    if len(sys.argv) > 1 and sys.argv[1][0] == '-' and sys.argv[1] not in ("-h","--help"):
        print("First argument must be the name of the transform")
        return

    if len(sys.argv) > 1 and sys.argv[1][0] != '-':
        transformer = find_transform(sys.argv[1])
        if not transformer: 
            print("Transform not found; use -l to list the available transforms")
            return
        transformer.add_args(parser)

    args = parser.parse_args()
    process_gedcom(args,transformer)


if __name__ == "__main__":
    main()
