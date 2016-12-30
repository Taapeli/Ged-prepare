#!/usr/bin/python3

"""
Read repository data from the Neo4j database and write it to the XML file.
Jorma Haapasalo, 2016.
 
"""

import sys
import argparse
from sys import stderr
from datetime import date
from xml.dom.minidom import getDOMImplementation
from classes.genealogy import connect_db, Repository

connect_db()
    

def read_repositories_from_Neo4j():
    result = Repository.get_repositories()

    cnt = 0
    repos = []
    
    for record in result:
        r = Repository()
        r.handle = record["repo"]['gramps_handle']
        r.change = record["repo"]['change']
        r.id = record["repo"]['id']
        r.rname = record["repo"]['rname']
        r.type = record["repo"]['type']
        repos.append(r)
        cnt += 1
    print("Number of repositories read: " + str(cnt))
    return repos
    

def write_repositories_to_xml_file(repos, f):
    cnt = cnt2 =0
    
    impl = getDOMImplementation()
    
    doc = impl.createDocument(None, "database", None)
    
    top_element = doc.documentElement

    header = doc.createElement("header")
    
    top_element.appendChild(header)

    created = doc.createElement("created")
    created.setAttribute("date", date.today().isoformat())
    created.setAttribute("version", 'Neo4j 3.1.0')
    
    header.appendChild(created)

    repositories = doc.createElement("repositories")
    
    top_element.appendChild(repositories)
    
    for repo in repos:

        repository = doc.createElement("repository")
        repository.setAttribute("handle", repo.handle)
        repository.setAttribute("change", repo.change)
        repository.setAttribute("id", repo.id)
        
        repositories.appendChild(repository)
        cnt2 += 1
                
        rname = doc.createElement("rname")
        repository.appendChild(rname)
        
        rnametext = doc.createTextNode(repo.rname)
        rname.appendChild(rnametext)
        
        cnt2 += 1
        
        rtype = doc.createElement("type")
        repository.appendChild(rtype)
        
        rtypetext = doc.createTextNode(repo.type)
        rtype.appendChild(rtypetext)
        
        repository.appendChild(rtype)
        cnt2 += 1
        
        cnt += 1
        
    doc.writexml( f,
                     indent="  ",
                     addindent="  ",
                     newl="\n")
    
    doc.unlink()
            
    print("Number of repositories written: " + str(cnt))
    print("Number of lines written: " + str(cnt2))


def process_neo4j(args):

    # Read all repositoeies from Neo4j and writo tpo the XML file
    try:
        repos = read_repositories_from_Neo4j()
    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)

    try:        
        with open(args.output_xml, 'wt', encoding='utf-8') as f:
            write_repositories_to_xml_file(repos, f)
    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)


def main():
    parser = argparse.ArgumentParser(description='Repositories from Neo4j to the XML file')
    parser.add_argument('output_xml', help="Name of the output XML file")

    if len(sys.argv) == 1:
        print("First argument must be the name of the output XML file")
        return

    args = parser.parse_args()

    process_neo4j(args)


if __name__ == "__main__":
    main()
