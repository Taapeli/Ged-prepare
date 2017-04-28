#!/usr/bin/python3

"""
Compare people of the user with people of Taapeli user in Neo4j database.
Jorma Haapasalo, 2017.
 
"""

import sys
import argparse
import time
from sys import stderr
from classes.genealogy import connect_db, Name, Person, User

connect_db()


def process_neo4j(args):

    # List people with the given name
    try:
    
        t = time.perf_counter()
        print_cnt = 0

        u = User()
        u.userid = args.userid
        result = u.get_ids_and_refnames_of_people_of_user()
        for record in result:
            p = Person()
            # This id is the unique key of the node
            uniq_id = record["id"]
            p.id = uniq_id
            refname = record["refname"]
            p.get_person_and_name_data_by_id()

            # Use the first name of the refname as a search key,
            # E.g. refname = "Matti Johannes" ---> search with "Matti"
            names = refname.split(" ")
                
            tresult = Name.get_ids_of_people_with_refname_and_user_given('Taapeli', names[0])
            for trecord in tresult:
                tp = Person()
                tp.id = trecord["id"]
            
                if print_cnt == 0:
                    print("\nUnique id pairs of people with the same first name in")
                    print("the compared db : the Taapeli db")
                
                print("\n" + str(uniq_id) + " : " + str(tp.id))
                print_cnt += 1
          
        print("\n\nNumber of id pairs printted out: " + str(print_cnt))
        elapsed_time = time.perf_counter() - t
        print("\nTime needed: " + str(elapsed_time) + " seconds")

    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)


def main():
    parser = argparse.ArgumentParser(description='Compare people of the user with people of Taapeli user in Neo4j database.')
    parser.add_argument('userid', help="The userid")

    if len(sys.argv) == 1:
        print("First argument must be the userid, which is the key of this compare")
        return

    args = parser.parse_args()

    process_neo4j(args)


if __name__ == "__main__":
    main()
