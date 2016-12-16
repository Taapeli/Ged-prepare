#!/usr/bin/python3

"""
Storing data from an XML file to the Neo4j database.
Jorma Haapasalo, 2016.

Parameters of main():
 1. The name of the input XML file.
 
"""

import sys
import time
import xml.dom.minidom
import argparse
from sys import stderr
from classes.genealogy import *

connect_db()


def handle_citations(collection):
    # Get all the citations in the collection
    citations = collection.getElementsByTagName("citation")
    
    print ("*****Citations*****")
    
    # Print detail of each citation
    for citation in citations:
        if citation.hasAttribute("handle"):
            handle = citation.getAttribute("handle")
        if citation.hasAttribute("change"):
            change = citation.getAttribute("change")
        if citation.hasAttribute("id"):
            pid = citation.getAttribute("id")
        
        c = Citation(handle, pid)
    
        if len(citation.getElementsByTagName('dateval') ) == 1:
            citation_dateval = citation.getElementsByTagName('dateval')[0]
            if citation_dateval.hasAttribute("val"):
                c.dateval = citation_dateval.getAttribute("val")
        elif len(citation.getElementsByTagName('dateval') ) > 1:
            print("Error: More than one dateval tag in a citation")
    
        if len(citation.getElementsByTagName('page') ) == 1:
            citation_page = citation.getElementsByTagName('page')[0]
            c.page = citation_page.childNodes[0].data
        elif len(citation.getElementsByTagName('page') ) > 1:
            print("Error: More than one page tag in a citation")
    
        if len(citation.getElementsByTagName('confidence') ) == 1:
            citation_confidence = citation.getElementsByTagName('confidence')[0]
            c.confidence = citation_confidence.childNodes[0].data
        elif len(citation.getElementsByTagName('confidence') ) > 1:
            print("Error: More than one confidence tag in a citation")
    
        if len(citation.getElementsByTagName('noteref') ) == 1:
            citation_noteref = citation.getElementsByTagName('noteref')[0]
            if citation_noteref.hasAttribute("hlink"):
                c.noteref_hlink = citation_noteref.getAttribute("hlink")
        elif len(citation.getElementsByTagName('noteref') ) > 1:
            print("Error: More than one noteref tag in a citation")
    
        if len(citation.getElementsByTagName('sourceref') ) == 1:
            citation_sourceref = citation.getElementsByTagName('sourceref')[0]
            if citation_sourceref.hasAttribute("hlink"):
                c.sourceref_hlink = citation_sourceref.getAttribute("hlink")
        elif len(citation.getElementsByTagName('sourceref') ) > 1:
            print("Error: More than one sourceref tag in a citation")
                
        c.save()
        
        # There can be so many individs to store that Cypher needs a pause
        time.sleep(0.1)
    
    c = Citation("handle", "id")
    results = c.tell()
    for result in results:
        print("Number of citations in db: " + str(result[0]))


def handle_events(collection):

    # Get all the events in the collection
    events = collection.getElementsByTagName("event")
    
    print ("*****Events*****")
    
    # Print detail of each event
    for event in events:
        if event.hasAttribute("handle"):
            handle = event.getAttribute("handle")
        if event.hasAttribute("change"):
            change = event.getAttribute("change")
        if event.hasAttribute("id"):
            pid = event.getAttribute("id")
        
        e = Event(handle, pid)
    
        if len(event.getElementsByTagName('type') ) == 1:
            event_type = event.getElementsByTagName('type')[0]
            e.type = event_type.childNodes[0].data
        elif len(event.getElementsByTagName('type') ) > 1:
            print("Error: More than one type tag in an event")
    
        if len(event.getElementsByTagName('dateval') ) == 1:
            event_dateval = event.getElementsByTagName('dateval')[0]
            if event_dateval.hasAttribute("val"):
                e.date = event_dateval.getAttribute("val")
        elif len(event.getElementsByTagName('dateval') ) > 1:
            print("Error: More than one dateval tag in an event")
    
        if len(event.getElementsByTagName('place') ) == 1:
            event_place = event.getElementsByTagName('place')[0]
            if event_place.hasAttribute("hlink"):
                e.place_hlink = event_place.getAttribute("hlink")
        elif len(event.getElementsByTagName('place') ) > 1:
            print("Error: More than one place tag in an event")
    
        if len(event.getElementsByTagName('citationref') ) == 1:
            event_citationref = event.getElementsByTagName('citationref')[0]
            if event_citationref.hasAttribute("hlink"):
                e.citationref_hlink = event_citationref.getAttribute("hlink")
        elif len(event.getElementsByTagName('citationref') ) > 1:
            print("Error: More than one citationref tag in an event")
                
        e.save()
        
        # There can be so many individs to store that Cypher needs a pause
        time.sleep(0.1)
    
    e = Event("handle", "id")
    results = e.tell()
    for result in results:
        print("Number of events in db: " + str(result[0]))


def handle_families(collection):
    # Get all the families in the collection
    families = collection.getElementsByTagName("family")
    
    print ("*****Families*****")
    
    # Print detail of each family
    for family in families:
        if family.hasAttribute("handle"):
            handle = family.getAttribute("handle")
        if family.hasAttribute("change"):
            change = family.getAttribute("change")
        if family.hasAttribute("id"):
            pid = family.getAttribute("id")
        
        f = Family(handle, pid)
    
        if len(family.getElementsByTagName('rel') ) == 1:
            family_rel = family.getElementsByTagName('rel')[0]
            if family_rel.hasAttribute("type"):
                f.rel_type = family_rel.getAttribute("type")
        elif len(family.getElementsByTagName('rel') ) > 1:
            print("Error: More than one rel tag in a family")
    
        if len(family.getElementsByTagName('father') ) == 1:
            family_father = family.getElementsByTagName('father')[0]
            if family_father.hasAttribute("hlink"):
                f.father = family_father.getAttribute("hlink")
        elif len(family.getElementsByTagName('father') ) > 1:
            print("Error: More than one father tag in a family")
    
        if len(family.getElementsByTagName('mother') ) == 1:
            family_mother = family.getElementsByTagName('mother')[0]
            if family_mother.hasAttribute("hlink"):
                f.mother = family_mother.getAttribute("hlink")
        elif len(family.getElementsByTagName('mother') ) > 1:
            print("Error: More than one mother tag in a family")
    
        if len(family.getElementsByTagName('eventref') ) >= 1:
            for i in range(len(family.getElementsByTagName('eventref') )):
                family_eventref = family.getElementsByTagName('eventref')[i]
                if family_eventref.hasAttribute("hlink"):
                    f.eventref_hlink.append(family_eventref.getAttribute("hlink"))
                if family_eventref.hasAttribute("role"):
                    f.eventref_role.append(family_eventref.getAttribute("role"))
    
        if len(family.getElementsByTagName('childref') ) >= 1:
            for i in range(len(family.getElementsByTagName('childref') )):
                family_childref = family.getElementsByTagName('childref')[i]
                if family_childref.hasAttribute("hlink"):
                    f.childref_hlink.append(family_childref.getAttribute("hlink"))
                    
        f.save()
        
        # There can be so many individs to store that Cypher needs a pause
        time.sleep(0.1)
    
    f = Family("handle", "id")
    results = f.tell()
    for result in results:
        print("Number of families in db: " + str(result[0]))


def handle_notes(collection):
    # Get all the notes in the collection
    notes = collection.getElementsByTagName("note")

    print ("*****Notes*****")

    # Print detail of each note
    for note in notes:
        if note.hasAttribute("handle"):
            handle = note.getAttribute("handle")
            if note.hasAttribute("change"):
                change = note.getAttribute("change")
        if note.hasAttribute("id"):
            pid = note.getAttribute("id")
        if note.hasAttribute("type"):
            ptype = note.getAttribute("type")
        
        n = Note(handle, pid, ptype)
    
        if len(note.getElementsByTagName('text') ) == 1:
            note_text = note.getElementsByTagName('text')[0]
            n.text = note_text.childNodes[0].data
            
        n.save()
        
        # There can be so many individs to store that Cypher needs a pause
        time.sleep(0.1)
    
    n = Note("handle", "id",  "type")
    results = n.tell()
    for result in results:
        print("Number of notes in db: " + str(result[0]))


def handle_people(collection):
    # Get all the people in the collection
    people = collection.getElementsByTagName("person")
    
    print ("*****People*****")
    
    # Print detail of each person
    for person in people:
        if person.hasAttribute("handle"):
            handle = person.getAttribute("handle")
        if person.hasAttribute("change"):
            change = person.getAttribute("change")
        if person.hasAttribute("id"):
            pid = person.getAttribute("id")
        
        p = Person(handle, pid)
    
        if len(person.getElementsByTagName('gender') ) == 1:
            person_gender = person.getElementsByTagName('gender')[0]
            p.gender = person_gender.childNodes[0].data
        elif len(person.getElementsByTagName('gender') ) > 1:
            print("Error: More than one gender tag in a person")
    
        if len(person.getElementsByTagName('name') ) >= 1:
            for i in range(len(person.getElementsByTagName('name') )):
                person_name = person.getElementsByTagName('name')[i]
                pname = Name()
                if person_name.hasAttribute("alt"):
                    pname.alt = person_name.getAttribute("alt")
                if person_name.hasAttribute("type"):
                    pname.type = person_name.getAttribute("type")
    
                if len(person_name.getElementsByTagName('first') ) == 1:
                    person_first = person_name.getElementsByTagName('first')[0]
                    if len(person_first.childNodes) == 1:
                        pname.first = person_first.childNodes[0].data
                    elif len(person_first.childNodes) > 1:
                        print("Error: More than one child node in a first name of a person")
                elif len(person_name.getElementsByTagName('first') ) > 1:
                    print("Error: More than one first name in a person")
    
                if len(person_name.getElementsByTagName('surname') ) == 1:
                    person_surname = person_name.getElementsByTagName('surname')[0]
                    if len(person_surname.childNodes ) == 1:
                        pname.surname = person_surname.childNodes[0].data
                    elif len(person_surname.childNodes) > 1:
                        print("Error: More than one child node in a surname of a person")
                elif len(person_name.getElementsByTagName('surname') ) > 1:
                    print("Error: More than one surname in a person")
    
                if len(person_name.getElementsByTagName('suffix') ) == 1:
                    person_suffix = person_name.getElementsByTagName('suffix')[0]
                    pname.suffix = person_suffix.childNodes[0].data
                elif len(person_name.getElementsByTagName('suffix') ) > 1:
                    print("Error: More than one suffix in a person")
                    
                p.name.append(pname)
    
        if len(person.getElementsByTagName('eventref') ) >= 1:
            for i in range(len(person.getElementsByTagName('eventref') )):
                person_eventref = person.getElementsByTagName('eventref')[i]
                if person_eventref.hasAttribute("hlink"):
                    p.eventref_hlink.append(person_eventref.getAttribute("hlink"))
                if person_eventref.hasAttribute("role"):
                    p.eventref_role.append(person_eventref.getAttribute("role"))
                    
        if len(person.getElementsByTagName('parentin') ) >= 1:
            for i in range(len(person.getElementsByTagName('parentin') )):
                person_parentin = person.getElementsByTagName('parentin')[i]
                if person_parentin.hasAttribute("hlink"):
                    p.parentin_hlink.append(person_parentin.getAttribute("hlink"))
    
        if len(person.getElementsByTagName('citationref') ) >= 1:
            for i in range(len(person.getElementsByTagName('citationref') )):
                person_citationref = person.getElementsByTagName('citationref')[i]
                if person_citationref.hasAttribute("hlink"):
                    p.citationref_hlink.append(person_citationref.getAttribute("hlink"))
                    
        p.save()
        
        # There can be so many individs to store that Cypher needs a pause
        time.sleep(0.1)
    
    p = Person("handle", "id")
    results = p.tell()
    for result in results:
        print("Number of people in db: " + str(result[0]))


def handle_places(collection):
    # Get all the places in the collection
    places = collection.getElementsByTagName("placeobj")
    
    print ("*****Places*****")
    
    # Print detail of each placeobj
    for placeobj in places:
        if placeobj.hasAttribute("handle"):
            handle = placeobj.getAttribute("handle")
        if placeobj.hasAttribute("change"):
            change = placeobj.getAttribute("change")
        if placeobj.hasAttribute("id"):
            pid = placeobj.getAttribute("id")
        if placeobj.hasAttribute("type"):
            ptype = placeobj.getAttribute("type")
        
        place = Place(handle, pid, ptype)
    
        if len(placeobj.getElementsByTagName('ptitle') ) == 1:
            placeobj_ptitle = placeobj.getElementsByTagName('ptitle')[0]
            place.ptitle = placeobj_ptitle.childNodes[0].data
        elif len(placeobj.getElementsByTagName('ptitle') ) > 1:
            print("Error: More than one ptitle in a place")
    
        if len(placeobj.getElementsByTagName('pname') ) >= 1:
            for i in range(len(placeobj.getElementsByTagName('pname') )):
                placeobj_pname = placeobj.getElementsByTagName('pname')[i]
                if placeobj_pname.hasAttribute("value"):
                    place.pname.append(placeobj_pname.getAttribute("value"))
    
        if len(placeobj.getElementsByTagName('placeref') ) == 1:
            placeobj_placeref = placeobj.getElementsByTagName('placeref')[0]
            if placeobj_placeref.hasAttribute("hlink"):
                place.placeref_hlink = placeobj_placeref.getAttribute("hlink")
        elif len(placeobj.getElementsByTagName('placeref') ) > 1:
            print("Error: More than one placeref in a place")
                
        place.save()
        
        # There can be so many individs to store that Cypher needs a pause
        time.sleep(0.1)
    
    p = Place("handle", "id", "type")
    results = p.tell()
    for result in results:
        print("Number of places in db: " + str(result[0]))


def handle_repositories(collection):
    # Get all the repositories in the collection
    repositories = collection.getElementsByTagName("repository")
    
    print ("*****Repositories*****")
    
    # Print detail of each repository
    for repository in repositories:
        if repository.hasAttribute("handle"):
            handle = repository.getAttribute("handle")
        if repository.hasAttribute("change"):
            change = repository.getAttribute("change")
        if repository.hasAttribute("id"):
            pid = repository.getAttribute("id")
        
        r = Repository(handle, pid)
    
        if len(repository.getElementsByTagName('rname') ) == 1:
            repository_rname = repository.getElementsByTagName('rname')[0]
            r.rname = repository_rname.childNodes[0].data
        elif len(repository.getElementsByTagName('rname') ) > 1:
            print("Error: More than one rname in a repository")
    
        if len(repository.getElementsByTagName('type') ) == 1:
            repository_type = repository.getElementsByTagName('type')[0]
            r.type =  repository_type.childNodes[0].data
        elif len(repository.getElementsByTagName('type') ) > 1:
            print("Error: More than one type in a repository")
    
        r.save()
        
        # There can be so many individs to store that Cypher needs a pause
        time.sleep(0.1)
    
    r = Repository("handle", "id")
    results = r.tell()
    for result in results:
        print("Number of repositories in db: " + str(result[0]))


def handle_sources(collection):
    # Get all the sources in the collection
    sources = collection.getElementsByTagName("source")
    
    print ("*****Sources*****")
    
    # Print detail of each source
    for source in sources:
        if source.hasAttribute("handle"):
            handle = source.getAttribute("handle")
        if source.hasAttribute("change"):
            change = source.getAttribute("change")
        if source.hasAttribute("id"):
            pid = source.getAttribute("id")
    
        s = Source(handle, pid)
    
        if len(source.getElementsByTagName('stitle') ) == 1:
            source_stitle = source.getElementsByTagName('stitle')[0]
            s.stitle = source_stitle.childNodes[0].data
        elif len(source.getElementsByTagName('stitle') ) > 1:
            print("Error: More than one stitle in a source")
    
        if len(source.getElementsByTagName('noteref') ) == 1:
            source_noteref = source.getElementsByTagName('noteref')[0]
            if source_noteref.hasAttribute("hlink"):
                s.noteref_hlink = source_noteref.getAttribute("hlink")
        elif len(source.getElementsByTagName('noteref') ) > 1:
            print("Error: More than one noteref in a source")
    
        if len(source.getElementsByTagName('reporef') ) == 1:
            source_reporef = source.getElementsByTagName('reporef')[0]
            if source_reporef.hasAttribute("hlink"):
                s.reporef_hlink = source_reporef.getAttribute("hlink")
        elif len(source.getElementsByTagName('reporef') ) > 1:
            print("Error: More than one reporef in a source")
    
        s.save()
        
        # There can be so many individs to store that Cypher needs a pause
        time.sleep(0.1)
    
    s = Source("handle", "id")
    results = s.tell()
    for result in results:
        print("Number of sources in db: " + str(result[0]))


def process_xml(args):

    # Open XML document using minidom parser
    try:
        DOMTree = xml.dom.minidom.parse(open(args.input_xml))
        collection = DOMTree.documentElement
    
        handle_notes(collection)
        handle_repositories(collection)
        handle_places(collection)
        handle_sources(collection)
        handle_citations(collection)
        handle_events(collection)
        handle_people(collection)
        handle_families(collection)
    except FileNotFoundError:
        print("Tiedostoa '{}' ei ole!".format(args.input_xml), file=stderr)
    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)



def main():
    parser = argparse.ArgumentParser(description='XML to Neo4j')
    parser.add_argument('input_xml', help="Name of the input XML file")

    if len(sys.argv) == 1:
        print("First argument must be the name of the XML file")
        return

    args = parser.parse_args()

    process_xml(args)


if __name__ == "__main__":
    main()
