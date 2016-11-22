#!/usr/bin/env python3

"""
Lähettäjä: <pekka.valta@kolumbus.fi>
Päiväys: 12. marraskuuta 2016 klo 17.26
Aihe: Kastettu paikan korjaus
Vastaanottaja: "Kujansuu, Kari" <kari.kujansuu@gmail.com>
Kopio: Juha Mäkeläinen <juha.makelainen@iki.fi>


Moi,
yhdessä gedcomissa oli runsaasti syntymäpaikkoja muodossa "(kastettu) Oulu". Ilmeisesti sukututkimusohjelma ei ole tukenut kastetiedon kunnon rekisteröintiä.

Voisitko lisätä paikkojen käsittelyyn säännön, että jos

1 BIRT
2 PLAC (kastettu) xxx

niin muutetaan muotoon

1 CHR
2 PLAC xxx

t.
Pekka

"""
import sys
import os
import argparse
from collections import defaultdict 
import re

def numeric(s):
    return s.replace(".","").isdigit()

class Output:
    def __init__(self,args):
        self.args = args
    def __enter__(self):
        if self.args.output_gedcom:
            self.f = open(self.args.output_gedcom,"w",encoding=self.args.encoding)
        else:
            self.f = None
        return self
        
    def emit(self,s):
        if self.f:
            self.f.write(s+"\n")        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.f:
            self.f.close()        
         
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
    parser.add_argument('output_gedcom', help="Name of the output GEDCOM file; this file will be created/overwritten" ) 
    #parser.add_argument('--display-changes', action='store_true',
    #                    help='Display changed places')
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


