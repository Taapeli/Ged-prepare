#!/usr/bin/python3

"""
List all surnames from the Neo4j database.
Jorma Haapasalo, 2016.
 
"""

import argparse
from sys import stderr
from classes.genealogy import connect_db, Name

connect_db()
    

def list_surnames():
    surnames = Name.get_surnames()

    for surname in surnames:
        print(surname[0])


def process_neo4j(args):

    # Read all surnames from Neo4j and print out
    try:
    
        list_surnames()
    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)


def main():
    parser = argparse.ArgumentParser(description='Surnames from Neo4j')

    args = parser.parse_args()

    process_neo4j(args)


if __name__ == "__main__":
    main()
