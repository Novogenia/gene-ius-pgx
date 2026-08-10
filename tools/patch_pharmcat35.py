# -*- coding: utf-8 -*-
"""
"Auf meine Liste" heisst jetzt "Medikament hinzufuegen".

Vorgabe Daniel, 2026-08-08: "der 'Funktion Medikament hinzufuegen' gibt es
den Button mit einem Herz auf meine Liste. Das sollten wir umschreiben in
'Medikament hinzufuegen'."

Der Knopf im Popup und in der Medikamentliste hiess "Auf meine Liste" - eine
zweite Formulierung fuer dieselbe Handlung, die einen Klick vorher noch
"Medikament hinzufuegen" hiess. Jetzt beide gleich.

Dazu das Symbol: das Herz stammt aus der Zeit, als der Knopf ein Merkzeichen
war. Seit v80 setzt er das Medikament auf die Einnahmeliste, seit v84 traegt
der Knopf, der dieses Popup oeffnet, ein Pluszeichen. Ein Herz daneben
erzaehlt eine andere Geschichte. Also:

  noch nicht auf der Liste  ->  Plus,   "Medikament hinzufuegen"
  schon auf der Liste       ->  Haken,  "Auf deiner Liste"

Der Haken statt des gefuellten Herzens sagt "erledigt" statt "gemerkt", und
der Hinweistext nennt weiterhin, dass ein Klick es wieder entfernt.
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

sub("""function addBtnHtml(id){
  const on=workspace.includes(id);
  /* Am Telefon ein breiter Knopf MIT Text - ein nackter Herzkreis sagt dort
     nicht, dass er das Medikament auf die Liste setzt. Am Desktop bleibt es
     der Kreis, die Beschriftung ist dort ausgeblendet. */
  return `<button class="heartbtn ${on?'on':''}" onclick="toggleWs('${id}',event)"
    aria-pressed="${on}" title="${on?'Auf deiner Liste &mdash; zum Entfernen klicken':'Medikament merken &mdash; auf deine Liste setzen'}">
    ${ico(on?'heart':'hearto','',17)}<span class="hb-l">${on?'Auf deiner Liste':'Auf meine Liste'}</span></button>`;
}""",
    """function addBtnHtml(id){
  const on=workspace.includes(id);
  /* Gleiche Handlung, gleiches Wort: der Knopf, der dieses Popup oeffnet,
     heisst "Medikament hinzufuegen" - dann darf der Knopf, der es dann
     tatsaechlich tut, nicht "Auf meine Liste" heissen. Das Herz stammt aus
     der Zeit, als das hier ein Merkzeichen war; seit v80 setzt es das
     Medikament auf die Einnahmeliste. Plus zum Hinzufuegen, Haken fuer
     erledigt. */
  return `<button class="heartbtn ${on?'on':''}" onclick="toggleWs('${id}',event)"
    aria-pressed="${on}" title="${on?'Auf deiner Liste &mdash; zum Entfernen klicken':'Auf deine Einnahmeliste setzen'}">
    ${ico(on?'s-check':'plus','',17)}<span class="hb-l">${on?'Auf deiner Liste':'Medikament hinzuf&uuml;gen'}</span></button>`;
}""",
    "Knopfbeschriftung und Symbol", wo="script")

# Der Erklaertext in der Medikamentliste nannte den alten Wortlaut.
sub("""      <b>Auf meine Liste</b> nimmst du eines auf &mdash; deine Auswahl steht unter""",
    """      <b>Medikament hinzuf&uuml;gen</b> nimmst du eines auf &mdash; deine Auswahl steht unter""",
    "Erklaertext der Medikamentliste", wo="script")

sub("""      <span style="font-size:13px">In der Medikamentliste suchen und mit
      <b>Auf meine Liste</b> aufnehmen.</span><br>""",
    """      <span style="font-size:13px">Such ein Medikament und nimm es mit
      <b>Medikament hinzuf&uuml;gen</b> auf.</span><br>""",
    "Erklaertext im leeren Zustand", wo="script")

sub("""      <p class="add-h">${workspace.length} auf deiner Liste &mdash; such ein Medikament und
        nimm es mit <b>Auf meine Liste</b> dazu.</p>""",
    """      <p class="add-h">${workspace.length} auf deiner Liste &mdash; such ein Medikament und
        nimm es mit <b>Medikament hinzuf&uuml;gen</b> dazu.</p>""",
    "Erklaertext im Popup", wo="script")

sub("""  /* Knopf "Auf meine Liste" - eine eigene Zeile UNTER der Karte, nicht mehr""",
    """  /* Knopf "Medikament hinzufuegen" - eine eigene Zeile UNTER der Karte, nicht mehr""",
    "Kommentar mit dem alten Wortlaut", wo="style")

# Derselbe Vorgang in der Detailansicht - gleiche Handlung, gleiches Wort und
# gleiches Symbol.
sub("""      ${ico(inWs?'heart':'hearto','',15)} ${inWs?'Auf deiner Medikamentenliste':'Zu deinen Medikamenten'}</button>""",
    """      ${ico(inWs?'s-check':'plus','',15)} ${inWs?'Auf deiner Liste':'Medikament hinzuf&uuml;gen'}</button>""",
    "Detailansicht: gleicher Wortlaut", wo="script")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
# Auf die sichtbaren Stellen pruefen, nicht auf jedes Vorkommen: der
# Kommentar oben zitiert den alten Wortlaut absichtlich.
assert "<b>Auf meine Liste</b>" not in s, "alter Wortlaut steht noch in einem Erklaertext"
assert "'Auf meine Liste'" not in s, "alter Wortlaut steht noch auf dem Knopf"
# Die Symboldefinitionen duerfen stehen bleiben; benutzt werden darf das Herz
# fuer das Hinzufuegen nicht mehr.
assert "ico(on?'heart'" not in s and "ico(inWs?'heart'" not in s, "Herz wird noch benutzt"
assert s.count("Medikament hinzuf&uuml;gen") >= 6, "neuer Wortlaut nicht ueberall"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
