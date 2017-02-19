#!/usr/bin/python3

"""
Set refnames to all names in the Neo4j database.
Jorma Haapasalo, 2017.
 
"""

import sys
import argparse
import time
from sys import stderr
from classes.genealogy import connect_db, Name, Refname

connect_db()


def process_neo4j(args):

    # List people with the given name
    try:
    
        t = time.perf_counter()

        result = Name.get_all_first_names()
        for record in result:
            first = record["first"]
            
            names = first.split(" ")
            for name in names:
                result = Refname.get_refname(name)
                
                for record in result:
                    aname = record["aname"]
                    bname = record["bname"]
                    
                    print("\nName: " + aname + " ---> Refname: " + bname)
                           
        elapsed_time = time.perf_counter() - t
        print("\nTime needed: " + str(elapsed_time) + " seconds")

    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)


def main():
    parser = argparse.ArgumentParser(description='Set reference name to all Names in Neo4j')

    args = parser.parse_args()

    process_neo4j(args)


if __name__ == "__main__":
    main()
