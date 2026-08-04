# -*- coding: utf-8 -*-
"""
Der Abdeckungs-CSS-Block ist im JavaScript gelandet: der Anker
'/* ================= ERKL' kommt nur EINMAL vor - aber im Skript, nicht im
Stylesheet. Die Zusicherung hat das nicht gemerkt, weil sie nur die Anzahl
prueft, nicht den Ort. Hier wird der Block ausgeschnitten und in <style>
gesetzt.
"""
import io

APP = "pgx_app.html"
s = io.open(APP, encoding="ascii").read()

START = "/* Abdeckungsblock im Arztbericht: was der Test wirklich lesen konnte */\n"
ENDE = "  .cov-tab td .warnpin{color:var(--unk-t);font-weight:800}\n"

i = s.index(START)
j = s.index(ENDE, i) + len(ENDE)
block = s[i:j]
assert ".cov{margin" in block and len(block) < 2000, "Block nicht wie erwartet: %d Zeichen" % len(block)

# 1. aus dem Skript herausnehmen (samt der Leerzeile danach)
rest = s[:i] + s[j:].lstrip("\n")
assert rest.count(".cov{margin") == 0, "Block war mehrfach vorhanden"

# 2. ins Stylesheet setzen, direkt vor der Regel fuer die Hinweiszeile
ANK = "  /* Hinweiszeile auf einer Genkarte, wenn PharmCAT nichts eindeutiges liefert */\n"
assert rest.count(ANK) == 1, "Stylesheet-Anker nicht eindeutig"
rest = rest.replace(ANK, block + ANK)

# 3. Kontrolle: liegt er jetzt im <style>?
si, se = rest.index("<style>"), rest.index("</style>")
bi = rest.index(".cov{margin")
assert si < bi < se, "Block liegt weiterhin nicht im Stylesheet"
assert all(ord(c) < 128 for c in rest), "nicht mehr rein ASCII"

io.open(APP, "w", encoding="ascii", newline="\n").write(rest)
print("verschoben: %d Zeichen CSS aus dem Skript ins Stylesheet" % len(block))
print("Datei: %d -> %d Zeichen" % (len(s), len(rest)))
