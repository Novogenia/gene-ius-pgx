# -*- coding: utf-8 -*-
"""
Erzeugt data/rs_befunde.js - Einzelpositionen mit Studienhinweis.

Quelle:
  PHARMACOGENETICS/drug_pharmacogenetics.csv   rsID:Genotyp + Richtung je Wirkstoff
  PHARMACOGENETICS/clinical_annotations.tsv    PharmGKB-Evidenzstufe je rsID
  data/pharmcat_profil.js                      die 611 tatsaechlich gelesenen Positionen

Aufgenommen wird eine Position nur, wenn PharmCAT sie bei dieser Probe
GELESEN hat UND der gerufene Genotyp in der Annotationsliste steht. Alles
andere waere geraten (Regel 1). Von 1.213 annotierten rsIDs bleiben so 119.

RICHTUNGSSEMANTIK - der Fallstrick dieser Datei:
Die Spalten clearance/dosage/efficacy/toxicity sind RELATIVE Vergleiche
innerhalb einer Annotation, keine absoluten Befunde.

    toxicity DECREASED = geringeres Risiko  = gutes Ergebnis
    toxicity INCREASED = hoeheres Risiko    = schlechtes Ergebnis
    efficacy DECREASED = schwaecheres Ansprechen
    efficacy INCREASED = besseres Ansprechen
    clearance/dosage   = veraenderter Abbau, weder gut noch schlecht

Wer "nicht NORMAL = auffaellig" liest, macht aus dem DPYD-Wildtyp
(rs3918290 C/C, toxicity DECREASED) einen Toxizitaetsbefund - ausgerechnet
an der sicherheitskritischsten Position des Panels. Beim ersten Durchlauf
genau so passiert.

Die Richtung gilt JE WIRKSTOFF, nicht je Gen. SLCO1B1 rs4149056 T/T ist die
normale Funktion - die Genkarte sagt das zu Recht - und steht trotzdem bei
Cyclophosphamid als ungueneriges Signal. Deshalb wird nie ein Gen-Verdikt
gebildet, immer nur Position + Wirkstoff.
"""
import csv, io, json, os, re, sys
from collections import defaultdict

D = r"C:\Users\DanielWallerstorfer\Novogenia GmbH\AI RESOURCES - Dokumente\PHARMACOGENETICS"
HIER = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HIER)
PROF = os.path.join(REPO, "data", "pharmcat_profil.js")
OUT = os.path.join(REPO, "data", "rs_befunde.js")

# Richtungscodes - so werden sie in der App verbalisiert
R_HOCH, R_NIEDRIG, R_SCHWACH, R_BESSER, R_PK = 1, 2, 3, 4, 5

def esc(t):
    """nach ASCII mit HTML-Entities, wie ueberall in diesem Projekt"""
    if t is None: return ""
    t = str(t).replace("&", "&amp;")
    out = []
    for c in t:
        o = ord(c)
        if o < 128: out.append(c)
        else: out.append("&#%d;" % o)
    return "".join(out)

# ------------------------------------------------ gelesene Positionen
s = io.open(PROF, encoding="ascii").read()
P_GENES = json.loads(re.search(r"^const P_GENES=(.*?);$", s, re.M).group(1))
gelesen = {}
for g in P_GENES:
    for v in g.get("var", []):
        gelesen[v[0]] = (g["g"], v[1])
print("gelesene Positionen mit rsID: %d" % len(gelesen))

# ------------------------------------------------ Evidenzstufe je rsID
RANG = {"1A": 0, "1B": 1, "2A": 2, "2B": 3, "3": 4, "4": 5}
stufe = {}
with io.open(os.path.join(D, "clinical_annotations.tsv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        lv = (r.get("Level of Evidence") or "").strip()
        if lv not in RANG: continue
        for rs in re.findall(r"rs\d+", r.get("Variant/Haplotypes") or ""):
            if rs not in stufe or RANG[lv] < RANG[stufe[rs]]:
                stufe[rs] = lv

def norm(gt):
    t = (gt or "").replace("|", "/").strip()
    if "/" in t: p = [x.strip() for x in t.split("/")]
    elif len(t) == 2 and t.isalpha(): p = [t[0], t[1]]
    else: return None
    if any(not x or not x.isalpha() for x in p): return None
    return tuple(sorted(x.upper() for x in p))

# ------------------------------------------------ Annotationen einlesen
roh = defaultdict(lambda: defaultdict(dict))   # rs -> genotyp -> wirkstoff -> code
with io.open(os.path.join(D, "drug_pharmacogenetics.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        m = re.match(r"^(rs\d+):(.+)$", (r.get("variants") or "").strip())
        if not m: continue
        rs, gt = m.group(1), m.group(2).strip()
        if rs not in gelesen: continue
        tox = (r.get("toxicity") or "").strip().upper()
        eff = (r.get("efficacy") or "").strip().upper()
        cle = (r.get("clearance") or "").strip().upper()
        dos = (r.get("dosage") or "").strip().upper()
        if   tox == "INCREASED": code = R_HOCH
        elif eff == "DECREASED": code = R_SCHWACH
        elif tox == "DECREASED": code = R_NIEDRIG
        elif eff == "INCREASED": code = R_BESSER
        elif cle not in ("", "NORMAL") or dos not in ("", "NORMAL"): code = R_PK
        else: continue
        drug = (r.get("drug") or "").strip().title()
        if not drug: continue
        # schaerfstes Signal je Wirkstoff behalten
        vor = {R_HOCH: 0, R_SCHWACH: 1, R_PK: 2, R_NIEDRIG: 3, R_BESSER: 4}
        alt = roh[rs][gt].get(drug)
        if alt is None or vor[code] < vor[alt]:
            roh[rs][gt][drug] = code

# ------------------------------------------------ auf den echten Genotyp filtern
drugs, didx = [], {}
def di(name):
    if name not in didx:
        didx[name] = len(drugs); drugs.append(name)
    return didx[name]

pos = []
ohne_stufe = 0
for rs, gts in roh.items():
    gen, gt = gelesen[rs]
    mein = norm(gt)
    if not mein: continue
    treffer = next((k for k in gts if norm(k) == mein), None)
    if not treffer: continue
    lv = stufe.get(rs)
    if not lv:
        ohne_stufe += 1
        continue
    # je Richtungscode die Wirkstoffe sammeln
    nach = defaultdict(list)
    for drug, code in gts[treffer].items():
        nach[code].append(di(drug))
    sig = [[c, sorted(v)] for c, v in sorted(nach.items())]
    pos.append([rs, esc(gen), esc(gt), lv, sig])

pos.sort(key=lambda p: (RANG.get(p[3], 9), p[1], p[0]))
print("Positionen mit belegtem Genotyp und Evidenzstufe: %d" % len(pos))
print("  ohne Evidenzstufe verworfen: %d" % ohne_stufe)
print("  Wirkstoffe im Namensregister: %d" % len(drugs))

vert = defaultdict(int)
for p in pos: vert[p[3]] += 1
print("  Evidenzstufen: " + ", ".join("%s=%d" % (k, vert[k]) for k in sorted(vert, key=lambda x: RANG[x])))
n_hoch = sum(1 for p in pos if any(c in (R_HOCH, R_SCHWACH) for c, _ in p[4]))
print("  davon mit mindestens einem ungueneigen Signal: %d" % n_hoch)
gene = sorted({p[1] for p in pos})
print("  betroffene Gene (%d): %s" % (len(gene), ", ".join(gene)))

# ------------------------------------------------ schreiben
def j(o): return json.dumps(o, separators=(",", ":"), ensure_ascii=True)

with io.open(OUT, "w", encoding="ascii", newline="\n") as f:
    f.write("/* ============================================================\n")
    f.write("   GENE-IUS PGx - Einzelpositionen mit Studienhinweis\n")
    f.write("   Erzeugt von 30_rs_befunde.py. Nicht von Hand aendern.\n")
    f.write("   Quelle: PharmGKB clinical annotations + Novogenia\n")
    f.write("           drug_pharmacogenetics.csv, geschnitten gegen die\n")
    f.write("           tatsaechlich gerufenen Positionen der Probe.\n")
    f.write("   %d Positionen, %d Wirkstoffe.\n" % (len(pos), len(drugs)))
    f.write("   Richtung gilt je Wirkstoff, nie je Gen - siehe Skriptkopf.\n")
    f.write("   ============================================================ */\n")
    f.write("/* Richtungscodes */\n")
    f.write("const R_RICHT={1:[\"h&ouml;heres Risiko\",\"s-up\"],2:[\"geringeres Risiko\",\"s-down\"],")
    f.write("3:[\"schw&auml;cheres Ansprechen\",\"s-down\"],4:[\"besseres Ansprechen\",\"s-up\"],")
    f.write("5:[\"ver&auml;nderter Abbau\",\"s-up\"]};\n")
    f.write("/* PharmGKB-Evidenzstufe -> Punkte von 4 und Klartext */\n")
    f.write("const R_EV={\"1A\":[4,\"Leitlinie oder Beipackzettel\"],\"1B\":[4,\"Mehrfach best&auml;tigt\"],")
    f.write("\"2A\":[3,\"Mehrere Studien\"],\"2B\":[3,\"Mehrere Studien\"],")
    f.write("\"3\":[2,\"Einzelne Studie\"],\"4\":[1,\"Einzelfallbericht\"]};\n")
    f.write("const R_DRUGS=%s;\n" % j(drugs))
    f.write("/* [rsID, Gen, Genotyp, Evidenzstufe, [[Richtung,[WirkstoffIndex..]]..]] */\n")
    f.write("const R_POS=%s;\n" % j(pos))

roh_txt = io.open(OUT, encoding="ascii").read()
assert all(ord(c) < 128 for c in roh_txt), "nicht rein ASCII"
print("\ngeschrieben: %s  %.1f kB" % (OUT, os.path.getsize(OUT) / 1024.0))
