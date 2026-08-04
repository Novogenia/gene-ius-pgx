# -*- coding: utf-8 -*-
"""
Der ehrliche Abdeckungstest: Wie viele unserer 2.694 Wirkstoffe finden sich
tatsaechlich in MED-RT wieder? Ein RXCUI, zu dem es keine Beziehungen gibt,
nuetzt nichts - egal wie gut das Namensmatching war.

Zusaetzlich: Namensabgleich ueber MED-RTs eigene from_name-Spalte. Das ist der
verlaesslichste Test, weil MED-RT den RxNorm-Namen mitliefert.
"""
import json, re, unicodedata
from collections import Counter, defaultdict

M = json.load(open("rxcui_map.json", encoding="utf-8"))
rel = json.load(open("medrt_rel.json", encoding="utf-8"))

def entkleide(s):
    s = unicodedata.normalize("NFKD", str(s).lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"\b(hydrochloride|hcl|sodium|potassium|calcium|sulfate|sulphate|maleate|"
               r"tartrate|citrate|mesylate|besylate|fumarate|succinate|acetate|phosphate|"
               r"nitrate|bromide|chloride|dihydrate|monohydrate|anhydrous|salt|base|"
               r"saeure|acid|um|e)\b", " ", s)
    return re.sub(r"[^a-z0-9]", "", s)

# MED-RT-Wirkstoffe: RXCUI -> Name, und Name -> RXCUI
medrt_rx = {}
for k, paare in rel.items():
    for fc, fn, tc, tn in paare:
        if fc and fc.isdigit():
            medrt_rx[fc] = fn
medrt_name = {}
for rx, nm in medrt_rx.items():
    medrt_name.setdefault(entkleide(nm), rx)
print("MED-RT kennt %d Wirkstoffe (RxNorm-Konzepte)" % len(medrt_rx))

# Beziehungen je RXCUI
byrx = defaultdict(lambda: defaultdict(list))
for k, paare in rel.items():
    for fc, fn, tc, tn in paare:
        if fc:
            byrx[fc][k].append(tn)

treffer_rx, treffer_name, keiner = [], [], []
for k, v in M.items():
    rx = v.get("rxcui")
    if rx and rx in byrx:
        v["medrt"] = rx; treffer_rx.append(v); continue
    # zweiter Versuch ueber den Namen
    alt = medrt_name.get(entkleide(v["name"]))
    if alt:
        v["medrt"] = alt
        v["medrt_via"] = "name"
        treffer_name.append((v["name"], medrt_rx[alt]))
    else:
        v["medrt"] = None
        keiner.append(v["name"])

print("\nMED-RT-Treffer ueber RXCUI:      %d" % len(treffer_rx))
print("zusaetzlich ueber Namensabgleich: %d" % len(treffer_name))
print("ohne jede MED-RT-Beziehung:       %d" % len(keiner))
ges = len(treffer_rx) + len(treffer_name)
print("=> nutzbare Abdeckung: %d von %d = %.0f %%" % (ges, len(M), 100 * ges / len(M)))

print("\nBeispiele Namenstreffer:")
for a, b in treffer_name[:8]:
    print("   %-30s == %s" % (a[:30], b))
print("\nBeispiele ohne Treffer (die brauchen Agentenrecherche):")
for n in keiner[:14]:
    print("   %s" % n)

# Welche Beziehungen stehen fuer unsere Wirkstoffe zur Verfuegung?
stat = Counter()
for v in M.values():
    if v.get("medrt"):
        for k in byrx[v["medrt"]]:
            stat[k] += 1
print("\nVerfuegbare Beziehungen ueber unsere Wirkstoffe:")
for k, c in stat.most_common():
    print("   %-14s %d Wirkstoffe" % (k, c))

json.dump(M, open("rxcui_map.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("\nrxcui_map.json aktualisiert (Feld 'medrt' ergaenzt)")
