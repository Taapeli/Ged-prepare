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
    

def get_event_and_place_data(event_link):
    event = Event()
    event.handle = event_link

    event.get_event_data()
    event.print_data()

    if event.place_hlink != '':
        place = Place()
        place.handle = event.place_hlink
        
        place.get_place_data()
        place.print_data()
    
    
def get_family_data(mp):

    # Get main person's Family data
    
    try:
        print("\nMAIN PERSON: \n")
        get_person_data(mp)
                         
        print("\nSPOUSE(S): \n")
        if mp.gender == 'M':
            result = mp.get_his_families()
        else:
            result = mp.get_her_families()
            
        for record in result:
            mf = Family()
            mf.handle = record["handle"]
            
            mf.get_family_data()
            mf.print_data()
                      
            # This is the event(s) of the family
            for event_link in mf.eventref_hlink:            
                get_event_and_place_data(event_link)        

            print("\n")
            spouse = Person()
            if mp.gender == 'M':
                spouse.handle = mf.mother
            else:
                spouse.handle = mf.father
            get_person_data(spouse)
                           
            print("\nCHILDREN: ")
            for child_link in mf.childref_hlink:            
                child = Person()
                child.handle = child_link
                print("\n")
                get_person_data(child)
                                                    
    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)
    

def get_parents_data(handle):

    # Get main person's parents data
    
    try:
        f = Family()
        f.handle = handle
        
        f.get_family_data()
#        f.print_data()
            
        print("\nFATHER: \n")
        father = Person()
        father.handle = f.father
        get_person_data(father)
                      
        print("\nMOTHER: \n")
        mother = Person()
        mother.handle = f.mother
        get_person_data(mother)
                                                    
    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)
        
        
def get_person_data(individ):
        
    individ.get_person_and_name_data()                
    individ.get_hlinks()
    individ.print_data()

    for event_link in individ.eventref_hlink:
        get_event_and_place_data(event_link)        


def process_neo4j(args):

    # Get family data of the person
    try:
    
        main_person = Person()
        main_person.handle = args.handle
        
        # The fetching of the family and parents data of the main person is
        # split to two operations:
        #
        # If there are no parents in the db the result of 
        # get_parentin_handle() operation is empty,
        # but the get_family_data operation prints out
        # the family of the main person.
        result = main_person.get_parentin_handle()            
        for record in result:
            get_parents_data(record["parentin_hlink"])

        get_family_data(main_person)

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
