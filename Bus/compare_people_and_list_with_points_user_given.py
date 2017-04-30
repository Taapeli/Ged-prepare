#!/usr/bin/python3

"""
Compare and give points the family data of two persons from the Neo4j database.
Jorma Haapasalo, 2017.
 
"""

import sys
import argparse
import time
from sys import stderr
from classes.genealogy import connect_db, Event, Family, Name, Person, Place, User

connect_db()

points = 0

def compare_event_and_place_data(event_links1, event_links2):
    global points
    events1 = []
    places1 = []
    for link in event_links1:
        event = Event()
        event.uniq_id = link
        event.get_event_data_by_id()
        events1.append(event)
        
        pname1 = ''
        if event.place_hlink != '':
            place = Place()
            place.uniq_id = event.place_hlink
            
            place.get_place_data_by_id()
            pname1 = place.pname
            
        places1.append(pname1)
    
    events2 = []
    places2 = []
    for link in event_links2:
        event = Event()
        event.uniq_id = link
        event.get_event_data_by_id()
        events2.append(event)
        
        pname2 = ''
        if event.place_hlink != '':
            place = Place()
            place.uniq_id = event.place_hlink
            
            place.get_place_data_by_id()
            pname2 = place.pname
            
        places2.append(pname2)
    
    for i in range (len(events1)):
        for j in range (len(events2)):
            if events1[i].type == events2[j].type:
                local_points = events1[i].get_points_for_compared_data(events2[j], 
                                          places1[i], places2[j])
                print("--- --- Local points: " + str(local_points) + " --- ---")
                points += local_points
    
    
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
            result = mp.get_his_families_by_id()
        else:
            result = mp.get_her_families_by_id()
            
        for record in result:
            mf = Family()
            mf.uniq_id = record["uniq_id"]
            
            mf.get_family_data_by_id()
                       
            spouse1 = Person()
            if mp.gender == 'M':
                spouse1.uniq_id = mf.mother
            else:
                spouse1.uniq_id = mf.father
   
            children1 = []
            for child_id in mf.childref_hlink:
                child = Person()
                child.uniq_id = child_id
                children1.append(child)
            
        if tp.gender == 'M':
            result = tp.get_his_families_by_id()
        else:
            result = tp.get_her_families_by_id()
            
        for record in result:
            tf = Family()
            tf.uniq_id = record["uniq_id"]
            
            tf.get_family_data_by_id()
                       
            spouse2 = Person()
            if tp.gender == 'M':
                spouse2.uniq_id = tf.mother
            else:
                spouse2.uniq_id = tf.father
   
            children2 = []
            for child_id in tf.childref_hlink:            
                child = Person()
                child.uniq_id = child_id
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
    

def compare_parents_data(id1, id2):

    # Get main person's parents data
    
    try:
        f1 = Family()
        f1.uniq_id = id1
        f1.get_family_data_by_id()
        
        f2 = Family()
        f2.uniq_id = id2
        f2.get_family_data_by_id()
            
        print("\nFATHER: \n")
        father1 = Person()
        father1.uniq_id = f1.father
        father2 = Person()
        father2.uniq_id = f2.father
        compare_person_data(father1, father2)
                      
        print("\nMOTHER: \n")
        mother1 = Person()
        mother1.uniq_id = f1.mother
        mother2 = Person()
        mother2.uniq_id = f2.mother
        compare_person_data(mother1, mother2)
                                                    
    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)
        
        
def compare_person_data(individ1, individ2):
    global points
    
    individ1.get_person_and_name_data_by_id()                
    individ1.get_hlinks_by_id()
    
    individ2.get_person_and_name_data_by_id()                
    individ2.get_hlinks_by_id()
    
    local_points = individ1.get_points_for_compared_data(individ2)
    print("--- --- Local points: " + str(local_points) + " --- ---")
    points += local_points

    compare_event_and_place_data(individ1.eventref_hlink, 
                                 individ2.eventref_hlink)
            

def process_neo4j(args):

    # Get family data of the person
    global points
    
    try:    
        t = time.perf_counter()
        print_cnt = 0
        
        total_points = []
        compared_ids = []
        taapeli_ids = []

        u = User()
        u.userid = args.userid
        result = u.get_ids_and_refnames_of_people_of_user()
        for record in result:
            p = Person()
            # This id is the unique key of the node
            p.uniq_id = record["id"]
            refname = record["refname"]
            p.get_person_and_name_data_by_id()

            # Use the first name of the refname as a search key,
            # E.g. refname = "Matti Johannes" ---> search with "Matti"
            names = refname.split(" ")
                
            tresult = Name.get_ids_of_people_with_refname_and_user_given('Taapeli', names[0])
            for trecord in tresult:
                tp = Person()
                tp.uniq_id = trecord["id"]
                
                # The fetching of the family and parents data of the main person is
                # split to two operations:
                #
                # If there are no parents in the db the result of 
                # get_parentin_id() operation is empty,
                # but the get_family_data operation prints out
                # the family of the main person.
                result = p.get_parentin_id()            
                for record in result:
                    main_parents_hlink = record["parentin_hlink"]
                    
                    result = tp.get_parentin_id()            
                    for record in result:
                        taapeli_parents_hlink = record["parentin_hlink"]
                        compare_parents_data(main_parents_hlink, taapeli_parents_hlink)
        
                compare_family_data(p, tp)
                
                total_points.append(points)
                compared_ids.append(p.uniq_id)
                taapeli_ids.append(tp.uniq_id)
                print_cnt += 1
                
        print("\nTotal points # Compared ids # Taapeli ids")
        print("-----------------------------------------")
        for i in range(len(total_points)):
            print("\n  " + str(total_points[i]) + "   #   " + str(compared_ids[i]) + "   #   " + str(taapeli_ids[i]))

        print("\nLines printted: " + str(print_cnt))
                
        elapsed_time = time.perf_counter() - t
        print("\nTime needed: " + str(elapsed_time) + " seconds")

    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)


def main():
    parser = argparse.ArgumentParser(description='Compare and give points the family data of two persons from Neo4j')
    parser.add_argument('userid', help="The userid")

    if len(sys.argv) == 1:
        print("First argument must be the userid, which is the key of this compare")
        return

    args = parser.parse_args()

    process_neo4j(args)


if __name__ == "__main__":
    main()
