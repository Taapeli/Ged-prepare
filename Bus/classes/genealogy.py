#!/usr/bin/python3

from neo4j.v1 import GraphDatabase, basic_auth
#from flask import flash
#import logging
from sys import stderr
import config as dbconf      # Tietokannan tiedot
from flask.globals import session

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
    """ Viittaus
            
        Properties:
                handle          
                id               esim. "C0001"
                confidence       str confidence
                noteref_hlink    str huomautuksen osoite
                sourceref_hlink  str lähteen osoite
     """

    def __init__(self):
        """ Luo uuden citation-instanssin """
        self.handle = ''
        self.id = ''
        self.noteref_hlink = ''
        self.sourceref_hlink = ''


    def save(self):
        """ Tallettaa sen kantaan """

        global session

        try:
            # Create a new Citation node
            query = """
                CREATE (n:Citation) 
                SET n.gramps_handle='{}', n.id='{}', n.confidence='{}'
                """.format(self.handle, self.id, self.confidence)
                
            session.run(query)
        except Exception as err:
            print("Virhe: {0}".format(err), file=stderr)

        try:
            # Make possible relations from the Citation node
            if self.noteref_hlink != '':
                query = """
                    MATCH (n:Citation) WHERE n.gramps_handle='{}'
                    MATCH (m:Source) WHERE m.gramps_handle='{}'
                    MERGE (n)-[r:SOURCE]->(m)
                     """.format(self.handle, self.noteref_hlink)
                                 
                session.run(query)
        except Exception as err:
            print("Virhe: {0}".format(err), file=stderr)

        try:   
            if self.sourceref_hlink != '':
                query = """
                    MATCH (n:Citation) WHERE n.gramps_handle='{}'
                    MATCH (m:Source) WHERE m.gramps_handle='{}'
                    MERGE (n)-[r:SOURCE]->(m)
                     """.format(self.handle, self.sourceref_hlink)
                                 
                session.run(query)
        except Exception as err:
            print("Virhe: {0}".format(err), file=stderr)
            
        return


    def print_data(self):
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

    
    @staticmethod       
    def get_total():
        """ Tulostaa lähteiden määrän tietokannassa """
        
        global session
                
        query = """
            MATCH (c:Citation) RETURN COUNT(c)
            """
        results =  session.run(query)
        
        for result in results:
            return str(result[0])


class Event:
    """ Tapahtuma
            
        Properties:
                handle          
                id                 esim. "E0001"
                type               esim. "Birth"
                date               str aika
                place_hlink        str paikan osoite
                citationref_hlink  str viittauksen osoite
     """

    def __init__(self):
        """ Luo uuden event-instanssin """
        self.handle = ''
        self.id = ''
        self.date = ''
        self.place_hlink = ''
        self.citationref_hlink = ''


    def save(self):
        """ Tallettaa sen kantaan """

        global session

        try:
            query = """
                CREATE (e:Event) 
                SET e.gramps_handle='{}', e.id='{}', e.type='{}', e.date='{}'
                """.format(self.handle, self.id, self.type, self.date)
                
            session.run(query)
        except Exception as err:
            print("Virhe: {0}".format(err), file=stderr)

        try:
            # Make possible relations from the Event node
            if self.place_hlink != '':
                query = """
                    MATCH (n:Event) WHERE n.gramps_handle='{}'
                    MATCH (m:Place) WHERE m.gramps_handle='{}'
                    MERGE (n)-[r:PLACE]->(m)
                     """.format(self.handle, self.place_hlink)
                                 
                session.run(query)
        except Exception as err:
            print("Virhe: {0}".format(err), file=stderr)

        try:
            if self.citationref_hlink != '':
                query = """
                    MATCH (n:Event) WHERE n.gramps_handle='{}'
                    MATCH (m:Citation) WHERE m.gramps_handle='{}'
                    MERGE (n)-[r:CITATION]->(m)
                     """.format(self.handle, self.citationref_hlink)
                                 
                session.run(query)
        except Exception as err:
            print("Virhe: {0}".format(err), file=stderr)
            
        return


    def print_data(self):
        """ Tulostaa tiedot """
        print ("Handle: " + self.handle)
        print ("Id: " + self.id)
        print ("Type: " + self.type)
        print ("Dateval: " + self.date)
        print ("Place_hlink: " + self.place_hlink)
        print ("Citationref_hlink: " + self.citationref_hlink)
        return True
        
    
    @staticmethod        
    def get_total():
        """ Tulostaa tapahtumien määrän tietokannassa """
        
        global session
                
        query = """
            MATCH (e:Event) RETURN COUNT(e)
            """
        results =  session.run(query)
        
        for result in results:
            return str(result[0])
   

class Family:
    """ Perhe
            
        Properties:
                handle          
                id              esim. "F0001"
                rel_type        str suhteen tyyppi
                father          str isän osoite
                mother          str äidin osoite
                eventref_hlink  str tapahtuman osoite
                eventref_role   str tapahtuman rooli
                childref_hlink  str lapsen osoite
     """

    def __init__(self):
        """ Luo uuden family-instanssin """
        self.handle = ''
        self.id = ''
        self.eventref_hlink = []
        self.eventref_role = []
        self.childref_hlink = []


    def save(self):
        """ Tallettaa sen kantaan """

        global session

        try:
            query = """
                CREATE (n:Family) 
                SET n.gramps_handle='{}', n.id='{}', n.rel_type='{}'
                """.format(self.handle, self.id, self.rel_type)
                
            session.run(query)
        except Exception as err:
            print("Virhe: {0}".format(err), file=stderr)

        try:
            # Make possible relations from the Family node
            if self.father != '':
                query = """
                    MATCH (n:Family) WHERE n.gramps_handle='{}'
                    MATCH (m:Person) WHERE m.gramps_handle='{}'
                    MERGE (n)-[r:FATHER]->(m)
                     """.format(self.handle, self.father)
                                 
                session.run(query)
        except Exception as err:
            print("Virhe: {0}".format(err), file=stderr)

        try:
            if self.mother != '':
                query = """
                    MATCH (n:Family) WHERE n.gramps_handle='{}'
                    MATCH (m:Person) WHERE m.gramps_handle='{}'
                    MERGE (n)-[r:MOTHER]->(m)
                     """.format(self.handle, self.mother)
                                 
                session.run(query)
        except Exception as err:
            print("Virhe: {0}".format(err), file=stderr)

        if len(self.eventref_hlink) > 0:
            for i in range(len(self.eventref_hlink)):
                try:
                    query = """
                        MATCH (n:Family) WHERE n.gramps_handle='{}'
                        MATCH (m:Event) WHERE m.gramps_handle='{}'
                        MERGE (n)-[r:EVENT]->(m)
                         """.format(self.handle, self.eventref_hlink[i])
                                 
                    session.run(query)
                except Exception as err:
                    print("Virhe: {0}".format(err), file=stderr)
                
                try:
                    query = """
                        MATCH (n:Family)-[r:EVENT]->(m:Event)
                        WHERE n.gramps_handle='{}' AND m.gramps_handle='{}'
                        SET r.role ='{}'
                         """.format(self.handle, self.eventref_hlink[i], self.eventref_role[i])
                                 
                    session.run(query)
                except Exception as err:
                    print("Virhe: {0}".format(err), file=stderr)
  
        if len(self.childref_hlink) > 0:
            for i in range(len(self.childref_hlink)):
                try:
                    query = """
                        MATCH (n:Family) WHERE n.gramps_handle='{}'
                        MATCH (m:Person) WHERE m.gramps_handle='{}'
                        MERGE (n)-[r:CHILD]->(m)
                         """.format(self.handle, self.childref_hlink[i])
                                 
                    session.run(query)
                except Exception as err:
                    print("Virhe: {0}".format(err), file=stderr)
            
        return


    def print_data(self):
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
        
    
    @staticmethod       
    def get_total():
        """ Tulostaa perheiden määrän tietokannassa """
        
        global session
                
        query = """
            MATCH (f:Family) RETURN COUNT(f)
            """
        results =  session.run(query)
        
        for result in results:
            return str(result[0])


class Name:
    """ Nimi
    
        Properties:
                type            str nimen tyyppi
                alt             str muun nimen numero
                first           str etunimi
                surname         str sukunimi
                suffix          str patronyymi
    """
    
    def __init__(self):
        """ Luo uuden name-instanssin """
        self.type = ''
        self.alt = ''
        self.first = ''
        self.surname = ''
        self.suffix = ''
        
        
    @staticmethod
    def get_people_with_surname(surname):
        """ Etsi kaikki henkilöt, joiden syntymä nimi on annettu"""
        
        global session
        
        query = """
            MATCH (p:Person)-[r:NAME]->(n:Name) WHERE n.surname='{}' RETURN p.gramps_handle AS handle
            """.format(surname)
        return session.run(query)
        
    
    @staticmethod
    def get_surnames():
        """ Listaa kaikki sukunimet tietokannassa """
        
        global session
        
        query = """
            MATCH (n:Name) RETURN distinct n.surname AS surname ORDER BY n.surname
            """
        return session.run(query)
    
    
class Note:
    """ Huomautus
            
        Properties:
                handle          
                id              esim. "N0001"
                type            str huomautuksen tyyppi
                text            str huomautuksen sisältö
     """

    def __init__(self):
        """ Luo uuden note-instanssin """
        self.handle = ''
        self.id = ''
        self.type = ''


    def save(self):
        """ Tallettaa sen kantaan """

        global session

        try:
            query = """
                CREATE (n:Note) 
                SET n.gramps_handle='{}', n.id='{}', n.type='{}', n.text='{}'
                """.format(self.handle, self.id, self.type, self.text)
                
            return session.run(query)
        except Exception as err:
            print("Virhe: {0}".format(err), file=stderr)


    def print_data(self):
        """ Tulostaa tiedot """
        print ("*****Note*****")
        print ("Handle: " + self.handle)
        print ("Id: " + self.id)
        print ("Type: " + self.type)
        print ("Text: " + self.text)
        return True
        
        
    @staticmethod
    def get_total():
        """ Tulostaa huomautusten määrän tietokannassa """
        
        global session
                
        query = """
            MATCH (n:Note) RETURN COUNT(n)
            """
            
        results =  session.run(query)
        
        for result in results:
            return str(result[0])


class Person:
    """ Henkilö
            
        Properties:
                handle          
                id                 esim. "I0001"
                gender             str sukupuoli
                name:
                   alt             str muun nimen nro
                   type            str nimen tyyppi
                   first           str etunimi
                   surname         str sukunimi
                   suffix          str patronyymi
                eventref_hlink     str tapahtuman osoite
                parentin_hlink     str vanhempien osoite
                citationref_hlink  str viittauksen osoite
     """

    def __init__(self):
        """ Luo uuden person-instanssin """
        self.handle = ''
        self.id = ''
        self.name = []
        self.eventref_role = []
        self.eventref_hlink = []
        self.parentin_hlink = []
        self.citationref_hlink = []


    def save(self):
        """ Tallettaa sen kantaan """

        global session
        
        if len(self.name) > 0:
            try:
                query = """
                    CREATE (p:Person) 
                    SET p.gramps_handle='{}', p.id='{}', p.gender='{}'
                    """.format(self.handle, self.id, self.gender)
                    
                session.run(query)
            except Exception as err:
                print("Virhe: {0}".format(err), file=stderr)

            try:
                names = self.name
                for name in names:
                    p_alt = name.alt
                    p_type = name.type
                    p_first = name.first
                    p_surname = name.surname
                    p_suffix = name.suffix
                    
                    query = """
                        CREATE (m:Name) 
                        SET m.alt='{}', m.type='{}', m.first='{}', m.surname='{}', m.suffix='{}'
                        WITH m
                        MATCH (n:Person) WHERE n.gramps_handle='{}'
                        MERGE (n)-[r:NAME]->(m)
                    """.format(p_alt, p_type, p_first, p_surname, p_suffix, self.handle)
                
                    session.run(query)
            except Exception as err:
                print("Virhe: {0}".format(err), file=stderr)

        # Make possible relations from the Person node
        if len(self.eventref_hlink) > 0:
            for i in range(len(self.eventref_hlink)):
                try:
                    query = """
                        MATCH (n:Person) WHERE n.gramps_handle='{}'
                        MATCH (m:Event) WHERE m.gramps_handle='{}'
                        MERGE (n)-[r:EVENT]->(m)
                         """.format(self.handle, self.eventref_hlink[i])
                                 
                    session.run(query)
                except Exception as err:
                    print("Virhe: {0}".format(err), file=stderr)

                try:
                    query = """
                        MATCH (n:Person)-[r:EVENT]->(m:Event)
                        WHERE n.gramps_handle='{}' AND m.gramps_handle='{}'
                        SET r.role ='{}'
                         """.format(self.handle, self.eventref_hlink[i], self.eventref_role[i])
                                 
                    session.run(query)
                except Exception as err:
                    print("Virhe: {0}".format(err), file=stderr)
   
        if len(self.parentin_hlink) > 0:
            try:
                query = """
                    MATCH (n:Person) WHERE n.gramps_handle='{}'
                    MATCH (m:Family) WHERE m.gramps_handle='{}'
                    MERGE (n)-[r:FAMILY]->(m)
                     """.format(self.handle, self.parentin_hlink[0])
                                 
                session.run(query)
            except Exception as err:
                print("Virhe: {0}".format(err), file=stderr)
   
        if len(self.citationref_hlink) > 0:
            try:
                query = """
                    MATCH (n:Person) WHERE n.gramps_handle='{}'
                    MATCH (m:Citation) WHERE m.gramps_handle='{}'
                    MERGE (n)-[r:CITATION]->(m)
                     """.format(self.handle, self.citationref_hlink[0])
                                 
                session.run(query)
            except Exception as err:
                print("Virhe: {0}".format(err), file=stderr)
        return
    
    
    def get_name_data(self):
        """ Luetaan kaikki henkilön tiedot """
        
        global session
                
        query = """
            MATCH (person:Person)-[r:NAME]-(name:Name) WHERE person.gramps_handle='{}' RETURN person, name ORDER BY name.alt
            """.format(self.handle)
        return  session.run(query)


    def print_data(self):
        """ Tulostaa tiedot """
        print ("*****Person*****")
        print ("Handle: " + self.handle)
        print ("Id: " + self.id)
        print ("Gender: " + self.gender)
        if len(self.name) > 0:
            names = self.name
            for pname in names:
                print ("Alt: " + pname.alt)
                print ("Type: " + pname.type)
                print ("First: " + pname.first)
                print ("Surname: " + pname.surname)
                print ("Suffix: " + pname.suffix)
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


    @staticmethod
    def get_total():
        """ Tulostaa henkilöiden määrän tietokannassa """
        
        global session
                
        query = """
            MATCH (p:Person) RETURN COUNT(p)
            """
        results =  session.run(query)
        
        for result in results:
            return str(result[0])


class Place:
    """ Paikka
            
        Properties:
                handle          
                id              esim. "P0001"
                type            str paikan tyyppi
                pname           str paikan nimi
                placeref_hlink  str paikan osoite
     """

    def __init__(self):
        """ Luo uuden place-instanssin """
        self.handle = ''
        self.id = ''
        self.type = ''
        self.pname = []
        self.placeref_hlink = ''


    def save(self):
        """ Tallettaa sen kantaan """

        global session
        
        if len(self.pname) >= 1:
            p_pname = self.pname[0]
            if len(self.pname) > 1:
                print("Warning: More than one pname in a place, handle: " + self.handle)
        else:
            p_pname = ''

        try:
            query = """
                CREATE (p:Place) 
                SET p.gramps_handle='{}', p.id='{}', p.type='{}', p.pname='{}'
                """.format(self.handle, self.id, self.type, p_pname)
                
            session.run(query)
        except Exception as err:
            print("Virhe: {0}".format(err), file=stderr)

        # Make possible relations from the Person node
        if len(self.placeref_hlink) > 0:
            try:
                query = """
                    MATCH (n:Place) WHERE n.gramps_handle='{}'
                    MATCH (m:Place) WHERE m.gramps_handle='{}'
                    MERGE (n)-[r:HIERARCY]->(m)
                     """.format(self.handle, self.placeref_hlink)
                                 
                session.run(query)
            except Exception as err:
                print("Virhe: {0}".format(err), file=stderr)
            
        return


    def print_data(self):
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
        
    
    @staticmethod       
    def get_total():
        """ Tulostaa paikkojen määrän tietokannassa """
        
        global session
                
        query = """
            MATCH (p:Place) RETURN COUNT(p)
            """
        results =  session.run(query)
        
        for result in results:
            return str(result[0])


class Repository:
    """ Arkisto
            
        Properties:
                handle          
                id              esim. "R0001"
                rname           str arkiston nimi
                type            str arkiston tyyppi

     """

    def __init__(self):
        """ Luo uuden repository-instanssin """
        self.handle = ''
        self.id = ''


    def save(self):
        """ Tallettaa sen kantaan """

        global session

        try:
            query = """
                CREATE (r:Repository) 
                SET r.gramps_handle='{}', r.id='{}', r.rname='{}', r.type='{}'
                """.format(self.handle, self.id, self.rname, self.type)
                
            session.run(query)
        except Exception as err:
            print("Virhe: {0}".format(err), file=stderr)
            
        return


    def print_data(self):
        """ Tulostaa tiedot """
        print ("*****Repository*****")
        print ("Handle: " + self.handle)
        print ("Id: " + self.id)
        print ("Rname: " + self.rname)
        print ("Type: " + self.type)
        return True
        
    
    @staticmethod       
    def get_total():
        """ Tulostaa arkistojen määrän tietokannassa """
        
        global session
                
        query = """
            MATCH (r:Repository) RETURN COUNT(r)
            """
        results =  session.run(query)
        
        for result in results:
            return str(result[0])


class Source:
    """ Lähde
            
        Properties:
                handle          
                id              esim. "S0001"
                stitle          str lähteen otsikko
                noteref_hlink   str huomautuksen osoite
                reporef_hlink   str arkiston osoite
     """

    def __init__(self):
        """ Luo uuden source-instanssin """
        self.handle = ''
        self.id = ''
        self.stitle = ''
        self.noteref_hlink = ''
        self.reporef_hlink = ''


    def save(self):
        """ Tallettaa sen kantaan """

        global session

        try:
            query = """
                CREATE (s:Source) 
                SET s.gramps_handle='{}', s.id='{}', s.stitle='{}'
                """.format(self.handle, self.id, self.stitle)
                
            session.run(query)
        except Exception as err:
            print("Virhe: {0}".format(err), file=stderr)
 
        # Make possible relations from the Source node
        if self.noteref_hlink != '':
            try:
                query = """
                    MATCH (n:Source) WHERE n.gramps_handle='{}'
                    MATCH (m:Note) WHERE m.gramps_handle='{}'
                    MERGE (n)-[r:NOTE]->(m)
                     """.format(self.handle, self.noteref_hlink)
                                 
                session.run(query)
            except Exception as err:
                print("Virhe: {0}".format(err), file=stderr)
   
        if self.reporef_hlink != '':
            try:
                query = """
                    MATCH (n:Source) WHERE n.gramps_handle='{}'
                    MATCH (m:Repository) WHERE m.gramps_handle='{}'
                    MERGE (n)-[r:REPOSITORY]->(m)
                     """.format(self.handle, self.reporef_hlink)
                                 
                session.run(query)
            except Exception as err:
                print("Virhe: {0}".format(err), file=stderr)
                
        return


    def print_data(self):
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
        
    
    @staticmethod       
    def get_total():
        """ Tulostaa lähteiden määrän tietokannassa """
        
        global session
                
        query = """
            MATCH (s:Source) RETURN COUNT(s)
            """
        results =  session.run(query)
        
        for result in results:
            return str(result[0])
    