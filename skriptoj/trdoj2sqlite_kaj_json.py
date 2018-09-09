# -*- coding: utf-8 -*-
# Tio dosiero estas un skripto, ke transformas la kde4 tradukajn dosierojo al un .sqlite dosiero...
import os
import json
from sqlite3 import *

#faras espereble la skripto kurebla de skript- kaj cxefdosierujo
trd_dir="../kurso4/tradukoj" if not "kurso4" in os.listdir() else "kurso4/tradukoj"
try:
    trd_files = os.listdir(trd_dir)
except Exception as e:
    print("Kie estas la kurso4 dosierojo :?\nMi cxesas por tio...");
    exit()

############################################
###########FILTRI POR LA TRADUKENDAJ########
############################################
trd_json = {}
i=0
print("legas la .trd-ojn")
#legi .trd dosieroj kaj preni la tradukojn de la etiketoj
lines = open(trd_dir+"/tradukendaj.tdf").read().split("\n")
sekcio = ""
#print(f)
for l in lines:
    l = l.strip()
    if l.startswith(";") or l=="": continue
    if l.startswith("[") and l.endswith("]"):
        sekcio = l[1:-1].lower()
        if not sekcio.lower() in trd_json:
            #print("\t"+sekcio)
            trd_json[sekcio.lower()] = {}
    if "=" in l:
        #print(l)
        etikedo, text = l.split("=", maxsplit=1)
        text = text.strip("\"")
        if not etikedo in trd_json[sekcio]:
            trd_json[sekcio][text] = {}

############################################
###########PRENAS LA TRADUKENDAJ############
############################################
for f in trd_files:
    if not f.endswith(".trd"): continue
    lang = f.replace(".trd","")
    lines = open(trd_dir+"/"+f).read().split("\n")
    sekcio = ""
    enda = True
    #print(f)
    for l in lines:
        l = l.strip()
        if l.startswith(";") or l=="": continue
        if l.startswith("[") and l.endswith("]"):
            sekcio = l[1:-1].lower()
            enda = True if sekcio.lower() in trd_json else False
        if "=" in l and enda:
            #print(l)
            etikedo, text = l.split("=", maxsplit=1)
            text = text.strip("\"")
            if etikedo in trd_json[sekcio] and enda:
                trd_json[sekcio][etikedo][lang] = text


############################################
##SKRIBAS LA TRADUKOJN AL JSON + SQL########
############################################
langs = [lang.replace(".trd","") for lang in trd_files if lang.endswith(".trd")]
meta  = ["etikedo", "sekcio"]
cols  = meta+langs
lang_str = " text NOT NULL, ".join(meta)+" text NOT NULL, "+" text, ".join(langs)+" text, PRIMARY KEY(etikedo, sekcio)"
cols_str = ",".join(cols)

#skribas la .sqlite-dosieron
conn = connect('trd.db')
c = conn.cursor()
# Create table
c.execute('CREATE TABLE IF NOT EXISTS trd (%s)' % lang_str )

# Insert a row of data
for sekcio_ in trd_json:
    for etikedo_ in trd_json[sekcio_]:
        etikedo_str = [etikedo_,sekcio_]+[trd_json[sekcio_][etikedo_][lang] if lang in trd_json[sekcio_][etikedo_] else "" for lang in langs]
        c.execute("INSERT INTO trd VALUES (%s)" % ",".join(["?"]*len(cols)), etikedo_str)
print("skribis la sqlite-dosieron")

# Save (commit) the changes
conn.commit()
conn.close()

### KOMPAKTAS LA JSON PER FIKSA INDIKILO
lang2ind = {langs[ind]:ind for ind in range(len(langs))}
compakta_json = {"index":lang2ind,"tradukoj":{}}
for sekcio_ in trd_json:
    compakta_json["tradukoj"][sekcio_]={}
    for etikedo_ in trd_json[sekcio_]:
        compakta_json["tradukoj"][sekcio_][etikedo_] = list(trd_json[sekcio_][etikedo_].values())

open("trd.json","w").write(json.dumps(compakta_json, ensure_ascii=False))
print("skribis la json-dosieron")
