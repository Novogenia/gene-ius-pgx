# -*- coding: utf-8 -*-
"""
Schritt 2: MED-RT herunterladen und die Indikationsbeziehungen extrahieren.

MED-RT (Medication Reference Terminology, US Veterans Affairs) ist die Quelle hinter
RxClass. Der Bulk-Download erspart uns 2.694 Einzelabfragen und ist reproduzierbar -
fuer ein Medizinprodukt muss belegbar sein, auf welchem Datenstand eine Aussage beruht.

Relevante Beziehungen:
  may_treat      Wirkstoff behandelt Krankheit
  may_prevent    Wirkstoff beugt Krankheit vor   (bei Clopidogrel die EINZIGE!)
  has_MoA        Wirkmechanismus                 (engste Alternative)
  has_EPC        Established Pharmacologic Class (zweite Ebene)
  CI_with        kontraindiziert bei             (Ausschlussfilter)

Ausgabe: medrt.json
"""
import io, json, os, re, sys, time, urllib.request, zipfile
import xml.etree.ElementTree as ET

UA = {"User-Agent": "Novogenia-PGx-Pipeline/1.0"}
URL = "https://evs.nci.nih.gov/ftp1/MED-RT/Core_MEDRT_XML.zip"
CACHE = "medrt_core.xml"
OUT = "medrt.json"
WANTED = {"may_treat", "may_prevent", "has_MoA", "has_EPC", "CI_with", "has_PE"}

# ------------------------------------------------------------------ laden
if not os.path.exists(CACHE):
    print("lade MED-RT ...")
    req = urllib.request.Request(URL, headers=UA)
    with urllib.request.urlopen(req, timeout=300) as r:
        data = r.read()
    print("  %.2f MB" % (len(data) / 1024 / 1024))
    z = zipfile.ZipFile(io.BytesIO(data))
    print("  Dateien:", z.namelist())
    xmlname = [n for n in z.namelist() if n.lower().endswith(".xml")][0]
    open(CACHE, "wb").write(z.read(xmlname))
    print("  entpackt:", xmlname)
print("XML: %.1f MB" % (os.path.getsize(CACHE) / 1024 / 1024))

# ------------------------------------------------------- Struktur ansehen
print("\nStruktur der ersten Elemente:")
tags = {}
for ev, el in ET.iterparse(CACHE, events=("end",)):
    tags[el.tag] = tags.get(el.tag, 0) + 1
    if sum(tags.values()) > 60000:
        break
    el.clear()
for t, c in sorted(tags.items(), key=lambda x: -x[1])[:12]:
    print("   %-24s %d" % (t, c))

# ------------------------------------------------------------- Konzepte
print("\nlese Konzepte (Name, Code, RxNorm-CUI) ...")
konzept = {}          # code -> {name, ns, rxcui}
n = 0
for ev, el in ET.iterparse(CACHE, events=("end",)):
    if el.tag != "concept":
        continue
    n += 1
    code = el.findtext("code")
    name = el.findtext("name")
    ns = el.findtext("namespace")
    rx = None
    for p in el.findall("property"):
        if (p.findtext("name") or "").upper() in ("RXCUI", "RX_CUI", "RXNORM_CUI"):
            rx = p.findtext("value")
    if code:
        konzept[code] = {"name": name, "ns": ns, "rxcui": rx}
    el.clear()
print("  %d Konzepte" % len(konzept))
ns_stat = {}
for v in konzept.values():
    ns_stat[v["ns"]] = ns_stat.get(v["ns"], 0) + 1
print("  Namensraeume:", sorted(ns_stat.items(), key=lambda x: -x[1])[:8])
print("  davon mit RxNorm-CUI:", sum(1 for v in konzept.values() if v["rxcui"]))

# ---------------------------------------------------------- Beziehungen
print("\nlese Beziehungen ...")
rel = {w: [] for w in WANTED}
alle = {}
for ev, el in ET.iterparse(CACHE, events=("end",)):
    if el.tag != "association":
        continue
    nm = el.findtext("name")
    alle[nm] = alle.get(nm, 0) + 1
    if nm in WANTED:
        rel[nm].append((el.findtext("from_code"), el.findtext("to_code"),
                        el.findtext("from_name"), el.findtext("to_name")))
    el.clear()
print("  Beziehungstypen gesamt:", len(alle))
for k, v in sorted(alle.items(), key=lambda x: -x[1])[:14]:
    print("   %-28s %d" % (k, v))
print("\n  davon uebernommen:")
for k in WANTED:
    print("   %-14s %d" % (k, len(rel[k])))

json.dump({"konzepte": konzept,
           "beziehungen": {k: v for k, v in rel.items()}},
          open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
print("\ngeschrieben: %s (%.1f MB)" % (OUT, os.path.getsize(OUT) / 1024 / 1024))

# ------------------------------------------------------------ Stichprobe
print("\nStichprobe Aspirin:")
asp = [c for c, v in konzept.items() if (v["name"] or "").lower() == "aspirin"]
for c in asp[:2]:
    print("  Konzept %s  ns=%s  rxcui=%s" % (c, konzept[c]["ns"], konzept[c]["rxcui"]))
    for k in ("may_treat", "may_prevent", "has_MoA", "has_EPC"):
        z = [t[3] for t in rel[k] if t[0] == c]
        if z:
            print("    %-12s %s" % (k, ", ".join(z[:7])))
