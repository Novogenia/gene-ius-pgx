# -*- coding: utf-8 -*-
"""
Schritt 6: Die drei Datensaetze aus den maschinellen Quellen bauen.

A) alternativen.json  - Rangfolge Wirkmechanismus > Wirkung > Indikation
B) interaktionen.json - additive pharmakodynamische Risiken aus has_PE
C) handelsnamen.json  - aus ClinPGx drugs.tsv (europaeische Marken)

Alles nur fuer Wirkstoffe, die wirklich in MED-RT stehen. Was fehlt, bleibt leer
und wird in der Luecken-Liste ausgewiesen - nicht geraten.
"""
import csv, io, json, re, urllib.request, zipfile
from collections import Counter, defaultdict

csv.field_size_limit(10**7)
UA = {"User-Agent": "Novogenia-PGx-Pipeline/1.0"}
def norm(s): return re.sub(r"\s+", " ", str(s)).strip().lower() if s else ""

M = json.load(open("rxcui_map.json", encoding="utf-8"))
rel = json.load(open("medrt_rel.json", encoding="utf-8"))

# unsere Wirkstoffe, die MED-RT kennt
unsere = {v["medrt"]: k for k, v in M.items() if v.get("medrt")}
print("Wirkstoffe mit MED-RT-Anschluss: %d" % len(unsere))

# Beziehungen indizieren
vor = defaultdict(lambda: defaultdict(set))     # rxcui -> rel -> {ziel}
rueck = defaultdict(lambda: defaultdict(set))   # rel -> ziel -> {rxcui}
name_von = {}
for k, paare in rel.items():
    for fc, fn, tc, tn in paare:
        if not fc or not tc: continue
        vor[fc][k].add(tn)
        rueck[k][tn].add(fc)
        if fn: name_von[fc] = fn

# ============================================ A) Alternativen
print("\n=== A) Alternativen ===")
GEWICHT = [("has_MoA", "gleicher Wirkmechanismus", 3),
           ("has_PE",  "gleiche Wirkung im Koerper", 2),
           ("may_treat", "gleiche Indikation", 1),
           ("may_prevent", "gleiche Vorbeugung", 1)]
alternativen = {}
for rx, key in unsere.items():
    punkte, grund = Counter(), defaultdict(set)
    for r, label, w in GEWICHT:
        for ziel in vor[rx].get(r, ()):
            for partner in rueck[r].get(ziel, ()):
                if partner == rx or partner not in unsere: continue
                punkte[partner] += w
                grund[partner].add(label + ": " + ziel.replace(" [MoA]", "").replace(" [PE]", ""))
    if not punkte: continue
    beste = sorted(punkte.items(), key=lambda x: (-x[1], name_von.get(x[0], "")))[:15]
    alternativen[key] = [{"key": unsere[p], "name": name_von.get(p, ""), "punkte": s,
                          "grund": sorted(grund[p])[:3]} for p, s in beste]
print("Wirkstoffe mit Alternativvorschlaegen: %d" % len(alternativen))
vt = Counter(len(v) for v in alternativen.values())
print("Anzahl Vorschlaege je Wirkstoff:", dict(sorted(vt.items())[:6]), "...")

for probe in ["clopidogrel", "omeprazole", "simvastatin", "citalopram", "aspirin"]:
    if probe in alternativen:
        print("  %-14s -> %s" % (probe,
              ", ".join("%s(%d)" % (a["name"], a["punkte"]) for a in alternativen[probe][:6])))

# ============================================ B) Interaktionen
print("\n=== B) Pharmakodynamische Wechselwirkungen ===")
# Echte MED-RT-Klassennamen, aus 03b ermittelt
RISIKO = {
 "Decreased Coagulation Factor Activity": ("Blutungsrisiko", "crit"),
 "Decreased Platelet Aggregation":        ("Blutungsrisiko", "crit"),
 "Decreased Thromboxane Activity":        ("Blutungsrisiko", "warn"),
 "Increased Coagulation Factor Activity": ("Thromboserisiko", "warn"),
 "Decreased Medullary Respiratory Drive": ("Atemdepression", "crit"),
 "Decreased Central Nervous System Organized Electrical Activity":
                                          ("Daempfung des Nervensystems", "warn"),
 "Increased Central Nervous System GABA Activity":
                                          ("Daempfung des Nervensystems", "warn"),
 "Increased Central Nervous System Serotonin Activity": ("Serotonin-Syndrom", "crit"),
 "Increased Serotonin Activity":          ("Serotonin-Syndrom", "crit"),
 "Decreased Serotonin Degradation":       ("Serotonin-Syndrom", "crit"),
 "Decreased Renal K+ Excretion":          ("Kaliumueberschuss", "crit"),
 "Increased Renal Na+ Excretion":         ("Salz- und Wasserverlust", "warn"),
 "Negative Chronotropy":                  ("verlangsamter Herzschlag", "warn"),
 "Positive Chronotropy":                  ("beschleunigter Herzschlag", "warn"),
 "Increased Insulin Secretion":           ("Unterzuckerung", "crit"),
 "Increased Glucose Transport into Cells":("Unterzuckerung", "warn"),
 "Decreased Immunologic Activity":        ("geschwaechte Immunabwehr", "warn"),
 "Decreased Organized Electrical Activity":("Herzrhythmusstoerung", "crit"),
}
paare = {}
for klasse, (label, sev) in RISIKO.items():
    voll = klasse + " [PE]"
    mitglieder = sorted(m for m in rueck["has_PE"].get(voll, ()) if m in unsere)
    if len(mitglieder) < 2: continue
    n = len(mitglieder)
    print("  %-32s %3d Wirkstoffe -> %5d Paare" % (label[:32], n, n * (n - 1) // 2))
    for i in range(n):
        for j in range(i + 1, n):
            a, b = mitglieder[i], mitglieder[j]
            sig = (a, b)
            alt = paare.get(sig)
            if alt is None or (sev == "crit" and alt["sev"] == "warn"):
                paare[sig] = {"a": unsere[a], "b": unsere[b], "sev": sev,
                              "risiko": label, "klasse": klasse}
print("\nPaare gesamt: %d" % len(paare))
# je Wirkstoff begrenzen, sonst erschlaegt "Blutdruck" alles
prowirk = Counter(); ix = []
for (a, b), v in sorted(paare.items(), key=lambda x: 0 if x[1]["sev"] == "crit" else 1):
    if prowirk[a] >= 15 or prowirk[b] >= 15: continue
    prowirk[a] += 1; prowirk[b] += 1; ix.append(v)
print("nach Begrenzung auf 15 Partner je Wirkstoff: %d" % len(ix))
print("davon kritisch: %d" % sum(1 for v in ix if v["sev"] == "crit"))

# ============================================ C) Handelsnamen
print("\n=== C) Handelsnamen ===")
req = urllib.request.Request("https://api.clinpgx.org/v1/download/file/data/drugs.zip", headers=UA)
with urllib.request.urlopen(req, timeout=180) as r:
    z = zipfile.ZipFile(io.BytesIO(r.read()))
tn = {}
for row in csv.DictReader(io.StringIO(z.read("drugs.tsv").decode("utf-8", "replace")), delimiter="\t"):
    t = (row.get("Trade Names") or "").strip()
    if not t: continue
    marken = [x.strip() for x in t.split(",") if x.strip()]
    for n in [row["Name"]] + [x.strip() for x in (row.get("Generic Names") or "").split(",")]:
        if n: tn.setdefault(norm(n), marken)
handel = {k: tn[k][:8] for k in M if k in tn}
print("Wirkstoffe mit Handelsnamen: %d von %d = %.0f %%"
      % (len(handel), len(M), 100 * len(handel) / len(M)))

json.dump(alternativen, open("alternativen.json", "w", encoding="utf-8"), ensure_ascii=False)
json.dump(ix, open("interaktionen.json", "w", encoding="utf-8"), ensure_ascii=False)
json.dump(handel, open("handelsnamen.json", "w", encoding="utf-8"), ensure_ascii=False)
print("\ngeschrieben: alternativen.json (%d), interaktionen.json (%d), handelsnamen.json (%d)"
      % (len(alternativen), len(ix), len(handel)))
