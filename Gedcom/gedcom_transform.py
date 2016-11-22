#!/usr/bin/env python3

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
    parser = argparse.ArgumentParser(description='GEDCOM transformation')
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
 
    if len(sys.argv) > 1 and sys.argv[1][0] != '-': 
        modname = sys.argv[1]
        if modname.endswith(".py"): modname = modname[:-3]
        transformer = __import__(modname)
        transformer.add_args(parser)
    
    args = parser.parse_args()
    
    process_gedcom(args,transformer)

    
if __name__ == "__main__":
    main()


