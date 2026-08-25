# -*- coding: utf-8 -*-
"""
Grundpruefung von index.html - vor jedem Commit.

Holt den GROESSTEN Skriptblock heraus und legt ihn fuer `node --check` ab.
Bewusst der groesste und nicht der erste: es hat schon einen zweiten, winzigen
Vorab-Block gegeben (v88), und der naive Griff nach dem ersten <script> haette
dann 130 Zeichen geprueft statt 770.000.

Aufruf:
    python tools/check_app.py
    node --check %TEMP%\\pgx_check.js

WAS DAS NICHT FINDET: `node --check` prueft nur die Syntax. Ein Aufruf einer
Funktion, die es nicht gibt, oder eine Konstante, die vor ihrer Deklaration
benutzt wird (Fallstrick 5), faellt erst im Browser auf. Nach jeder Aenderung
also zusaetzlich die Seite oeffnen und die Konsole ansehen.
"""
import io
import os
import re
import sys

APP = "index.html"
s = io.open(APP, encoding="ascii").read()

fehler = []

# --- rein ASCII (Regel 2) ---
if not all(ord(c) < 128 for c in s):
    schlimm = [(i, repr(c)) for i, c in enumerate(s) if ord(c) >= 128][:5]
    fehler.append("nicht rein ASCII, erste Stellen: %s" % schlimm)

# --- den groessten Skriptblock finden ---
bloecke = [m.group(1) for m in re.finditer(r"<script>(.*?)</script>", s, re.S)]
if not bloecke:
    fehler.append("kein <script>-Block gefunden")
    bloecke = [""]
gross = max(bloecke, key=len)

ziel = os.path.join(os.environ.get("TEMP", "."), "pgx_check.js")
io.open(ziel, "w", encoding="ascii", newline="\n").write(gross)

print("Datei         : %d Zeichen" % len(s))
print("Skriptbloecke : %d (groesster: %d Zeichen)" % (len(bloecke), len(gross)))
print("Zum Pruefen   : node --check %s" % ziel)

# --- benutzte Symbole muessen definiert sein ---
# Ein ico('...') auf ein Symbol, das es nicht gibt, rendert einen leeren
# Platz - stumm. Genau das ist beim Bau von v88 passiert (ico('info')).
definiert = set(re.findall(r'symbol id="([a-z0-9-]+)"', s))
benutzt = set(re.findall(r"ico\('([a-z0-9-]+)'", s))
fehlend = sorted(benutzt - definiert)
if fehlend:
    fehler.append("ico() zeigt auf Symbole, die es nicht gibt: %s" % ", ".join(fehlend))
print("Symbole       : %d definiert, %d benutzt, %d fehlend"
      % (len(definiert), len(benutzt), len(fehlend)))

if fehler:
    print("\nFEHLER:")
    for f in fehler:
        print("  - %s" % f)
    sys.exit(1)
print("\nIn Ordnung.")
