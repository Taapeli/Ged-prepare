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
        self.log = True
        if 'nolog' in self.args and args.nolog: 
            self.log = False
        self.newname = None

    def __enter__(self):
        if 'input_gedcom' in self.args and self.args.input_gedcom:
            self.input_gedcom = self.args.input_gedcom
        if 'output_gedcom' in self.args and self.args.output_gedcom:
            self.output_filename = self.args.output_gedcom
        else:
            # create tempfile in the same directory so you can rename it later
            tempfile.tempdir = os.path.dirname(self.input_gedcom) 
            self.tempname = tempfile.mktemp()
            self.newname = self.generate_name(self.input_gedcom)
            self.output_filename = self.tempname
        if 'encoding' in self.args:
            enc = self.args.encoding
        else:
            enc = 'UTF-8'
        self.f = open(self.output_filename, "w", encoding=enc)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.f.close()
        if 'dryrun' in self.args and self.args.dryrun:
            return
        self.save()

    def emit(self, s):
        if 'display_changes' in self.args and self.display_changes:
            if s.strip() != self.original_line:
                print(self.original_line,"->",s)
                self.original_line = ""
        self.f.write(s+"\n")
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
            if self.newname:
                self.emit("2 CONT _SAVEDFILE " + self.newname)

    def save(self):
        if 'output_gedcom' in self.args:
            out_name = self.args.output_gedcom
            print("Output saved as '{}'".format(out_name))
        else: # No out_name
            if 'input_gedcom' in self.args:
                in_name = self.args.input_gedcom
                if not self.args.output_gedcom:
                    # Only input given
                    os.rename(in_name, self.newname)
                    os.rename(self.tempname, in_name)
                    print("Input file renamed to '{}'".format(self.newname))
                    print("New version saved as '{}'".format(in_name))

    def generate_name(self,name):
        i = 0
        while True:
            newname = "{}.{}".format(name,i)
            if not os.path.exists(newname): 
                return newname
            i += 1
