# -*- coding: utf-8 -*-
"""
Tauscht den PharmCAT-Datenblock in pgx_app.html gegen den aktuell erzeugten aus.
Wird nach jedem Lauf von build_pharmcat.py aufgerufen.
"""
import io, sys

APP = "pgx_app.html"
DATA = "pharmcat_profil.js"
A = "/* ===== BEGIN PHARMCAT PROFIL (erzeugt, nicht von Hand aendern) ===== */\n"
E = "/* ===== END PHARMCAT PROFIL ===== */\n"

s = io.open(APP, encoding="ascii").read()
blk = io.open(DATA, encoding="ascii").read()
i, j = s.index(A), s.index(E)
alt = len(s[i + len(A):j])
s = s[:i + len(A)] + blk + s[j:]
assert all(ord(c) < 128 for c in s)
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("Datenblock getauscht: %d -> %d Zeichen" % (alt, len(blk)))
