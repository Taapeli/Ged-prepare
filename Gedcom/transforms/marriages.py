#!/usr/bin/env python3

"""
Avio-PLAC:n hajoittaminen
pekka.valta@kolumbus.fi
5.11.2016 16.48 
	
-> minä, Juha
Moi,
vilkaisin gedcomista, miltä näyttää avioliitto, jossa on paikan nimeen lykätty myös sulhasen ja morsiamen kotipaikat. Tämä tapahan on itse asiassa hyvin tehokas ja ainoa mahdollinen, jos sukututkimusohjelma ei tue asuinpaikka-tapahtumia. Sen voisi jopa antaa suosituksena, jos näin kirjattu tieto kyettäisiin purkamaan.

0 @F0712@ FAM
1 HUSB @I33884@
1 WIFE @I33885@
1 MARR
2 DATE 1 APR 1839
2 PLAC Pielavesi, (Säviä 8/Taipale 10)
2 ADDR
3 CTRY Pielavesi, (Säviä 8/Taipale 10)

Grampsista varmistin, että henkilöiden ID:t olivat samat kuin gedcomissa.

Nyt seuraa tiiseri teille ohjelmointitaitoisille:

Päättelisin Grampsin (uuden) erillistyökalun logiikaksi sen, että sen jälkeen kun gedcom on luettu Grampsiin, luetaan työkalulla gedcomia uudelleen ja kun MARR-tietoryhmässä kohdataan PLAC teksti a (b/c),
muodostetaan ja päivitetään kantaan
- henkilölle HUSB RESI b,a , jossa DATE=FAM DATE date
- henkilölle WIFE RESI c,a , jossa DATE=FAM DATE date
- MARR PLAC < a

Jos oikein hienostelisi, niin ottaisi huomioon lisätapaukset, jossa on kylän lisäksi talokin
(Säviä Vuorimäki/Sulkavanjärvi Petäjämäki)

Mallia sorsapohjaksi löytynee Data Entry Grampletista, jonka kautta voi syöttää syntymä/kuolintapahtumia.

Näillä ideoilla pyhäinpäivän keskellä


"""

version = "1.0"


from collections import defaultdict 
import re
#from PIL.SpiderImagePlugin import outfile

class FamInfo:
    husb = None
    wife = None
    date = None
    place = ""
   
class Place:
    def __init__(self,place,date):
        self.place = place
        self.date = date
    def __repr__(self):
        pass

resi = defaultdict(list) # key=@individ-id@ value=[(place,date),...]
fams = defaultdict(FamInfo) # key=@fam@, value=FamInfo
fixedfams = {} # key=@fam@ value=place

def add_args(parser):
    pass

def initialize(args):
    pass

def phase1(args,line,level,path,tag,value):
    '''
		1st traverse: finding all families
    '''
    if path.endswith(".HUSB"):  # @fam@.HUSB @husb@
        parts = path.split(".")
        fam = parts[0]
        #husbands[fam] = value
        fams[fam].husb = value
    if path.endswith(".WIFE"):  # @fam@.WIFE @wife@
        parts = path.split(".")
        fam = parts[0]
        #wives[fam] = value
        fams[fam].wife = value
    if path.endswith(".MARR.DATE"):  # @fam@.MARR.DATE date
        parts = path.split(".")
        fam = parts[0]
        #dates[fam] = value
        fams[fam].date = value
    if path.endswith(".MARR.PLAC"):  # @fam@.MARR.PLAC place
        parts = path.split(".")
        fam = parts[0]
        place = value
        fams[fam].place = value

def phase2(args):
    '''
        Parse multiple places mentioned as marriage location: "loc1, (loc2, loc3)"
    '''
    for fam,faminfo in fams.items():
        m = re.match(r"([^,]+), \(([^/]+)/([^/]+)\)",faminfo.place)
        if m:
            husb_place = m.group(2)+", "+m.group(1)
            wife_place = m.group(3)+", "+m.group(1)
            resi[faminfo.husb].append((husb_place,faminfo.date))
            resi[faminfo.wife].append((wife_place,faminfo.date))
            fixedfams[fam] = m.group(1)

def phase3(args,line,level,path,tag,value,f):
    '''
        2nd traverse: creating the new GEDCOM file
    '''
    if value == "INDI":
        key = line.split()[1]
        if key in resi:
            f.emit(line)
            for place,date in resi[key]:
                f.emit("1 RESI")
                f.emit("2 TYPE marriage")
                if date: f.emit("2 DATE " + date)
                f.emit("2 PLAC " + place)
            return
    if path.endswith(".MARR.PLAC"):  # @fam@.MARR.PLAC place
        parts = path.split(".")
        fam = parts[0]
        if fam in fixedfams:
            line = "{} {} {}".format(level,"PLAC", fixedfams[fam])
        f.emit(line)
        return
    f.emit(line)
                       
