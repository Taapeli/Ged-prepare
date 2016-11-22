#!/usr/bin/env python3
"""
Lähettäjä: <pekka.valta@kolumbus.fi>
Päiväys: 12. marraskuuta 2016 klo 17.26
Aihe: Kastettu paikan korjaus
Vastaanottaja: "Kujansuu, Kari" <kari.kujansuu@gmail.com>
Kopio: Juha Mäkeläinen <juha.makelainen@iki.fi>


Moi,
yhdessä gedcomissa oli runsaasti syntymäpaikkoja muodossa "(kastettu) Oulu". Ilmeisesti sukututkimusohjelma ei ole tukenut kastetiedon kunnon rekisteröintiä.

Voisitko lisätä paikkojen käsittelyyn säännön, että jos

1 BIRT
2 PLAC (kastettu) xxx

niin muutetaan muotoon

1 CHR
2 PLAC xxx

t.
Pekka

"""

ids = set()

def add_args(parser):
    parser.add_argument("--testiparametri")

def initialize(args):
    pass

def phase1(args,line,path,tag,value):
    if path.endswith(".BIRT.PLAC") and value.startswith("(kastettu)"):  # @id@.BIRT.PLACE (kastettu) xxx
        parts = path.split(".")
        id = parts[0]
        ids.add(id)

def phase2(args):
    pass

def phase3(args,line,path,tag,value,f):
    parts = path.split(".")
    id = parts[0]
    if id in ids:
        if tag == "BIRT": tag = "CHR"
        if tag == "PLAC" and value.startswith("(kastettu)"): value = " ".join(value.split()[1:])
        line = line.split()[0] + " " + tag + " " + value
    f.emit(line)


