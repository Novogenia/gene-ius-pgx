# -*- coding: utf-8 -*-
"""
Entpackt Hristos PharmCAT-3.2.0-Archiv und verschafft einen Ueberblick:
welche Proben, welche Gene bestimmt, wie viele Wirkstoff-Empfehlungen greifen.
"""
import json, os, tarfile
from collections import Counter, defaultdict

SRC = (r"C:\Users\DanielWallerstorfer\Novogenia GmbH\IT - Dokumente\General"
       r"\PharmCAT Validation 20260730\pharmcat-v3.2.0-40-sample-assay-enriched-reports.tar.gz")
ZIEL = "pharmcat40"

if not os.path.isdir(ZIEL):
    print("entpacke ...")
    with tarfile.open(SRC, "r:gz") as t:
        # nur die Auswertungsdateien, nicht die VCFs
        m = [x for x in t.getmembers()
             if x.isfile() and (x.name.endswith(".report.json")
                                or x.name.endswith(".match.json")
                                or x.name.endswith(".phenotype.json")
                                or x.name.endswith(".report.tsv")
                                or x.name.endswith(".outside.tsv")
                                or x.name.endswith("match_warnings.txt"))]
        t.extractall(ZIEL, members=m)
    print("  %d Dateien" % len(m))

wurzel = os.path.join(ZIEL, "outputs")
proben = sorted(os.listdir(wurzel))
print("Proben: %d\n" % len(proben))

def kopf(t): print("\n" + "=" * 92 + "\n" + t + "\n" + "=" * 92)

# ------------------------------------------------ Uebersicht je Probe
kopf("Uebersicht: auffaellige Gene und verwertbare Empfehlungen je Probe")
NORMAL = {"Normal Metabolizer", "Normal Function", "Normal", "Uncertain Susceptibility",
          "Indeterminate", "n/a", "", "No Result"}
zeilen = []
for p in proben:
    fj = os.path.join(wurzel, p, p + ".report.json")
    if not os.path.exists(fj): continue
    j = json.load(open(fj, encoding="utf-8"))
    auff, offen, cyp2d6 = [], 0, ""
    for g, val in j.get("genes", {}).items():
        for r in (val if isinstance(val, list) else [val]):
            dl = r.get("recommendationDiplotypes") or r.get("sourceDiplotypes") or []
            d = dl[0] if dl else {}
            ph = "/".join(d.get("phenotypes") or [])
            if r.get("geneSymbol") == "CYP2D6" or g == "CYP2D6":
                cyp2d6 = (d.get("label") or "") + (" [" + ph + "]" if ph else "")
            if not ph or ph in ("No Result", "n/a"): offen += 1
            elif ph not in NORMAL: auff.append((r.get("geneSymbol") or g) + " " + ph.split()[0])
    # Empfehlungen mit Handlungsbedarf
    stark = 0
    for q, grp in j.get("drugs", {}).items():
        for n, d in grp.items():
            for gl in d.get("guidelines", []):
                for a in gl.get("annotations", []):
                    if a.get("classification") in ("Strong", "Moderate"): stark += 1
    zeilen.append((p, len(auff), offen, stark, cyp2d6, ", ".join(auff[:5])))

zeilen.sort(key=lambda x: (-x[1], -x[3]))
print("%-20s %5s %5s %6s  %-24s %s" % ("PROBE", "auff", "offen", "S/M", "CYP2D6", "auffaellige Gene"))
print("-" * 92)
for z in zeilen:
    print("%-20s %5d %5d %6d  %-24s %s" % z)

# ------------------------------------------------ Gen-Abdeckung ueber die Kohorte
kopf("Wie oft ist ein Gen ueber die 40 Proben bestimmt?")
best, ges = Counter(), Counter()
phenc = defaultdict(Counter)
for p in proben:
    fj = os.path.join(wurzel, p, p + ".report.json")
    if not os.path.exists(fj): continue
    j = json.load(open(fj, encoding="utf-8"))
    for g, val in j.get("genes", {}).items():
        for r in (val if isinstance(val, list) else [val]):
            sym = r.get("geneSymbol") or g
            ges[sym] += 1
            dl = r.get("recommendationDiplotypes") or []
            ph = "/".join((dl[0].get("phenotypes") or []) if dl else [])
            phenc[sym][ph or "(leer)"] += 1
            if ph and ph not in ("No Result", "n/a"): best[sym] += 1
for g in sorted(ges):
    top = ", ".join("%s x%d" % (k, v) for k, v in phenc[g].most_common(4))
    print("%-9s %2d/%2d bestimmt   %s" % (g, best[g], ges[g], top))
