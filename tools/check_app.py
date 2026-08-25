# -*- coding: utf-8 -*-
"""
Grundpruefung von index.html - vor jedem Commit.

Holt den GROSSEN Skriptblock heraus (nicht den ersten besten: es gibt seit
v88 einen winzigen Vorab-Block, der die Ansichtsklasse setzt) und legt ihn
fuer `node --check` ab. Prueft ausserdem ASCII und meldet ein paar Kennzahlen.

Aufruf:  python tools/check_app.py
Danach:  node --check <ausgegebener Pfad>
"""
import io
import os
import re
import sys

APP = "index.html"
s = io.open(APP, encoding="ascii").read()

fehler = []

# --- rein ASCII ---
if not all(ord(c) < 128 for c in s):
    schlimm = [(i, repr(c)) for i, c in enumerate(s) if ord(c) >= 128][:5]
    fehler.append("nicht rein ASCII, erste Stellen: %s" % schlimm)

# --- den groessten Skriptblock finden ---
bloecke = []
for m in re.finditer(r"<script>(.*?)</script>", s, re.S):
    bloecke.append((len(m.group(1)), m.group(1)))
if not bloecke:
    fehler.append("kein <script>-Block gefunden")
    bloecke = [(0, "")]
bloecke.sort()
gross = bloecke[-1][1]

ziel = os.path.join(os.environ.get("TEMP", "."), "pgx_check.js")
io.open(ziel, "w", encoding="ascii", newline="\n").write(gross)

print("Datei      : %d Zeichen" % len(s))
print("Skriptbloecke: %d (groesster: %d Zeichen)" % (len(bloecke), len(gross)))
print("Zum Pruefen: node --check %s" % ziel)

# --- Kennzahlen, die schon Fehler aufgedeckt haben ---
for name, muster in [
    ("Symbol 'info'", 'id="info"'),
    ("x-only-Regel", "body.m-einfach .x-only"),
    ("s-only-Regel", "body.m-experte .s-only"),
    ("Umschalter", 'class="modesw"'),
]:
    print("%-16s: %s" % (name, "ja" if muster in s else "FEHLT"))

if fehler:
    print("\nFEHLER:")
    for f in fehler:
        print("  - %s" % f)
    sys.exit(1)
