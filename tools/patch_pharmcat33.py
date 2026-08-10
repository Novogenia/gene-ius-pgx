# -*- coding: utf-8 -*-
"""
Aktionsknoepfe an die Karte anhaengen statt frei darunter schweben zu lassen.

Vorgabe Daniel, 2026-08-08, mit Screenshot: "Platten schweben noch immer
irgendwo verloren umher. Die Button"

Auf dem Bild haengen die beiden Knoepfe - Alternative waehlen und Entfernen -
rechtsbuendig unter jeder Karte, durch eine Luecke von ihr getrennt und ohne
Beschriftung. Sie sehen aus, als gehoerten sie zu nichts.

URSACHE: am Desktop liegen sie absolut RECHTS NEBEN der Karte (right:-44px),
dort ist die Zuordnung ueber die Position eindeutig. Fuer das Telefon hatte
ich sie in v78 nur aus der absoluten Lage geholt und rechtsbuendig unter die
Karte gestellt - eine reine Notloesung, damit sie nicht aus dem Bild ragen.
Zwei nackte Symbolquadrate ohne Bezug und ohne Text.

JETZT: eine Leiste, die direkt an der Karte klebt. Die Karte verliert unten
ihre Rundung, die Leiste bekommt sie - beides zusammen ist optisch ein
Block. Zwei gleich breite Felder mit Symbol UND Text:

    [ Alternative waehlen ] [ Entfernen ]

Bei unauffaelligen Wirkstoffen steht links "Keine Alternative noetig" als
abgeblendetes Feld, wie bisher der abgeblendete Haken.

Die Beschriftungen erscheinen nur am Telefon; am Desktop bleibt die
bewaehrte Anordnung rechts neben der Karte, dort ist kein Platz fuer Text
und die Position erklaert die Zugehoerigkeit.
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

# ------------------------------------------------------- Beschriftungen
sub("""function wsActions(id,sev,replaced){
  const swap=replaced
    ? `<button class="wbtn alt" title="Ersetzung aufheben" onclick="event.stopPropagation();chooseAlt('${id}','')">${ico('swap','',17)}</button>`
    : sev==='ok'
      ? `<button class="wbtn good" title="Unauff&auml;llig &mdash; keine Alternative n&ouml;tig" disabled>${ico('s-check','',17)}</button>`
      : `<button class="wbtn alt" title="Alternative w&auml;hlen" onclick="event.stopPropagation();openAltPick('${id}')">${ico('swap','',17)}</button>`;
  return `<div class="wsactions">${swap}
    <button class="wbtn del" title="Von deiner Liste entfernen" onclick="event.stopPropagation();removeWs('${id}')">${ico('trash','',17)}</button>
  </div>`;
}""",
    """function wsActions(id,sev,replaced){
  /* Die Beschriftungen sieht man nur am Telefon - dort haengt die Leiste
     unter der Karte und braucht Worte. Am Desktop steht sie rechts daneben,
     da erklaert die Position die Zugehoerigkeit und Text passt nicht hin. */
  const L=t=>`<span class="wb-l">${t}</span>`;
  const swap=replaced
    ? `<button class="wbtn alt" title="Ersetzung aufheben" onclick="event.stopPropagation();chooseAlt('${id}','')">${ico('swap','',17)}${L('Ersetzung aufheben')}</button>`
    : sev==='ok'
      ? `<button class="wbtn good" title="Unauff&auml;llig &mdash; keine Alternative n&ouml;tig" disabled>${ico('s-check','',17)}${L('Keine Alternative n&ouml;tig')}</button>`
      : `<button class="wbtn alt" title="Alternative w&auml;hlen" onclick="event.stopPropagation();openAltPick('${id}')">${ico('swap','',17)}${L('Alternative w&auml;hlen')}</button>`;
  return `<div class="wsactions">${swap}
    <button class="wbtn del" title="Von deiner Liste entfernen" onclick="event.stopPropagation();removeWs('${id}')">${ico('trash','',17)}${L('Entfernen')}</button>
  </div>`;
}""",
    "Aktionsknoepfe mit Beschriftung", wo="script")

sub("""  .wbtn{width:38px;height:38px;border-radius:11px;border:1.5px solid var(--line2);background:#fff;display:grid;place-items:center;cursor:pointer;color:var(--muted)}""",
    """  .wbtn{width:38px;height:38px;border-radius:11px;border:1.5px solid var(--line2);background:#fff;
    display:flex;align-items:center;justify-content:center;gap:8px;cursor:pointer;color:var(--muted);font:inherit}
  .wbtn svg{flex:none;width:17px;height:17px}
  .wb-l{display:none}""",
    "Knopf als Flexzeile, Beschriftung am Desktop aus", wo="style")

# ------------------------------------------------- Leiste an der Karte
sub("""    .wsactions{position:static;transform:none;right:auto;top:auto;
      display:flex;flex-direction:row;gap:8px;justify-content:flex-end;
      margin:-6px 0 12px}""",
    """    /* Eine Leiste, die an der Karte klebt: die Karte verliert unten ihre
       Rundung, die Leiste bekommt sie - zusammen ein Block. Vorher hingen
       hier zwei nackte Symbolquadrate rechtsbuendig im Nichts. */
    .wsactions{position:static;transform:none;right:auto;top:auto;
      display:grid;grid-template-columns:1fr 1fr;gap:1.5px;margin:0;
      background:var(--line2);border:1.5px solid var(--line2);border-top:0;
      border-radius:0 0 16px 16px;overflow:hidden}
    .wrow .card{border-bottom-left-radius:0;border-bottom-right-radius:0}
    .wsactions .wbtn{width:auto;height:auto;min-height:46px;border:0;border-radius:0;
      font-size:12.5px;font-weight:750;padding:0 10px}
    .wsactions .wbtn.good{color:var(--ok-t)}
    .wsactions .wbtn.del{color:var(--crit-t)}
    .wb-l{display:inline;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}""",
    "Aktionsleiste an der Karte", wo="style")

sub("""    .wsactions{margin:-4px 0 0}
    .wrow{margin-bottom:20px}
    .wrow .card{margin-bottom:0}""",
    """    .wrow{margin-bottom:20px}
    .wrow .card{margin-bottom:0}""",
    "doppelte Randregel entfernen", wo="style")

sub("""    .wbtn{width:44px}""",
    """""",
    "feste Knopfbreite am Telefon entfernen", wo="style")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
assert s.count('class="wb-l"') == 1, "Beschriftung nicht ueber den Helfer erzeugt"
assert s.count("wb-l{display:none}") == 1, "Beschriftung am Desktop nicht ausgeblendet"
assert "grid-template-columns:1fr 1fr" in s, "Leiste ist nicht zweispaltig"
assert ".wsactions{margin:-4px 0 0}" not in s, "alte Randregel steht noch"
assert s.count(".wbtn{width:44px}") == 0, "feste Knopfbreite steht noch"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
