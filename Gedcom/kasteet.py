#!/usr/bin/env python3

ids = set()

do_phase1 = True

def add_args(parser):
    parser.add_argument("--testiparametri")

def initialize(args):
    pass

def phase1(args,line,path,tag,value):
    if path.endswith(".BIRT.PLAC") and value.startswith("(kastettu)"):  # @id@.BIRT.PLACE (kastettu) xxx
        parts = path.split(".")
        id = parts[0]
        ids.add(id)

def phase2(args):
    pass

def phase3(args,line,path,tag,value,f):
    parts = path.split(".")
    id = parts[0]
    if id in ids:
        if tag == "BIRT": tag = "CHR"
        if tag == "PLAC" and value.startswith("(kastettu)"): value = " ".join(value.split()[1:])
        line = line.split()[0] + " " + tag + " " + value
    f.emit(line)


