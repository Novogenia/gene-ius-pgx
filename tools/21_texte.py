# -*- coding: utf-8 -*-
"""
Welche Empfehlungstexte liefert PharmCAT fuer NA17454? Grundlage fuer eine
nachvollziehbare Zuordnung auf die Ampel - nicht geraten, sondern am Wortlaut
der Quelle entlang.
"""
import json, os, re
from collections import Counter, defaultdict

P = "NA17454"
j = json.load(open(os.path.join("pharmcat40", "outputs", P, P + ".report.json"), encoding="utf-8"))

ann = []
for q, grp in j["drugs"].items():
    for n, d in grp.items():
        for gl in d.get("guidelines", []):
            for a in gl.get("annotations", []):
                ann.append(dict(n=n, q=d.get("source"), kl=a.get("classification") or "",
                                rec=(a.get("drugRecommendation") or "").strip(),
                                imp=" | ".join(a.get("implications") or []),
                                alt=bool(a.get("alternateDrugAvailable")),
                                dos=bool(a.get("dosingInformation")),
                                oth=bool(a.get("otherPrescribingGuidance"))))
print("Annotationen:", len(ann))
print("Quellen:", dict(Counter(a["q"] for a in ann)))
print("Klassifikation:", dict(Counter(a["kl"] for a in ann)))
print("Flags: alternateDrug %d | dosingInformation %d | otherGuidance %d"
      % (sum(a["alt"] for a in ann), sum(a["dos"] for a in ann), sum(a["oth"] for a in ann)))

print("\n" + "=" * 96)
print("Flag-Kombination x Klassifikation  (alt/dos/oth)")
print("=" * 96)
c = Counter((a["kl"], "%d%d%d" % (a["alt"], a["dos"], a["oth"])) for a in ann)
for (kl, f), v in sorted(c.items(), key=lambda x: -x[1]):
    print("  %-18s %s  %3d" % (kl, f, v))

print("\n" + "=" * 96)
print("Haeufigste Empfehlungstexte (gekuerzt)")
print("=" * 96)
t = Counter(a["rec"][:150] for a in ann if a["rec"])
for txt, v in t.most_common(28):
    print("%3d  %s" % (v, txt))

print("\n" + "=" * 96)
print("Alles mit alternateDrugAvailable - das sind die scharfen Faelle")
print("=" * 96)
for a in sorted([x for x in ann if x["alt"]], key=lambda x: x["n"]):
    print("%-26s %-12s %-10s %s" % (a["n"][:26], a["q"], a["kl"], a["rec"][:110]))

print("\n" + "=" * 96)
print("Beispiele ohne Handlungsbedarf")
print("=" * 96)
for a in [x for x in ann if not x["alt"] and not x["dos"]][:12]:
    print("%-26s %-12s %-18s %s" % (a["n"][:26], a["q"], a["kl"], a["rec"][:100] or "(kein Text)"))
