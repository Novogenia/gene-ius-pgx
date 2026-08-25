# -*- coding: utf-8 -*-
"""
Zwei Mangel aus der Nachmessung von v88.

1. BERUEHRFLAECHE. Die Umschaltflaechen sind am Telefon 32px hoch. Empfohlen
   sind 44px (Apple HIG, Material). Die Kopfleiste ist 60px hoch, also passt
   eine hoehere Flaeche hinein, ohne dass etwas verschoben wird: Knopf auf
   38px, Umschalter damit 46px - bleibt 14px unter der Leistenhoehe.

   38 statt 44, weil die Kopfleiste sonst wachsen muesste. 38px ist der
   groesste Wert, der ohne Umbau der Leiste hineinpasst, und deutlich naeher
   an der Empfehlung als 32.

2. FEHLENDE ENTITY. Im Hinweistext der Genansicht stand "uebrigen" statt
   "&uuml;brigen" - beim Schreiben des Patches vergessen. Die Datei bleibt
   rein ASCII, Umlaute gehoeren als Entity hinein (Regel 2).
"""
import io

APP = "index.html"
s = io.open(APP, encoding="ascii").read()
orig = len(s)
n = 0


def sub(alt, neu, was, anzahl=1, wo=None):
    global s, n
    c = s.count(alt)
    assert c == anzahl, "PATCH '%s': %d erwartet, %d gefunden" % (was, anzahl, c)
    if wo:
        i = s.index(alt)
        si, se = s.index("<style>"), s.index("</style>")
        assert (wo == "style") == (si < i < se), "PATCH '%s': falscher Bereich" % was
    s = s.replace(alt, neu)
    n += 1
    print("  ok  %s" % was)


print("Patche %s (%d Zeichen)" % (APP, orig))

sub("""    .modesw{margin:0;flex:none}
    .msw-b{min-height:30px;padding:0 11px;font-size:12px}""",
    """    .modesw{margin:0;flex:none}
    /* 38px statt 30: die Kopfleiste ist 60px hoch, mehr passt nicht hinein,
       ohne sie umzubauen. Empfohlen waeren 44px - 38 ist der groesste Wert,
       der ohne Umbau hineingeht, und deutlich naeher dran als vorher. */
    .msw-b{min-height:38px;padding:0 11px;font-size:12px}""",
    "Groessere Beruehrflaeche am Telefon", wo="style")

sub("""Die uebrigen
      ${versteckt}""",
    """Die &uuml;brigen
      ${versteckt}""",
    "Fehlende Umlaut-Entity im Hinweistext", wo="script")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
assert "Die uebrigen" not in s, "der Text ohne Entity steht noch da"
assert s.count(".msw-b{min-height:38px") == 1, "Beruehrflaeche nicht gesetzt"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
