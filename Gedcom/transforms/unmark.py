#!/usr/bin/env python3
"""
Restores marked tags: <tag>-X -> <tag>
"""

version = "1.0"

def add_args(parser):
    pass

def initialize(args):
    pass

def phase3(args,line,level,path,tag,value,f):
    if tag.endswith("-X"):
        tag = tag[:-2]
        line = "{} {} {}".format(level,tag,value)
    f.emit(line)


