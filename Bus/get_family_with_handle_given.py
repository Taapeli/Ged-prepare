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
        
        f.get_family_data()
        f.print_data()
                                    
        # This is the event(s) of the family
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
            
        print("\nFATHER: \n")
        father = Person()
        father.handle = f.father
        
        father.get_person_and_name_data()
        father.get_hlinks()
        father.print_data()
                
        for event_link in father.eventref_hlink:
            event = Event()
            event.handle = event_link
        
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
        mother.get_hlinks()
        mother.print_data()

        for event_link in mother.eventref_hlink:
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
            child.get_hlinks()
            print("\n")
            child.print_data()
            
            for event_link in child.eventref_hlink:
                event = Event()
                event.handle = event_link
        
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
            get_family_data(record["parentin_hlink"])

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
