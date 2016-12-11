'''
Created on 22.11.2016

@author: jm
'''

class PersonName(object):
    '''
    Contains Gedcom individual name information from tags:
    - NAME typically 'givn/surn/spfx'
    - GIVN
    - SURN
    - SPFX
    - _CALL
    '''
    NONAME = 'N'   # Marker for missing name part
    rows = []

    def __init__(self):
        pass

    def __str__(self):
        return "PersonName({})".format(self.get_name())

    def appendRow(self, level, tag, value):
        # Store a new row
        self.rows.append("{} {} {}".format(level, tag, value))


    def add(self, path, level, tag, value):
        ''' Processes arguments of a gedcom line.
            Returns True, while the path is one of name definitions
        Arguments example:
            path='@I0001@.NAME'
            tag='NAME'
            value='Antti /Puuhaara/'
        '''
        if tag == 'NAME':
            #  Processes the value of NAME tag and tries to parse it to givn, surn, spfx fields
            self.name = value
            parts = self.name.split('/')
            if len(parts) == 3:     # Contains '/Surname/'
                self.givn, self.surn, self.spfx = parts
                if (self.givn):
                    gnames = self.givn.split()
                    l = len(gnames) - 1
                    if (l > 0) & \
                       ((gnames[-1].endswith('poika') | (gnames[-1].endswith('tytär')))):
                        print('# {}: {} | {!r} | {!r}'.format(path, gnames, self.surn, self.spfx))
                        self.spfx = gnames[-1]
                        self.givn = ' '.join(gnames[0:-1])
                    else:
                        self.givn = self.givn.rstrip()
                else:
                    self.givn = self.NONAME
                self.name = "{}/{}/{}".format(self.givn, self.surn, self.spfx)
                self.appendRow(level, tag, self.name)
            return True
        elif tag == 'GIVN':
            # TODO: Should compare the name parts from NAME tag to this given here!
            self.givn = value
            self.appendRow(level, tag, self.name)
            return True
        elif tag == 'SURN':
            self.surn = value
            self.appendRow(level, tag, self.name)
            return True
        elif tag == 'SPFX':
            self.spfx = value
            self.appendRow(level, tag, self.name)
            return True
        elif tag == '_CALL':    # So called call name
            self.call = value
            self.appendRow(level, tag, self.name)
            return True
        else:
            self.appendRow(level, tag, self.name)
            return False

    def get_name(self):
        try:
            return self.name
        except AttributeError:
            return "<unknown>"

    def get_givn(self):
        return self.givn

    def get_surn(self):
        return self.surn

    def get_spfx(self):
        return self.spfx

    def get_call(self):
        return self.call

    def get_rows(self):
        # Return all stored rows associated to this person name
        return self.rows

if __name__ == "__main__":
    myname = PersonName()
    myname.add('@I0001@.NAME', 'NAME', "Antti /Puuhaara/")
    print ("-->" + myname.get_name())
    myname = PersonName()
    myname.add('@I0002@.NAME', 'NAME', "Hello World")
    print ("-->" + myname.get_name())
    myname = PersonName()
    myname.add('@I0003@.NAME', 'NAME', "Anders (Antti) Juhonpoika /Puuhaara/")
    print ("-->" + myname.get_name())
