#!/usr/bin/python3

"""
Get the reference name of the given first name from the Neo4j database.
Jorma Haapasalo, 2017.
 
"""

import sys
import argparse
from sys import stderr
from classes.genealogy import connect_db, Refname

connect_db()


def process_neo4j(args):

    # List some data of the people with given surname
    try:
    
        names = args.first_name.split(" ")
        for name in names:
            record = None
            r = Refname(name)
            result = r.get_refname()
            for record in result:
                aname = record["aname"]
                bname = record["bname"]
                
                print("\nName: " + aname + " ---> Refname: " + bname)
                
            if not record:
                first_line = "\nName: '" + name + "' is self a reference name.\n"
                result = r.get_name()
                for record in result:
                    aname = record["aname"]
                    bname = record["bname"]
                
                    print(first_line + "\nName: " + aname + " ---> Refname: " + bname)
                    first_line = ''
                
            if not record:
               print("\nName: '" + name + "' is not found")

    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)


def main():
    parser = argparse.ArgumentParser(description='Find reference name of the given first name from Neo4j')
    parser.add_argument('first_name', help="First name of the people whose reference name to be fetched")

    if len(sys.argv) == 1:
        print("First argument must be the first name, which is the key of this search")
        return

    args = parser.parse_args()

    process_neo4j(args)


if __name__ == "__main__":
    main()
