#!/usr/bin/python3

"""
Compare people of the user with people of Taapeli user in Neo4j database.
This program uses another python program to print out all (i.e. anchestors,
descendants, birth, death, etc.) data of the persons to be compared.
Jorma Haapasalo, 2017.
 
"""

import sys
import argparse
import time
import subprocess
from sys import stderr
from classes.genealogy import connect_db, Name, Person, User

connect_db()


def process_neo4j(args):

    # List people with the given name
    try:
    
        t = time.perf_counter()

        u = User()
        u.userid = args.userid
        result = u.get_refnames_of_people_of_user()
        for record in result:
            p = Person()
            p.handle = record["handle"]
            refname = record["refname"]
            p.get_person_and_name_data()

            # Use the first name of the refname as a search key,
            # E.g. refname = "Matti Johannes" ---> search with "Matti"
            names = refname.split(" ")
                
            tresult = Name.get_people_with_refname_and_user_given('Taapeli', names[0])
            for trecord in tresult:
                tp = Person()
                tp.handle = trecord["handle"]
                
                print("\nPerson in the compare db:")
                call_string = "python3 get_family_with_handle_given.py " + p.handle
                subprocess.call(call_string, shell=True)
                
                print("\nPerson in the Taapeli db:")
                call_string = "python3 get_family_with_handle_given.py " + tp.handle
                subprocess.call(call_string, shell=True)
                
                print("\n#-------------------------------------------------------------------#\n")
                                   
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
