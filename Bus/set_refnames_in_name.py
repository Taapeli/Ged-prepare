#!/usr/bin/python3

"""
Set refnames of the all first names in the Neo4j database.
Jorma Haapasalo, 2017.
 
"""

import argparse
import time
from sys import stderr
from classes.genealogy import connect_db, Name, Refname

connect_db()


def process_neo4j(args):

    # List refnames of all names in the Neo4j database
    # If there is no refname in db, then the name is handled as a refname.
    try:
    
        t = time.perf_counter()

        result = Name.get_all_first_names()
        for record1 in result:
            first = record1["first"]
            
            ref_name = ''
            names = first.split(" ")
            for name in names:
                record2 = None # If there is no refname
                result = Refname.get_refname(name)
                
                for record2 in result:
#                    aname = record2["aname"]
                    bname = record2["bname"]
                    ref_name = ref_name + " " + bname
                    # print("\nName: " + aname + " ---> Refname: " + bname)
                    
                if not record2:
                    ref_name = ref_name + " " + name
                    
            print("\nName in db: " + first + " ---> refname: " + ref_name)
            
            n = Name()
            n.first = first
            n.refname = ref_name
            n.set_refname()
                   
                           
        elapsed_time = time.perf_counter() - t
        print("\nTime needed: " + str(elapsed_time) + " seconds")

    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)


def main():
    parser = argparse.ArgumentParser(description='Set reference name to all first names in Neo4j')

    args = parser.parse_args()

    process_neo4j(args)


if __name__ == "__main__":
    main()
