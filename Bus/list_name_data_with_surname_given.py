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
    

def get_name_data(handle, pid):

    # Get Person and Name data
    
    try:
        p = Person(handle, pid)
        results = p.get_name_data()
        for result in results:
            p.gender = result[0]['gender']
            p.name = []
            if len(result[1]) > 0:
                pname = Name()
                pname.alt = result[1]['alt']
                pname.type = result[1]['type']
                pname.first = result[1]['first']
                pname.surname = result[1]['surname']
                pname.suffix = result[1]['suffix']
                p.name.append(pname)
            p.print_data()
    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)


def process_neo4j(args):

    # List some data of the people with given surname
    try:
    
        results = Name.get_people_with_surname(args.surname)
        for result in results:
            get_name_data(result[0], result[1])

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
