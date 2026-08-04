# -*- coding: utf-8 -*-
"""
Schritt 3: Taugen MED-RTs physiologische Wirkungen (has_PE) als lizenzfreier Ersatz
fuer die DrugBank-Wechselwirkungen?

Idee: Zwei Wirkstoffe mit derselben riskanten Wirkung addieren diese Wirkung.
Zwei Blutverduenner = Blutungsrisiko. Zwei QT-verlaengernde = Rhythmusrisiko.
Das ist genau die Sorte Wechselwirkung, die DrugBank als "risk or severity of
bleeding can be increased" formuliert - nur mechanistisch hergeleitet statt
aus einer lizenzpflichtigen Tabelle abgeschrieben.
"""
import json
from collections import Counter, defaultdict

rel = json.load(open("medrt_rel.json", encoding="utf-8"))
pe = rel["has_PE"]          # (from_code, from_name, to_code, to_name)
moa = rel["has_MoA"]

print("has_PE-Beziehungen: %d" % len(pe))
klassen = Counter(r[3] for r in pe)
print("verschiedene Wirkungsklassen: %d" % len(klassen))
print("\nDie 30 groessten:")
for n, c in klassen.most_common(30):
    print("   %-58s %4d Wirkstoffe" % (n[:58], c))

# Welche davon sind sicherheitsrelevant, wenn sie sich addieren?
RISIKO = {
    "Decreased Platelet Aggregation": ("Blutungsrisiko", "crit"),
    "Decreased Coagulation Factor Activity": ("Blutungsrisiko", "crit"),
    "Increased Coagulation Factor Activity": ("Thromboserisiko", "warn"),
    "Prolonged QT Interval": ("QT-Verlaengerung am Herzen", "crit"),
    "Decreased Central Nervous System Organized Electrical Activity":
        ("Daempfung des Nervensystems", "warn"),
    "Decreased Respiratory Rate": ("Atemdepression", "crit"),
    "Decreased Blood Pressure": ("zu niedriger Blutdruck", "warn"),
    "Increased Blood Pressure": ("Blutdruckanstieg", "warn"),
    "Decreased Heart Rate": ("verlangsamter Herzschlag", "warn"),
    "Increased Heart Rate": ("beschleunigter Herzschlag", "warn"),
    "Decreased Blood Glucose": ("Unterzuckerung", "crit"),
    "Increased Blood Glucose": ("erhoehter Blutzucker", "warn"),
    "Decreased Potassium Ion Concentration": ("Kaliummangel", "warn"),
    "Increased Potassium Ion Concentration": ("Kaliumueberschuss", "crit"),
    "Decreased Immunologic Activity": ("geschwaechte Immunabwehr", "warn"),
    "Decreased Renal Function": ("Nierenbelastung", "crit"),
    "Increased Serotonin Activity": ("Serotonin-Syndrom", "crit"),
    "Decreased Cholinergic Activity": ("anticholinerge Wirkung", "warn"),
    "Decreased Sympathetic Nervous System Activity": ("Kreislaufdaempfung", "warn"),
    "Decreased Gastric Acid Secretion": ("verminderte Magensaeure", "warn"),
}

print("\n=== Sicherheitsrelevante Klassen - so viele Paare entstehen ===")
gesamt = 0
byklasse = defaultdict(list)
for fc, fn, tc, tn in pe:
    kurz = tn.replace(" [PE]", "").strip()
    if kurz in RISIKO:
        byklasse[kurz].append((fc, fn))
for k, (label, sev) in RISIKO.items():
    n = len(byklasse.get(k, []))
    paare = n * (n - 1) // 2
    gesamt += paare
    if n:
        print("  %-46s %3d Wirkstoffe -> %6d Paare  [%s]" % (label[:46], n, paare, sev))
print("\n  Summe moeglicher Paare: %d" % gesamt)
print("  (wird spaeter auf die Wirkstoffe unserer Liste begrenzt)")

print("\n=== Beispiel: wer teilt 'Decreased Platelet Aggregation'? ===")
z = sorted({fn for fc, fn in byklasse.get("Decreased Platelet Aggregation", [])})
print("  %d Wirkstoffe: %s" % (len(z), ", ".join(z[:22])))

print("\n=== Und die Wirkmechanismen (has_MoA) als engste Alternative ===")
mk = Counter(r[3] for r in moa)
print("  %d verschiedene Mechanismen, die 12 groessten:" % len(mk))
for n, c in mk.most_common(12):
    print("   %-56s %4d" % (n[:56], c))
