'''
Created on 16.1.2017

@author: jm
'''

curpath = []

class GedcomLine(object):
    '''
    Gedcom line container
    - level
    - tag
    - value
    '''

    def __init__(self, line, linenum):
        '''
        Constructor: Parses and stores the next gedcom line
        '''
        global curpath

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

        
    def get_parts(self):
        return (line, self.level, self.path, self.tag, self.value)


    def get_line(self):
        return "{} {} {}".format(self.level, self.tag, self.value)
    


# class GedcomLine(object):
#     ''' Gedcom line container '''
#     def __init__(self, path, level, tag, value):
#         self.path = path
#         self.level = level
#         self.tag = tag
#         self.value = value
    


