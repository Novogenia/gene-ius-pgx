# -*- coding: utf-8 -*-
"""
Erzeugt data/dummy_genotypen.js - ERFUNDENE Genotypen fuer die Positionen,
die PharmCAT nicht liefert.

ACHTUNG - DIESE DATEI ENTHAELT KEINE ECHTEN MESSWERTE.

Bis v66 galt Regel 1 ohne Ausnahme: kein geratener Genotyp. Auf Ansage von
Daniel (2026-08-06) wird sie fuer den Clickdummy ausgesetzt - "Mal einen
Dummy-Genotyp und gehe davon aus, dass du diese in Zukunft ueber als Input
fuer die App bekommst." Die echten 611 PharmCAT-Positionen bleiben unangetastet
und werden NICHT ueberschrieben; die Dummies fuellen nur die Luecke.

Damit die Fiktion nie fuer ein Ergebnis gehalten werden kann:
  - jede erzeugte Position traegt das Feld d=1
  - die App zeigt auf jeder betroffenen Karte "Demo-Genotyp"
  - die Genansicht traegt oben einen Hinweisstreifen
  - diese Datei ist an ihrem Namen erkennbar und wird von resplice/build
    nicht angefasst

WIE DER GENOTYP GEWAEHLT WIRD

Nur Genotypen, die fuer die jeweilige rsID ueberhaupt annotiert sind - ein
Genotyp ausserhalb der Annotationsliste waere doppelt sinnlos. Die Auswahl
ist DETERMINISTISCH ueber einen Hash der rsID, damit derselbe Lauf immer
dasselbe Profil ergibt und Screenshots reproduzierbar bleiben.

Gewichtung ANTEIL_GUENSTIG: so viel Prozent der Positionen bekommen den
guenstigsten annotierten Genotyp, der Rest verteilt sich auf die uebrigen.
Ohne Gewichtung waere praktisch jedes Gen auffaellig - bei rund 480 Genen ein
unbrauchbares Bild. Gemessen an den erzeugten Daten:

    72 %  ->  247 von 482 Genen auffaellig (51 %)
    85 %  ->  206 von 482 Genen auffaellig (43 %)
    92 %  ->  185 von 482 Genen auffaellig (38 %)   <- eingestellt

Gene mit vielen Positionen sammeln fast zwangslaeufig ein unguenstiges
Signal ein, deshalb liegt der Genanteil deutlich ueber dem Positionsanteil.

Ersetzt wird das Ganze, sobald eine echte Roh-VCF vorliegt: dann liefert
30_rs_befunde.py die Positionen aus echten Genotypen und dieser Generator
faellt ersatzlos weg.
"""
import csv, io, json, os, re, hashlib
from collections import defaultdict

D = r"C:\Users\DanielWallerstorfer\Novogenia GmbH\AI RESOURCES - Dokumente\PHARMACOGENETICS"
HIER = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HIER)
PROF = os.path.join(REPO, "data", "pharmcat_profil.js")
OUT = os.path.join(REPO, "data", "dummy_genotypen.js")

R_HOCH, R_NIEDRIG, R_SCHWACH, R_BESSER, R_PK = 1, 2, 3, 4, 5
GUT = (R_NIEDRIG, R_BESSER)        # guenstige Richtungen
SCHLECHT = (R_HOCH, R_SCHWACH)     # unguenstige Richtungen
ANTEIL_GUENSTIG = 92               # Prozent


def esc(t):
    if t is None: return ""
    t = str(t).replace("&", "&amp;")
    return "".join(c if ord(c) < 128 else "&#%d;" % ord(c) for c in t)


def norm(gt):
    t = (gt or "").replace("|", "/").strip()
    if "/" in t: p = [x.strip() for x in t.split("/")]
    elif len(t) == 2 and t.isalpha(): p = [t[0], t[1]]
    else: return None
    if any(not x or not x.isalpha() for x in p): return None
    return tuple(sorted(x.upper() for x in p))


def wuerfel(rs, n):
    """deterministisch aus der rsID - kein random, damit reproduzierbar"""
    h = hashlib.sha256(rs.encode("ascii")).digest()
    return (h[0] << 8 | h[1]) % n


# ------------------------------------------- schon echt bestimmte Positionen
s = io.open(PROF, encoding="ascii").read()
P_GENES = json.loads(re.search(r"^const P_GENES=(.*?);$", s, re.M).group(1))
echt = set()
for g in P_GENES:
    for v in g.get("var", []):
        echt.add(v[0])
print("echte Positionen aus PharmCAT: %d" % len(echt))

# ------------------------------------------------------- Evidenz und Gen
RANG = {"1A": 0, "1B": 1, "2A": 2, "2B": 3, "3": 4, "4": 5}
stufe, gen_von = {}, {}
with io.open(os.path.join(D, "clinical_annotations.tsv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        lv = (r.get("Level of Evidence") or "").strip()
        if lv not in RANG: continue
        gene = (r.get("Gene") or "").strip()
        for rs in re.findall(r"rs\d+", r.get("Variant/Haplotypes") or ""):
            if rs not in stufe or RANG[lv] < RANG[stufe[rs]]:
                stufe[rs] = lv
                if gene: gen_von[rs] = gene

# --------------------------------------------------------- Annotationen
roh = defaultdict(lambda: defaultdict(dict))
gen_csv = {}
with io.open(os.path.join(D, "drug_pharmacogenetics.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        m = re.match(r"^(rs\d+):(.+)$", (r.get("variants") or "").strip())
        if not m: continue
        rs, gt = m.group(1), m.group(2).strip()
        if rs in echt: continue                      # echte Werte bleiben echt
        if not norm(gt): continue
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
        vor = {R_HOCH: 0, R_SCHWACH: 1, R_PK: 2, R_NIEDRIG: 3, R_BESSER: 4}
        alt = roh[rs][gt].get(drug)
        if alt is None or vor[code] < vor[alt]:
            roh[rs][gt][drug] = code
        g = (r.get("genes") or "").split(",")[0].strip()
        if g and rs not in gen_csv: gen_csv[rs] = g

print("annotierte Positionen ohne echten Wert: %d" % len(roh))

# ------------------------------------------------------- Genotyp waehlen
drugs, didx = [], {}
def di(name):
    if name not in didx:
        didx[name] = len(drugs); drugs.append(name)
    return didx[name]

pos = []
for rs, gts in roh.items():
    gen = gen_von.get(rs) or gen_csv.get(rs)
    if not gen or ";" in gen or not stufe.get(rs):
        continue                                   # ohne klares Gen keine Karte
    kand = sorted(gts.keys())
    if not kand: continue
    # guenstigster Kandidat: keiner der Wirkstoffe unguenstig, moeglichst viele guenstig
    def punkte(k):
        w = gts[k].values()
        return (sum(1 for c in w if c in SCHLECHT), -sum(1 for c in w if c in GUT))
    kand.sort(key=punkte)
    guenstig = kand[0]
    w = wuerfel(rs, 100)
    if w < ANTEIL_GUENSTIG or len(kand) == 1:
        gt = guenstig
    else:
        gt = kand[1 + wuerfel(rs + "x", len(kand) - 1)]
    nach = defaultdict(list)
    for drug, code in gts[gt].items():
        nach[code].append(di(drug))
    sig = [[c, sorted(v)] for c, v in sorted(nach.items())]
    pos.append([rs, esc(gen), esc(gt), stufe[rs], sig])

pos.sort(key=lambda p: (RANG.get(p[3], 9), p[1], p[0]))

gene = sorted({p[1] for p in pos})
neg = sum(1 for p in pos if any(c in SCHLECHT for c, _ in p[4]))
gene_neg = sorted({p[1] for p in pos if any(c in SCHLECHT for c, _ in p[4])})
print("erzeugte Demo-Positionen: %d in %d Genen" % (len(pos), len(gene)))
print("  davon mit unguenstigem Signal: %d (in %d Genen)" % (neg, len(gene_neg)))
print("  Wirkstoffe im Register: %d" % len(drugs))
vert = defaultdict(int)
for p in pos: vert[p[3]] += 1
print("  Evidenzstufen: " + ", ".join("%s=%d" % (k, vert[k]) for k in sorted(vert, key=lambda x: RANG[x])))

def j(o): return json.dumps(o, separators=(",", ":"), ensure_ascii=True)

with io.open(OUT, "w", encoding="ascii", newline="\n") as f:
    f.write("/* ============================================================\n")
    f.write("   GENE-IUS PGx - DEMO-GENOTYPEN, KEINE MESSWERTE\n")
    f.write("   Erzeugt von 31_dummy_genotypen.py. Nicht von Hand aendern.\n")
    f.write("\n")
    f.write("   Diese Positionen sind ERFUNDEN. Sie fuellen die Luecke, bis\n")
    f.write("   eine echte Roh-VCF vorliegt. Die %d echten PharmCAT-Positionen\n" % len(echt))
    f.write("   sind NICHT enthalten und werden nicht ueberschrieben.\n")
    f.write("\n")
    f.write("   Auswahl deterministisch aus der rsID, nur aus annotierten\n")
    f.write("   Genotypen, %d %% zugunsten des guenstigsten Kandidaten\n" % ANTEIL_GUENSTIG)
    f.write("   gewichtet. Jede Position traegt d=1.\n")
    f.write("   %d Positionen in %d Genen.\n" % (len(pos), len(gene)))
    f.write("   ============================================================ */\n")
    f.write("const DUMMY_AKTIV=true;\n")
    f.write("const D_DRUGS=%s;\n" % j(drugs))
    f.write("/* [rsID, Gen, Genotyp, Evidenzstufe, [[Richtung,[WirkstoffIndex..]]..]] */\n")
    f.write("const D_POS=%s;\n" % j(pos))

txt = io.open(OUT, encoding="ascii").read()
assert all(ord(c) < 128 for c in txt), "nicht rein ASCII"
print("\ngeschrieben: %s  %.1f kB" % (OUT, os.path.getsize(OUT) / 1024.0))
