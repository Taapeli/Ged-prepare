#!/usr/bin/python3

"""
Get the family data of the person from the Neo4j database.
Jorma Haapasalo, 2017.
 
"""

import sys
import argparse
from sys import stderr
from classes.genealogy import connect_db, Family, Name, Person

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
            
        print("\nFATHER: ")
        result = f.get_father()
        for record in result:            
            father = Person()
            father.handle = record["father"]
            result = father.get_name_data()
            for record in result:
                father.gender = record["person"]['gender']
                father.name = []
                if len(record["name"]) > 0:
                    pname = Name()
                    pname.alt = record["name"]['alt']
                    pname.type = record["name"]['type']
                    pname.first = record["name"]['first']
                    pname.surname = record["name"]['surname']
                    pname.suffix = record["name"]['suffix']
                    father.name.append(pname)
                father.print_data()
                      
        print("\nMOTHER: ")
        result = f.get_mother()
        for record in result:            
            mother = Person()
            mother.handle = record["mother"]
            result = mother.get_name_data()
            for record in result:
                mother.gender = record["person"]['gender']
                mother.name = []
                if len(record["name"]) > 0:
                    pname = Name()
                    pname.alt = record["name"]['alt']
                    pname.type = record["name"]['type']
                    pname.first = record["name"]['first']
                    pname.surname = record["name"]['surname']
                    pname.suffix = record["name"]['suffix']
                    mother.name.append(pname)
                mother.print_data()
                            
        print("\nCHILDREN: ")
        result = f.get_children()
        for record in result:            
            child = Person()
            child.handle = record["children"]
            result = child.get_name_data()
            for record in result:
                child.gender = record["person"]['gender']
                child.name = []
                if len(record["name"]) > 0:
                    pname = Name()
                    pname.alt = record["name"]['alt']
                    pname.type = record["name"]['type']
                    pname.first = record["name"]['first']
                    pname.surname = record["name"]['surname']
                    pname.suffix = record["name"]['suffix']
                    child.name.append(pname)
                child.print_data()
            
    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)


def process_neo4j(args):

    # Get family data of the person
    try:
    
        p = Person()
        p.handle = args.handle
        result = p.get_family()
        for record in result:
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
