# -*- coding: utf-8 -*-
"""
Ueberlappung im Hinzufuege-Knopf beseitigen.

Vorgabe Daniel, 2026-08-08, mit Screenshot: "ueberlappungen von text".

ZWEI FEHLER IN EINER REGEL, beide aus v80, als der Knopf eine Beschriftung
bekam:

  .heartbtn{position:absolute;top:9px;right:9px;...;height:32px;
    border-radius:999px;padding:0 12px;gap:7px;
    ...display:grid;place-items:center;...;padding:0}

  1. display:grid mit place-items:center legt BEIDE Kinder - das Herzsymbol
     und den Text - in dieselbe Rasterzelle. Sie liegen damit uebereinander.
     Das ist die Ueberlappung auf dem Bild.
  2. Am Ende derselben Regel steht nochmals padding:0 und hebt das
     padding:0 12px davor auf. Der Text hatte also nicht einmal Platz.

Dazu kam, dass der Knopf absolut ueber der Karte liegt (top:9px, right:9px)
und dort ohnehin auf Statuszeile und Aufklapppfeil trifft, sobald er breiter
als die 32px des frueheren Kreises wird.

LOESUNG: der Knopf ist keine Ueberlagerung mehr, sondern eine eigene Zeile
unter der Karte - in allen Groessen gleich. Das war am Telefon seit v79
schon so; jetzt gilt es auch am Desktop. Damit kann er per Konstruktion
nichts mehr verdecken, und die Beschriftung hat Platz.

Die Sonderregel fuer .lirow .cstate (22px Abstand rechts, damit der Kreis
nicht auf der Statuszeile lag) faellt ersatzlos weg - es liegt nichts mehr
darueber.
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

# ------------------------------------------------- Knopf aus der Ueberlagerung
sub("""  /* Herz-Merkbutton in der Karte */
  .lirow{position:relative}
  .heartbtn{position:absolute;top:9px;right:9px;z-index:3;height:32px;border-radius:999px;
    padding:0 12px;gap:7px;
    border:1.5px solid var(--line2);background:#fff;display:grid;place-items:center;cursor:pointer;
    color:var(--faint);transition:.14s;padding:0}
  .heartbtn:hover{border-color:var(--plum);color:var(--plum);transform:scale(1.08)}
  .heartbtn.on{background:var(--plum);border-color:var(--plum);color:#fff}
  .lirow{width:var(--cardw);max-width:100%}
  .lirow .cstate{margin-right:22px}""",
    """  /* Knopf "Auf meine Liste" - eine eigene Zeile UNTER der Karte, nicht mehr
     als Kreis darueber. Als Ueberlagerung traf er Statuszeile und
     Aufklapppfeil, sobald er eine Beschriftung bekam; ausserdem lagen mit
     display:grid und place-items:center Symbol und Text in derselben
     Rasterzelle und damit uebereinander. Beides ist mit einer normalen
     Flex-Zeile im Fluss per Konstruktion ausgeschlossen. */
  .lirow{width:var(--cardw);max-width:100%}
  .lirow .card{margin-bottom:0}
  .heartbtn{display:flex;align-items:center;justify-content:center;gap:8px;
    width:100%;min-height:40px;margin:8px 0 14px;border-radius:11px;padding:0 14px;
    border:1.5px solid var(--line2);background:#fff;cursor:pointer;font:inherit;
    color:var(--muted);transition:.14s}
  .heartbtn:hover{border-color:var(--plum);color:var(--plum);background:var(--plum-050)}
  .heartbtn.on{background:var(--plum);border-color:var(--plum);color:#fff}
  .heartbtn svg{flex:none;width:17px;height:17px}""",
    "Knopf als eigene Zeile unter der Karte", wo="style")

# Die Mobilregel wird dadurch weitgehend ueberfluessig - nur die Groesse bleibt.
sub("""    /* Aus dem Herzkreis wird ein breiter Knopf mit Text - ein nackter Kreis
       sagt am Telefon nicht, dass er das Medikament auf die Liste setzt. */
    .heartbtn{position:static;width:100%;height:auto;min-height:46px;border-radius:12px;
      display:flex;align-items:center;justify-content:center;gap:9px;margin-top:9px;
      font-size:14px;font-weight:800}
    .hb-l{display:inline}""",
    """    /* Der Knopf steht seit v82 in allen Groessen unter der Karte; am Telefon
       nur groesser fuer die Beruehrflaeche. */
    .heartbtn{min-height:46px;font-size:14px}""",
    "Mobilregel auf das Noetige kuerzen", wo="style")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
i = s.index(".heartbtn{")
block = s[i:s.index("}", i)]
assert "position:absolute" not in block, "Knopf liegt noch ueber der Karte"
assert "display:grid" not in block, "Symbol und Text laegen wieder in derselben Zelle"
assert block.count("padding") == 1, "padding steht mehrfach in derselben Regel"
assert ".lirow .cstate" not in s, "Ausgleichsabstand fuer den Kreis steht noch"
assert s.count(".heartbtn{") == 2, "Knopfregel nicht genau zweimal (Basis + Telefon)"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
