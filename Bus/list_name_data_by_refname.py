#!/usr/bin/python3

"""
List some data of the people with given refname from the Neo4j database.
Jorma Haapasalo, 2017.
 
"""

import sys
import argparse
from sys import stderr
from classes.genealogy import connect_db, Name, Person

connect_db()
    

def get_name_data(handle):

    # Get Person and Name data
    
    try:
        p = Person()
        p.handle = handle
        p.get_person_and_name_data()
        p.print_data()
    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)


def process_neo4j(args):

    # List some data of the people with given refname
    try:
    
        result = Name.get_people_with_refname(args.refname)
        for record in result:
            get_name_data(record["handle"])

    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)


def main():
    parser = argparse.ArgumentParser(description='Some data of the people with given refname from Neo4j')
    parser.add_argument('refname', help="Refname of the people whose data be fetched")

    if len(sys.argv) == 1:
        print("First argument must be the refname, which is the key of this search")
        return

    args = parser.parse_args()

    process_neo4j(args)


if __name__ == "__main__":
    main()
