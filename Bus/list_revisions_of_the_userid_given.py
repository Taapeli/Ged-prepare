#!/usr/bin/python3

"""
List all revisions of the given userid from the Neo4j database.
Jorma Haapasalo, 2017.
 
"""

import sys
import argparse
import time
from sys import stderr
from classes.genealogy import connect_db, User

connect_db()


def process_neo4j(args):

    # List people with the given name
    try:
    
        record = None
        time_stamps = []
        t = time.perf_counter()

        u = User()
        u.userid = args.userid
        result = u.get_revisions_of_the_user()
        for record in result:
            time_stamps.append(record["date"])
            
        if (not record):
            print("\nUnknown userid: " + args.userid)
        else:
            print("\nTime stamps of the user: " + args.userid)
            print("--------------------------------\n")
            for time_stamp in time_stamps:
                print(time_stamp)

                           
        elapsed_time = time.perf_counter() - t
        print("\nTime needed: " + str(elapsed_time) + " seconds")

    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)


def main():
    parser = argparse.ArgumentParser(description='List all revisions of the given userid from Neo4j')
    parser.add_argument('userid', help="The userid")

    if len(sys.argv) == 1:
        print("First argument must be the userid")
        return

    args = parser.parse_args()

    process_neo4j(args)


if __name__ == "__main__":
    main()
