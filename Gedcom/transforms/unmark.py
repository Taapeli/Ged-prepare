#!/usr/bin/env python3
"""
Restores marked tags: <tag>-X -> <tag>
"""

version = "1.0"

def add_args(parser):
    pass

def initialize(args):
    pass

def phase3(args,line,path,tag,value,f):
    if tag.endswith("-X"):
        tag = tag[:-2]
        level = line.split()[0]
        line = "{} {} {}".format(level,tag,value)
    f.emit(line)


