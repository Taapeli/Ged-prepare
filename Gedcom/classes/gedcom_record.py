'''
Created on 16.1.2017

@author: jm
'''

import re
from sys import stderr
from classes.gedcom_line import GedcomLine
from classes.person_name import PersonName

class GedcomRecord(object):
    '''
    Stores a Gedcom logical record, which includes level 0 record (0 INDI) 
    with all it's lines (with level > 0)

    Methods:
    __init__(...)    An object instance is created using the level 0 line
    add(...)         Other, higher level rows are added
    get_lines()      Returns an iterable containing the lines
    
    The fixes are don mostly from '1 NAME givn/surn/nsfx' row.
    If NAME has significant changes, the original value is also written to 'NOTE orig_'
    
    '''
    def __str__(self):
        return "GedcomRecord({})".format(self.id)


    def __init__(self, gedline):
        ''' Creates a new instance of gedcom logical record
            which includes a group of gredcom lines starting with a level0 record.
        '''
        self.rows = []
        # date contains tuples like {'BIRT':1820}
        self.date = []
        # Latest PersonName index in self.rows
        self.currname = -1
        # Store level 0 line
        if not type(gedline) is GedcomLine:
            raise RuntimeError("GedcomLine argument expected")
        self.level = gedline.level
        self.path = gedline.path
        self.value = gedline.value
        self.add_member(gedline)

    
    def add_member(self, gedline):
        ''' Adds a gedcom line to record set.
            "2 NAME" line is added as a PersonName object, others as GedcomLine objects
        '''
        if gedline.level == 1 and gedline.tag == 'NAME':
            self.currname = len(self.rows)
            self.rows.append(PersonName(gedline))
        else:
            self.rows.append(gedline)

 
    def emit(self, f):
        ''' Writes the stored data associated to this person as new gedcom lines to file f
          #TODO Tagien yhdistely ja tietojen muokkaus: 
                patronyymit vuosiluvun mukaan, ristiriitaiset tiedot
        '''
        for obj in self.rows:
            if type(obj) == PersonName:
                for line in obj.get_lines():
                    f.emit(line)
            else:
                # type GedcomLine
                f.emit(str(obj))


    def store_date(self, year, tag):
        if type(year) == int:
            self.date.append({tag:year})
        else:
            print ("{} ERROR: Invalid {} year".format(self.path, tag), file=stderr)


    def get_nameobject(self):
        ''' Returns the latest object of type PersonName '''
        if self.currname >= 0:
            return self.rows[self.currname]