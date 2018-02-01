# -*- coding: utf-8 -*-
'''
Created on 11.01.2017

@author: Timo Nallikari
 
'''
import sys
# import codecs
# sys.stdout = codecs.getwriter('utf8')(sys.stdout)
# sys.stderr = codecs.getwriter('utf8')(sys.stderr)

import csv
import argparse

import urllib.request
from html.parser import HTMLParser

import logging
LOG = logging.getLogger('dihainfo')

tag     = None
repository = None
source  = None

class DIHAParser(HTMLParser):
                 
    def __init__(self, cout, LOG):
        HTMLParser.__init__(self)
        self.inArchive = False
        self.inLink = False
        self.inRow = False
        self.inTable = False                
        self.countArchives = 0
        self.currLink = None
        self.reponame = None
        self.repohref = None  
        self.rowcount = 0
#        self.regexb = "^([A-ZÅÄÖa-zåäö., ]*)"

        self.LOG = LOG        
        self.writer = open(cout, 'w', encoding='UTF-8', newline = '\n')
        self.r_writer = csv.writer(self.writer, delimiter=',')

    def handle_starttag(self, tag, attrs):
        
        if tag == 'table':
#            if len(attrs) > 0:
#            print('In table ' + str(attrs))
            self.inTable = True
            self.inArchive = False
            self.inRow = False
            self.InLink = False

        #=======================================================================
        # elif self.inTable and tag == 'th':
        #     if len(attrs) >= 0:
        #         print('In table header ' + str(attrs))
        #=======================================================================

        elif self.inArchive and tag == 'tr':
            if len(attrs) > 0:
                print('In table row ' + str(attrs))
                self.inRow = True  

        elif self.inArchive and tag == 'a':
            if len(attrs) > 0 and attrs[0][0] == 'href':
                self.repohref = attrs[0]
                self.currLink = attrs[0][1].replace(r"\'", "")
                print('In link ' + self.currLink)
            self.inLink = True                
            #===================================================================              
            # self.rowcount += 1
            # if len(attrs) < 1:
            #     pass
            # else:
            #     print (tag + ' ' + str(attrs))
            #     self.repohref = attrs[0]
            #     self.inLink = True
            #===================================================================

    def handle_endtag(self, tag):
        if tag == "a":
            self.inLink = False
        elif tag == "tr":    
            self.inRow = False            
        elif tag =='table':
            self.inTable = False
            if self.inArchive:
                self.inArchive = False
                self.inRow = False
                self.InLink = False                 
                print('inArchive = False') 
            
    def handle_data(self, data):
        if data.startswith('\n') or data == '':
            pass        
        if self.inTable and data == 'Arkisto':
                self.inArchive = True
                print('inArchive=True')
        elif self.inArchive and self.inLink:
            print('Data ' + data)
            atun = ''
            rparts = self.currLink.split('=')
            if len(rparts) > 1:
                atun = rparts[1].split("&")[0]
                try:
                    self.r_writer.writerow([atun, data, self.currLink])
                    self.LOG.debug('Parsed: ' + atun + '/' + self.currLink)
                    self.countArchives += 1
                except  IOError: 
                    LOG.error('IOError in file handling: ' + IOError.filename)
                        
    def handle_comment(self, data):
#            LOG.debug("Comment  :", data)
        return
    def handle_entityref(self, name):
#            c = chr(name2codepoint[name])
#            LOG.debug("Named ent:", c)
        return
    def handle_charref(self, name):
#            if name.startswith('x'):
#                c = chr(int(name[1:], 16))
#            else:
#                c = chr(int(name))
#            LOG.debug("Num ent  :", c)
        return
    def handle_decl(self, data):
#            LOG.debug("Decl     :", data)
        return
    
    def handle_close(self):
        self.writer.close()
        self.close()
        return(self.countArchives)

def main(argv):
    if argv is None:
        argv = sys.argv   
#    LOG.debug(argv)   
    parser = argparse.ArgumentParser(description='Write a csv file of repositories from DIHA url.')
    parser.add_argument('modl', help = 'Module name')
    parser.add_argument('fdir', help = 'Directory for output and log files')
    parser.add_argument('in_url', help = 'Input url - repositories and sources.')
    parser.add_argument('cout', help = 'Output file of type .csv.')

    parser.print_help() 
    args = parser.parse_args(argv)
    
    fdir = args.fdir
    in_url = args.in_url
    cout = fdir + args.cout
    
    fh = logging.FileHandler(fdir + 'fetchdiharepos.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    LOG.addHandler(fh)                   

    LOG.info('File directory for program ' + argv[0] + ' is ' + fdir)
    LOG.info('  input url  ' + in_url)
    LOG.info('  output file ' + cout)
 
    nparser = DIHAParser(cout, LOG)
    with urllib.request.urlopen(in_url) as response:
        html = response.read().decode('utf-8')
        nparser.feed(str(html))
    r_count = nparser.handle_close()
 
    LOG.info('Data retrieved.')
    LOG.info('    Repositories   ' + str(r_count))
    
if __name__ == '__main__':
    sys.exit(main(['fetchdiharepos', 'C:/Temp/NARC2/', 'http://digihakemisto.appspot.com/', 'diharepos.csv'] ))
