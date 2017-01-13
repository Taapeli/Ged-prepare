#!/usr/bin/python3

"""
Get the family data of the person from the Neo4j database.
Jorma Haapasalo, 2017.
 
"""

import sys
import argparse
from sys import stderr
from classes.genealogy import connect_db, Family, Person

connect_db()
    

def get_family_data(handle):

    # Get Family data
    
    try:
        f = Family()
        f.handle = handle
        result = f.get_family_data()
        for record in result:
            f.id = record["family"]['id']
            f.rel_type = record["family"]['rel_type']
            
        result = f.get_father()
        for record in result:
            f.father = record["father"]
             
        result = f.get_mother()
        for record in result:
            f.mother = record["mother"]
            
        f.print_data()
    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)


def process_neo4j(args):

    # Get family data of the person
    try:
    
        p = Person()
        p.handle = args.handle
        result = p.get_family()
        for record in result:
            print(record)
            get_family_data(record["handle"])

    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)


def main():
    parser = argparse.ArgumentParser(description='The family data of the person from Neo4j')
    parser.add_argument('handle', help="Handle of the people whose data be fetched")

    if len(sys.argv) == 1:
        print("First argument must be the handle, which is the key of this search")
        return

    args = parser.parse_args()

    process_neo4j(args)


if __name__ == "__main__":
    main()
