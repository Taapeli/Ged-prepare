#!/usr/bin/python3

"""
Read repository data from the Neo4j database and write it to the XML file.
Jorma Haapasalo, 2016.
 
"""

import sys
import argparse
from sys import stderr
from classes.genealogy import connect_db, Repository, XML_generator

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
    
    lines = XML_generator.get_xml_header()
    for line in lines:
        f.write(line)
        cnt2 += 1
        
    # Write the begin tag
    output_line = '  <repositories>\n'
    f.write(output_line)
    cnt2 += 1
    
    for repo in repos:
        output_line = '    ' +\
            '<repository handle="' + repo.handle + '"' +\
            ' change="' + repo.change + '"' +\
            ' id="' + repo.id + '">\n'
            
        f.write(output_line)
        cnt2 += 1
        
        output_line = '      ' +\
            '<rname>' + repo.rname + '</rname>\n'
        
        f.write(output_line)
        cnt2 += 1
        
        output_line = '      ' +\
            '<type>' + repo.type + '</type>\n'
        
        f.write(output_line)
        cnt2 += 1
        
        output_line = '    ' +\
            '</repository>\n'
            
        f.write(output_line)
        cnt2 += 1
        cnt += 1
        
    # Write the end tag
    output_line = '  </repositories>\n'
    f.write(output_line)
    cnt2 += 1
        
    # Write the end of database tag
    output_line = '</database>\n'
    f.write(output_line)
    cnt2 += 1
    
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
