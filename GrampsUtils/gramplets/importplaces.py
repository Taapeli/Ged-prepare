'''
Created on 12.1.2017

@author: TimNal
'''
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2015-2016 Nick Hall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#


"""Import / Database Processing / Import repository-place hierarchies from cvs file """

import os
import sys
import csv
import time
import logging
LOG = logging.getLogger()
LOG.setLevel(logging.DEBUG)

from gramps.gen.errors import GrampsImportError
from gramps.gen.db import DbTxn
from gramps.gen.lib import Note, NoteType, Place, PlaceName, PlaceRef, PlaceType, Source, Tag
from gramps.gen.utils.libformatting import ImportInfo
# from gramps.gui.utils import ProgressMeter
# from gramps.gen.plug.utils import OpenFileOrStdin
# from gramps.gen.config import config as configman

from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

# LOG = logging.getLogger(".importPlaces")
#from gramps.gen.utils.libformatting import ImportInfo

#-------------------------------------------------------------------------
#
# Import Place hierarchies from a csv file
#
#-------------------------------------------------------------------------

refstr = 'r'


pidno = None
tag = None
country = None            # Current country
state = None              # Current state 
municipality = None       # Current municipality
village = None            # Current village


def importPlaceHierarchy(db, filename, user):
    
    all_countries = []                     # Countries in the database 
    states_of_current_country = []         # States in the current country
    municipalities_of_current_state = []   # Municipalities in the current state
    villages_of_current_municipality = []  # Villages in the current municipality

    
    h_count = 0    # Header line count
    c_count = 0    # Country count (valtio)
    p_count = 0    # State count (lääni)
    m_count = 0    # Municipality count (kunta)
    v_count = 0    # Village count (kylä)
    u_count = 0    # Unknown row count

    def get_countries(db):
        countries = []
        for handle in db.find_place_child_handles(''):
            place = db.get_place_from_handle(handle)
            if int(place.get_type()) == PlaceType.COUNTRY:
                countries.append(place)
        return countries
        
    def findNextPidno(pidstrt):
        with DbTxn(_("Find next pidno"), db):
            db.set_repository_id_prefix(pidstrt + '%04d')  
            next_pidno = db.find_next_place_gramps_id() 
            LOG.debug('Next pidno = ' + next_pidno)
            db.set_repository_id_prefix('R%04d') 
        return next_pidno             
                       
    def findPlace(pid, handle, pname):
        place = None
        if pid != '':
            with DbTxn(_("Read place"), db):
                place = db.get_place_from_id(pid)
                if place != None:    
                    LOG.info('Place read by id: ' + handle + ' ' + place.get_name().get_value())
                else:    
                    LOG.error('Place NOT found by id: ' + handle + ' ' + pname)
                    raise GrampsImportError('Place NOT found by id: ', pid + '/' + pname)
        return place  
    
    def checkPlaceDuplicate(pname, old_places):
        place = None
        if len(old_places) > 0:
            for old_place in old_places:
                LOG.debug('Comparing ' + pname + ' with ' + old_place.get_name().get_value())
                if old_place.get_name().get_value() == pname:
    #                LOG.debug('Found match ' + pname + ' with ' + place.get_name().get_value() + ' of type ' + place.__class__.__name__ ) 
                    return old_place
     
        return None
 
    def addPlace(pname, ptype, refPlace=None, plang='fi'):
        place = Place()
        placeName = PlaceName() 
        placeName.set_value(pname)
        placeName.set_language(plang)
        place.set_name(placeName)
#        place.set_change_time(chgtime)
        place.set_type(ptype)
        place.add_tag(tags[ptype])
        if refPlace != None:
            placeRef = PlaceRef()
            placeRef.set_reference_handle(refPlace.get_handle())
            place.add_placeref(placeRef)
#        tag.set_color("#EF2929")
        with DbTxn(_("Add Place"), db) as trans:
            phandle = db.add_place(place, trans)

            LOG.debug('Place added: ' + place.get_name().get_value() + ' ' + phandle)
        return place 
    
    def checkTagExistence(otext):

        with DbTxn(_("Read Tag"), db):
            tag = db.get_tag_from_name(otext)
        if tag != None: 
                LOG.debug('Tag found by name, no duplicates: ' + otext + ' ' + tag.get_name())       
        else:       
            tag = Tag()                  
            tag.set_name(otext)
            tag.set_color("#EF2929")
            with DbTxn(_("Add Tag"), db) as trans:
                thandle = db.add_tag(tag, trans)
                LOG.debug('Tag added: ' + tag.get_name() + ' ' + thandle)
        return tag    
    
    chgtime = int(time.time())
    LOG.info("   chgtime = " + str(chgtime)) 
                
   
    fdir = os.path.dirname(filename) 
    '''
    fh = logging.FileHandler(fdir + '\\placeimport.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    LOG.addHandler(fh) 
    '''                  
    LOG.info("   fdir = " + fdir)
    cout = fdir + "\\result0.csv" 
    LOG.debug('ini file handling')
     
    '''   
    config = configman.register_manager("importplaces")
    config.register("options.repositoryidrng", "1000")    
    config.register("options.repositoryincr", "1") 
    config.register("options.placeidrng", "1000")    
    config.register("options.placeidincr", "1") 
    config.register("options.refstring", "r") 
    config.load()
    config.save()
    
    repository_idrange = int(config.get('options.repositoryidrng'))
    repository_incr = int(config.get('options.repositoryincr'))
    place_idrange = int(config.get('options.placeidrng'))
    place_idincr = int(config.get('options.placeidincr'))
    refstr = config.get('options.refstring')
    place_idno = 0
    '''


    tags = {}
#              Dictionary  tagtypes     placetype: tag name    
    tagTypes = {PlaceType.COUNTRY: "Referenssivaltio", 
                PlaceType.STATE: "Referenssilääni", 
                PlaceType.MUNICIPALITY: "Referenssikunta", 
                PlaceType.VILLAGE: "Referenssikylä"}
           
    for key, value in tagTypes.items():
        tags[key] = checkTagExistence(value).get_handle()
        
    all_countries = get_countries(db)    
        
    try:
        with open(cout, 'w', newline = '\n', encoding="utf-8") as csv_out:
            r_writer = csv.writer(csv_out, delimiter=';')
            with open(filename, 'r', encoding="utf-8") as t_in:
#                rhandle = None
                phandle = None
                t_dialect = csv.Sniffer().sniff(t_in.read(1024))
                t_in.seek(0)
                t_reader = csv.reader(t_in, t_dialect)
                LOG.info('CSV input file delimiter is ' + t_dialect.delimiter)
         
                for row in t_reader:
                    rectype = row[0]         # Record type = Gramps place type name (fi_FI)
#                    LOG.debug('Row type: -' + row[0] + '-')
                    if rectype == 'type':
                        LOG.debug('First row: ' + row[0])
                        h_count += 1  
                        r_writer.writerow([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]])
                    else:
                        idno = row[1]                       # Possibly previously assigned Gramps object id
                        handle = row[2].strip('"')          # Possibly previously assigned Gramps object handle
                        pname = row[3].strip()
#                        LOG.debug("Rectype " + rectype +'  name = ' + pname)

                        if rectype == 'valtio':
                            LOG.debug('Country row: ' + pname)
                            c_count += 1
                            result = None
                            if handle != '':
                                result = findPlace(idno, handle, pname)
                            else:
                                result = checkPlaceDuplicate(pname, all_countries)     
                            if result != None:
                                LOG.debug('Country row is a duplicate of ' + result.get_name().get_value() + ' and updates the existing one)')
                                country = result
                                # &TODO: some updating    
                                with DbTxn(_("Update Country"), db) as trans:
                                    db.commit_place(country, trans)                                
                            else:
                                country = addPlace(pname, PlaceType.COUNTRY)
                            states_of_current_country = []
                            for cname, handle in db.find_backlink_handles(country.get_handle(), ['Place']):
                                states_of_current_country.append(db.get_place_from_handle(handle))

                            chandle = country.get_handle()
                            cidno = country.get_gramps_id()                                
                            try: 
                                r_writer.writerow([row[0], row[1],cidno, chandle, row[4], row[5], row[6], row[7]])
                            except IOError:    
                                LOG.error('Error writing country-csv '  + IOError.strerror)   
                            LOG.debug('Old states ' + str(len(states_of_current_country)))
                            
                        elif rectype == 'lääni':
                            LOG.debug('State row: ' + pname)
                            result = None
                            p_count += 1
                            if handle != '':
                                result = findPlace(idno, handle, pname)
                            else:
                                result = checkPlaceDuplicate(pname, states_of_current_country)
                            if result != None:
                                LOG.debug('State row is a duplicate of ' + result.get_name().get_value() + ' and updates the existing one)')
                                state = result
                                # &TODO: some updating  
                                with DbTxn(_("Update State"), db) as trans:
                                    db.commit_place(state, trans)
                            else:       
                                state = addPlace(pname, PlaceType.STATE, country)
                                states_of_current_country.append(state)
                            municipalities_of_current_state = []
                            for cname, handle in db.find_backlink_handles(state.get_handle(), ['Place']):
                                municipalities_of_current_state.append(db.get_place_from_handle(handle))

                            phandle = state.get_handle()
                            pidno = state.get_gramps_id()                                
                            try: 
                                r_writer.writerow([row[0], row[1], pidno, phandle, row[4], row[5], row[6], row[7]])
                            except IOError:    
                                LOG.error('Error writing state-csv '  + IOError.strerror) 
                            LOG.debug('Old municipalities ' + str(len(municipalities_of_current_state)))                                 
    
                        elif rectype == 'kunta':
                            LOG.debug('Municipality row: ' + pname)
                            m_count += 1
                            result = None
                            if handle != '':
                                result = findPlace(idno, handle, pname)
                            else:
                                result = checkPlaceDuplicate(pname, municipalities_of_current_state) 
                            if result != None:
                                LOG.debug('Municipality row is a duplicate of ' + result.get_name().get_value() + ' and updates the existing one)')
                                municipality = result
                                # &TODO: some updating  
                                with DbTxn(_("Update Municipality"), db) as trans:
                                    db.commit_place(municipality, trans)                                                
                            else:  
                                municipality = addPlace(pname, PlaceType.MUNICIPALITY, state)
                                municipalities_of_current_state.append(municipality)
                            villages_of_current_municipality = []
                            for cname, handle in db.find_backlink_handles(municipality.get_handle(), ['Place']):
                                villages_of_current_municipality.append(db.get_place_from_handle(handle))

                            mhandle = municipality.get_handle()
                            midno = municipality.get_gramps_id()                    
                            try:
                                r_writer.writerow([row[0], row[1], midno, mhandle, row[4], row[5], row[6], row[7]])
                            except IOError:    
                                LOG.error('Error writing municipality-csv '  + IOError.strerror)
                            LOG.debug('Old municipalities ' + str(len(municipalities_of_current_state)))    
 
                        elif rectype == 'kylä': 
                            LOG.debug('Village row: ' + pname)
                            v_count += 1
                            if handle != '':
                                result = findPlace(idno, handle, pname)
                            else:
                                result = checkPlaceDuplicate(pname, villages_of_current_municipality)     
                            if result != None:
                                LOG.debug('Village row is a duplicate of ' + result.get_name().get_value() + ' and updates the existing one)')                                
                                village = result
                                # &TODO: some updating                 
                                with DbTxn(_("Update Village"), db) as trans:
                                    db.commit_place(village, trans)                                
                            else: 
                                village = addPlace(pname, PlaceType.VILLAGE, municipality)
                                villages_of_current_municipality.append(village)           
                            vhandle = village.get_handle()
                            vidno = village.get_gramps_id()                    
                            try:
                                r_writer.writerow([row[0], row[1], vidno, vhandle, row[4], row[5], row[6], row[7]])
                            except IOError:    
                                LOG.error('Error writing village-csv '  + IOError.strerror) 
                            LOG.debug('Old villages ' + str(len(villages_of_current_municipality))) 
    
                        else:
                            u_count += 1
                            LOG.error('Unknown rectype: ' + rectype)
                            raise GrampsImportError('Unknown record type ' + rectype)
        
    except:
        exc = sys.exc_info()[0]
        LOG.error('*** Something went really wrong! ', exc )
        
        return ImportInfo({_('Results'): _('Something went really wrong  ')})
    
    results =  {  _('Results'): _('Input file handled.')
                , _('    Countries      '): str(c_count)
                , _('    States         '): str(p_count)
                , _('    Municipalities '): str(m_count)
                , _('    Villages       '): str(v_count)
                , _('    Unknown types  '): str(u_count)
                , _('  Total            '): str(c_count + p_count + m_count + v_count + u_count)  }
     
    LOG.info('Input file handled.')
    LOG.info('    Countries      ' + str(c_count))
    LOG.info('    States         ' + str(p_count))
    LOG.info('    Municipalities ' + str(m_count))
    LOG.info('    Villages       ' + str(v_count))
    LOG.info('    Unknown types  ' + str(u_count))
    LOG.info('  Total            ' + str(c_count + p_count + m_count + v_count + u_count))
    
    db.enable_signals()
    db.request_rebuild()

    return ImportInfo(results)   

                       

