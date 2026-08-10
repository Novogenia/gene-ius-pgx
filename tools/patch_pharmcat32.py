# -*- coding: utf-8 -*-
"""
Statuszeile der Karte laeuft in den Aufklapppfeil.

Vorgabe Daniel, 2026-08-08, mit Screenshot: "layout problem und
ueberlappungen". Auf dem Bild laeuft "INTERAKTION" in den Pfeil rechts.

GEMESSEN auf einer 352px-Karte bei 390px Fensterbreite:

  .cstate   271..333   Breite 62
  .sw       261..343   Breite 82     <- 20px breiter als sein Behaelter
  .cchev    335..353

Die Statusspalte hat eine feste Breite:

  .cstate{flex:none;width:62px;...}

Das reichte, solange dort OK, ALARM, ACHTUNG oder OFFEN stand. Seit v75
gibt es INTERAKTION - 82px bei 11px Schrift, auf dem Telefon 12px und
entsprechend mehr. Das Label quillt links ueber die Wirkstoffbezeichnung
und rechts ueber den Pfeil.

  width:62px  ->  min-width:62px, max-width:96px

Damit waechst die Spalte auf den Text, .cmain schrumpft entsprechend (es
hat flex:1 1 auto und min-width:0), und der Pfeil bleibt frei. Die
Obergrenze verhindert, dass ein noch laengeres Wort die Wirkstoffspalte
auffrisst; als zweite Absicherung darf das Label umbrechen.

WARUM MEINE PRUEFUNG DAS NICHT GEFUNDEN HAT: ich habe .sw gegen .cname,
.cbrands und .cstate geprueft, aber nicht gegen .cchev - und die
Ueberlappung mit .cmain war mit 7px Hoehe unter meiner Schwelle von 40px2.
Die Pruefung im Skriptkopf vergleicht jetzt alle Kopfelemente paarweise,
ohne Flaechenschwelle.
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

sub("""  .cstate{flex:none;width:62px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px}""",
    """  /* Keine feste Breite mehr: "INTERAKTION" braucht 82px, "OK" 62px reichten.
     Die Spalte waechst auf den Text, .cmain schrumpft dafuer (flex:1 1 auto,
     min-width:0). Die Obergrenze verhindert, dass ein langes Wort die
     Wirkstoffspalte auffrisst. */
  .cstate{flex:none;min-width:62px;max-width:96px;display:flex;flex-direction:column;
    align-items:center;justify-content:center;gap:4px}""",
    "Statusspalte waechst mit dem Text", wo="style")

sub("""  .cstate .sw{font-size:11px;font-weight:800;letter-spacing:.02em;text-transform:uppercase;text-align:center;line-height:1.1}""",
    """  .cstate .sw{font-size:11px;font-weight:800;letter-spacing:.02em;text-transform:uppercase;
    text-align:center;line-height:1.1;max-width:100%;overflow-wrap:anywhere}""",
    "Statuszeile darf umbrechen", wo="style")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
assert ".cstate{flex:none;width:62px" not in s, "feste Breite steht noch"
assert ".cstate{flex:none;min-width:62px;max-width:96px" in s, "Grenzen fehlen"
assert "overflow-wrap:anywhere" in s, "Umbruch der Statuszeile fehlt"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
