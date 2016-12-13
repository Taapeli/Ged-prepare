'''
Created on 8.11.2016

@author: Timo Nallikari
 
'''

import argparse
import csv
import logging
from sys import argv
import sys

from jsonutils.create_gramps_object import CreateGrampsObject 


tag     = None
thandle = None
repository = None
rhandle    = None 
source  = None
shandle = None

logging.basicConfig(level=logging.DEBUG)

def main(argv):
#    def main(argv = ['write_json_sources', 'C:/Temp/', 'Lahteet.txt', 'Result.json', Result.csv, 500000, 500000]):
    if argv is None:
        argv = sys.argv   
    print(argv)   
    parser = argparse.ArgumentParser(description='Write a json file for importing repositories and sources into Gramps.')
    parser.add_argument('modl', help = 'Module name')
    parser.add_argument('fdir', help = 'Directory for input and output files')
    parser.add_argument('fin', help = 'Input file of type .csv - tags, repositories and sources.')
    parser.add_argument('fout', help = 'Output file of type .json - repositories and sources.')
    parser.add_argument('cout', help = 'Output file of type .csv - input file with ids and handles added.')
    parser.add_argument('ridno', default = 1000, help = 'Repository id numeric part starting value.')
    parser.add_argument('ridincr', default = 10, help = 'Repository id numeric part increment.')
#    args = parser.parse_args()
    parser.print_help() 
    args = parser.parse_args(argv)
    
    fdir = args.fdir
    fin  = fdir + args.fin 
    fout = fdir + args.fout            
    cout = fdir + args.cout
    repository_idno = int(args.ridno)
    repository_incr = int(args.ridincr)
        
#    if len(argv) != 7:
#        logging.error('Wrong number of arguments: ' + str(len(argv)))
#        return 8

#    fdir = argv[1]                   # Directory for input and output files
#    fin  = fdir + argv[2]            # Input file
#    fout = fdir + argv[3]            # Output file
#    cout = fdir + argv[4]
#    repository_idno = int(argv[5])   # Start value for repository id numbers
#    repository_incr = int(argv[6])   # Increment value  for repository id numbers
    source_idno = 0                  # Start value for source id number within repository
    
    logging.info('File directory for program ' + argv[0] + ' is ' + fdir)
    logging.info('  input file  ' + fin)
    logging.info('  output file ' + fout)
    logging.info('  output file ' + cout)

    rtag = None            # Tag used for repositories
    stag = None            # Tag used for sources
        
    t_count = 0
    r_count = 0
    s_count = 0
    c_count = 0
    u_count = 0
        
    cgo = CreateGrampsObject()
      
    try:

        with open(cout, 'w', newline = '\n') as csv_out:
            r_writer = csv.writer(csv_out, delimiter=',')
            with open(fout, 'w', encoding='UTF-8') as j_out:
                rectype = ''
                arctype = ''
                with open(fin, 'r') as t_in:
                    t_dialect = csv.Sniffer().sniff(t_in.read(1024))
                    t_in.seek(0)
                    t_reader = csv.reader(t_in, t_dialect)
                    logging.info('CSV input file delimiter is ' + t_dialect.delimiter)
                    for row in t_reader:
                        rhandle = None
                        shandle = None
                        thandle = None 
                        logging.debug(row)
                        rectype = row[0]         # Object type = Gramps object id prefix character
                        idno = row[2]            # Possibly previously assigned Gramps object id
                        handle = row[3]          # Possibly previously assigned Gramps object handle
                        otext = row[4].strip()
                        
                        if rectype == 'T':
                            t_count += 1
                            recobj  = row[1]     # Tag related to repository or source
                            if handle != '':
                                thandle = handle
                            tagr = cgo.buildTag(otext, thandle)
                            if   recobj == 'R': 
                                rtag = tagr[0]     # The tag for repositories
                            elif recobj == 'S': 
                                stag = tagr[0]     # The tag for sources
                            print(tagr[0].to_struct(), file=j_out) 
                            try: 
                                r_writer.writerow([rectype, recobj, '', tagr[1], otext, '', '', '', ''])
                            except:    
                                logging.error('Error writing T-csv')                                      
                        elif rectype == 'R':
                            r_count += 1
                            arctype = row[1]         # repository type
                            if handle != '':
                                rhandle = handle
                            if idno == '':
                                repository_idno = repository_idno + repository_incr
                                ridno = rectype + 'ref' + arctype + str(repository_idno)
                            else:
                                ridno = idno    
                            repor = cgo.buildRepository(ridno, otext, rtag, int(arctype), rhandle)
                            print(repor[0].to_struct(), file=j_out)
                            try: 
                                r_writer.writerow([rectype, arctype, ridno, repor[1], otext, '', '', '', ''])
                            except:    
                                logging.error('Error writing R-csv')
                        elif rectype == 'S':
                            s_count += 1
                            if handle != '':
                                shandle = handle
                            if idno == '':    
                                source_idno = source_idno + 1
                                sidno = rectype +'ref' + str(arctype) + str(repository_idno * 1000 + source_idno)
                            else:
                                sidno = idno 
                            attribs = (row[5], row[6], row[7])   
                            sour = cgo.buildSource(sidno, otext, stag, repor[0], shandle, attribs)
                            print(sour[0].to_struct(), file=j_out)
                            try:
                                r_writer.writerow([rectype, arctype, sidno, sour[1], otext, attribs[0], attribs[1], attribs[2], ''])
                            except:    
                                logging.error('Error writing S-csv')
                        elif rectype == '#':
                            c_count += 1      
                        else:
                            u_count += 1
                            logging.error('Unknown rectype: + rectype')
                logging.info('Input file handled.')

                logging.info('    Tags           ' + str(t_count))
                logging.info('    Repositories   ' + str(r_count))
                logging.info('    Sources        ' + str(s_count))
                logging.info('    Comments       ' + str(c_count))
                logging.info('  Total            ' + str(t_count + r_count + s_count + c_count + u_count))
    except  IOError: 
        logging.error(IOError.winerror)
        logging.error('IOError in j_out handling')
        return 8    
    
if __name__ == '__main__':
    sys.exit(main(argv))
