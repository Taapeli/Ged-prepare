#!/usr/bin/python3

"""
Get the family data of the person from the Neo4j database.
Jorma Haapasalo, 2017.
 
"""

import sys
import argparse
from sys import stderr
from classes.genealogy import connect_db, Event, Family, Name, Person, Place

connect_db()
    

def get_family_data(handle):

    # Get Family data
    
    try:
        f = Family()
        f.handle = handle
        
        f.get_family_object()
        f.print_data()
            
        print("\nFATHER: ")
        father = Person()
        father.handle = f.father

        father.name = []
        
        father_name_result = father.get_name_data()
        for father_name_record in father_name_result:
            father.gender = father_name_record["person"]['gender']
            
            if len(father_name_record["name"]) > 0:
                pname = Name()
                pname.alt = father_name_record["name"]['alt']
                pname.type = father_name_record["name"]['type']
                pname.first = father_name_record["name"]['first']
                pname.surname = father_name_record["name"]['surname']
                pname.suffix = father_name_record["name"]['suffix']
                father.name.append(pname)
                        
        father.print_data()
                
        birth_result = father.get_birth_handle()
        for birth_record in birth_result:
            event = Event()
            event.handle = birth_record["handle"]
        
            event_result = event.get_event_data()
            for event_record in event_result:
                event.id = event_record["event"]["id"]
                event.type = event_record["event"]["type"]
                event.date = event_record["event"]["date"]
                event.print_data()

                event_place_result = event.get_place_handle()
                for event_place_record in event_place_result:
                    place = Place()
                    place.handle = event_place_record["handle"]
                    
                    place_result = place.get_place_data()
                    for place_record in place_result:
                        place.id = place_record["place"]["id"]
                        place.type = place_record["place"]["type"]
                        place.pname = place_record["place"]["pname"]
                        place.print_data()
                
        death_result = father.get_death_handle()
        for death_record in death_result:
            event = Event()
            event.handle = death_record["handle"]
        
            event_result = event.get_event_data()
            for event_record in event_result:
                event.id = event_record["event"]["id"]
                event.type = event_record["event"]["type"]
                event.date = event_record["event"]["date"]
                event.print_data()
        
                event_place_result = event.get_place_handle()
                for event_place_record in event_place_result:
                    place = Place()
                    place.handle = event_place_record["handle"]
                    
                    place_result = place.get_place_data()
                    for place_record in place_result:
                        place.id = place_record["place"]["id"]
                        place.type = place_record["place"]["type"]
                        place.pname = place_record["place"]["pname"]
                        place.print_data()
                      
        print("\nMOTHER: ")
        mother = Person()
        mother.handle = f.mother
        
        mother.name = []

        mother_name_result = mother.get_name_data()
        for mother_name_record in mother_name_result:
            mother.gender = mother_name_record["person"]['gender']
            if len(mother_name_record["name"]) > 0:
                pname = Name()
                pname.alt = mother_name_record["name"]['alt']
                pname.type = mother_name_record["name"]['type']
                pname.first = mother_name_record["name"]['first']
                pname.surname = mother_name_record["name"]['surname']
                pname.suffix = mother_name_record["name"]['suffix']
                mother.name.append(pname)
                
        mother.print_data()

        birth_result = mother.get_birth_handle()
        for birth_record in birth_result:
            event = Event()
            event.handle = birth_record["handle"]
        
            event_result = event.get_event_data()
            for event_record in event_result:
                event.id = event_record["event"]["id"]
                event.type = event_record["event"]["type"]
                event.date = event_record["event"]["date"]
                event.print_data()
        
                event_place_result = event.get_place_handle()
                for event_place_record in event_place_result:
                    place = Place()
                    place.handle = event_place_record["handle"]
                    
                    place_result = place.get_place_data()
                    for place_record in place_result:
                        place.id = place_record["place"]["id"]
                        place.type = place_record["place"]["type"]
                        place.pname = place_record["place"]["pname"]
                        place.print_data()
                
        death_result = mother.get_death_handle()
        for death_record in death_result:
            event = Event()
            event.handle = death_record["handle"]
        
            event_result = event.get_event_data()
            for event_record in event_result:
                event.id = event_record["event"]["id"]
                event.type = event_record["event"]["type"]
                event.date = event_record["event"]["date"]
                event.print_data()
        
                event_place_result = event.get_place_handle()
                for event_place_record in event_place_result:
                    place = Place()
                    place.handle = event_place_record["handle"]
                    
                    place_result = place.get_place_data()
                    for place_record in place_result:
                        place.id = place_record["place"]["id"]
                        place.type = place_record["place"]["type"]
                        place.pname = place_record["place"]["pname"]
                        place.print_data()
                            
        print("\nCHILDREN: ")
        
        for child_link in f.childref_hlink:            
            child = Person()
            child.handle = child_link

            child.name = []
            
            children_name_result = child.get_name_data()
            for children_name_record in children_name_result:
                child.gender = children_name_record["person"]['gender']
                
                if len(children_name_record["name"]) > 0:
                    pname = Name()
                    pname.alt = children_name_record["name"]['alt']
                    pname.type = children_name_record["name"]['type']
                    pname.first = children_name_record["name"]['first']
                    pname.surname = children_name_record["name"]['surname']
                    pname.suffix = children_name_record["name"]['suffix']
                    child.name.append(pname)
                    
            print("\n")
            child.print_data()
            
            birth_result = child.get_birth_handle()
            for birth_record in birth_result:
                event = Event()
                event.handle = birth_record["handle"]
            
                event_result = event.get_event_data()
                for event_record in event_result:
                    event.id = event_record["event"]["id"]
                    event.type = event_record["event"]["type"]
                    event.date = event_record["event"]["date"]
                    event.print_data()
                                        
                    event_place_result = event.get_place_handle()
                    for event_place_record in event_place_result:
                        place = Place()
                        place.handle = event_place_record["handle"]
                        
                        place_result = place.get_place_data()
                        for place_record in place_result:
                            place.id = place_record["place"]["id"]
                            place.type = place_record["place"]["type"]
                            place.pname = place_record["place"]["pname"]
                            place.print_data()
            
            death_result = child.get_death_handle()
            for death_record in death_result:
                event = Event()
                event.handle = death_record["handle"]
            
                event_result = event.get_event_data()
                for event_record in event_result:
                    event.id = event_record["event"]["id"]
                    event.type = event_record["event"]["type"]
                    event.date = event_record["event"]["date"]
                    event.print_data()
            
                    event_place_result = event.get_place_handle()
                    for event_place_record in event_place_result:
                        place = Place()
                        place.handle = event_place_record["handle"]
                        
                        place_result = place.get_place_data()
                        for place_record in place_result:
                            place.id = place_record["place"]["id"]
                            place.type = place_record["place"]["type"]
                            place.pname = place_record["place"]["pname"]
                            place.print_data()
                                        
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
    parser.add_argument('handle', help="Handle of the person whose data be fetched")

    if len(sys.argv) == 1:
        print("First argument must be the handle, which is the key of this search")
        return

    args = parser.parse_args()

    process_neo4j(args)


if __name__ == "__main__":
    main()
