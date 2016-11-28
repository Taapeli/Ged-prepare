#!/usr/bin/python3

from xml.dom.minidom import parse
import xml.dom.minidom

class Citation:
    """ Lähteen paikka
            
        Properties:
                handle          
                id              esim. "C0001"
                confidence      str confidence
                sourceid        str lähteen osoite
     """

    def __init__(self, handle, id):
        """ Luo uuden citation-instanssin """
        self.handle = handle
        self.id = id
        self.noteref_hlink = ''
        self.sourceref_hlink = ''

    def save(self):
        """ Tallettaa sen kantaan """
        citation = Node(self.label, handle=self.handle, id=self.id)
        graph.create(citation)
        return True

    def print(self):
        """ Tulostaa tiedot """
        print ("*****Citation*****")
        print ("Handle: " + self.handle)
        print ("Id: " + self.id)
        print ("Confidence: " + self.confidence)
        if self.noteref_hlink != '':
            print ("Noteref_hlink: " + self.noteref_hlink)
        if self.sourceref_hlink != '':
            print ("Sourceref_hlink: " + self.sourceref_hlink)
        return True

class Event:
    """ Tapahtuma
            
        Properties:
                handle          
                id                 esim. "E0001"
                type               esim. "Birth"
                date               str aika
                place_hlink        str paikan osoite
                citationref_hlink  str lähteen paikan osoite
     """

    def __init__(self, handle, id):
        """ Luo uuden event-instanssin """
        self.handle = handle
        self.id = id

    def save(self):
        """ Tallettaa sen kantaan """
        event = Node(self.label, handle=self.handle, id=self.id)
        graph.create(event)
        return True

    def print(self):
        """ Tulostaa tiedot """
        print ("Handle: " + self.handle)
        print ("Id: " + self.id)
        print ("Type: " + self.type)
        print ("Dateval: " + self.date)
        print ("Place_hlink: " + self.place_hlink)
        print ("Citationref_hlink: " + self.citationref_hlink)
        return True

class Family:
    """ Perhe
            
        Properties:
                handle          
                id              esim. "F0001"
                rel             str suhde
                father          str isän osoite
                mother          str äidin osoite
                eventref_hlink  str tapahtuman osoite
                eventref_role   str tapahtuman rooli
                childref_hlink  str lapsen osoite
     """

    def __init__(self, handle, id):
        """ Luo uuden family-instanssin """
        self.handle = handle
        self.id = id
        self.eventref_hlink = []
        self.eventref_role = []
        self.childref_hlink = []

    def save(self):
        """ Tallettaa sen kantaan """
        family = Node(self.label, handle=self.handle, id=self.id)
        graph.create(family)
        return True

    def print(self):
        """ Tulostaa tiedot """
        print ("*****Family*****")
        print ("Handle: " + self.handle)
        print ("Id: " + self.id)
        print ("Rel: " + self.rel_type)
        print ("Father: " + self.father)
        print ("Mother: " + self.mother)
        if len(self.eventref_hlink) > 0:
            for i in range(len(self.eventref_hlink)):
                print ("Eventref_hlink: " + self.eventref_hlink[i])
        if len(self.eventref_role) > 0:
            for i in range(len(self.eventref_role)):
                print ("Role: " + self.eventref_role[i])
        if len(self.childref_hlink) > 0:
            for i in range(len(self.childref_hlink)):
                print ("Childref_hlink: " + self.childref_hlink[i])
        return True

class Note:
    """ Huomautus
            
        Properties:
                handle          
                id              esim. "I0001"
                type            str huomautuksen tyyppi
                text            str huomautuksen sisältö
     """

    def __init__(self, handle, id, type):
        """ Luo uuden note-instanssin """
        self.handle = handle
        self.id = id
        self.type = type

    def save(self):
        """ Tallettaa sen kantaan """
        note = Node(self.label, handle=self.handle, id=self.id)
        graph.create(note)
        return True

    def print(self):
        """ Tulostaa tiedot """
        print ("*****Note*****")
        print ("Handle: " + self.handle)
        print ("Id: " + self.id)
        print ("Type: " + self.type)
        print ("Text: " + self.text)
        return True

class Person:
    """ Henkilö
            
        Properties:
                handle          
                id              esim. "I0001"
                gender          str sukupuoli
                alt             str muun nimen nro
                type            str nimen tyyppi
                first           str etunimi
                surname         str sukunimi
                suffix          str patronyymi
                eventref        str tapahtuman osoite
                parentin        str vanhempien osoite
                citationref     str lähteen paikan osoite
     """

    def __init__(self, handle, id):
        """ Luo uuden person-instanssin """
        self.handle = handle
        self.id = id
        self.alt = []
        self.type = []
        self.first = []
        self.surname = []
        self.suffix = []
        self.eventref_role = []
        self.eventref_hlink = []
        self.parentin_hlink = []
        self.citationref_hlink = []

    def save(self):
        """ Tallettaa sen kantaan """
        person = Node(self.label, handle=self.handle, id=self.id)
        graph.create(person)
        return True

    def print(self):
        """ Tulostaa tiedot """
        print ("*****Person*****")
        print ("Handle: " + self.handle)
        print ("Id: " + self.id)
        print ("Gender: " + self.gender)
        if len(self.alt) > 0:
            for i in range(len(self.alt)):
                print ("Alt: " + self.alt[i])
        if len(self.type) > 0:
            for i in range(len(self.type)):
                print ("Type: " + self.type[i])
        if len(self.first) > 0:
            for i in range(len(self.first)):
                print ("First: " + self.first[i])
        if len(self.surname) > 0:
            for i in range(len(self.surname)):
                print ("Surname: " + self.surname[i])
        if len(self.suffix) > 0:
            for i in range(len(self.suffix)):
                print ("Suffix: " + self.suffix[i])
        if len(self.eventref_hlink) > 0:
            for i in range(len(self.eventref_hlink)):
                print ("Eventref_hlink: " + self.eventref_hlink[i])
        if len(self.eventref_role) > 0:
            for i in range(len(self.eventref_role)):
                print ("Eventref_role: " + self.eventref_role[i])
        if len(self.parentin_hlink) > 0:
            for i in range(len(self.parentin_hlink)):
                print ("Parentin_hlink: " + self.parentin_hlink[i])
        if len(self.citationref_hlink) > 0:
            for i in range(len(self.citationref_hlink)):
                print ("Citationref_hlink: " + self.citationref_hlink[i])
        return True

class Place:
    """ Paikka
            
        Properties:
                handle          
                id              esim. "I0001"
                type            str paikan tyyppi
                pname           str paikan nimi
                placeref_hlink  str paikan osoite
     """

    def __init__(self, handle, id, type):
        """ Luo uuden place-instanssin """
        self.handle = handle
        self.id = id
        self.type = type
        self.pname = []
        self.placeref_hlink = ''

    def save(self):
        """ Tallettaa sen kantaan """
        place = Node(self.label, handle=self.handle, id=self.id)
        graph.create(place)
        return True

    def print(self):
        """ Tulostaa tiedot """
        print ("*****Placeobj*****")
        print ("Handle: " + self.handle)
        print ("Id: " + self.id)
        print ("Type: " + self.type)
        if len(self.pname) > 0:
            for i in range(len(self.pname)):
                print ("Pname: " + self.pname[i])
        if self.placeref_hlink != '':
            print ("Placeref_hlink: " + self.placeref_hlink)
        return True

class Repository:
    """ Arkisto
            
        Properties:
                handle          
                id              esim. "I0001"
                rname           str arkiston nimi
                type            str arkiston tyyppi

     """

    def __init__(self, handle, id, type):
        """ Luo uuden repository-instanssin """
        self.handle = handle
        self.id = id

    def save(self):
        """ Tallettaa sen kantaan """
        place = Node(self.label, handle=self.handle, id=self.id)
        graph.create(repository)
        return True

    def print(self):
        """ Tulostaa tiedot """
        print ("*****Repository*****")
        print ("Handle: " + self.handle)
        print ("Id: " + self.id)
        print ("Rname: " + self.rname)
        print ("Type: " + self.type)
        return True

class Source:
    """ Lähde
            
        Properties:
                handle          
                id              esim. "I0001"
                stitle          str lähteen otsikko
                noteref_hlink   str huomautuksen osoite
                reporef_hlink   str repositoryn osoite
     """

    def __init__(self, handle, id):
        """ Luo uuden source-instanssin """
        self.handle = handle
        self.id = id
        self.stitle = ''
        self.noteref_hlink = ''
        self.reporef_hlink = ''

    def save(self):
        """ Tallettaa sen kantaan """
        source = Node(self.label, handle=self.handle, id=self.id)
        graph.create(person)
        return True

    def print(self):
        """ Tulostaa tiedot """
        print ("*****Source*****")
        print ("Handle: " + self.handle)
        print ("Id: " + self.id)
        if self.stitle != '':
            print ("Stitle: " + self.stitle)
        if self.noteref_hlink != '':
            print ("Noteref_hlink: " + self.noteref_hlink)
        if self.reporef_hlink != '':
            print ("Reporef_hlink: " + self.reporef_hlink)
        return True

# Open XML document using minidom parser
DOMTree = xml.dom.minidom.parse("pohjanmaa_referenssi.txt")
collection = DOMTree.documentElement

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
        id = event.getAttribute("id")
    
    e = Event(handle, id)

    if len(event.getElementsByTagName('type') ) == 1:
        event_type = event.getElementsByTagName('type')[0]
        e.type = event_type.childNodes[0].data

    if len(event.getElementsByTagName('dateval') ) == 1:
        event_dateval = event.getElementsByTagName('dateval')[0]
        if event_dateval.hasAttribute("val"):
            e.date = event_dateval.getAttribute("val")

    if len(event.getElementsByTagName('place') ) == 1:
        event_place = event.getElementsByTagName('place')[0]
        if event_place.hasAttribute("hlink"):
            e.place_hlink = event_place.getAttribute("hlink")

    if len(event.getElementsByTagName('citationref') ) == 1:
        event_citationref = event.getElementsByTagName('citationref')[0]
        if event_citationref.hasAttribute("hlink"):
            e.citationref_hlink = event_citationref.getAttribute("hlink")
            
    e.print()


#------------------------------------------------------------------------

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
        id = family.getAttribute("id")
    
    f = Family(handle, id)

    if len(family.getElementsByTagName('rel') ) == 1:
        family_rel = family.getElementsByTagName('rel')[0]
        if family_rel.hasAttribute("type"):
            f.rel_type = family_rel.getAttribute("type")

    if len(family.getElementsByTagName('father') ) == 1:
        family_father = family.getElementsByTagName('father')[0]
        if family_father.hasAttribute("hlink"):
            f.father = family_father.getAttribute("hlink")

    if len(family.getElementsByTagName('mother') ) == 1:
        family_mother = family.getElementsByTagName('mother')[0]
        if family_mother.hasAttribute("hlink"):
            f.mother = family_mother.getAttribute("hlink")

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
                
    f.print()


#------------------------------------------------------------------------

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
        id = person.getAttribute("id")
    
    p = Person(handle, id)

    if len(person.getElementsByTagName('gender') ) == 1:
        person_gender = person.getElementsByTagName('gender')[0]
        p.gender = person_gender.childNodes[0].data

    if len(person.getElementsByTagName('name') ) >= 1:
        for i in range(len(person.getElementsByTagName('name') )):
            person_name = person.getElementsByTagName('name')[i]
            if person_name.hasAttribute("alt"):
                p.alt.append(person_name.getAttribute("alt"))
            if person_name.hasAttribute("type"):
                p.type.append(person_name.getAttribute("type"))

        if len(person_name.getElementsByTagName('first') ) >= 1:
            for j in range(len(person_name.getElementsByTagName('first') )):
                person_first = person_name.getElementsByTagName('first')[i]
                p.first.append(person_first.childNodes[i].data)

        if len(person_name.getElementsByTagName('surname') ) >= 1:
            for j in range(len(person_name.getElementsByTagName('surname') )):
                person_surname = person_name.getElementsByTagName('surname')[i]
                if len(person_surname.childNodes) >= 1:
                    p.surname.append(person_surname.childNodes[0].data)

        if len(person_name.getElementsByTagName('suffix') ) >= 1:
            for j in range(len(person_name.getElementsByTagName('suffix') )):
                person_suffix = person_name.getElementsByTagName('suffix')[i]
                p.suffix.append(person_suffix.childNodes[0].data)

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
                
    p.print()

#------------------------------------------------------------------------

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
        id = citation.getAttribute("id")
    
    c = Citation(handle, id)

    if len(citation.getElementsByTagName('dateval') ) == 1:
        citation_dateval = citation.getElementsByTagName('dateval')[0]
        if citation_dateval.hasAttribute("val"):
            c.dateval = citation_dateval.getAttribute("val")

    if len(citation.getElementsByTagName('page') ) == 1:
        citation_page = citation.getElementsByTagName('page')[0]
        c.page = citation_page.childNodes[0].data

    if len(citation.getElementsByTagName('confidence') ) == 1:
        citation_confidence = citation.getElementsByTagName('confidence')[0]
        c.confidence = citation_confidence.childNodes[0].data

    if len(citation.getElementsByTagName('noteref') ) == 1:
        citation_noteref = citation.getElementsByTagName('noteref')[0]
        if citation_noteref.hasAttribute("hlink"):
            c.noteref_hlink = citation_noteref.getAttribute("hlink")

    if len(citation.getElementsByTagName('sourceref') ) == 1:
        citation_sourceref = citation.getElementsByTagName('sourceref')[0]
        if citation_sourceref.hasAttribute("hlink"):
            c.sourceref_hlink = citation_sourceref.getAttribute("hlink")
            
    c.print()


#------------------------------------------------------------------------

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
        id = source.getAttribute("id")
    
    s = Source(handle, id)

    if len(source.getElementsByTagName('stitle') ) == 1:
        source_stitle = source.getElementsByTagName('stitle')[0]
        s.stitle = source_stitle.childNodes[0].data

    if len(source.getElementsByTagName('noteref') ) == 1:
        source_noteref = source.getElementsByTagName('noteref')[0]
        if source_noteref.hasAttribute("hlink"):
            s.noteref_hlink = source_noteref.getAttribute("hlink")

    if len(source.getElementsByTagName('reporef') ) == 1:
        source_reporef = source.getElementsByTagName('reporef')[0]
        if source_reporef.hasAttribute("hlink"):
            s.reporef_hlink = source_reporef.getAttribute("hlink")
    
    s.print()


#------------------------------------------------------------------------

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
        id = placeobj.getAttribute("id")
    if placeobj.hasAttribute("type"):
        type = placeobj.getAttribute("type")
    
    place = Place(handle, id, type)

    if len(placeobj.getElementsByTagName('ptitle') ) == 1:
        placeobj_ptitle = placeobj.getElementsByTagName('ptitle')[0]
        place.ptitle = placeobj_ptitle.childNodes[0].data

    if len(placeobj.getElementsByTagName('pname') ) >= 1:
        for i in range(len(placeobj.getElementsByTagName('pname') )):
            placeobj_pname = placeobj.getElementsByTagName('pname')[i]
            if placeobj_pname.hasAttribute("value"):
                place.pname.append(placeobj_pname.getAttribute("value"))

    if len(placeobj.getElementsByTagName('placeref') ) == 1:
        placeobj_placeref = placeobj.getElementsByTagName('placeref')[0]
        if placeobj_placeref.hasAttribute("hlink"):
            place.placeref_hlink = placeobj_placeref.getAttribute("hlink")
            
    place.print()

#------------------------------------------------------------------------

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
        id = repository.getAttribute("id")
    
    r = Repository(handle, id, type)

    if len(repository.getElementsByTagName('rname') ) == 1:
        repository_rname = repository.getElementsByTagName('rname')[0]
        r.rname = repository_rname.childNodes[0].data

    if len(repository.getElementsByTagName('type') ) == 1:
        repository_type = repository.getElementsByTagName('type')[0]
        r.type =  repository_type.childNodes[0].data

    r.print()

#------------------------------------------------------------------------

# Get all the repositories in the collection
notes = collection.getElementsByTagName("note")

print ("*****Notes*****")

# Print detail of each note
for note in notes:
    if note.hasAttribute("handle"):
        handle = note.getAttribute("handle")
    if note.hasAttribute("change"):
        change = note.getAttribute("change")
    if note.hasAttribute("id"):
        id = note.getAttribute("id")
    if note.hasAttribute("type"):
        type = note.getAttribute("type")
    
    n = Note(handle, id, type)

    if len(note.getElementsByTagName('text') ) == 1:
        note_text = note.getElementsByTagName('text')[0]
        n.text = note_text.childNodes[0].data
        
    n.print()

