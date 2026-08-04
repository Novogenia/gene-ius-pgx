# -*- coding: utf-8 -*-
"""Struktur der drei PharmCAT-Ausgaben verstehen, bevor etwas gebaut wird."""
import json, os

D = r"C:\Users\DanielWallerstorfer\Downloads"
F_MATCH = os.path.join(D, "pharmcat.match (1).json")
F_PHENO = os.path.join(D, "pharmcat.phenotype (1).json")
F_REPORT = os.path.join(D, "pharmcat.report (1).tsv")

def kopf(t): print("\n" + "=" * 74 + "\n" + t + "\n" + "=" * 74)

# ---------------------------------------------------------------- phenotype
kopf("phenotype.json - geneReports (23 Gene)")
p = json.load(open(F_PHENO, encoding="utf-8"))
gr = p["geneReports"]

print("Felder eines Gen-Reports (ABCG2):")
for k, v in gr["ABCG2"].items():
    if isinstance(v, list): print("   %-34s Liste[%d]" % (k, len(v)))
    elif isinstance(v, dict): print("   %-34s Objekt %s" % (k, list(v.keys())[:6]))
    else: print("   %-34s %s" % (k, repr(v)[:60]))

kopf("Ein vollstaendig gerufenes Gen: CYP2C19")
print(json.dumps(gr["CYP2C19"], ensure_ascii=False, indent=1)[:3500])

kopf("recommendationDiplotypes + Phaenotyp je Gen")
for g in sorted(gr):
    r = gr[g]
    rd = r.get("recommendationDiplotypes") or []
    sd = r.get("sourceDiplotypes") or []
    def kurz(dl):
        out = []
        for d in dl:
            lab = d.get("label") or "?"
            ph = d.get("phenotypes") or []
            ac = d.get("activityScore")
            out.append("%s | %s%s" % (lab, "/".join(ph) if ph else "-",
                                     "" if ac in (None, "") else " | AS=%s" % ac))
        return " ;; ".join(out) if out else "(leer)"
    print("%-9s called=%-5s src: %s" % (g, r.get("called"), kurz(sd)))
    if rd and kurz(rd) != kurz(sd):
        print("          rec: %s" % kurz(rd))
    rdg = r.get("relatedDrugs") or []
    print("          Wirkstoffe(%d): %s" % (len(rdg), ", ".join(rdg[:10])))

# ---------------------------------------------------------------- report tsv
kopf("report.tsv")
with open(F_REPORT, encoding="utf-8-sig", newline="") as f:
    zeilen = f.read().splitlines()
print("Zeilen:", len(zeilen))
for i, z in enumerate(zeilen[:14]):
    print("  %2d: %s" % (i, z[:250]))
