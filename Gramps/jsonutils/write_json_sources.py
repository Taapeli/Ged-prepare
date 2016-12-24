'''
Created on 8.11.2016

@author: Timo Nallikari
 
'''

import sys

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
#    def main(argv = ["write_json_sources", "C:/Temp/", "Lahteet.txt", "Result.json", Result.csv, 500000, 500000]):
    if argv is None:
        argv = sys.argv   
        
    if len(argv) != 7:
        print("Wrong number of arguments")
        return 8
    
    fdir = argv[1]                   # Directory for input and output files
    fin  = fdir + argv[2]            # Input file
    fout = fdir + argv[3]            # Output file
    cout = fdir + argv[4]
    repository_idno = int(argv[5])   # Start value for repository id numbers
    repository_incr = int(argv[6])   # Increment value  for repository id numbers
    source_idno = 0                  # Start value for source id number within repository
    
    print("File directory for program " + argv[0] + " is " + fdir)
    print("  input file  " + fin)
    print("  output file " + fout)

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
                    t_reader = csv.reader(t_in, delimiter=',')
                    for line in t_reader:
    #                    print(line)
                        rhandle = None
                        shandle = None
                        
                        row =  line
                        print(row)
                        rectype = row[0]         # Object type = Gramps object id prefix character
                        idno = row[2]            # Alternative way to assign Gramps object id's
                        handle = row[3]
                        otext = row[4].strip()
                        
                        if rectype == "T":
                            recobj  = row[1] 
                            tagr = cgo.buildTag(otext, thandle)
                            if   recobj == "R": rtag = tagr[0]     # The tag for repositories
                            elif recobj == "S": stag = tagr[0]     # The tag for sources
                            print(tagr[0].to_struct(), file=j_out)
                            try: 
                                r_writer.writerow([rectype, recobj, '', tagr[1], otext])
                            except:    
                                print("Error writing T-csv")                                      
                        elif rectype == "R":
                            arctype = row[1]         # repository type
                            repository_idno = repository_idno + repository_incr
                            ridno = rectype + "ref" + arctype + str(repository_idno)
                            repor = cgo.buildRepository(ridno, otext, rtag, int(arctype), rhandle)
                            print(repor[0].to_struct(), file=j_out)
                            try: 
                                r_writer.writerow([rectype, arctype, ridno, repor[1], otext])
                            except:    
                                print("Error writing R-csv")
                        elif rectype == "S":
                            otext = row[4].strip()
                            source_idno = source_idno + 1
                            sidno = rectype +"ref" + str(arctype) + str(repository_idno * 1000 + source_idno)
                            sour = cgo.buildSource(sidno, otext, stag, repor[0], shandle)
                            print(sour[0].to_struct(), file=j_out)
                            try:
                                r_writer.writerow([rectype, arctype, sidno, sour[1], otext])
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
