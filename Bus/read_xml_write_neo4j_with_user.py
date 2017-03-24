#!/usr/bin/python3

"""
Storing data from an XML file to the Neo4j database under a specific userid.
Jorma Haapasalo, 2016.

Parameters of main():
 1. The name of the input XML file.
 2. The UserId.
 
"""

import sys
import time
import xml.dom.minidom
import argparse
from sys import stderr
from classes.genealogy import connect_db, Citation, Event, Family, Name, Note, Person, Place, Repository, Source, User

connect_db()


def handle_citations(collection):
    # Get all the citations in the collection
    citations = collection.getElementsByTagName("citation")
    
    print ("*****Citations*****")
    counter = 0
    
    # Print detail of each citation
    for citation in citations:
        
        c = Citation()
        
        if citation.hasAttribute("handle"):
            c.handle = citation.getAttribute("handle")
        if citation.hasAttribute("change"):
            c.change = citation.getAttribute("change")
        if citation.hasAttribute("id"):
            c.id = citation.getAttribute("id")
    
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
        counter += 1
        
        # There can be so many individs to store that Cypher needs a pause
        time.sleep(0.1)
        
    print("Number of citations stored: " + str(counter))


def handle_events(collection, userid):
    # Get all the events in the collection
    events = collection.getElementsByTagName("event")
    
    print ("*****Events*****")
    counter = 0
    
    # Print detail of each event
    for event in events:

        e = Event()
        
        if event.hasAttribute("handle"):
            e.handle = event.getAttribute("handle")
        if event.hasAttribute("change"):
            e.change = event.getAttribute("change")
        if event.hasAttribute("id"):
            e.id = event.getAttribute("id")
            
        if len(event.getElementsByTagName('type') ) == 1:
            event_type = event.getElementsByTagName('type')[0]
            # If there are type tags, but no type data
            if (len(event_type.childNodes) > 0):
                e.type = event_type.childNodes[0].data
            else:
                e.type = ''
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
                
        e.save(userid)
        
        # There can be so many individs to store that Cypher needs a pause
        time.sleep(0.1)
        counter += 1
        
    print("Number of events stored: " + str(counter))


def handle_families(collection):
    # Get all the families in the collection
    families = collection.getElementsByTagName("family")
    
    print ("*****Families*****")
    counter = 0
    
    # Print detail of each family
    for family in families:
        
        f = Family()
        
        if family.hasAttribute("handle"):
            f.handle = family.getAttribute("handle")
        if family.hasAttribute("change"):
            f.change = family.getAttribute("change")
        if family.hasAttribute("id"):
            f.id = family.getAttribute("id")
    
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
        counter += 1
        
        # There can be so many individs to store that Cypher needs a pause
        time.sleep(0.1)
        
    print("Number of families stored: " + str(counter))


def handle_notes(collection):
    # Get all the notes in the collection
    notes = collection.getElementsByTagName("note")

    print ("*****Notes*****")
    counter = 0

    # Print detail of each note
    for note in notes:
        
        n = Note()

        if note.hasAttribute("handle"):
            n.handle = note.getAttribute("handle")
        if note.hasAttribute("change"):
            n.change = note.getAttribute("change")
        if note.hasAttribute("id"):
            n.id = note.getAttribute("id")
        if note.hasAttribute("type"):
            n.type = note.getAttribute("type")
    
        if len(note.getElementsByTagName('text') ) == 1:
            note_text = note.getElementsByTagName('text')[0]
            n.text = note_text.childNodes[0].data
            
        n.save()
        counter += 1
        
        # There can be so many individs to store that Cypher needs a pause
        time.sleep(0.1)
        
    print("Number of notes stored: " + str(counter))
    

def handle_people(collection, userid):
    # Get all the people in the collection
    people = collection.getElementsByTagName("person")
    
    print ("*****People*****")
    counter = 0
    
    # Print detail of each person
    for person in people:
        
        p = Person()

        if person.hasAttribute("handle"):
            p.handle = person.getAttribute("handle")
        if person.hasAttribute("change"):
            p.change = person.getAttribute("change")
        if person.hasAttribute("id"):
            p.id = person.getAttribute("id")
    
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
                    
        p.save(userid)
        counter += 1
        
        # There can be so many individs to store that Cypher needs a pause
        time.sleep(0.1)
        
    print("Number of people stored: " + str(counter))


def handle_places(collection):
    # Get all the places in the collection
    places = collection.getElementsByTagName("placeobj")
    
    print ("*****Places*****")
    counter = 0
    
    # Print detail of each placeobj
    for placeobj in places:
        
        place = Place()

        if placeobj.hasAttribute("handle"):
            place.handle = placeobj.getAttribute("handle")
        if placeobj.hasAttribute("change"):
            place.change = placeobj.getAttribute("change")
        if placeobj.hasAttribute("id"):
            place.id = placeobj.getAttribute("id")
        if placeobj.hasAttribute("type"):
            place.type = placeobj.getAttribute("type")
    
        if len(placeobj.getElementsByTagName('ptitle') ) == 1:
            placeobj_ptitle = placeobj.getElementsByTagName('ptitle')[0]
            place.ptitle = placeobj_ptitle.childNodes[0].data
        elif len(placeobj.getElementsByTagName('ptitle') ) > 1:
            print("Error: More than one ptitle in a place")
    
        if len(placeobj.getElementsByTagName('pname') ) >= 1:
            for i in range(len(placeobj.getElementsByTagName('pname') )):
                placeobj_pname = placeobj.getElementsByTagName('pname')[i]
                if placeobj_pname.hasAttribute("value"):
                    place.pname = placeobj_pname.getAttribute("value")
    
        if len(placeobj.getElementsByTagName('placeref') ) == 1:
            placeobj_placeref = placeobj.getElementsByTagName('placeref')[0]
            if placeobj_placeref.hasAttribute("hlink"):
                place.placeref_hlink = placeobj_placeref.getAttribute("hlink")
        elif len(placeobj.getElementsByTagName('placeref') ) > 1:
            print("Error: More than one placeref in a place")
                
        place.save()
        counter += 1
        
        # There can be so many individs to store that Cypher needs a pause
        time.sleep(0.1)
    
    print("Number of places stored: " + str(counter))


def handle_repositories(collection):
    # Get all the repositories in the collection
    repositories = collection.getElementsByTagName("repository")
    
    print ("*****Repositories*****")
    counter = 0
    
    # Print detail of each repository
    for repository in repositories:
        
        r = Repository()

        if repository.hasAttribute("handle"):
            r.handle = repository.getAttribute("handle")
        if repository.hasAttribute("change"):
            r.change = repository.getAttribute("change")
        if repository.hasAttribute("id"):
            r.id = repository.getAttribute("id")
    
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
        counter += 1
        
        # There can be so many individs to store that Cypher needs a pause
        time.sleep(0.1)
        
    print("Number of repositories stored: " + str(counter))


def handle_sources(collection):
    # Get all the sources in the collection
    sources = collection.getElementsByTagName("source")
    
    print ("*****Sources*****")
    counter = 0
    
    # Print detail of each source
    for source in sources:
    
        s = Source()

        if source.hasAttribute("handle"):
            s.handle = source.getAttribute("handle")
        if source.hasAttribute("change"):
            s.change = source.getAttribute("change")
        if source.hasAttribute("id"):
            s.id = source.getAttribute("id")
    
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
            if source_reporef.hasAttribute("medium"):
                s.reporef_medium = source_reporef.getAttribute("medium")
        elif len(source.getElementsByTagName('reporef') ) > 1:
            print("Error: More than one reporef in a source")
    
        s.save()
        counter += 1
        
        # There can be so many individs to store that Cypher needs a pause
        time.sleep(0.1)
        
    print("Number of sources stored: " + str(counter))

        
def number_of_citations():
    print("Number of citations in db: " + Citation.get_total())
        
        
def number_of_events():
    print("Number of events in db: " + Event.get_total())
        
        
def number_of_families():
    print("Number of families in db: " + Family.get_total())
        
        
def number_of_notes():
    print("Number of notes in db: " + Note.get_total())
        
        
def number_of_people():
    print("Number of people in db: " + Person.get_total())
        
        
def number_of_places():
    print("Number of places in db: " + Place.get_total())
        
        
def number_of_repositories():
    print("Number of repositories in db: " + Repository.get_total())
        
        
def number_of_sources():
    print("Number of sources in db: " + Source.get_total())


def process_xml(args):

    # Open XML document using minidom parser
    try:
        DOMTree = xml.dom.minidom.parse(open(args.input_xml))
        collection = DOMTree.documentElement
        
        # Create User if needed
        User.create_user(args.userid)
    
        t = time.perf_counter()
        handle_notes(collection)
        elapsed_time = time.perf_counter() - t
        print("Time needed: " + str(elapsed_time) + " seconds")
        number_of_notes()
        
        t = time.perf_counter()
        handle_repositories(collection)
        elapsed_time = time.perf_counter() - t
        print("Time needed: " + str(elapsed_time) + " seconds")
        number_of_repositories()
        
        t = time.perf_counter()
        handle_places(collection)
        elapsed_time = time.perf_counter() - t
        print("Time needed: " + str(elapsed_time) + " seconds")
        number_of_places()
        
        t = time.perf_counter()
        handle_sources(collection)
        elapsed_time = time.perf_counter() - t
        print("Time needed: " + str(elapsed_time) + " seconds")
        number_of_sources()
        
        t = time.perf_counter()
        handle_citations(collection)
        elapsed_time = time.perf_counter() - t
        print("Time needed: " + str(elapsed_time) + " seconds")
        number_of_citations()
        
        t = time.perf_counter()
        handle_events(collection, args.userid)
        elapsed_time = time.perf_counter() - t
        print("Time needed: " + str(elapsed_time) + " seconds")
        number_of_events()
        
        t = time.perf_counter()
        handle_people(collection, args.userid)
        elapsed_time = time.perf_counter() - t
        print("Time needed: " + str(elapsed_time) + " seconds")
        number_of_people()
        
        t = time.perf_counter()
        handle_families(collection)
        elapsed_time = time.perf_counter() - t
        print("Time needed: " + str(elapsed_time) + " seconds")
        number_of_families()
        
    except FileNotFoundError:
        print("Tiedostoa '{}' ei ole!".format(args.input_xml), file=stderr)
    except Exception as err:
        print("Virhe: {0}".format(err), file=stderr)



def main():
    parser = argparse.ArgumentParser(description='XML to Neo4j under the specific userid')
    parser.add_argument('input_xml', help="Name of the input XML file")
    parser.add_argument('userid', help="The UserId of the genealogical researcher")

    if len(sys.argv) == 1:
        print("There must be two arguments: the name of the XML file and the the userid of the researcher")
        return

    args = parser.parse_args()

    process_xml(args)


if __name__ == "__main__":
    main()
