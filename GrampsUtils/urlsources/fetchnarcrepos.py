# -*- coding: utf-8 -*-
'''
Created on 11.01.2017

@author: Timo Nallikari
 
'''

import sys
import csv
import argparse

import urllib.request
from html.parser import HTMLParser

import logging
LOG = logging.getLogger('getnarcinfo')

tag     = None
repository = None
source  = None

class NARCParser(HTMLParser):
    
    
    def __init__(self, cout):
        HTMLParser.__init__(self)
        self.inLink = False
        self.inDiv = False       
        self.dataArray = []
        self.countArchives = 0
        self.lasttag = None
        self.lastvalue = None
        self.lasthref = None
        self.reponame = None
        self.repohref = None
        self.regexb = "^([A-ZÅÄÖa-zåäö., ]*)"
        
        self.writer = open(cout, 'w', encoding='UTF-8', newline = '\n')
        self.r_writer = csv.writer(self.writer, delimiter=',')

    def handle_starttag(self, tag, attrs):

        if tag == 'a':
            if len(attrs) < 2:
                pass
            elif attrs[1] != ('title', 'Arkisto'):
                pass
            else:
#                print (tag + ' ' + str(attrs))
                self.repohref = attrs[0]
                self.inLink = True
                self.inDiv = False
        elif tag == 'ul' and self.inLink:
            if len(attrs) > 0:
                print (tag + ' ' + str(attrs))
                self.inDiv = True     

    def handle_endtag(self, tag):
        if tag == "a":
            self.inLink = False
        elif tag == "ul":    
            self.inDiv = False
            
    def handle_data(self, data):
        if self.inLink or self.inDiv:
            if len(data) < 3:
                pass
            else:
#                print('Href: >', self.repohref[1], '<')
#                print('Data: >', data, '<')
                rparts = self.repohref[1].split('=')
                if len(rparts) > 2:
                    atun = rparts[1].split("&")[0]
                    amnimeke = rparts[2].strip()
                    animeke = data.strip(' -')
 
                    try:
                        self.r_writer.writerow([atun, animeke, amnimeke])
                        LOG.debug('Parsed: ' + atun + '/' + animeke + '/' + amnimeke)
                        self.countArchives += 1
                    except  IOError: 
                        LOG.error('IOError in file handling: ' + IOError.filename)
                        
    def handle_comment(self, data):
#            print("Comment  :", data)
        return
    def handle_entityref(self, name):
#            c = chr(name2codepoint[name])
#            print("Named ent:", c)
        return
    def handle_charref(self, name):
#            if name.startswith('x'):
#                c = chr(int(name[1:], 16))
#            else:
#                c = chr(int(name))
#            print("Num ent  :", c)
        return
    def handle_decl(self, data):
#            print("Decl     :", data)
        return
    
    def handle_close(self):
        self.writer.close()
        self.close()
        return(self.countArchives)

def main(argv):
    if argv is None:
        argv = sys.argv   
#    print(argv)   
    parser = argparse.ArgumentParser(description='Write a csv file of repositories from NARC url.')
    parser.add_argument('modl', help = 'Module name')
    parser.add_argument('fdir', help = 'Directory for output and log files')
    parser.add_argument('in_url', help = 'Input url - repositories and sources.')
    parser.add_argument('cout', help = 'Output file of type .csv.')

    parser.print_help() 
    args = parser.parse_args(argv)
    
    fdir = args.fdir
    in_url = args.in_url
    LOG.info('Html-sivun URL  ' + in_url)
    cout = fdir + args.cout
    LOG.info('Tulostiedosto  ' + cout)
    
    fh = logging.FileHandler(fdir + 'fetchnarcrepos.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    LOG.addHandler(fh)                   
    
    LOG.info('File directory for program ' + argv[0] + ' is ' + fdir)
    LOG.info('  input url  ' + in_url)
    LOG.info('  output file ' + cout)
 
    nparser = NARCParser(cout)
    with urllib.request.urlopen(in_url) as response:
        html = response.read()
        nparser.feed(str(html))
    r_count = nparser.handle_close()
 
    LOG.info('Data retrieved.')
    LOG.info('    Repositories   ' + str(r_count))
    
if __name__ == '__main__':
    sys.exit(main(['fetchnarcrepos.py', 'C:/Temp/NARC2/','http://digi.narc.fi/digi/puu.ka', 'narcrepos.csv'] ))
