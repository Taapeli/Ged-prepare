#!/usr/bin/python3

from neo4j.v1 import GraphDatabase, basic_auth
#from flask import flash
from datetime import date
import logging
from sys import stderr
import instance.config as dbconf      # Tietokannan tiedot
#from flask.globals import session

def connect_db():
    """ 
        genelogy-paketin tarvitsema tietokantayhteys
        Ks- http://neo4j.com/docs/developer-manual/current/#driver-manual-index
        
    """
    global driver, session

    #logging.debug("-- dbconf = {}".format(dir(dbconf)))
#    if 'session' in globals():
#        print ("connect_db - already done")
    if hasattr(dbconf,'DB_HOST_PORT'):
        print ("connect_db - server {}".format(dbconf.DB_HOST_PORT))
        driver = GraphDatabase.driver(dbconf.DB_HOST_PORT, auth=basic_auth(dbconf.DB_USER, dbconf.DB_AUTH))
        session = driver.session()
        #authenticate(dbconf.DB_HOST_PORT, dbconf.DB_USER, dbconf.DB_AUTH)
        #graph = Graph('http://{0}/db/data/'.format(dbconf.DB_HOST_PORT))
    else:
        print ("connect_db - default local – EI TUETTU?")
        driver = GraphDatabase.driver("bolt://localhost", auth=basic_auth("neo4j", "localTaapeli"))
        session = driver.session()
    return session

#     # Palautetaan tietokannan sijainnin hostname
#     return driver.url


class Citation:
    """ Viittaus
            
        Properties:
                handle          
                change
                id               esim. "C0001"
                confidence       str confidence
                noteref_hlink    str huomautuksen osoite
                sourceref_hlink  str lähteen osoite
     """

    def __init__(self):
        """ Luo uuden citation-instanssin """
        self.handle = ''
        self.change = ''
        self.id = ''
        self.noteref_hlink = ''
        self.sourceref_hlink = ''

    
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


    def print_data(self):
        """ Tulostaa tiedot """
        print ("*****Citation*****")
        print ("Handle: " + self.handle)
        print ("Change: " + self.change)
        print ("Id: " + self.id)
        print ("Confidence: " + self.confidence)
        if self.noteref_hlink != '':
            print ("Noteref_hlink: " + self.noteref_hlink)
        if self.sourceref_hlink != '':
            print ("Sourceref_hlink: " + self.sourceref_hlink)
        return True


    def save(self):
        """ Tallettaa sen kantaan """

        global session

        try:
            # Create a new Citation node
            query = """
                CREATE (n:Citation) 
                SET n.gramps_handle='{}', 
                    n.change='{}', 
                    n.id='{}', 
                    n.confidence='{}'
                """.format(self.handle, self.change, self.id, self.confidence)
                
            session.run(query)
        except Exception as err:
            print("Virhe: {0}".format(err), file=stderr)

        try:
            # Make relation to the Note node
            if self.noteref_hlink != '':
                query = """
                    MATCH (n:Citation) WHERE n.gramps_handle='{}'
                    MATCH (m:Note) WHERE m.gramps_handle='{}'
                    MERGE (n)-[r:NOTE]->(m)
                     """.format(self.handle, self.noteref_hlink)
                                 
                session.run(query)
        except Exception as err:
            print("Virhe: {0}".format(err), file=stderr)

        try:   
            # Make relation to the Source node
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


class Event:
    """ Tapahtuma
            
        Properties:
                handle          
                change
                id                 esim. "E0001"
                type               esim. "Birth"
                description        esim. ammatin kuvaus
                date               str aika
                place_hlink        str paikan osoite
                attr_type          str lisätiedon tyyppi
                attr_value         str lisätiedon arvo
                citationref_hlink  str viittauksen osoite
     """

    def __init__(self):
        """ Luo uuden event-instanssin """
        self.handle = ''
        self.change = ''
        self.id = ''
        self.description = ''
        self.date = ''
        self.place_hlink = ''
        self.attr_type = ''
        self.attr_value = ''
        self.citationref_hlink = ''
    
    
    def get_citation_handle(self):
        """ Luetaan tapahtuman viittauksen handle """
        
        global session
                
        query = """
            MATCH (event:Event)-[r:CITATION]->(c:Citation) 
                WHERE event.gramps_handle='{}'
                RETURN c.gramps_handle AS citationref_hlink
            """.format(self.handle)
        return  session.run(query)


    def get_event_data(self):
        """ Luetaan tapahtuman tiedot """
        
        global session
                
        query = """
            MATCH (event:Event)
                WHERE event.gramps_handle='{}'
                RETURN event
            """.format(self.handle)
        event_result = session.run(query)

        for event_record in event_result:
            self.id = event_record["event"]["id"]
            self.change = event_record["event"]["change"]
            self.type = event_record["event"]["type"]
            self.date = event_record["event"]["date"]
    
            event_place_result = self.get_place_handle()
            for event_place_record in event_place_result:
                self.place_hlink = event_place_record["handle"]
    
            event_citation_result = self.get_citation_handle()
            for event_citation_record in event_citation_result:
                self.citationref_hlink = event_citation_record["citationref_hlink"]
                
        return True
    
    
    def get_place_handle(self):
        """ Luetaan tapahtuman paikan handle """
        
        global session
                
        query = """
            MATCH (event:Event)-[r:PLACE]->(place:Place) 
                WHERE event.gramps_handle='{}'
                RETURN place.gramps_handle AS handle
            """.format(self.handle)
        return  session.run(query)
        
    
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


    def print_data(self):
        """ Tulostaa tiedot """
        print ("*****Event*****")
        print ("Handle: " + self.handle)
        print ("Change: " + self.change)
        print ("Id: " + self.id)
        print ("Type: " + self.type)
        print ("Description: " + self.description)
        print ("Dateval: " + self.date)
        print ("Place_hlink: " + self.place_hlink)
        print ("Attr_type: " + self.attr_type)
        print ("Attr_value: " + self.attr_value)
        print ("Citationref_hlink: " + self.citationref_hlink)
        return True


    def print_compared_data(self, comp_event, pname1, pname2, print_out=True):
        points = 0
        """ Tulostaa pää- ja vertailtavan tapahtuman tiedot """
        print ("*****Events*****")
        if print_out:
            print ("Handle: " + self.handle + " # " + comp_event.handle)
            print ("Change: " + self.change + " # " + comp_event.change)
            print ("Id: " + self.id + " # " + comp_event.id)
            print ("Type: " + self.type + " # " + comp_event.type)
            print ("Description: " + self.description + " # " + comp_event.description)
            print ("Dateval: " + self.date + " # " + comp_event.date)
            print ("Place: " + pname1 + " # " + pname2)
        # Give points if dates match
        if self.date == comp_event.date:
            points += 1
        return points


    def save(self, userid):
        """ Tallettaa sen kantaan """

        global session
        
        today = date.today()

        try:
            query = """
                CREATE (e:Event) 
                SET e.gramps_handle='{}', 
                    e.change='{}', 
                    e.id='{}', 
                    e.type='{}', 
                    e.description='{}',
                    e.date='{}',
                    e.attr_type='{}',
                    e.attr_value='{}'
                """.format(self.handle, self.change, self.id, self.type, 
                           self.description, self.date, self.attr_type, 
                           self.attr_value)
                
            session.run(query)
        except Exception as err:
            print("Virhe: {0}".format(err), file=stderr)

        try:
            query = """
                MATCH (u:User) WHERE u.userid='{}'  
                MATCH (n:Event) WHERE n.gramps_handle='{}'
                MERGE (u)-[r:REVISION]->(n)
                SET r.date='{}'
                """.format(userid, self.handle, today)
                
            session.run(query)
        except Exception as err:
            print("Virhe: {0}".format(err), file=stderr)

        try:
            # Make relation to the Place node
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
            # Make relation to the Citation node
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
   

class Family:
    """ Perhe
            
        Properties:
                handle          
                change
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
        self.change = ''
        self.id = ''
        self.eventref_hlink = []
        self.eventref_role = []
        self.childref_hlink = []
    
    
    def get_children(self):
        """ Luetaan perheen lasten tiedot """
        
        global session
                
        query = """
            MATCH (family:Family)-[r:CHILD]->(p:Person)
                WHERE family.gramps_handle='{}'
                RETURN p.gramps_handle AS children
            """.format(self.handle)
        return  session.run(query)
    
    
    def get_event_data(self):
        """ Luetaan perheen tapahtumien tiedot """
        
        global session
                
        query = """
            MATCH (family:Family)-[r:EVENT]->(event:Event)
                WHERE family.gramps_handle='{}'
                RETURN r.role AS eventref_role, event.gramps_handle AS eventref_hlink
            """.format(self.handle)
        return  session.run(query)
    
    
    def get_family_data(self):
        """ Luetaan perheen tiedot """
        
        global session
                
        query = """
            MATCH (family:Family)
                WHERE family.gramps_handle='{}'
                RETURN family
            """.format(self.handle)
        family_result = session.run(query)
        
        for family_record in family_result:
            self.change = family_record["family"]['change']
            self.id = family_record["family"]['id']
            self.rel_type = family_record["family"]['rel_type']
            
        father_result = self.get_father()
        for father_record in father_result:            
            self.father = father_record["father"]

        mother_result = self.get_mother()
        for mother_record in mother_result:            
            self.mother = mother_record["mother"]

        event_result = self.get_event_data()
        for event_record in event_result:            
            self.eventref_hlink.append(event_record["eventref_hlink"])
            self.eventref_role.append(event_record["eventref_role"])

        children_result = self.get_children()
        for children_record in children_result:            
            self.childref_hlink.append(children_record["children"])
            
        return True
    
    
    def get_father(self):
        """ Luetaan perheen isän tiedot """
        
        global session
                
        query = """
            MATCH (family:Family)-[r:FATHER]->(p:Person)
                WHERE family.gramps_handle='{}'
                RETURN p.gramps_handle AS father
            """.format(self.handle)
        return  session.run(query)
    
    
    def get_mother(self):
        """ Luetaan perheen äidin tiedot """
        
        global session
                
        query = """
            MATCH (family:Family)-[r:MOTHER]->(p:Person)
                WHERE family.gramps_handle='{}'
                RETURN p.gramps_handle AS mother
            """.format(self.handle)
        return  session.run(query)
        
    
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


    def print_data(self):
        """ Tulostaa tiedot """
        print ("*****Family*****")
        print ("Handle: " + self.handle)
        print ("Change: " + self.change)
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


    def save(self):
        """ Tallettaa sen kantaan """

        global session

        try:
            query = """
                CREATE (n:Family) 
                SET n.gramps_handle='{}', 
                    n.change='{}', 
                    n.id='{}', 
                    n.rel_type='{}'
                """.format(self.handle, self.change, self.id, self.rel_type)
                
            session.run(query)
        except Exception as err:
            print("Virhe: {0}".format(err), file=stderr)

        try:
            # Make relation to the Person node
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
            # Make relation to the Person node
            if self.mother != '':
                query = """
                    MATCH (n:Family) WHERE n.gramps_handle='{}'
                    MATCH (m:Person) WHERE m.gramps_handle='{}'
                    MERGE (n)-[r:MOTHER]->(m)
                     """.format(self.handle, self.mother)
                                 
                session.run(query)
        except Exception as err:
            print("Virhe: {0}".format(err), file=stderr)

        # Make relation(s) to the Event node
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
  
        # Make relation(s) to the Person node
        if len(self.childref_hlink) > 0:
            for i in range(len(self.childref_hlink)):
                try:
                    query = """
                        MATCH (n:Family) WHERE n.gramps_handle='{}'
                        MATCH (m:Person) WHERE m.gramps_handle='{}'
                        MERGE (n)-[r:CHILD]->(m)
                        MERGE (n)<-[s:FAMILY]-(m)
                         """.format(self.handle, self.childref_hlink[i])
                                 
                    session.run(query)
                except Exception as err:
                    print("Virhe: {0}".format(err), file=stderr)
            
        return


class Name:
    """ Nimi
    
        Properties:
                type            str nimen tyyppi
                alt             str muun nimen numero
                first           str etunimi
                refname         str reference name
                surname         str sukunimi
                suffix          str patronyymi
    """
    
    def __init__(self):
        """ Luo uuden name-instanssin """
        self.type = ''
        self.alt = ''
        self.first = ''
        self.refname = ''
        self.surname = ''
        self.suffix = ''
        
        
    @staticmethod
    def get_people_with_refname(refname):
        """ Etsi kaikki henkilöt, joiden referenssinimi on annettu"""
        
        global session
        
        query = """
            MATCH (p:Person)-[r:NAME]->(n:Name) WHERE n.refname STARTS WITH '{}'
                RETURN p.gramps_handle AS handle
            """.format(refname)
        return session.run(query)

        
    @staticmethod
    def get_people_with_refname_and_user_given(userid, refname):
        """ Etsi kaikki käyttäjän henkilöt, joiden referenssinimi on annettu"""
        
        global session
        
        query = """
            MATCH (u:User)-[r:REVISION]->(p:Person)-[s:NAME]->(n:Name) 
                WHERE u.userid='{}' AND n.refname STARTS WITH '{}'
                RETURN p.gramps_handle AS handle
            """.format(userid, refname)
        return session.run(query)

        
    @staticmethod
    def get_ids_of_people_with_refname_and_user_given(userid, refname):
        """ Etsi kaikki käyttäjän henkilöt, joiden referenssinimi on annettu"""
        
        global session
        
        query = """
            MATCH (u:User)-[r:REVISION]->(p:Person)-[s:NAME]->(n:Name) 
                WHERE u.userid='{}' AND n.refname STARTS WITH '{}'
                RETURN ID(p) AS id
            """.format(userid, refname)
        return session.run(query)
        
    @staticmethod
    def get_people_with_surname(surname):
        """ Etsi kaikki henkilöt, joiden sukunimi on annettu"""
        
        global session
        
        query = """
            MATCH (p:Person)-[r:NAME]->(n:Name) WHERE n.surname='{}'
                RETURN p.gramps_handle AS handle
            """.format(surname)
        return session.run(query)
        
    
    @staticmethod
    def get_all_first_names():
        """ Listaa kaikki etunimet tietokannassa """
        
        global session
        
        query = """
            MATCH (n:Name) RETURN distinct n.first AS first
                ORDER BY n.first
            """
        return session.run(query)
        
    
    @staticmethod
    def get_surnames():
        """ Listaa kaikki sukunimet tietokannassa """
        
        global session
        
        query = """
            MATCH (n:Name) RETURN distinct n.surname AS surname
                ORDER BY n.surname
            """
        return session.run(query)
    
    def set_refname(self):
        """Asetetaan etunimen referenssinimi """
        
        global session
        
        query = """
            MATCH (n:Name) WHERE n.first='{}' 
            SET n.refname='{}'
            """.format(self.first, self.refname)
        return session.run(query)
        
    
    
class Note:
    """ Huomautus
            
        Properties:
                handle          
                change
                id              esim. "N0001"
                type            str huomautuksen tyyppi
                text            str huomautuksen sisältö
     """

    def __init__(self):
        """ Luo uuden note-instanssin """
        self.handle = ''
        self.change = ''
        self.id = ''
        self.type = ''
        
        
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


    def print_data(self):
        """ Tulostaa tiedot """
        print ("*****Note*****")
        print ("Handle: " + self.handle)
        print ("Change: " + self.change)
        print ("Id: " + self.id)
        print ("Type: " + self.type)
        print ("Text: " + self.text)
        return True


    def save(self):
        """ Tallettaa sen kantaan """

        global session

        try:
            query = """
                CREATE (n:Note) 
                SET n.gramps_handle='{}', 
                    n.change='{}', 
                    n.id='{}', 
                    n.type='{}', 
                    n.text='{}'
                """.format(self.handle, self.change, self.id, self.type, self.text)
                
            return session.run(query)
        except Exception as err:
            print("Virhe {}: {}".format(err.__class__.__name__, str(err), file=stderr))
            raise SystemExit("Stopped due to errors")    # Stop processing


class Person:
    """ Henkilö
            
        Properties:
                handle          
                change
                id                 esim. "I0001"
                gender             str sukupuoli
                name:
                   alt             str muun nimen nro
                   type            str nimen tyyppi
                   first           str etunimi
                   refname         str referenssinimi
                   surname         str sukunimi
                   suffix          str patronyymi
                eventref_hlink     str tapahtuman osoite
                eventref_role      str tapahtuman rooli
                parentin_hlink     str vanhempien osoite
                citationref_hlink  str viittauksen osoite
     """

    def __init__(self):
        """ Luo uuden person-instanssin """
        self.handle = ''
        self.change = ''
        self.id = ''
        self.name = []
        self.eventref_hlink = []
        self.eventref_role = []
        self.parentin_hlink = []
        self.citationref_hlink = []
    
    
    def get_citation_handle(self):
        """ Luetaan henkilön viittauksen handle """
        
        global session
                
        query = """
            MATCH (person:Person)-[r:CITATION]->(c:Citation) 
                WHERE person.gramps_handle='{}'
                RETURN c.gramps_handle AS citationref_hlink
            """.format(self.handle)
        return  session.run(query)
    
    
    def get_event_data(self):
        """ Luetaan henkilön tapahtumien handlet """
        
        global session
                
        query = """
            MATCH (person:Person)-[r:EVENT]->(event:Event) 
                WHERE person.gramps_handle='{}'
                RETURN r.role AS eventref_role, event.gramps_handle AS eventref_hlink
            """.format(self.handle)
        return  session.run(query)
    
    
    def get_her_families(self):
        """ Luetaan naisen perheiden handlet """
        
        global session
                
        query = """
            MATCH (person:Person)<-[r:MOTHER]-(family:Family) 
                WHERE person.gramps_handle='{}'
                RETURN family.gramps_handle AS handle
            """.format(self.handle)
        return  session.run(query)
    
    
    def get_his_families(self):
        """ Luetaan miehen perheiden handlet """
        
        global session
                
        query = """
            MATCH (person:Person)<-[r:FATHER]-(family:Family) 
                WHERE person.gramps_handle='{}'
                RETURN family.gramps_handle AS handle
            """.format(self.handle)
        return  session.run(query)

    
    def get_hlinks(self):
        """ Luetaan henkilön linkit """
            
        event_result = self.get_event_data()
        for event_record in event_result:            
            self.eventref_hlink.append(event_record["eventref_hlink"])
            self.eventref_role.append(event_record["eventref_role"])

        family_result = self.get_parentin_handle()
        for family_record in family_result:            
            self.parentin_hlink.append(family_record["parentin_hlink"])
            
        citation_result = self.get_citation_handle()
        for citation_record in citation_result:            
            self.citationref_hlink.append(citation_record["citationref_hlink"])
            
        return True
    
    
    def get_parentin_handle(self):
        """ Luetaan henkilön perheen handle """
        
        global session
                
        query = """
            MATCH (person:Person)-[r:FAMILY]->(family:Family) 
                WHERE person.gramps_handle='{}'
                RETURN family.gramps_handle AS parentin_hlink
            """.format(self.handle)
        return  session.run(query)
    
    
    def get_person_and_name_data(self):
        """ Luetaan kaikki henkilön tiedot """
        
        global session
                
        query = """
            MATCH (person:Person)-[r:NAME]-(name:Name) 
                WHERE person.gramps_handle='{}'
                RETURN person, name
                ORDER BY name.alt
            """.format(self.handle)
        person_result = session.run(query)
        
        for person_record in person_result:
            self.change = person_record["person"]['change']
            self.id = person_record["person"]['id']
            self.gender = person_record["person"]['gender']
            
            if len(person_record["name"]) > 0:
                pname = Name()
                pname.alt = person_record["name"]['alt']
                pname.type = person_record["name"]['type']
                pname.first = person_record["name"]['first']
                pname.refname = person_record["name"]['refname']
                pname.surname = person_record["name"]['surname']
                pname.suffix = person_record["name"]['suffix']
                self.name.append(pname)
    
    
    def get_person_and_name_data_by_id(self):
        """ Luetaan kaikki henkilön tiedot """
        
        global session
                
        query = """
            MATCH (person:Person)-[r:NAME]-(name:Name) 
                WHERE ID(person)={}
                RETURN person, name
                ORDER BY name.alt
            """.format(self.id)
        person_result = session.run(query)
        
        for person_record in person_result:
            self.change = person_record["person"]['change']
            self.id = person_record["person"]['id']
            self.gender = person_record["person"]['gender']
            
            if len(person_record["name"]) > 0:
                pname = Name()
                pname.alt = person_record["name"]['alt']
                pname.type = person_record["name"]['type']
                pname.first = person_record["name"]['first']
                pname.refname = person_record["name"]['refname']
                pname.surname = person_record["name"]['surname']
                pname.suffix = person_record["name"]['suffix']
                self.name.append(pname)
                
                
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


    def print_data(self):
        """ Tulostaa tiedot """
        print ("*****Person*****")
        print ("Handle: " + self.handle)
        print ("Change: " + self.change)
        print ("Id: " + self.id)
        print ("Gender: " + self.gender)
        if len(self.name) > 0:
            names = self.name
            for pname in names:
                print ("Alt: " + pname.alt)
                print ("Type: " + pname.type)
                print ("First: " + pname.first)
                print ("Refname: " + pname.refname)
                print ("Surname: " + pname.surname)
                print ("Suffix: " + pname.suffix)
        if len(self.eventref_hlink) > 0:
            for i in range(len(self.eventref_hlink)):
                print ("Eventref_hlink: " + self.eventref_hlink[i])
                print ("Eventref_role: " + self.eventref_role[i])
        if len(self.parentin_hlink) > 0:
            for i in range(len(self.parentin_hlink)):
                print ("Parentin_hlink: " + self.parentin_hlink[i])
        if len(self.citationref_hlink) > 0:
            for i in range(len(self.citationref_hlink)):
                print ("Citationref_hlink: " + self.citationref_hlink[i])
        return True


    def print_compared_data(self, comp_person, print_out=True):
        """ Tulostaa kahden henkilön tiedot vieretysten """
        points = 0
        print ("*****Person*****")
        if (print_out):
            print ("Handle: " + self.handle + " # " + comp_person.handle)
            print ("Change: " + self.change + " # " + comp_person.change)
            print ("Id: " + self.id + " # " + comp_person.id)
            print ("Gender: " + self.gender + " # " + comp_person.gender)
        if len(self.name) > 0:
            alt1 = []
            type1 = []
            first1 = []
            refname1 = []
            surname1 = []
            suffix1 = [] 
            alt2 = []
            type2 = []
            first2 = []
            refname2 = [] 
            surname2 = []
            suffix2 = []
            
            names = self.name
            for pname in names:
                alt1.append(pname.alt)
                type1.append(pname.type)
                first1.append(pname.first)
                refname1.append(pname.refname)
                surname1.append(pname.surname)
                suffix1.append(pname.suffix)
            
            names2 = comp_person.name
            for pname in names2:
                alt2.append(pname.alt)
                type2.append(pname.type)
                first2.append(pname.first)
                refname2.append(pname.refname)
                surname2.append(pname.surname)
                suffix2.append(pname.suffix)
                
            if (len(first2) >= len(first1)):
                for i in range(len(first1)):
                    # Give points if refnames match
                    if refname1[i] != ' ':
                        if refname1[i] == refname2[i]:
                            points += 1
                    if (print_out):
                        print ("Alt: " + alt1[i] + " # " + alt2[i])
                        print ("Type: " + type1[i] + " # " + type2[i])
                        print ("First: " + first1[i] + " # " + first2[i])
                        print ("Refname: " + refname1[i] + " # " + refname2[i])
                        print ("Surname: " + surname1[i] + " # " + surname2[i])
                        print ("Suffix: " + suffix1[i] + " # " + suffix2[i])
            else:
                for i in range(len(first2)):
                    # Give points if refnames match
                    if refname1[i] == refname2[i]:
                        points += 1
                    if (print_out):
                        print ("Alt: " + alt1[i] + " # " + alt2[i])
                        print ("Type: " + type1[i] + " # " + type2[i])
                        print ("First: " + first1[i] + " # " + first2[i])
                        print ("Refname: " + refname1[i] + " # " + refname2[i])
                        print ("Surname: " + surname1[i] + " # " + surname2[i])
                        print ("Suffix: " + suffix1[i] + " # " + suffix2[i])

        return points


    def save(self, userid):
        """ Tallettaa sen kantaan """

        global session
        
        today = date.today()
        
        try:
            query = """
                CREATE (p:Person) 
                SET p.gramps_handle='{}', 
                    p.change='{}', 
                    p.id='{}', 
                    p.gender='{}'
                """.format(self.handle, self.change, self.id, self.gender)
                
            session.run(query)
        except Exception as err:
            print("Virhe: {0}".format(err), file=stderr)

        try:
            query = """
                MATCH (u:User )WHERE u.userid='{}'
                MATCH (n:Person) WHERE n.gramps_handle='{}'
                MERGE (u)-[r:REVISION]->(n)
                SET r.date='{}'
                """.format(userid, self.handle, today)
                
            session.run(query)
        except Exception as err:
            print("Virhe: {0}".format(err), file=stderr)
            
        if len(self.name) > 0:
            try:
                names = self.name
                for name in names:
                    p_alt = name.alt
                    p_type = name.type
                    p_first = name.first
                    p_refname = name.refname
                    p_surname = name.surname
                    p_suffix = name.suffix
                    
                    query = """
                        CREATE (m:Name) 
                        SET m.alt='{}', 
                            m.type='{}', 
                            m.first='{}', 
                            m.refname='{}', 
                            m.surname='{}', 
                            m.suffix='{}'
                        WITH m
                        MATCH (n:Person) WHERE n.gramps_handle='{}'
                        MERGE (n)-[r:NAME]->(m)
                    """.format(p_alt, 
                               p_type, 
                               p_first, 
                               p_refname, 
                               p_surname, 
                               p_suffix, 
                               self.handle)
                
                    session.run(query)
            except Exception as err:
                print("Virhe: {0}".format(err), file=stderr)

        # Make possible relations to the Event node
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
                         """.format(self.handle, 
                                    self.eventref_hlink[i], 
                                    self.eventref_role[i])
                                 
                    session.run(query)
                except Exception as err:
                    print("Virhe: {0}".format(err), file=stderr)
   
        # Make relations to the Family node
        # This is done in Family.save(), because the Family object is not yet created
#        if len(self.parentin_hlink) > 0:
#            for i in range(len(self.parentin_hlink)):
#                try:
#                    query = """
#                        MATCH (n:Person) WHERE n.gramps_handle='{}'
#                        MATCH (m:Family) WHERE m.gramps_handle='{}'
#                        MERGE (n)-[r:FAMILY]->(m)
#                        """.format(self.handle, self.parentin_hlink[i])
#                                 
#                    session.run(query)
#                except Exception as err:
#                    print("Virhe: {0}".format(err), file=stderr)
   
        # Make relations to the Citation node
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


class Place:
    """ Paikka
            
        Properties:
                handle          
                change
                id              esim. "P0001"
                type            str paikan tyyppi
                pname           str paikan nimi
                placeref_hlink  str paikan osoite
     """

    def __init__(self):
        """ Luo uuden place-instanssin """
        self.handle = ''
        self.change = ''
        self.id = ''
        self.type = ''
        self.pname = ''
        self.placeref_hlink = ''
    
    
    def get_place_data(self):
        """ Luetaan kaikki paikan tiedot """
        
        global session
                
        query = """
            MATCH (place:Place)
                WHERE place.gramps_handle='{}'
                RETURN place
            """.format(self.handle)
        place_result = session.run(query)
        
        for place_record in place_result:
            self.change = place_record["place"]["change"]
            self.id = place_record["place"]["id"]
            self.type = place_record["place"]["type"]
            self.pname = place_record["place"]["pname"]
            
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


    def print_data(self):
        """ Tulostaa tiedot """
        print ("*****Placeobj*****")
        print ("Handle: " + self.handle)
        print ("Change: " + self.change)
        print ("Id: " + self.id)
        print ("Type: " + self.type)
        if self.pname != '':
            print ("Pname: " + self.pname)
        if self.placeref_hlink != '':
            print ("Placeref_hlink: " + self.placeref_hlink)
        return True


    def save(self):
        """ Tallettaa sen kantaan """

        global session
        
        if len(self.pname) >= 1:
            p_pname = self.pname
            if len(self.pname) > 1:
                print("Warning: More than one pname in a place, " + 
                      "handle: " + self.handle)
        else:
            p_pname = ''

        try:
            query = """
                CREATE (p:Place) 
                SET p.gramps_handle='{}', 
                    p.change='{}', 
                    p.id='{}', 
                    p.type='{}', 
                    p.pname='{}'
                """.format(self.handle, self.change, self.id, self.type, p_pname)
                
            session.run(query)
        except Exception as err:
            print("Virhe: {0}".format(err), file=stderr)

        # Make hierarchy relations to the Place node
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


class Refname:
    """
        ( Refname {oid, nimi} ) -[reftype]-> (Refname)
                   reftype = (etunimi, sukunimi, patronyymi)
        Properties:                                             input source
            oid     1, 2 ...                                    (created in save())
            name    1st letter capitalized                      (Nimi)
            refname * the std name referenced, if exists        (RefNimi)
            reftype * which kind of reference refname points to ('REFFIRST')
            gender  gender 'F', 'M' or ''                       (Sukupuoli)
            source  points to Source                            (Lähde)
            
        * Note: refnamea ja reftypeä ei talleteta tekstinä, vaan kannassa tehdään
                viittaus tyyppiä reftype ko Refname-olioon
    """
    # TODO: source pitäisi olla viite lähdetietoon, nyt sinne on laitettu lähteen nimi

    label = "Refname"
    REFTYPES = ['REFFIRST', 'REFLAST', 'REFPATRO']

#   Type-property poistettu tarpeettomana. Esim. samasta nimestä "Persson" voisi
#   olla linkki REFLAST nimeen "Pekanpoika" ja REFPATRO nimeen "Pekka".
#   Ei tarvita useita soluja.
#   __REFNAMETYPES = ['undef', 'fname', 'lname', 'patro', 'place', 'occu']

    def __init__(self, nimi):
        """ Luodaan referenssinimi
            Nimi talletetaan alkukirjain isolla, alku- ja loppublankot poistettuna
        """
        if nimi:
            self.name = nimi.strip().title()
        else:
            self.name = None

    def __eq__(self, other):
        "Mahdollistaa vertailun 'refname1 == refname2'"
        if isinstance(other, self.__class__):
            return self.name() == other.name()
        else:
            return False

    def __str__(self):
        s = "(Refname {0}oid={1}, name='{2}'".format('{', self.oid, self.name)
        if 'gender' in dir(self):
            s += ", gender={}".format(self.gender)
        if 'refname' in dir(self):
            s += "{0}) -[{1}]-> (Refname {2}".format('}', self.reftype, '{')
            if 'vid' in dir(self):
                s += "oid={}, ".format(self.vid)
            s += "name='{}'".format(self.refname)
        s += "{})".format('}')
        return s

    def save(self):
        """ Referenssinimen tallennus kantaan. Kysessä on joko 
            - nimi ilman viittausta, olkoon (A:{name=name})
            - nimi ja viittaus, (A:{name=name})-->(B:{name=refname})
            Edellytetään, että tälle oliolle on asetettu:
            - name (Nimi)
            Tunniste luodaan tai käytetään sitä joka löytyi kannasta
            - oid (int)
            Lisäksi tallennetaan valinnaiset tiedot:
            - gender (Sukupuoli='M'/'N'/'')
            - source (Lähde merkkijonona)
            - reference 
              (a:Refname {nimi='Nimi'}) -[r:Reftype]-> (b:Refname {nimi='RefNimi'})
        """
        # TODO: source pitäisi tallettaa Source-objektina
        
        global session
        
        # Pakolliset tiedot
        if self.name == None:
            raise NameError
        
        # Asetetaan A:n attribuutit
        a_attr = "{name:'" + self.name + "'"
        if hasattr(self, 'gender'):
            a_attr += ", gender:'{}'".format(self.gender)
        if hasattr(self, 'source'):
            a_attr += ", source:'{}'".format(self.source)
        a_attr += '}'
#        a_newoid = get_new_oid()

        if hasattr(self, 'refname'):
            # Luodaan viittaus (A:{name=name})-->(B:{name=refname})
            # Jos A tai B puuttuvat kannasta, ne luodaan
            b_attr = "{name:'" + self.refname + "'}"
#            b_newoid = get_new_oid()
            query="""
                MERGE (a:Refname {})
                MERGE (b:Refname {})
                CREATE UNIQUE (a)-[:REFFIRST]->(b)
                RETURN a.id AS aid, a.name AS aname, b.id AS bid, b.name AS bname;""".format(a_attr, b_attr)
                
            try:
                result = session.run(query)
        
                for record in result:
                    a_oid = record["aid"]
                    a_name = record["aname"]
                    b_oid = record["bid"]
                    b_name = record["bname"]
                    
                    logging.debug('Luotiin (a {}:{})'.format(a_oid, a_name))
                    logging.debug('Luotiin (b {}:{})'.format(b_oid, b_name))
                    logging.debug('Luotiin ({}:{})-->({}:{})'.format(a_oid, a_name, b_oid, b_name))
                    
            except Exception as err:
                print("Virhe: {0}".format(err), file=stderr)
                logging.warning('Lisääminen (a)-->(b) ei onnistunut: {}'.format(err))

        else:
            # Luodaan (A:{name=name}) ilman viittausta B:hen
            # Jos A puuttuu kannasta, se luodaan
            query="""
                 MERGE (a:Refname {})
                 RETURN a.id AS aid, a.name AS aname;""".format(a_attr)
            try:
                result = session.run(query)
        
                for record in result:
                    a_oid = record["aid"]
                    a_name = record["aname"]
                    
                    logging.debug('Luotiin{} ({}:{})'.format(a_attr,  a_oid, a_name))
                    
            except Exception as err:
                # Ei ole kovin fataali, ehkä jokin attribuutti hukkuu?
                print("Virhe: {0}".format(err), file=stderr)
                logging.warning('Lisääminen (a) ei onnistunut: {}'.format(err))

    @staticmethod   
    def get_refname(name):
        """ Haetaan nimeä vastaava referenssinimi
        """
        global session
        query="""
            MATCH (a:Refname)-[r:REFFIRST]->(b:Refname) WHERE a.name='{}'
            RETURN a.name AS aname, b.name AS bname LIMIT 1;""".format(name)
            
        try:
            return session.run(query)
    
        except Exception as err:
            print("Virhe: {0}".format(err), file=stderr)
            logging.warning('Kannan lukeminen ei onnistunut: {}'.format(err))
            
            
    @staticmethod   
    def get_name(name):
        """ Haetaan referenssinimi
        """
        global session
        query="""
            MATCH (a:Refname)-[r:REFFIRST]->(b:Refname) WHERE b.name='{}'
            RETURN a.name AS aname, b.name AS bname;""".format(name)
            
        try:
            return session.run(query)
        
        except Exception as err:
            print("Virhe: {0}".format(err), file=stderr)
            logging.warning('Kannan lukeminen ei onnistunut: {}'.format(err))
        
        
    def get_typed_refnames(reftype=""):
        """ Haetaan kannasta kaikki referenssinimet sekä lista nimistä, jotka
            viittaavat ko refnameen. 
            Palautetaan referenssinimen attribuutteja sekä lista nimistä, 
            jotka suoraan tai ketjutetusti viittaavat ko. referenssinimeen
            [Kutsu: datareader.lue_refnames()]
        """
        global session
        query="""
             MATCH (a:Refname)
               OPTIONAL MATCH (m:Refname)-[:«reftype1»*]->(a:Refname)
               OPTIONAL MATCH (a:Refname)-[:«reftype2»]->(n:Refname)
             RETURN a.id, a.name, a.gender, a.source,
               COLLECT ([n.oid, n.name, n.gender]) AS base,
               COLLECT ([m.oid, m.name, m.gender]) AS other
             ORDER BY a.name"""
        return session.run(query)

    def getrefnames():
        """ Haetaan kannasta kaikki Refnamet 
            Palautetaan Refname-olioita, johon on haettu myös mahdollisen
            viitatun referenssinimen nimi ja tyyppi.
            [Kutsu: datareader.lue_refnames()]
        """
        global sessiopn
        query = """
             MATCH (n:Refname)
             OPTIONAL MATCH (n:Refname)-[r]->(m)
             RETURN n,r,m;"""
        return session.run(query)


class Repository:
    """ Arkisto
            
        Properties:
                handle          
                change
                id              esim. "R0001"
                rname           str arkiston nimi
                type            str arkiston tyyppi

     """

    def __init__(self):
        """ Luo uuden repository-instanssin """
        self.handle = ''
        self.change = ''
        self.id = ''
        
    
    @staticmethod       
    def get_repositories():
        """ Luetaan kaikki arkistot """
        
        global session
                
        query = """
            MATCH (repo:Repository) RETURN repo
            """
        return  session.run(query)
    
    
    @staticmethod       
    def get_repository(rname):
        """ Luetaan arkiston handle """
        
        global session
                
        query = """
            MATCH (repo:Repository) WHERE repo.rname='{}'
                RETURN repo
            """.format(rname)
        return  session.run(query)
                
    
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


    def print_data(self):
        """ Tulostaa tiedot """
        print ("*****Repository*****")
        print ("Handle: " + self.handle)
        print ("Change: " + self.change)
        print ("Id: " + self.id)
        print ("Rname: " + self.rname)
        print ("Type: " + self.type)
        return True


    def save(self):
        """ Tallettaa sen kantaan """

        global session

        try:
            query = """
                CREATE (r:Repository) 
                SET r.gramps_handle='{}', 
                    r.change='{}', 
                    r.id='{}', 
                    r.rname='{}', 
                    r.type='{}'
                """.format(self.handle, self.change, self.id, self.rname, self.type)
                
            session.run(query)
        except Exception as err:
            print("Virhe: {0}".format(err), file=stderr)
            
        return


class Source:
    """ Lähde
            
        Properties:
                handle          
                change
                id              esim. "S0001"
                stitle          str lähteen otsikko
                noteref_hlink   str huomautuksen osoite
                reporef_hlink   str arkiston osoite
                reporef_medium  str arkiston laatu, esim. "Book"
     """

    def __init__(self):
        """ Luo uuden source-instanssin """
        self.handle = ''
        self.change = ''
        self.id = ''
        self.stitle = ''
        self.noteref_hlink = ''
        self.reporef_hlink = ''
        self.reporef_medium = ''
        
    
    @staticmethod       
    def get_sources(repository_handle):
        """ Luetaan kaikki arkiston lähteet """
        
        global session
                
        query = """
            MATCH (source:Source)-[r:REPOSITORY]->(repo:Repository) 
                WHERE repo.gramps_handle='{}' 
                RETURN r.medium AS medium, source
            """.format(repository_handle)
        return  session.run(query)
        
    
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


    def print_data(self):
        """ Tulostaa tiedot """
        print ("*****Source*****")
        print ("Handle: " + self.handle)
        print ("Change: " + self.change)
        print ("Id: " + self.id)
        if self.stitle != '':
            print ("Stitle: " + self.stitle)
        if self.noteref_hlink != '':
            print ("Noteref_hlink: " + self.noteref_hlink)
        if self.reporef_hlink != '':
            print ("Reporef_hlink: " + self.reporef_hlink)
        return True
        

    def save(self):
        """ Tallettaa sen kantaan """

        global session

        try:
            query = """
                CREATE (s:Source) 
                SET s.gramps_handle='{}', 
                    s.change='{}', 
                    s.id='{}', 
                    s.stitle='{}'
                """.format(self.handle, self.change, self.id, self.stitle)
                
            session.run(query)
        except Exception as err:
            print("Virhe: {0}".format(err), file=stderr)
 
        # Make relation to the Note node
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
   
        # Make relation to the Repository node
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
                
            # Set the medium data of the Source node
            try:
                query = """
                    MATCH (n:Source)-[r:REPOSITORY]->(m) 
                        WHERE n.gramps_handle='{}'
                    SET r.medium='{}'
                     """.format(self.handle, self.reporef_medium)
                                 
                session.run(query)
            except Exception as err:
                print("Virhe: {0}".format(err), file=stderr)
                
        return
    
    
class User:
    """ Käyttäjä
            
        Properties:
                userid          esim. User123
     """
     
    @staticmethod       
    def create_user(userid):
        """ Käyttäjä tallennetaan kantaan, jos hän ei jo ole siellä"""

        global session
        
        try:
            record = None
            query = """
                MATCH (u:User) WHERE u.userid='{}' RETURN u.userid
                """.format(userid)
                
            result = session.run(query)
            
            for record in result:
                continue
            
            if not record:
                # User doesn't exist in db, the userid should be stored there
                try:
                    query = """
                        CREATE (u:User) 
                        SET u.userid='{}'
                        """.format(userid)
                        
                    session.run(query)
            
                except Exception as err:
                    print("Virhe: {0}".format(err), file=stderr)
            
        except Exception as err:
            print("Virhe: {0}".format(err), file=stderr)
        
        
    def get_ids_and_refnames_of_people_of_user(self):
        """ Etsi kaikki käyttäjän henkilöt"""
        
        global session
        
        query = """
            MATCH (u:User)-[r:REVISION]->(p:Person)-[s:NAME]->(n:Name) WHERE u.userid='{}'
                RETURN ID(p) AS id, n.refname AS refname
            """.format(self.userid)
        return session.run(query)
        
        
    def get_refnames_of_people_of_user(self):
        """ Etsi kaikki käyttäjän henkilöt"""
        
        global session
        
        query = """
            MATCH (u:User)-[r:REVISION]->(p:Person)-[s:NAME]->(n:Name) WHERE u.userid='{}'
                RETURN p.gramps_handle AS handle, n.refname AS refname
            """.format(self.userid)
        return session.run(query)
        
        
    def get_revisions_of_the_user(self):
        """ Etsi kaikki käyttäjän versiot"""
        
        global session
        
        query = """
            MATCH (u:User)-[r:REVISION]->() WHERE u.userid='{}'
                RETURN distinct r.date AS date ORDER BY r.date
            """.format(self.userid)
        return session.run(query)
        
        
    @staticmethod       
    def get_all_userids():
        """ Listaa kaikki käyttäjätunnukset"""
        
        global session
        
        query = """
            MATCH (u:User) RETURN u.userid AS userid ORDER BY u.userid
            """
        return session.run(query)


