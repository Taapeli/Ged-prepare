'''
Generic GEDCOM transformer 
Kari Kujansuu, 2016.

'''
import tempfile
import sys
import os
import getpass
import time

class Output:
    def __init__(self,args):
        self.args = args
        self.log = True
        if args['nolog']: self.log = False
        if args['output_gedcom']: self.output_filename = args['output_gedcom']
        self.encoding = args['encoding']
        self.newname = None

    def __enter__(self):
#        args = self.args
        if 'input_gedcom' in self.args:
            input_gedcom = self.args.input_gedcom
            if self.args.output_gedcom:
                self.output_filename = self.args.output_gedcom
            else:
                tempfile.tempdir = os.path.dirname(input_gedcom) # create tempfile in the same directory so you can rename it later
                self.tempname = tempfile.mktemp()
                self.newname = self.generate_name(input_gedcom)
                self.output_filename = self.tempname
        self.f = open(self.output_filename,"w",encoding=self.encoding)
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.f.close()
        if not self.args['dryrun']:
            self.save()

    def emit(self,s):
        if 'display_changes' in self.args and self.args['display_changes']:
            if s.strip() != self.original_line:
                print(self.original_line,"->",s)
                self.original_line = ""
        self.f.write(s+"\n")
        if self.log:
            self.log = False
            args = sys.argv[1:]
#             self.emit("1 NOTE _TRANSFORM v.{} {}".format(_VERSION, sys.argv[0]))
            self.emit("2 CONT _COMMAND {} {}".format(os.path.basename(sys.argv[0]), " ".join(args)))
            user = getpass.getuser()
            if not user:
                user = "Unnamed"
            datestring = time.strftime("%d %b %Y %H:%M:%S", time.localtime(time.time()))
            self.emit("2 CONT _DATE {} {}".format(user, datestring))
            if self.newname:
                self.emit("2 CONT _SAVEDFILE " + self.newname)

    def save(self):
        if 'output_gedcom' in self.args:
            out_name = self.args['output_gedcom']
            print("Output saved as '{}'".format(out_name))
        else: # No output named
            if 'input_gedcom' in self.args:
                in_name = self.args['input_gedcom']
                if not hasattr(self.args, 'output_gedcom'):
                    # Only input given
                    os.rename(in_name,self.newname)
                    os.rename(self.tempname,in_name)
                    print("Created file {!r}\nPrevious version saved as {!r}".format(in_name, self.newname))


    def generate_name(self,name):
        i = 0
        while True:
            newname = "{}.{}".format(name,i)
            if not os.path.exists(newname): return newname
            i += 1

