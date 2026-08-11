# -*- coding: utf-8 -*-
"""
"Medikament hinzufuegen" gehoert IN die Karte, nicht darunter.

Vorgabe Daniel, 2026-08-11: "geben wir den button zu medikament hinzufuegen
bitte nicht unter sondern in oder rechts neben die Medikamentkarte"

Seit v82 stand der Knopf als eigene Zeile UNTER der Karte - das loeste zwar
die Ueberlappung, machte aber aus einem Element zwei, die nur durch Naehe
zusammengehoeren. Genau dieselbe Kritik wie bei den Aktionsknoepfen in v83.

Rechts DANEBEN geht nicht ohne die Rasterordnung zu brechen: die Karten
stehen in einem auto-fill-Raster mit 352px Spaltenbreite, ein Knopf daneben
haette die Spalte gesprengt oder die Karte schmal gedrueckt. Also hinein.

Der Knopf ist jetzt eine Fusszeile INNERHALB des Kartenrahmens, durch eine
Trennlinie vom Kopf abgesetzt. Er sitzt ausserhalb von .cbody und bleibt
damit sichtbar, auch wenn die Karte zugeklappt ist - in .cbody waere er erst
nach dem Aufklappen zu sehen gewesen, und dann findet ihn niemand.

Umgesetzt ueber eine Option an cardHtml statt ueber ein zweites Element im
Wrapper: nur so liegt der Knopf wirklich im selben Kasten und erbt dessen
Rundung und Rahmen.
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

# ------------------------------------------- Knopf in die Karte hineinnehmen
sub("""      ${ctx==='detail'?'':`<button class="btn btn-plum btn-wide" onclick="event.stopPropagation();openDetail('${id}')">Mehr Information ${ico('arr','',16)}</button>`}
    </div>
  </div>`;
}""",
    """      ${ctx==='detail'?'':`<button class="btn btn-plum btn-wide" onclick="event.stopPropagation();openDetail('${id}')">Mehr Information ${ico('arr','',16)}</button>`}
    </div>
    ${opts.add?addBtnHtml(id):''}
  </div>`;
}""",
    "cardHtml: Knopf als Fusszeile in der Karte", wo="script")

sub("""function listItemHtml(id,ctx,opts){
  return `<div class="lirow">${cardHtml(id,ctx,opts||{})}${addBtnHtml(id)}</div>`;
}""",
    """function listItemHtml(id,ctx,opts){
  /* Der Knopf wird von cardHtml INNERHALB des Kartenrahmens gesetzt, nicht
     mehr hier daneben - sonst sind es zwei Kaesten, die nur durch Naehe
     zusammengehoeren (Vorgabe Daniel, 2026-08-11). */
  return `<div class="lirow">${cardHtml(id,ctx,Object.assign({add:true},opts||{}))}</div>`;
}""",
    "listItemHtml: Knopf nicht mehr daneben", wo="script")

# ------------------------------------------------------------------- CSS
sub("""  .heartbtn{display:flex;align-items:center;justify-content:center;gap:8px;
    width:100%;min-height:40px;margin:8px 0 14px;border-radius:11px;padding:0 14px;
    border:1.5px solid var(--line2);background:#fff;cursor:pointer;font:inherit;
    color:var(--muted);transition:.14s}
  .heartbtn:hover{border-color:var(--plum);color:var(--plum);background:var(--plum-050)}
  .heartbtn.on{background:var(--plum);border-color:var(--plum);color:#fff}
  .heartbtn svg{flex:none;width:17px;height:17px}""",
    """  /* Fusszeile INNERHALB der Karte: keine eigene Umrandung, nur eine
     Trennlinie nach oben, und unten die Rundung der Karte. Sie steht
     ausserhalb von .cbody und bleibt deshalb auch bei zugeklappter Karte
     sichtbar. */
  .heartbtn{display:flex;align-items:center;justify-content:center;gap:8px;
    width:100%;min-height:42px;margin:0;padding:0 14px;
    border:0;border-top:1px solid var(--line);border-radius:0 0 17px 17px;
    background:transparent;cursor:pointer;font:inherit;font-weight:750;
    color:var(--plum);transition:.14s}
  .heartbtn:hover{background:var(--plum-050)}
  .heartbtn.on{background:var(--ok-bg);color:var(--ok-t);border-top-color:var(--ok-ln)}
  .heartbtn svg{flex:none;width:17px;height:17px}""",
    "CSS: Knopf als Kartenfusszeile", wo="style")

sub("""    .heartbtn{min-height:46px;font-size:14px}""",
    """    .heartbtn{min-height:48px;font-size:14.5px}""",
    "Mobil: groessere Beruehrflaeche", wo="style")

# Der Ausgleichsabstand unter der Karte wird nicht mehr gebraucht.
sub("""    .lirow{margin-bottom:16px}
    .lirow .card{margin-bottom:0}""",
    """    .lirow{margin-bottom:16px}""",
    "Mobil: Randregel der Karte entfernen", wo="style")

sub("""  .lirow{width:var(--cardw);max-width:100%}
  .lirow .card{margin-bottom:0}""",
    """  .lirow{width:var(--cardw);max-width:100%}""",
    "Randregel der Karte entfernen", wo="style")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
assert s.count("${opts.add?addBtnHtml(id):''}") == 1, "Knopf nicht in der Karte"
assert "${cardHtml(id,ctx,opts||{})}${addBtnHtml(id)}" not in s, "Knopf steht noch neben der Karte"
assert s.count("addBtnHtml(id)") == 2, "addBtnHtml wird nicht genau zweimal verwendet"
# Der Knopf muss AUSSERHALB von .cbody stehen, sonst ist er erst nach dem
# Aufklappen sichtbar.
i = s.index("${opts.add?addBtnHtml(id):''}")
davor = s[:i]
assert davor.rstrip().endswith("</div>"), "Knopf steht nicht hinter dem schliessenden .cbody"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
