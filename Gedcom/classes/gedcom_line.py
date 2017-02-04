'''
Created on 16.1.2017

@author: jm
'''

from sys import stderr

class GedcomLine(object):
    '''
    Gedcom line container, which can also carry the lower level gedcom lines.
    
    Example
    - level     2
    - tag       'GIVN'
    - value     'Johan'
    - members[] {path:gedline, ...}
    
    TODO: Tarkasta rivijoukon muodostus
    '''
    # Current path elemements
    # See https://docs.python.org/3/faq/programming.html#how-do-i-create-static-class-data-and-static-class-methods
    path_elem = []

    def __init__(self, line, linenum=0):
        '''
        Constructor: Parses and stores the next gedcom line
        '''
        self.members = {}
        self.line = line
        self.path = ""

        tkns = line.split(None,2)
        self.level = int(tkns[0])
        self.tag = tkns[1]
        self.set_path(self.level, self.tag)
        if len(tkns) > 2:
            self.value = tkns[2]
        else:
            self.value = ""


    def __str__(self):
        ''' Get the original line '''
        try:
            ret = "{} {} {}".format(self.level, self.tag, self.value).strip()
        except:
            ret = "* Not complete *"
        return ret
    

    def add_member(self, gedline):
        ''' Store a next level gedcom line
            Line "2 GIVN Johan" is stored the path as key: {'@I0001@.NAME.GIVN':GedcomLine()}
        '''
        if not type(gedline) is GedcomLine:
            raise RuntimeError("GedcomLine argument expected")
        self.members.append({gedline.path:gedline})


    def get_member(self):
        ''' Iterator for members of this '''
        for gedline in self.members:
            yield(gedline)


    def find_member(self, path):
        #TODO: Onko tarpeeton?
        pass


    def set_path(self, level, tag):
        ''' Update self.path with given tag and level '''
        if level > len(GedcomLine.path_elem):
            raise RuntimeError("{} Invalid level {}: {}".format(self.path, level, self.line))
        if level == len(GedcomLine.path_elem):
            GedcomLine.path_elem.append(tag)
        else:
            GedcomLine.path_elem[level] = tag
            GedcomLine.path_elem = GedcomLine.path_elem[:self.level+1]
        self.path = ".".join(GedcomLine.path_elem)
        return self.path

    
    def get_year(self):
        '''If value has a four digit last part, the numeric value of it is returned
        '''
        p = self.value.split()
        try:
            if len(p) > 0 and len(p[-1]) == 4:
                return int(p[-1])
        except:
            return None


    def emit(self, f):
        # Print out current line to file f
        f.emit(str(self))
