#!/usr/bin/python3

"""
Read source data from the Neo4j database and write it to the XML file.
Jorma Haapasalo, 2016.
 
"""

import sys
import argparse
from sys import stderr
from datetime import date
from xml.dom.minidom import getDOMImplementation
from classes.genealogy import connect_db, Repository, Source

connect_db()
    

def read_repository_from_Neo4j(repository_name):
    result = Repository.get_repository(repository_name)

    repos = []
    for record in result:
        r = Repository()
        r.handle = record["repo"]['gramps_handle']
        r.change = record["repo"]['change']
        r.id = record["repo"]['id']
        r.rname = record["repo"]['rname']
        r.type = record["repo"]['type']
        repos.append(r)
        
    return repos
    

def read_sources_from_Neo4j(repository_handle):
    result = Source.get_sources(repository_handle)

    cnt = 0
    sources = []
    for record in result:
        s = Source()
        s.handle = record["source"]['gramps_handle']
        s.change = record["source"]['change']
        s.id = record["source"]['id']
        s.stitle = record["source"]['stitle']
        
        if record["source"]['reporef_hlink']:
            s.reporef_hlink = record["source"]['reporef_hlink']
        
        if record["medium"]:
            s.reporef_medium = record["medium"]
            
        sources.append(s)
        cnt += 1
    print("Number of sources read: " + str(cnt))
    return sources
    

def write_sources_to_xml_file(repository_handle, repos, repo_sources, f):
    cnt = cnt2 = cnt3 = 0
     
    impl = getDOMImplementation()
    
    doc = impl.createDocument(None, "top", None)
    cnt2 += 3 # xml and two database tags
    
    top_element = doc.documentElement
    
    database = doc.createElement("database")
    database.setAttribute("xmlns", 'http://gramps-project.org/xml/1.7.1/')
    top_element.appendChild(database)
    cnt2 += 1

    header = doc.createElement("header")
    top_element.appendChild(header)
    cnt2 += 2
    
    created = doc.createElement("created")
    created.setAttribute("date", date.today().isoformat())
    created.setAttribute("version", 'Neo4j 3.1.0')
    header.appendChild(created)
    cnt2 += 1
    
    sources = doc.createElement("sources")
    top_element.appendChild(sources)
    cnt2 += 2
    
    for repo_source in repo_sources:

        source = doc.createElement("source")
        source.setAttribute("handle", repo_source.handle)
        source.setAttribute("change", repo_source.change)
        source.setAttribute("id", repo_source.id)
        sources.appendChild(source)
        cnt2 += 2
                
        stitle = doc.createElement("stitle")
        source.appendChild(stitle)
        
        stitle_text = doc.createTextNode(repo_source.stitle)
        stitle.appendChild(stitle_text)
        cnt2 += 1

        reporef = doc.createElement("reporef")
        reporef.setAttribute("hlink", repository_handle)
        reporef.setAttribute("medium", repo_source.reporef_medium)
        source.appendChild(reporef)
        cnt2 += 1
        
        cnt += 1
     
    repositories = doc.createElement("repositories")
    top_element.appendChild(repositories)
    cnt2 += 2
       
    for repo in repos:

        repository = doc.createElement("repository")
        repository.setAttribute("handle", repo.handle)
        repository.setAttribute("change", repo.change)
        repository.setAttribute("id", repo.id)
        repositories.appendChild(repository)
        cnt2 += 1
                
        rname = doc.createElement("rname")
        repository.appendChild(rname)
        
        rname_text = doc.createTextNode(repo.rname)
        rname.appendChild(rname_text)
        cnt2 += 1
        
        rtype = doc.createElement("type")
        repository.appendChild(rtype)
        cnt2 += 1
        
        rtypetext = doc.createTextNode(repo.type)
        rtype.appendChild(rtypetext)
        repository.appendChild(rtype)
        cnt2 += 1
        
        cnt3 += 1
        
        
    doc.writexml( f,
                 indent="  ",
                 addindent="  ",
                 newl="\n")
    
    doc.unlink()
    
    print("Number of sources written: " + str(cnt))
    print("Number of repositories written: " + str(cnt3))
    print("Number of lines written: " + str(cnt2))


def process_neo4j(args):

    # Read all sources of the repository from Neo4j and write to the XML file
    try:
        repos= read_repository_from_Neo4j(args.repository)
        for repo in repos:
            repository_handle = repo.handle
    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)
        
    try:
        sources = read_sources_from_Neo4j(repository_handle)
    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)

    try:        
        with open(args.output_xml, 'wt', encoding='utf-8') as f:
            write_sources_to_xml_file(repository_handle, repos, sources, f)
    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)


def main():
    parser = argparse.ArgumentParser(description='Sources of the Repository from Neo4j to the XML file')
    parser.add_argument('repository', help="Name of the repository")
    parser.add_argument('output_xml', help="Name of the output XML file")

    if len(sys.argv) == 1:
        print("The arguments must be the name of the repository and the name of the output XML file")
        return

    args = parser.parse_args()

    process_neo4j(args)


if __name__ == "__main__":
    main()
