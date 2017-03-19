'''
Created on 19.3.2017

@author: jm
'''
import sys
import os
from neo4j.v1 import GraphDatabase, basic_auth
# Set include path work like in our root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from classes.genealogy import connect_db

if __name__ == '__main__':
    print('Db-connect test with classes.genealogy.connect_db')
    if len(sys.argv) < 2:
        print("Usage: {} name".format(__file__), file=sys.stderr)
        exit(1)

    session = connect_db()
    if session and not session.connection.closed:
        print("I:Session opened")
    else:
        print("F:Got not no session!")
        exit()

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

