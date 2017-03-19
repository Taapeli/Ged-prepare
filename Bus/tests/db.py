'''
Created on 19.3.2017

@author: jm
'''
import sys
import os
from neo4j.v1 import GraphDatabase, basic_auth

UNAME="neo4j"
PASSWD="2000Neo4j"

if __name__ == '__main__':
    print('Basic db-connect test')
    if len(sys.argv) < 2:
        print("Usage: {} name".format(__file__), file=sys.stderr)
        exit(1)

    print ("I:connecting with {}/{}".format(UNAME, PASSWD))
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth(UNAME, PASSWD))
    session = driver.session()
    print("I:Session opened")

    nm=sys.argv[1]
    query = '''MATCH (a:TestPerson) 
        WHERE a.name = '{}' 
        RETURN a.name AS name, a.title AS title, a.birth AS birth'''.format(nm)
    print("#db read test\n\t" + query)
    
    try:
        result = session.run(query)
        print("I:Results:")
        for record in result:
            print("I:\t", record["title"], record["name"], record["birth"])

    except Exception as e:
        print ("E:{}: {}".format(e.__class__.__name__, e))

    try:
        print("I:Closing session ")
        session.close()
        print("I:Session closed.")

    except Exception as e:
        print ("E:{}: {}".format(e.__class__.__name__, e))

