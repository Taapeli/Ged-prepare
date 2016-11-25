#!/usr/bin/env python3

"""
Generic GEDCOM transformer.

The transforms are specified by separate Python modules ("plugins"). 

The name of the plugin is passed as the first parameter. This can be the name of the Python file ("module.py") 
or just the name of the module ("module"). In both case the .py file must be in the current directory
or on the PYTHONPATH.

The second parameter is the name of the input GEDCOM file. This is also the name of the output file.

An optional --encoding parameter can be passed to specify the character encoding used to 
read and write the GEDCOM files. The default is UTF-8.

The optional parameter --display_changes can be specified to allow the plugins to
show the modification. The plugin must implement the logic to do that.
 
The optional parameter --dryrun means that the changes are not saved and the input file is not modified.

If the --dryrun parameter is not specified then the original input file is
renamed by adding a sequence number to the file name and the new version of
the file is saved with the same name as the input file. These names are displayed at the
end of the program.

A plugin may contain the following functions:

- add_args(parser)            
- initialize(args)
- phase1(args,line,path,tag,value)
- phase2(args)
- phase3(args,line,path,tag,value,output_file)
            
Function phase1 and phase2 are optional - or they can be defined with an empty body (pass).

Function initialize is called once in the beginning of the transformation.

Function phase1 is called once for each line in the input GEDCOM file. It can be used to collect
and store information about the GEDCOM to be used in the subsequent phases.

Function phase2 is called once after phase1 but before phase2. 

Function phase3 is called once for each line in the input GEDCOM file. It is called after phase2.
This function should produce the output GEDCOM by calling output_file.emit
for each line in the output file. If an input line is not modified then emit should
be called with the original line as the parameter.

The parameters:
- "args" is the object returned by ArgumentParser.parse_args.
- "line" is the original line in the input GEDCOM (unicode string)
- "path" is the current hierarchy of the GEDCOM tags, e.g @I123@.BIRT.DATE representing the DATE tag
  inside the BIRT tag for the individual @I123@.
- "tag" is the current tag (last part of path)
- "value" is the value for the current tag, e.g. a date or a name
- "output_file" is a file-like object containing the method emit(string) that is used to produce the output
- "parser" is the ArgumentParser object of the argparse module

The function add_args is called in the beginning of the program and it allows
the plugin to add its own arguments for the program. The values of the arguments
are stored in the "args" object that is passed to the other functions. 

"""


import sys
import os
import argparse
from collections import defaultdict 
import re
import tempfile 

def numeric(s):
    return s.replace(".","").isdigit()

class Output:
    def __init__(self,args):
        self.args = args
    def __enter__(self):
        self.tempname = tempfile.mktemp()
        self.f = open(self.tempname,"w",encoding=self.args.encoding)
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.f.close()        
        if not self.args.dryrun:
            self.save() 
         
    def emit(self,s):  
        self.f.write(s+"\n")        
    def save(self):
        input_gedcom = self.args.input_gedcom
        newname = self.generate_name(input_gedcom)
        os.rename(input_gedcom,newname)
        os.rename(self.tempname,input_gedcom)
        print("Input file renamed to '{}'".format(newname))
        print("New version saved as '{}'".format(input_gedcom))
    def generate_name(self,name):
        i = 0 
        while True:
            newname = "{}.{}".format(name,i)
            if not os.path.exists(newname): return newname
            i += 1  

         
def read_gedcom(args):
    curpath = [None]
    for linenum,line in enumerate(open(args.input_gedcom,encoding=args.encoding)):
        
        line = line[:-1]
        if line[0] == "\ufeff": line = line[1:]
        tkns = line.split(None,2)
        level = int(tkns[0])
        tag = tkns[1]
        if level > len(curpath):
            raise RuntimeError("Invalid level:"+line)
        if level == len(curpath):
            curpath.append(tag)
        else:
            curpath[level] = tag
            curpath = curpath[:level+1] 
        if len(tkns) > 2: 
            value = tkns[2]
        else:
            value = ""
        yield (line,".".join(curpath),tag,value)

            
def process_gedcom(args,transformer):

    transformer.initialize(args)
    
    if hasattr(transformer,"phase1"):
        for line,path,tag,value in read_gedcom(args):
            transformer.phase1(args,line,path,tag,value)

    if hasattr(transformer,"phase2"):
        transformer.phase2(args)

    with Output(args) as f:
        for line,path,tag,value in read_gedcom(args):
            transformer.phase3(args,line,path,tag,value,f)


                       
def main(): 
    parser = argparse.ArgumentParser(description='GEDCOM transformations')
    parser.add_argument('transform', help="Name of the transform (Python module)")
    parser.add_argument('input_gedcom', help="Name of the input GEDCOM file")
    #parser.add_argument('output_gedcom', help="Name of the output GEDCOM file; this file will be created/overwritten" ) 
    parser.add_argument('--display-changes', action='store_true',
                        help='Display changed rows')
    parser.add_argument('--dryrun', action='store_true',
                        help='Do not produce an output file')
    #parser.add_argument('--display-nonchanges', action='store_true',
    #                    help='Display unchanged places')
    parser.add_argument('--encoding', type=str, default="utf-8",
                        help="UTF-8, ISO8859-1 tai jokin muu")
 
    if len(sys.argv) > 1 and sys.argv[1][0] == '-' and sys.argv[1] not in ("-h","--help"):
        print("First argument must be the name of the transform")
        return
     
    if len(sys.argv) > 1 and sys.argv[1][0] != '-': 
        modname = sys.argv[1]
        if modname.endswith(".py"): modname = modname[:-3]
        transformer = __import__(modname)
        transformer.add_args(parser)
    
    args = parser.parse_args()
    
    process_gedcom(args,transformer)

    
if __name__ == "__main__":
    main()


