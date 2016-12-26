#!/usr/bin/python3

"""
Read source data from the Neo4j database and write it to the XML file.
Jorma Haapasalo, 2016.
 
"""

import sys
import argparse
from sys import stderr
from classes.genealogy import connect_db, Repository, Source

connect_db()
    

def read_repository_from_Neo4j(repository_name):
    result = Repository.get_repository(repository_name)

    for record in result:
        handle = record["repository.gramps_handle"]
        
    return handle
    

def read_sources_from_Neo4j(repository_handle, sources):
    result = Source.get_sources(repository_handle)

    cnt = 0
    for record in result:
        s = Source()
        s.handle = record["source"]['gramps_handle']
        s.id = record["source"]['id']
        s.stitle = record["source"]['stitle']
        
        if record["source"]['reporef_hlink']:
            s.reporef_hlink = record["source"]['reporef_hlink']
            
        sources.append(s)
        cnt += 1
    print("Number of sources read: " + str(cnt))
    

def write_sources_to_xml_file(repository_handle, sources, f):
    cnt = cnt2 =0
    
    # Write the begin group tag
    output_line = '  <sources>\n'
    f.write(output_line)
    cnt2 += 1
    
    for source in sources:
        output_line = '    ' +\
            '<source handle="' + source.handle + '"'\
            ' id="' + source.id + '">\n'
            
        f.write(output_line)
        cnt2 += 1
        
        output_line = '      ' +\
            '<stitle>' + source.stitle + '</stitle>\n'
        
        f.write(output_line)
        cnt2 += 1
        
        output_line = '      ' +\
            '<reporef hlink="' + repository_handle + '">\n'
        
        f.write(output_line)
        cnt2 += 1
        
        output_line = '    ' +\
            '</source>\n'
            
        f.write(output_line)
        cnt2 += 1
        cnt += 1
        
    
    # Write the end group tag
    output_line = '  </sources>\n'
    f.write(output_line)
    cnt2 += 1
    
    print("Number of sources written: " + str(cnt))
    print("Number of lines written: " + str(cnt2))


def process_neo4j(args):

    # Read all sources of the repository from Neo4j and writo to the XML file
    try:
        repository_handle = ''
        repository_handle = read_repository_from_Neo4j(args.repository)
        print("Repository handle_ " + repository_handle)
    except Exception as err:
        print("Virhe01: {0}".format(err), file=stderr)
        
    try:
        sources = []
        read_sources_from_Neo4j(repository_handle, sources)
    except Exception as err:
        print("Virhe02: {0}".format(err), file=stderr)

    try:        
        f = open(args.output_xml, 'wt', encoding='utf-8')
        write_sources_to_xml_file(repository_handle, sources, f)
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
