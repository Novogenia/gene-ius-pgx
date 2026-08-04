# -*- coding: utf-8 -*-
"""
Warum sind CYP2D6, VKORC1, HLA-B nicht rufbar? Fehlende VCF-Positionen zaehlen.
Das ist die einzige Stelle, an der aus dem Befund eine Handlungsanweisung wird.
"""
import json, os
from collections import Counter

D = r"C:\Users\DanielWallerstorfer\Downloads"
def kopf(t): print("\n" + "=" * 74 + "\n" + t + "\n" + "=" * 74)

m = json.load(open(os.path.join(D, "pharmcat.match (1).json"), encoding="utf-8"))
print("PharmCAT-Metadaten:")
for k, v in m["metadata"].items(): print("   %-26s %s" % (k, v))
print("\nVCF-Warnungen:", len(m.get("vcfWarnings") or {}))
for pos, w in list((m.get("vcfWarnings") or {}).items())[:10]:
    print("   %-22s %s" % (pos, (w[0] if isinstance(w, list) else w)[:120]))

kopf("Positionen je Gen: vorhanden vs. fehlend")
print("%-9s %8s %8s %8s  %s" % ("GEN", "gerufen", "fehlend", "Score", "Diplotypen"))
print("-" * 74)
for r in sorted(m["results"], key=lambda x: x["gene"]):
    g = r["gene"]
    md = r.get("matchData") or {}
    fehlend = len(md.get("missingPositions") or [])
    da = len(r.get("variants") or [])
    dl = r.get("diplotypes") or []
    sc = dl[0].get("score") if dl and isinstance(dl[0], dict) else ""
    print("%-9s %8d %8d %8s  %d" % (g, da, fehlend, sc if sc is not None else "", len(dl)))

kopf("CYP2D6 im Detail - welche Positionen fehlen")
c = [r for r in m["results"] if r["gene"] == "CYP2D6"]
if c:
    r = c[0]
    md = r["matchData"]
    mp = md.get("missingPositions") or []
    print("gerufene Positionen: %d | fehlende: %d" % (len(r.get("variants") or []), len(mp)))
    print("phased:", r.get("phased"), "| effectivelyPhased:", md.get("effectivelyPhased"))
    print("\nfehlende rsIDs (erste 40):")
    for p in mp[:40]:
        print("   %-14s %-16s %s" % (p.get("rsid") or "-", p.get("chromosomeHgvsName") or "-",
                                     ",".join(p.get("cpicAlleles") or [])))
    if len(mp) > 40: print("   ... und %d weitere" % (len(mp) - 40))
    print("\nnicht rufbare Haplotypen: %d" % len(r.get("uncallableHaplotypes") or []))
    print("   " + ", ".join((r.get("uncallableHaplotypes") or [])[:30]))

kopf("VKORC1 / HLA-B / CYP4F2 - je eine Position entscheidet")
for gen in ("VKORC1", "HLA-B", "CYP4F2", "ABCG2", "IFNL3"):
    rr = [r for r in m["results"] if r["gene"] == gen]
    if not rr:
        print("%-9s nicht im match.json (wird nur im phenotype.json gefuehrt)" % gen); continue
    r = rr[0]
    mp = (r.get("matchData") or {}).get("missingPositions") or []
    print("%-9s fehlende Positionen: %d" % (gen, len(mp)))
    for p in mp[:6]:
        print("            %-14s %s" % (p.get("rsid") or "-", p.get("chromosomeHgvsName") or "-"))

kopf("Fazit fuer die VCF-Pipeline")
ges = sum(len((r.get("matchData") or {}).get("missingPositions") or []) for r in m["results"])
hab = sum(len(r.get("variants") or []) for r in m["results"])
print("Positionen im VCF vorhanden: %d" % hab)
print("Positionen, die PharmCAT erwartet aber nicht findet: %d" % ges)
print("Abdeckung: %.1f %%" % (100.0 * hab / (hab + ges) if hab + ges else 0))
