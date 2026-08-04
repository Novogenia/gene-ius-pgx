# -*- coding: utf-8 -*-
"""Die echten Namen der sicherheitsrelevanten Wirkungsklassen finden."""
import json, re
from collections import Counter

rel = json.load(open("medrt_rel.json", encoding="utf-8"))
pe = Counter(r[3].replace(" [PE]", "") for r in rel["has_PE"])
moa = Counter(r[3].replace(" [MoA]", "") for r in rel["has_MoA"])

suche = {
    "QT / Herzrhythmus": r"qt|repolariz|arrhythm|electrical activity|chronotrop",
    "Blutung / Gerinnung": r"platelet|coagulat|fibrinol|thromb|hemorrh|bleed",
    "Atmung": r"respirat|ventilat",
    "Nervensystem gedaempft": r"central nervous|sedat|consciousness|somnolen",
    "Serotonin": r"serotonin",
    "Anticholinerg": r"cholinerg",
    "Blutzucker": r"glucose|glycem|insulin secretion",
    "Kalium / Elektrolyte": r"potassium|sodium ion|electrolyte|magnesium|calcium ion",
    "Niere": r"renal|glomerul|nephro|urin",
    "Leber": r"hepat|liver",
    "Blutdruck": r"blood pressure|vasodilat|vasoconstrict",
    "Immunsystem": r"immunolog|immune|lymphocyte|neutroph",
    "Knochenmark": r"erythro|leuko|thrombocyt|myelo|hematopo",
    "Krampfschwelle": r"seizure|convuls|epilep",
}

print("=== Passende Wirkungsklassen (has_PE) je Risikothema ===")
for thema, pat in suche.items():
    tr = [(n, c) for n, c in pe.items() if re.search(pat, n, re.I)]
    tr.sort(key=lambda x: -x[1])
    print("\n%s:" % thema)
    if not tr:
        print("   keine")
    for n, c in tr[:7]:
        print("   %-56s %4d" % (n[:56], c))

print("\n\n=== Und in den Wirkmechanismen (has_MoA) ===")
for thema, pat in [("QT / Ionenkanal", r"potassium channel|sodium channel|herg|calcium channel"),
                   ("Serotonin", r"serotonin"),
                   ("Gerinnung", r"platelet|coagul|thromb|vitamin k|factor xa|p2y12"),
                   ("Opioid", r"opioid"),
                   ("Benzodiazepin / GABA", r"gaba|benzodiaz")]:
    tr = [(n, c) for n, c in moa.items() if re.search(pat, n, re.I)]
    tr.sort(key=lambda x: -x[1])
    print("\n%s:" % thema)
    for n, c in tr[:7]:
        print("   %-56s %4d" % (n[:56], c))
