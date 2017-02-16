'''
Generic GEDCOM transformer
Kari Kujansuu, 2016.

'''
import sys
import os
import getpass
import time
import tempfile

class Output:
    def __init__(self, args):
        self.args = args
        if 'nolog' in self.args and args.nolog: 
            self.log = False
        else:
            self.log = True
        if 'display_changes' in self.args: 
            self.display_changes = args.display_changes
        else:
            self.display_changes = False
        if 'encoding' in self.args:
            self.encoding = self.args.encoding
        else:
            self.encoding = 'UTF-8'
        if 'input_gedcom' in self.args:
            self.in_name = self.args.input_gedcom
        else:
            self.in_name = None
        if 'output_gedcom' in self.args:
            self.out_name = self.args.output_gedcom
        else:
            self.out_name = None
        self.new_name = None

    def __enter__(self):
        if not self.out_name:
            # create tempfile in the same directory so you can rename it later
            tempfile.tempdir = os.path.dirname(self.in_name) 
            self.temp_name = tempfile.mktemp()
            self.new_name = self.generate_name(self.in_name)
            self.out_name = self.temp_name
        self.f = open(self.out_name, "w", encoding=self.encoding)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.f.close()
        if 'dryrun' in self.args and self.args.dryrun:
            return
        self.save()

    def emit(self, line):
        ''' Process an input line '''
        if self.display_changes and line.strip() != self.original_line:
            print('{:>36} –> {}'.format(self.original_line, line))
            self.original_line = ""
        self.f.write(line+"\n")

        if self.log:
            self.log = False
            args = sys.argv[1:]
            try:
                v = " v." + _VERSION
            except NameError:
                v = ""
            self.emit("1 NOTE _TRANSFORM{} {}".format(v, sys.argv[0]))
            self.emit("2 CONT _COMMAND {} {}".\
                      format(os.path.basename(sys.argv[0]), " ".join(args)))
            user = getpass.getuser()
            if not user:
                user = "Unnamed"
            datestring = time.strftime("%d %b %Y %H:%M:%S", 
                                       time.localtime(time.time()))
            self.emit("2 CONT _DATE {} {}".format(user, datestring))
            if self.new_name:
                self.emit("2 CONT _SAVEDFILE " + self.new_name)

    def save(self):
        if self.out_name:
            print("Output saved as '{}'".format(self.out_name))
        else:
            if self.in_name:
                if self.out_name == None:
                    # Only input given
                    os.rename(self.in_name, self.new_name)
                    os.rename(self.temp_name, self.in_name)
                    print("Input file renamed to '{}'".format(self.new_name))
                    print("New version saved as '{}'".format(self.in_name))

    def generate_name(self,name):
        i = 0
        while True:
            newname = "{}.{}".format(name,i)
            if not os.path.exists(newname): 
                return newname
            i += 1
