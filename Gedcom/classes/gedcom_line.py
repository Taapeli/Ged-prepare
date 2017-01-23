'''
Created on 16.1.2017

@author: jm
'''

curpath = []

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

    def __init__(self, line, linenum):
        '''
        Constructor: Parses and stores the next gedcom line
        '''
        global curpath
#         self.path = path
#         self.level = level
#         self.tag = tag
#         self.value = value
        self.members = {}
        
        tkns = line.split(None,2)
        self.level = int(tkns[0])
        self.tag = tkns[1]
        if self.level > len(curpath):
            raise RuntimeError("Invalid level {}: {}".format(linenum, line))
        if self.level == len(curpath):
            curpath.append(self.tag)
        else:
            curpath[self.level] = self.tag
            curpath = curpath[:self.level+1]
        if len(tkns) > 2:
            self.value = tkns[2]
        else:
            self.value = ""
        self.path = ".".join(curpath)


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
        pass


    def get_parts(self):
        return (line, self.level, self.path, self.tag, self.value)

    def get_line(self):
        return "{} {} {}".format(self.level, self.tag, self.value)
    
    def get_year(self):
        '''If value has a for digit last part, the numeric value of it is returned '''
        p = split(self.value)
        try:
            if len(p) > 0 and len(p[:-1]) == 4:
                return int(p[:-1])
        except:
            return None
    
    def emit(self, f):
        # Print out current line to file f
        f.emit(self.get_line())

