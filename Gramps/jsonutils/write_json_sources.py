'''
Created on 8.11.2016

@author: Timo Nallikari
 
'''

import sys
#from gramps.gen.lib import Repository as repository
#from gramps.gen.lib import Source as source, Tag

from Gramps.jsonutils.create_gramps_object import CreateGrampsObject
from sys import argv
import csv

tag     = None
thandle = None
repository = None
rhandle    = None
source  = None
shandle = None

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
    cout = fdir + "result.csv"
    repository_idno = int(argv[4])   # Start value for repository id numbers
    repository_incr = int(argv[5])   # Increment value  for repository id numbers
    source_idno = 0                  # Start value for source id number within repository
    
    print("File directory for program " + argv[0] + " is " + fdir)
    print("  input file  " + fin)
    print("  output file " + fout)
    
    tag  = None
    rtag = None            # Tag used for repositories
    stag = None            # Tag used for sources
        
    cgo = CreateGrampsObject()
      
    try:

        with open(cout, "w", newline = "\n") as csv_out:
            r_writer = csv.writer(csv_out, delimiter=',')
            with open(fout, "w", encoding="UTF-8") as j_out:
                rectype = ""
                arctype = ""
                with open(fin, "r") as t_in:

                    for line in t_in:
                        rhandle = None
                        shandle = None
                        
                        ttext =  line.strip('\n ')
                        print(ttext)
                        rectype = ttext[0]         # Object type = Gramps object id prefix character
                        recobj  = ttext[2]         # Tag: host object type   Repository: repository type
    #                    idno = ttext[5:11]         # Alternative way to assign Gramps object id's
                        otext = ttext[15:len(ttext)]
    #                    print("-" + rectype + "-" + idno + "-" + otext + "-")
                        
                        if rectype == "T":
                            tagr = cgo.buildTag(otext, thandle)
                            if   recobj == "R": rtag = tagr[0]     # The tag for repositories
                            elif recobj == "S": stag = tagr[0]     # The tag for sources
                            print(tagr[0].to_struct(), file=j_out)
                                       
                        elif rectype == "R":
                            arctype = int(recobj)
                            repository_idno = repository_idno + repository_incr
                            ridno = rectype + "ref" + str(arctype) + str(repository_idno)
                            repor = cgo.buildRepository(ridno, otext, rtag, int(recobj), rhandle)
                            print(repor[0].to_struct(), file=j_out)
                            try: 
                                r_writer.writerow([ridno, repor[1], otext])
                            except:    
                                print("Error writing R-csv")
                        elif rectype == "S":
                            source_idno = source_idno + 1
                            sidno = rectype +"ref" + str(arctype) + str(repository_idno * 1000 + source_idno)
                            sour = cgo.buildSource(sidno, otext, stag, repor[0], shandle)
                            print(sour[0].to_struct(), file=j_out)
    #                        shandle = source.get_handle()
                            try:
                                r_writer.writerow([sidno, sour[1], otext])
                            except:    
                                print("Error writing S-csv")
                        else:
                            print("Unknown rectype: + rectype")
                print("Input file handled.")
    except  IOError: 
        print(IOError.winerror)
        print("IOError in j_out handling")
        return 8    
    
if __name__ == '__main__':
    sys.exit(main(argv))
