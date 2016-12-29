'''
Created on 8.11.2016

@author: Timo Nallikari
 
'''

import sys
import csv
import argparse
from sys import argv

from jsonutils.create_gramps_object import CreateGrampsObject
import logging
LOG = logging.getLogger()

tag     = None
thandle = None
repository = None
rhandle    = None 
source  = None
shandle = None

refstr = ''

def main(argv):
#    def main(argv = ['write_json_sources', 'C:/Temp/', 'Sources.csv', 'Result.json', Result.csv, 500000, 500000]):
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
    parser.add_argument('refind', default = '', help = 'Reference instamce indicator part for Gramps id.')
    parser.print_help() 
    args = parser.parse_args(argv)
    
    fdir = args.fdir
    fin  = fdir + args.fin 
    fout = fdir + args.fout            
    cout = fdir + args.cout
    repository_idno = int(args.ridno)
    repository_incr = int(args.ridincr)
    refstr = args.refind
    
    fh = logging.FileHandler(fdir + '\\writejsonsources.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setLevel(LOG.info)
    fh.setFormatter(formatter)
    LOG.addHandler(fh)                   

    source_idno = 0                  # Start value for source id number within repository
    
    LOG.info('File directory for program ' + argv[0] + ' is ' + fdir)
    LOG.info('  input file  ' + fin)
    LOG.info('  output file ' + fout)
    LOG.info('  output file ' + cout)

    tags = {}

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
                    LOG.info('CSV input file delimiter is ' + t_dialect.delimiter)
                    for row in t_reader:
                        rhandle = None
                        shandle = None
                        thandle = None 
                        LOG.debug(row)
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
                            print(tagr[0].to_struct(), file=j_out)
                            tags[recobj] = tagr[0]
                            try: 
                                r_writer.writerow([rectype, recobj, '', tagr[1], otext, '', '', '', ''])
                            except:    
                                LOG.error('Error writing T-csv') 
                                                                     
                        elif rectype == 'R':
                            r_count += 1
                            arctype = row[1]         # repository type
                            if handle != '':
                                rhandle = handle
                            if idno == '':
                                repository_idno = repository_idno + repository_incr
                                ridno = rectype + refstr + arctype + str(repository_idno)
                            else:
                                ridno = idno 
                            repor = cgo.buildRepository(ridno, otext, tags.get(rectype), int(arctype), rhandle)
                            print(repor[0].to_struct(), file=j_out)
                            try: 
                                r_writer.writerow([rectype, arctype, ridno, repor[1], otext, '', '', '', ''])
                            except:    
                                LOG.error('Error writing R-csv')
                                
                        elif rectype == 'S':
                            s_count += 1
                            if handle != '':
                                shandle = handle
                            if idno == '':    
                                source_idno = source_idno + 1
                                sidno = rectype + refstr + str(arctype) + str(repository_idno * 1000 + source_idno)
                            else:
                                sidno = idno 
                            attribs = (row[5], row[6], row[7])   
                            sour = cgo.buildSource(sidno, otext, tags.get(rectype), repor[0], shandle, attribs)
                            print(sour[0].to_struct(), file=j_out)
                            try:
                                r_writer.writerow([rectype, arctype, sidno, sour[1], otext, attribs[0], attribs[1], attribs[2], ''])
                            except:    
                                LOG.error('Error writing S-csv')
                        elif rectype == '#':
                            c_count += 1      
                        else:
                            u_count += 1
                            LOG.error('Unknown rectype: + rectype')
                LOG.info('Input file handled.')
                LOG.info('    Tags           ' + str(t_count))
                LOG.info('    Repositories   ' + str(r_count))
                LOG.info('    Sources        ' + str(s_count))
                LOG.info('    Comments       ' + str(c_count))
                LOG.info('    Unknown types  ' + str(u_count))
                LOG.info('  Total            ' + str(t_count + r_count + s_count + c_count + u_count))
    except  IOError: 
        LOG.error('IOError in file handling: ' + IOError.filename)
        return 8    
    
if __name__ == '__main__':
    sys.exit(main(argv))
