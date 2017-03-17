'''
Created on 17.3.2017

@author: jm
'''

import argparse
import sys
import os
import time
from neo4j.v1 import GraphDatabase, basic_auth
from neo4j.v1.api import CypherError

# Set include path work like in our root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


if __name__ == '__main__':
    ''' Connect to db 
        1. with configured passwd OR given --pw myPassword
        2. read from db with --read option
        3. write to db with --update option
    '''
    parser = argparse.ArgumentParser(description='Test connection to Neo4j database')
    parser.add_argument("-p", "--pw", help="db connect password")
    parser.add_argument("-r", "--read", help="open db for reading", action="store_true")
    parser.add_argument("-u", "--update", help="open db for update", action="store_true")
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        print("Use --help for help")
        exit()

    ''' Connect to db '''
    if args.pw:
        print ("I:connecting with {}/{}".format("neo4j", args.pw))
        
        driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", args.pw))
        session = driver.session()
        print("I:Session opened")
        
    else:
        print ("I:Connecting with project settings")
        from classes.genealogy import connect_db
        session = connect_db()
        if session:
            print("I:Session opened")
        else:
            print("W:Got no session!")
            exit()

    ''' Update db '''
    if args.update:
        birth = time.strftime("%a %H:%M:%S", time.localtime())
        query = '''CREATE (a:TestPerson 
                   {name:"Arthur", title:"King", birth:"''' + birth + '"})'
        print("I:db update test\n\t" + query)
        
        try:
            result = session.run(query)
        except CypherError as e:
            print ("E:#Cypher error: {}".format(e))
        except Exception as e:
            print ("E:{} error: {}".format(e.__class__, e))
        
    ''' Read from db '''
    if args.read:
        query = '''MATCH (a:TestPerson) 
            WHERE a.name = 'Arthur' 
            RETURN a.name AS name, a.title AS title, a.birth AS birth'''
        print("#db read test\n\t" + query)
        
        try:
            result = session.run(query)
            print(list(result))
            for record in result:
                print("I:\tGot {} {} (s:{})".format(record["title"], record["name"], record["birth"]))
        except CypherError as e:
            print ("E:Cypher error: {}".format(e))
        except Exception as e:
            print ("E:{} error: {}".format(e.__class__, e))
    try:
        session.close()
        print("I:Session closed")
    except CypherError as e:
        print ("E:Cypher error when closing session: {}".format(e))
    except Exception as e:
        print ("E:{} error: {}".format(e.__class__, e))
        
