#!/usr/bin/python3

"""
Compare people of the user with people of Taapeli user in Neo4j database.
Jorma Haapasalo, 2017.
 
"""

import sys
import argparse
import time
from sys import stderr
from classes.genealogy import connect_db, Name, User

connect_db()


def process_neo4j(args):

    # List people with the given name
    try:
    
        t = time.perf_counter()

        u = User()
        u.userid = args.userid
        result = u.get_refnames_of_people_of_user()
        for record in result:
            n = Name()
            n.refname = record["refname"]
            n.surname = record["surname"]

            trecord = None
            tresult = Name.get_people_with_refname_and_user_given('Taapeli', n.refname)
            for trecord in tresult:
                tn = Name()
                tn.refname = trecord["refname"]
                tn.surname = trecord["surname"]
                
                print("Person in compare db: " + n.refname + n.surname)
                print("Person in Taapeli db: " + tn.refname + tn.surname + "\n")
                                   
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
