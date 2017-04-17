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
    

def compare_event_and_place_data(event_links1, event_links2):
    events1 = []
    places1 = []
    for link in event_links1:
        event = Event()
        event.handle = link
        event.get_event_data()
        events1.append(event)
        
        pname1 = ''
        if event.place_hlink != '':
            place = Place()
            place.handle = event.place_hlink
            
            place.get_place_data()
            pname1 = place.pname
            
        places1.append(pname1)
    
    events2 = []
    places2 = []
    for link in event_links2:
        event = Event()
        event.handle = link
        event.get_event_data()
        events2.append(event)
        
        pname2 = ''
        if event.place_hlink != '':
            place = Place()
            place.handle = event.place_hlink
            
            place.get_place_data()
            pname2 = place.pname
            
        places2.append(pname2)
    
    for i in range (len(events1)):
        for j in range (len(events2)):
            if events1[i].type == events2[j].type:
                events1[i].print_compared_data(events2[j], places1[i], places2[j])
    
    
def compare_family_data(mp, tp):

    # Get main and the compared person's Family data
    
    try:
        spouse1 = None
        spouse2 = None
        children1 = None
        children2 = None

        print("\nMAIN PERSONS: \n")
        compare_person_data(mp, tp)
                         
        if mp.gender == 'M':
            result = mp.get_his_families()
        else:
            result = mp.get_her_families()
            
        for record in result:
            mf = Family()
            mf.handle = record["handle"]
            
            mf.get_family_data()
                       
            spouse1 = Person()
            if mp.gender == 'M':
                spouse1.handle = mf.mother
            else:
                spouse1.handle = mf.father
   
            children1 = []
            for child_link in mf.childref_hlink:
                child = Person()
                child.handle = child_link
                children1.append(child)
            
        if tp.gender == 'M':
            result = tp.get_his_families()
        else:
            result = tp.get_her_families()
            
        for record in result:
            tf = Family()
            tf.handle = record["handle"]
            
            tf.get_family_data()
                       
            spouse2 = Person()
            if tp.gender == 'M':
                spouse2.handle = tf.mother
            else:
                spouse2.handle = tf.father
   
            children2 = []
            for child_link in tf.childref_hlink:            
                child = Person()
                child.handle = child_link
                children2.append(child)
            
        if spouse1:
            if spouse2:
                print("\nSPOUSE(S): \n")
                compare_person_data(spouse1, spouse2)
        
        if children1:
            if children2:
                print("\nCHILDREN: ")
                if (len(children2) >= len(children1)):
                    for i in range (len(children1)):
                        print("\n")
                        compare_person_data(children1[i], children2[i])
                
    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)
    

def compare_parents_data(handle1, handle2):

    # Get main person's parents data
    
    try:
        f1 = Family()
        f1.handle = handle1
        f1.get_family_data()
        
        f2 = Family()
        f2.handle = handle2
        f2.get_family_data()
            
        print("\nFATHER: \n")
        father1 = Person()
        father1.handle = f1.father
        father2 = Person()
        father2.handle = f2.father
        compare_person_data(father1, father2)
                      
        print("\nMOTHER: \n")
        mother1 = Person()
        mother1.handle = f1.mother
        mother2 = Person()
        mother2.handle = f2.mother
        compare_person_data(mother1, mother2)
                                                    
    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)
        
        
def compare_person_data(individ1, individ2):
        
    individ1.get_person_and_name_data()                
    individ1.get_hlinks()
    
    individ2.get_person_and_name_data()                
    individ2.get_hlinks()
    
    individ1.print_compared_data(individ2)

    compare_event_and_place_data(individ1.eventref_hlink, individ2.eventref_hlink)
            

def process_neo4j(args):

    # Get family data of the person
    try:
    
        main_person = Person()
        main_person.handle = args.handle1
        
        taapeli_person = Person()
        taapeli_person.handle = args.handle2
        
        # The fetching of the family and parents data of the main person is
        # split to two operations:
        #
        # If there are no parents in the db the result of 
        # get_parentin_handle() operation is empty,
        # but the get_family_data operation prints out
        # the family of the main person.
        result = main_person.get_parentin_handle()            
        for record in result:
            main_parents_hlink = record["parentin_hlink"]
            
            result = taapeli_person.get_parentin_handle()            
            for record in result:
                taapeli_parents_hlink = record["parentin_hlink"]
                compare_parents_data(main_parents_hlink, taapeli_parents_hlink)

        compare_family_data(main_person, taapeli_person)

    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)


def main():
    parser = argparse.ArgumentParser(description='The family data of two persons from Neo4j')
    parser.add_argument('handle1', help="Handle of the person of the specific user")
    parser.add_argument('handle2', help="Handle of the person of the Taapeli user")

    if len(sys.argv) <= 2:
        print("There must be two handles, which are the keys of this search")
        return

    args = parser.parse_args()

    process_neo4j(args)


if __name__ == "__main__":
    main()
