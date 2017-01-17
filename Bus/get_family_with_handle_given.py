#!/usr/bin/python3

"""
Get the family data of the person from the Neo4j database.
Jorma Haapasalo, 2017.
 
"""

import sys
import argparse
from sys import stderr
from classes.genealogy import connect_db, Event, Family, Person, Place

connect_db()
    

def get_family_data(handle):

    # Get Family data
    
    try:
        f = Family()
        f.handle = handle
        
        f.get_family_object()
        f.print_data()
            
        print("\nFATHER: \n")
        father = Person()
        father.handle = f.father
        
        father.get_person_and_name_data()
        father.print_data()
                
        birth_result = father.get_birth_handle()
        for birth_record in birth_result:
            event = Event()
            event.handle = birth_record["handle"]
        
            event.get_event_data()
            event.print_data()

            if event.place_hlink != '':
                place = Place()
                place.handle = event.place_hlink
                    
                place.get_place_data()
                place.print_data()
                
        death_result = father.get_death_handle()
        for death_record in death_result:
            event = Event()
            event.handle = death_record["handle"]
        
            event.get_event_data()
            event.print_data()
        
            if event.place_hlink != '':
                place = Place()
                place.handle = event.place_hlink
                    
                place.get_place_data()
                place.print_data()
                      
        print("\nMOTHER: \n")
        mother = Person()
        mother.handle = f.mother
        
        mother.get_person_and_name_data()                
        mother.print_data()

        birth_result = mother.get_birth_handle()
        for birth_record in birth_result:
            event = Event()
            event.handle = birth_record["handle"]
        
            event.get_event_data()
            event.print_data()
        
            if event.place_hlink != '':
                place = Place()
                place.handle = event.place_hlink
                    
                place.get_place_data()
                place.print_data()
                
        death_result = mother.get_death_handle()
        for death_record in death_result:
            event = Event()
            event.handle = death_record["handle"]
        
            event.get_event_data()
            event.print_data()
        
            if event.place_hlink != '':
                place = Place()
                place.handle = event.place_hlink
                    
                place.get_place_data()
                place.print_data()
                                    
        for event_link in f.eventref_hlink:            
            event = Event()
            event.handle = event_link
        
            event.get_event_data()
            event.print_data()
        
            if event.place_hlink != '':
                place = Place()
                place.handle = event.place_hlink
                    
                place.get_place_data()
                place.print_data()
                            
        print("\nCHILDREN: ")
        for child_link in f.childref_hlink:            
            child = Person()
            child.handle = child_link

            child.get_person_and_name_data()                
            print("\n")
            child.print_data()
            
            birth_result = child.get_birth_handle()
            for birth_record in birth_result:
                event = Event()
                event.handle = birth_record["handle"]
        
                event.get_event_data()
                event.print_data()
            
                if event.place_hlink != '':
                    place = Place()
                    place.handle = event.place_hlink
                    
                    place.get_place_data()
                    place.print_data()
            
            death_result = child.get_death_handle()
            for death_record in death_result:
                event = Event()
                event.handle = death_record["handle"]
        
                event.get_event_data()
                event.print_data()
            
                if event.place_hlink != '':
                    place = Place()
                    place.handle = event.place_hlink
                    
                    place.get_place_data()
                    place.print_data()
                                        
    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)


def process_neo4j(args):

    # Get family data of the person
    try:
    
        p = Person()
        p.handle = args.handle
        result = p.get_parentin_handle()
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
