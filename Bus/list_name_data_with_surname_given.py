#!/usr/bin/python3

"""
List some data of the people with given surname from the Neo4j database.
Jorma Haapasalo, 2016.
 
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
        result = p.get_name_data()
        for record in result:
            p.gender = record["person"]['gender']
            p.name = []
            if len(record["name"]) > 0:
                pname = Name()
                pname.alt = record["name"]['alt']
                pname.type = record["name"]['type']
                pname.first = record["name"]['first']
                pname.surname = record["name"]['surname']
                pname.suffix = record["name"]['suffix']
                p.name.append(pname)
            p.print_data()
    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)


def process_neo4j(args):

    # List some data of the people with given surname
    try:
    
        result = Name.get_people_with_surname(args.surname)
        for record in result:
            get_name_data(record["handle"])

    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)


def main():
    parser = argparse.ArgumentParser(description='Some data of the people with given surname from Neo4j')
    parser.add_argument('surname', help="Surname of the people whose data be fetched")

    if len(sys.argv) == 1:
        print("First argument must be the surname, which is the key of this search")
        return

    args = parser.parse_args()

    process_neo4j(args)


if __name__ == "__main__":
    main()
