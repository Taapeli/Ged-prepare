'''
Created on 1.2.2017

@author: TimNal
'''


''' 
    Utility / Import Data Processing / Add Narc repository information to  Narc cvs file 

    Narcin hierarkia:
    ---------------- 

    Arkiston muodostaja (seurakunta)
        Arkisto (Repository) (seurakunnan arkisto)                <===
            Sarja (rippikirjat tms.)
                Lähdeluettelo
                    Lähde (Source) (rippikirja nnnn-mmmm)         <===   

    Narc-aineiston rsin/sour_in rakenne:
    ----------------------
    
    0 Päänimeke       Arkiston nimi
    1 Sartun          Arkistosarjan tunniste    
    2 Nimeke          Sarjan nimi
    3 AY_tunnus       Lähteen tunniste     nnnnnn.KA --> http://digi.narc.fi/digi/dosearch.ka?ay=nnnnnn.KA
    4 Nimeke2         Lähteen nimi 
    5 Tunniste        Lähteen arkistotunnus, signum 
    6 Alkuvuosi       Lähteen alkuvuosi 
    7 Loppuvuosi      Lähteen loppuvuosi 
    8 Lyhytnimeke     Lähteen koostettu nimi  (täydennetty osin alkuperäiseen aineistoon)
    
    Puunäkymän html-koodista eristetyn täydennysaineiston rin/repo_in rakenne:
    -------------------------------------------------------------

    0 Atun            Arkiston tunnus     nnnnnn.KA --> http://digi.narc.fi/digi/dosearch.ka?atun=nnnnnn.KA   
    1 Päänimeke       Arkiston nimi 
    2 Nimeke0         Arkistonmuodostajan nimi
       
     Tulosaineiston rsout/sour_out rakenne:
    -----------------------

    0 Atun            Arkiston tunnus     nnnnnn.KA --> http://digi.narc.fi/digi/dosearch.ka?atun=nnnnnn.KA   
    1 Päänimeke       Arkiston nimi 
    2 Nimeke0         Arkistonmuodostajan nimi
    3 Sartun          Arkistosarjan tunniste    
    4 Nimeke          Sarjan nimi
    5 AY_tunnus       Lähteen tunniste     nnnnnn.KA --> http://digi.narc.fi/digi/dosearch.ka?ay=nnnnnn.KA
    6 Nimeke2         Lähteen nimi 
    7 Tunniste        Lähteen arkistotunnus, signum 
    8 Alkuvuosi       Lähteen alkuvuosi 
    9 Loppuvuosi      Lähteen loppuvuosi 
   10 Lyhytnimeke     Lähteen koostettu nimi  (täydennetty osin alkuperäiseen aineistoon)
     
'''

import sys
import csv
import argparse
import logging
LOG = logging.getLogger('amend')
LOG.setLevel(logging.DEBUG)

def main(argv):
#    def main(argv = ['write_json_sources', 'C:/Temp/', 'Sources.csv', 'Repos.json', 'Result.csv']):
    if argv is None:
        argv = sys.argv   
    print(argv)   
    parser = argparse.ArgumentParser(
        description='Add repository information to a csv file for importing repositories and sources into Gramps.')
    parser.add_argument('modl', help = 'Module name')
    parser.add_argument('fdir', help = 'Directory for input and output files')
    parser.add_argument('rsin', help = 'Input file of type .csv - tags, repositories and sources.')
    parser.add_argument('rin', help = 'Output file of type .csv - repositories with ids and names')
    parser.add_argument('rsout', help = 'Output file of type .csv - input file with ids and names added.')
    parser.print_help() 
    args = parser.parse_args(argv)
    
    fdir = args.fdir
    rsin  = fdir + args.rsin 
    rin = fdir + args.rin            
    rsout = fdir + args.rsout    
 
    fh = logging.FileHandler(fdir + 'amendnarcsources.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    LOG.addHandler(fh) 
                
    LOG.info("   fdir = " + fdir)

    r_count = 0
    s_count = 0
    c_count = 0

    with open(rsout, 'w', encoding="utf-8-sig", newline='\n') as sour_out:
        s_writer = csv.writer(sour_out, delimiter=',')
        with open(rin, 'r', encoding="utf-8-sig") as repo_in:
            r_reader = csv.reader(repo_in, delimiter=',')
            with open(rsin, 'r', encoding="utf-8-sig") as sour_in:
                s_reader = csv.reader(sour_in, delimiter=',')
                for reporow in r_reader:
                    r_count += 1
                    repoid = reporow[0]
                    reponame = reporow[1]
                    nimeke0 = reporow[2]

                    for srcrow in s_reader:
                        LOG.debug("    " + srcrow[0] + ' ' + srcrow[4])
                        s_count += 1
                        if reponame < srcrow[0]:
                            LOG.debug(reponame + ' < ' + srcrow[0] + ' luetaan repo_in')
                            for reporow in r_reader:
                                r_count += 1
                                repoid = reporow[0]
                                reponame = reporow[1]
                                nimeke0 = reporow[2]                   
                                break
                            pass    
                        if reponame > srcrow[0]:
                            LOG.debug(reponame + ' > ' + srcrow[0] + ' luetaan sour_in')
                            continue                     
                        else:   #  reponame['label'] == srcrow[0]:
                            LOG.debug(reponame + ' = ' + srcrow[0] + ' talletetaan')
                            s_writer.writerow([repoid, srcrow[0], nimeke0,
                                               srcrow[1], srcrow[2], srcrow[3], srcrow[4], 
                                               srcrow[5], srcrow[6], srcrow[7], srcrow[8]])
                            c_count += 1
                
    print('')
    LOG.info('Input file handled.')
    LOG.info('    Repositories read  ' + str(r_count))
    LOG.info('    Sources read       ' + str(s_count))
    LOG.info('    Sources changed    ' + str(c_count))
        
if __name__ == '__main__':
    sys.exit(main(argv = ['amend_narc_repos', 'C:\\temp\\narc1\\', 'Sources.csv', 'Repos.csv', 'Result.csv']))
             
