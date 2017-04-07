#!/usr/bin/python3

"""
List all userids in the Neo4j database.
Jorma Haapasalo, 2017.
 
"""

import argparse
import time
from sys import stderr
from classes.genealogy import connect_db, User

connect_db()


def process_neo4j(args):

    # List users in the Neo4j database
    try:
    
        t = time.perf_counter()

        result = User.get_all_userids()
        print("\nUserids in db: ")
        print("--------------")
        for record in result:
            userid = record["userid"]
                                
            print(userid)
                   
                           
        elapsed_time = time.perf_counter() - t
        print("\nTime needed: " + str(elapsed_time) + " seconds")

    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)


def main():
    parser = argparse.ArgumentParser(description='List all users in Neo4j')

    args = parser.parse_args()

    process_neo4j(args)


if __name__ == "__main__":
    main()
