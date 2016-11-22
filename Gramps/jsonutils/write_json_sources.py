'''
Created on 8.11.2016

@author: Timo Nallikari
 
'''

import sys

from Gramps.jsonutils.create_gramps_object import CreateGrampsObject
from sys import argv


def main(argv):
#    def main(argv = ["write_json_sources", "C:/Temp/", "Lahteet.txt", "JsonIn.json", 500000, 500000]):
    if argv is None:
        argv = sys.argv   
        
    if len(argv) != 6:
        print("Wrong number of arguments")
        return 8
    
    fdir = argv[1]                   # Directory for input and output files
    fin  = fdir + argv[2]            # Input file
    fout = fdir + argv[3]            # Output file
    repository_idno = int(argv[4])   # Start value for repository id numbers
    repository_incr = int(argv[5])   # Increment value  for repository id numbers
    source_idno = 0                  # Start value for source id number within repository
    
    print("File directory for program " + argv[0] + " is " + fdir)
    print("  input file  " + fin)
    print("  output file " + fout)
    
    tag  = None
    rtag = None            # Tag used for repositories
    stag = None            # Tag used for sources
    
    repository = None
    source = None
    
    cgo = CreateGrampsObject()
      
    try:
        with open(fout, "w", encoding="UTF-8") as j_out:
            rectype = ""
            arctype = ""
            with open(fin, "r") as t_in:
                for line in t_in:
                    ttext =  line.strip('\n ')
                    print(ttext)
                    rectype = ttext[0]         # Object type = Gramps object id prefix character
                    recobj  = ttext[2]         # Tag: host object type   Repository: repository type
                    idno = ttext[5:11]         # Alternative way to assign Gramps object id's
                    otext = ttext[15:len(ttext)]
#                    print("-" + rectype + "-" + idno + "-" + otext + "-")
                    
                    if rectype == "T":
                        tag = cgo.buildTag(otext)
                        if   recobj == "R": rtag = tag      # The tag for repositories
                        elif recobj == "S": stag = tag      # The tag for sources
                        print(tag.to_struct(), file=j_out)
                                   
                    elif rectype == "R":
                        arctype = int(recobj)
                        repository_idno = repository_idno + repository_incr
                        ridno = rectype + "ref" + str(arctype * 1000 + repository_idno)
                        repository = cgo.buildRepository(ridno, otext, rtag, int(recobj))
                        print(repository.to_struct(), file=j_out)
   
                    elif rectype == "S":
                        source_idno = source_idno + 1
                        sidno = rectype +"ref" + str(arctype) + str(repository_idno * 1000 + source_idno)
#                        sidno = ""
                        source = cgo.buildSource(sidno, otext, stag, repository)
                        print(source.to_struct(), file=j_out)
                    else:
                        print("Something strange happened.")
                print("Input file handled.")
    except  IOError: 
        print(IOError.winerror)
        print("IOError in j_out handling")
        return 8    
    
if __name__ == '__main__':
    sys.exit(main(argv))
