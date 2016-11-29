#!/usr/bin/python3

from neo4j.v1 import GraphDatabase, basic_auth
#from flask import flash
#import logging
#import sys
import config as dbconf      # Tietokannan tiedot

def connect_db():
    """ 
        genelogy-paketin tarvitsema tietokantayhteys
        Ks- http://neo4j.com/docs/developer-manual/current/#driver-manual-index
        
    """
    global session

    #logging.debug("-- dbconf = {}".format(dir(dbconf)))
#    if 'session' in globals():
#        print ("connect_db - already done")
    if 'DB_HOST_PORT' in dir(dbconf):
        print ("connect_db - server {}".format(dbconf.DB_HOST_PORT))
        driver = GraphDatabase.driver(dbconf.DB_HOST_PORT, auth=basic_auth(dbconf.DB_USER, dbconf.DB_AUTH))
        session = driver.session()
        #authenticate(dbconf.DB_HOST_PORT, dbconf.DB_USER, dbconf.DB_AUTH)
        #graph = Graph('http://{0}/db/data/'.format(dbconf.DB_HOST_PORT))
    else:
        print ("connect_db - default local – EI TUETTU?")
        driver = GraphDatabase.driver("bolt://localhost", auth=basic_auth("neo4j", "localTaapeli"))
        session = driver.session()

    # Palautetaan tietokannan sijainnin hostname
    return driver.url

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

        global session
                
        query = """
            CREATE (c:Citation) 
            SET c.id='{}', c.confidence='{}', c.noteref_hlink='{}', c.sourceref_hlink='{}'
            """.format(self.id, self.confidence, self.noteref_hlink, self.sourceref_hlink)
            
        return session.run(query)

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
#        event = Node(self.label, handle=self.handle, id=self.id)
#        graph.create(event)
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
#        family = Node(self.label, handle=self.handle, id=self.id)
#        graph.create(family)
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
                id              esim. "N0001"
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
#        note = Node(self.label, handle=self.handle, id=self.id)
#        graph.create(note)
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
#        person = Node(self.label, handle=self.handle, id=self.id)
#        graph.create(person)
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
                id              esim. "P0001"
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
#        place = Node(self.label, handle=self.handle, id=self.id)
#        graph.create(place)
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
                id              esim. "R0001"
                rname           str arkiston nimi
                type            str arkiston tyyppi

     """

    def __init__(self, handle, id, type):
        """ Luo uuden repository-instanssin """
        self.handle = handle
        self.id = id

    def save(self):
        """ Tallettaa sen kantaan """
#        place = Node(self.label, handle=self.handle, id=self.id)
#        graph.create(repository)
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
                id              esim. "S0001"
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
#        source = Node(self.label, handle=self.handle, id=self.id)
#        graph.create(person)
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


