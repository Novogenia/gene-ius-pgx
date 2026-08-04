# -*- coding: utf-8 -*-
"""Was steht wirklich in den MED-RT-Beziehungen? Namensraeume und Codes pruefen."""
import json
import xml.etree.ElementTree as ET
from collections import Counter

F = "Core_MEDRT_2026.07.06_XML.xml"
WANTED = {"may_treat", "may_prevent", "has_MoA", "has_PE", "CI_with", "has_TC", "has_SC"}

rel = {w: [] for w in WANTED}
ns_from, ns_to = Counter(), Counter()
for ev, el in ET.iterparse(F, events=("end",)):
    if el.tag != "association":
        continue
    nm = el.findtext("name")
    if nm in WANTED:
        fn, fc = el.findtext("from_name"), el.findtext("from_code")
        tn, tc = el.findtext("to_name"), el.findtext("to_code")
        ns_from[el.findtext("from_namespace")] += 1
        ns_to[el.findtext("to_namespace")] += 1
        rel[nm].append((fc, fn, tc, tn))
    el.clear()

print("from_namespace:", ns_from.most_common())
print("to_namespace:  ", ns_to.most_common())
for k in WANTED:
    print("  %-12s %6d" % (k, len(rel[k])))

print("\nBeispielzeilen may_treat:")
for r in rel["may_treat"][:4]:
    print("   from %s '%s'  ->  to %s '%s'" % r)

print("\nAspirin:")
for k in ("may_treat", "may_prevent", "has_MoA", "has_PE"):
    z = [r for r in rel[k] if (r[1] or "").lower() == "aspirin"]
    if z:
        print("  %-12s (from_code=%s): %s" % (k, z[0][0], ", ".join(x[3] for x in z[:8])))

print("\nClopidogrel:")
for k in ("may_treat", "may_prevent", "has_MoA", "has_PE"):
    z = [r for r in rel[k] if (r[1] or "").lower() == "clopidogrel"]
    print("  %-12s %d: %s" % (k, len(z), ", ".join(x[3] for x in z[:6])))

# Rueckwaerts: wer verhindert dasselbe wie Clopidogrel?
ziel = {r[2] for r in rel["may_prevent"] if (r[1] or "").lower() == "clopidogrel"}
gleiche = sorted({r[1] for r in rel["may_prevent"] if r[2] in ziel})
print("\nWirkstoffe mit denselben may_prevent-Zielen wie Clopidogrel (%d):" % len(gleiche))
print("  ", ", ".join(gleiche[:25]))

json.dump({k: v for k, v in rel.items()}, open("medrt_rel.json", "w", encoding="utf-8"),
          ensure_ascii=False)
print("\ngeschrieben: medrt_rel.json")
