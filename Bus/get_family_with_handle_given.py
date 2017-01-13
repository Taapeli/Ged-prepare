#!/usr/bin/python3

"""
Get the family data of the person from the Neo4j database.
Jorma Haapasalo, 2017.
 
"""

import sys
import argparse
from sys import stderr
from classes.genealogy import connect_db, Event, Family, Name, Person

connect_db()
    

def get_family_data(handle):

    # Get Family data
    
    try:
        f = Family()
        f.handle = handle
        family_result = f.get_family_data()
        for family_record in family_result:
            f.id = family_record["family"]['id']
            f.rel_type = family_record["family"]['rel_type']
            
        print("\nFATHER: ")
        father_result = f.get_father()
        for father_record in father_result:            
            father = Person()
            father.handle = father_record["father"]
            
            father_name_result = father.get_name_data()
            for father_name_record in father_name_result:
                father.gender = father_name_record["person"]['gender']
                father.name = []
                if len(father_name_record["name"]) > 0:
                    pname = Name()
                    pname.alt = father_name_record["name"]['alt']
                    pname.type = father_name_record["name"]['type']
                    pname.first = father_name_record["name"]['first']
                    pname.surname = father_name_record["name"]['surname']
                    pname.suffix = father_name_record["name"]['suffix']
                    father.name.append(pname)
                    
                    birth_result = father.get_birth_handle()
                    for birth_record in birth_result:
                        event = Event()
                        event.handle = birth_record["handle"]
                    
                        event_result = event.get_event_date()
                        for event_record in event_result:
                            event_date = event_record["date"]
                            print("Birth date: " + str(event_date))
                            
                father.print_data()
                      
        print("\nMOTHER: ")
        mother_result = f.get_mother()
        for mother_record in mother_result:            
            mother = Person()
            mother.handle = mother_record["mother"]
            
            mother_name_result = mother.get_name_data()
            for mother_name_record in mother_name_result:
                mother.gender = mother_name_record["person"]['gender']
                mother.name = []
                if len(mother_name_record["name"]) > 0:
                    pname = Name()
                    pname.alt = mother_name_record["name"]['alt']
                    pname.type = mother_name_record["name"]['type']
                    pname.first = mother_name_record["name"]['first']
                    pname.surname = mother_name_record["name"]['surname']
                    pname.suffix = mother_name_record["name"]['suffix']
                    mother.name.append(pname)
                                        
                    birth_result = mother.get_birth_handle()
                    for birth_record in birth_result:
                        event = Event()
                        event.handle = birth_record["handle"]
                    
                        event_result = event.get_event_date()
                        for event_record in event_result:
                            event_date = event_record["date"]
                            print("Birth date: " + str(event_date))

                mother.print_data()
                            
        print("\nCHILDREN: ")
        children_result = f.get_children()
        for children_record in children_result:            
            child = Person()
            child.handle = children_record["children"]
            children_name_result = child.get_name_data()
            for children_name_record in children_name_result:
                child.gender = children_name_record["person"]['gender']
                child.name = []
                if len(children_name_record["name"]) > 0:
                    pname = Name()
                    pname.alt = children_name_record["name"]['alt']
                    pname.type = children_name_record["name"]['type']
                    pname.first = children_name_record["name"]['first']
                    pname.surname = children_name_record["name"]['surname']
                    pname.suffix = children_name_record["name"]['suffix']
                    child.name.append(pname)
                                        
                    birth_result = child.get_birth_handle()
                    for birth_record in birth_result:
                        event = Event()
                        event.handle = birth_record["handle"]
                    
                        event_result = event.get_event_date()
                        for event_record in event_result:
                            event_date = event_record["date"]
                            print("\nBirth date: " + str(event_date))
                            
                child.print_data()
            
    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)


def process_neo4j(args):

    # Get family data of the person
    try:
    
        p = Person()
        p.handle = args.handle
        result = p.get_family_handle()
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
