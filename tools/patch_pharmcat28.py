# -*- coding: utf-8 -*-
"""
Telefon: aufklappbare Bereiche unter "Deine Medikamente", Anrede, Menuenamen.

Vorgaben Daniel, 2026-08-08:

  1. "unter Medikamente muessen wir anders vorgehen. Bei der Handdarstellung
     vielleicht eine linke und eine rechte Section, wo jeweils eine der
     beiden aufklappt, wenn man draufklickt: Links ist die Suche der
     Medikamente. Rechts ist das Hinzufuegen der Medikamente."
  2. "Das Ganze vielleicht auch etwas weniger Platz bedarfstechnisch
     designen."
  3. "wir brauchen wahrscheinlich links Medikamente einen Button, der auf
     die Liste gibt."
  4. "Wir sollten auch generell den Nutzer oder die Nutzerin mit 'du'
     ansprechen ... Immer direkt die Person ansprechen. Das ist nicht immer
     der Fall."
  5. "Der Menuepunkt rechts unten 'Datenbank' sollte 'Medikamentliste' sein.
     'Medikamente' sollte 'Deine Medikamente'."

ZU 1: Am Telefon standen beide Spalten untereinander - erst die ganze Suche
mit bis zu 150 Karten, danach irgendwo weit unten die eigene Liste. Jetzt
sind es zwei Bereiche mit Kopfzeile, von denen immer genau einer offen ist.
Voreingestellt ist die eigene Liste; das ist die Ansicht, die man oeffnet,
um nachzusehen, nicht um zu suchen.

Die Struktur bleibt fuer den Desktop unveraendert: die Kopfzeilen sind dort
ausgeblendet, beide Bereiche offen, das dreispaltige Raster mit dem
Ziehpfeil steht wie bisher.

ZU 3: Das Herz war ein 44px-Kreis ohne Beschriftung - am Telefon nicht als
"auf meine Liste" erkennbar. Es wird dort zu einem breiten Knopf mit Text.

ZU 4: Vier Stellen sprachen in der dritten Person ueber die Patientin
("die Medikamente, die Lisa tatsaechlich einnimmt", "Lisa nimmt derzeit",
"bei Lisa gefunden", "die Lisa besprechen moechte"). Alle auf direkte
Anrede umgestellt. Die Ueberschrift der Startseite heisst jetzt
"Lisa, das ist dein Ergebnis" statt "Was die Auswertung ergeben hat".

ZU 5: Die Tableiste bekommt zweizeilige Beschriftungen - "Deine
Medikamente" passt nicht in ein Fuenftel von 390px auf eine Zeile.
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

# ============================================================ 5. Menuenamen
sub("""  {id:"meine",label:"Deine Medikamente",kurz:"Medikamente",ic:"n-pill",badge:"ws",group:"Deine Daten"},""",
    """  {id:"meine",label:"Deine Medikamente",kurz:"Deine<br>Medikamente",ic:"n-pill",badge:"ws",group:"Deine Daten"},""",
    "Tab: Deine Medikamente", wo="script")

sub("""  {id:"liste",label:"Alle Medikamente",kurz:"Datenbank",ic:"n-list",group:"Datenbank"}""",
    """  {id:"liste",label:"Alle Medikamente",kurz:"Medikament-<br>liste",ic:"n-list",group:"Datenbank"}""",
    "Tab: Medikamentliste", wo="script")

sub("""  .tabbar .tab .tb-l{font-size:11px;font-weight:750;letter-spacing:-.01em;
    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%}""",
    """  /* Zweizeilig: "Deine Medikamente" passt nicht in ein Fuenftel von 390px
     auf eine Zeile. 11px ist die Untergrenze der Pruefroutine. */
  .tabbar .tab .tb-l{font-size:11px;font-weight:750;letter-spacing:-.015em;
    line-height:1.12;text-align:center;max-width:100%}""",
    "CSS: zweizeilige Tabbeschriftung", wo="style")

# ==================================================== 4. Direkte Anrede
sub("""    <div><b>Das sind die Medikamente, die ${PATIENT} tats&auml;chlich einnimmt.</b>
      Links suchen und auf das <b>Herz</b> klicken (oder die Karte nach rechts ziehen). Verbundene Karten beeinflussen sich gegenseitig.${ihelp("ix")}</div></div>""",
    """    <div><b>${PATIENT}, das sind die Medikamente, die du tats&auml;chlich einnimmst.</b>
      Such sie links und setz sie mit dem Knopf auf deine Liste. Verbundene Karten beeinflussen sich gegenseitig.${ihelp("ix")}</div></div>""",
    "Anrede: eigene Medikamente", wo="script")

sub("""            <h2>${PATIENT} nimmt derzeit ${workspace.length} Medikamente</h2>""",
    """            <h2>${PATIENT}, du nimmst derzeit ${workspace.length} Medikamente</h2>""",
    "Anrede: Anzahl", wo="script")

sub("""    dann normale, zuletzt ultraschnelle. Die hervorgehobenen Allele wurden bei ${PATIENT} gefunden,""",
    """    dann normale, zuletzt ultraschnelle. Die hervorgehobenen Allele wurden bei dir gefunden,""",
    "Anrede: Allele", wo="script")

sub("""  <p class="dnote">Wirkstoffe, die ${PATIENT} besprechen m&ouml;chte &mdash; unabh&auml;ngig davon,""",
    """  <p class="dnote">Wirkstoffe, die du besprechen m&ouml;chtest &mdash; unabh&auml;ngig davon,""",
    "Anrede: Merkliste", wo="script")

sub("""  <div class="sec-title" style="margin-top:26px">Was die Auswertung ergeben hat</div>""",
    """  <div class="sec-title" style="margin-top:26px">${PATIENT}, das ist dein Ergebnis</div>""",
    "Anrede: Ueberschrift der Startseite", wo="script")

# ================================ 1+2. Aufklappbare Bereiche am Telefon
sub("""let openCards={}, openBoxes={dose:false,gene:false,alt:false}, openGenes={}, altChoice={}, altMenuOpen=null;""",
    """let openCards={}, openBoxes={dose:false,gene:false,alt:false}, openGenes={}, altChoice={}, altMenuOpen=null;
/* Am Telefon ist unter "Deine Medikamente" immer genau einer der beiden
   Bereiche offen. Voreingestellt die eigene Liste - das ist die Ansicht,
   die man oeffnet um nachzusehen, nicht um zu suchen. Am Desktop ohne
   Wirkung, dort sind beide Bereiche offen. */
let meineAuf='liste';
function setMeine(t){meineAuf=t;render();}""",
    "Zustand der aufklappbaren Bereiche", wo="script")

sub("""  <div class="split">
    <div>
      <div class="toolbar">
        <div class="colh">${ico('c-search','',16)} Schritt 1 &mdash; Medikament suchen</div>
        ${toolbarInner()}
      </div>
      <div class="listcount" id="listcount"></div>
      <div class="col-scroll" id="listcol"></div>
    </div>""",
    """  <div class="split">
    <div class="msec ${meineAuf==='suche'?'auf':''}">
      <button class="msec-h" onclick="setMeine('suche')" aria-expanded="${meineAuf==='suche'}">
        ${ico('c-search','',17)}<span class="msec-t">Medikament suchen</span>
        ${ico('chev','msec-c',16)}</button>
      <div class="msec-b">
        <div class="toolbar">
          <div class="colh">${ico('c-search','',16)} Schritt 1 &mdash; Medikament suchen</div>
          ${toolbarInner()}
        </div>
        <div class="listcount" id="listcount"></div>
        <div class="col-scroll" id="listcol"></div>
      </div>
    </div>""",
    "Suchbereich aufklappbar", wo="script")

sub("""    <div class="wsurface" id="ws" ondragover="wsOver(event)" ondragleave="wsLeave(event)" ondrop="wsDrop(event)">""",
    """    <div class="msec ${meineAuf==='liste'?'auf':''}">
    <button class="msec-h" onclick="setMeine('liste')" aria-expanded="${meineAuf==='liste'}">
      ${ico('n-pill','',17)}<span class="msec-t">Deine Liste</span>
      <span class="msec-n">${workspace.length}</span>
      ${ico('chev','msec-c',16)}</button>
    <div class="msec-b">
    <div class="wsurface" id="ws" ondragover="wsOver(event)" ondragleave="wsLeave(event)" ondrop="wsDrop(event)">""",
    "Listenbereich aufklappbar - Anfang", wo="script")

sub("""      ${ixScoreHtml()}
      <div id="wsrows"></div>
    </div>
  </div>`;
}""",
    """      ${ixScoreHtml()}
      <div id="wsrows"></div>
    </div>
    </div></div>
  </div>`;
}""",
    "Listenbereich aufklappbar - Ende", wo="script")

sub("""  /* Wechselwirkungszeile - nur am Telefon, dort ersetzt sie die Linie */""",
    """  /* Aufklappbare Bereiche - Kopfzeilen nur am Telefon sichtbar */
  .msec-h{display:none;align-items:center;gap:10px;width:100%;margin-bottom:12px;
    padding:13px 15px;min-height:52px;border-radius:14px;cursor:pointer;font:inherit;
    font-size:15px;font-weight:800;text-align:left;color:var(--ink);
    background:#fff;border:1.5px solid var(--line2);-webkit-tap-highlight-color:transparent}
  .msec.auf>.msec-h{border-color:var(--plum);color:var(--plum);box-shadow:0 2px 8px rgba(94,0,71,.10)}
  .msec-h>svg:first-child{flex:none;width:17px;height:17px}
  .msec-t{flex:1;min-width:0}
  .msec-n{flex:none;min-width:24px;height:24px;border-radius:999px;background:var(--plum);
    color:#fff;font-size:12px;font-weight:800;line-height:24px;text-align:center;padding:0 7px}
  .msec-c{flex:none;width:16px;height:16px;transition:.18s;opacity:.6}
  .msec.auf .msec-c{transform:rotate(180deg)}
  /* Wechselwirkungszeile - nur am Telefon, dort ersetzt sie die Linie */""",
    "CSS: Kopfzeilen der Bereiche", wo="style")

sub("""    .tabbar{display:flex}""",
    """    .tabbar{display:flex}
    /* Immer genau ein Bereich offen - sonst steht die eigene Liste hinter
       150 Suchtreffern und ist nicht auffindbar. */
    .msec-h{display:flex}
    .msec>.msec-b{display:none}
    .msec.auf>.msec-b{display:block}
    /* Weniger Platzbedarf. Achtung: .scope, .colh und .wsurface werden
       weiter unten im Stylesheet nochmals definiert und wuerden hier
       verlieren - sie stehen deshalb im Schlussblock. */
    .toolbar{padding:0;background:none;border:0;box-shadow:none}
    .col-scroll{max-height:none;overflow:visible;padding-right:0}
    .wstitle{font-size:20px}
    .sec-title{margin-bottom:10px}""",
    "Mobilschale: Bereiche und weniger Platz", wo="style")

# ============================================ 3. Knopf statt nacktem Herz
sub("""function addBtnHtml(id){
  const on=workspace.includes(id);
  return `<button class="heartbtn ${on?'on':''}" onclick="toggleWs('${id}',event)"
    aria-pressed="${on}" title="${on?'Auf deiner Liste &mdash; zum Entfernen klicken':'Medikament merken &mdash; auf deine Liste setzen'}">
    ${ico(on?'heart':'hearto','',17)}</button>`;
}""",
    """function addBtnHtml(id){
  const on=workspace.includes(id);
  /* Am Telefon ein breiter Knopf MIT Text - ein nackter Herzkreis sagt dort
     nicht, dass er das Medikament auf die Liste setzt. Am Desktop bleibt es
     der Kreis, die Beschriftung ist dort ausgeblendet. */
  return `<button class="heartbtn ${on?'on':''}" onclick="toggleWs('${id}',event)"
    aria-pressed="${on}" title="${on?'Auf deiner Liste &mdash; zum Entfernen klicken':'Medikament merken &mdash; auf deine Liste setzen'}">
    ${ico(on?'heart':'hearto','',17)}<span class="hb-l">${on?'Auf deiner Liste':'Auf meine Liste'}</span></button>`;
}""",
    "Hinzufuegeknopf mit Beschriftung", wo="script")

sub("""  .msec-c{flex:none;width:16px;height:16px;transition:.18s;opacity:.6}""",
    """  .msec-c{flex:none;width:16px;height:16px;transition:.18s;opacity:.6}
  .hb-l{display:none}""",
    "CSS: Beschriftung am Desktop aus", wo="style")

sub("""    .heartbtn,.wbtn{width:44px}""",
    """    .wbtn{width:44px}
    .lirow{margin-bottom:16px}
    .lirow .card{margin-bottom:0}""",
    "Mobil: Abstand der Suchtreffer", wo="style")

# Was weiter unten im Stylesheet nochmals definiert wird, muss ans Ende -
# bei gleicher Spezifitaet gewinnt die spaetere Regel. Betroffen und
# gemessen: .heartbtn (blieb 32px breit und absolut), .scope, .colh und
# .wsurface. Derselbe Fehler wie bei den Modalen in v78.
sub("""  @media(max-width:820px){
    .ixmodal,.genemodal,.altpick,.infomodal{""",
    """  @media(max-width:820px){
    /* Aus dem Herzkreis wird ein breiter Knopf mit Text - ein nackter Kreis
       sagt am Telefon nicht, dass er das Medikament auf die Liste setzt. */
    .heartbtn{position:static;width:100%;height:auto;min-height:46px;border-radius:12px;
      display:flex;align-items:center;justify-content:center;gap:9px;margin-top:9px;
      font-size:14px;font-weight:800}
    .hb-l{display:inline}
    /* Platz sparen: Erklaerkasten kleiner, Schrittzeilen weg - die
       Bereichskopfzeilen sagen dasselbe kuerzer -, Arbeitsflaeche ohne
       eigenen Kasten, weil sie am Telefon die ganze Breite ist. */
    .scope{padding:11px 13px;font-size:13px;margin-bottom:14px}
    .colh{display:none}
    .wsurface{padding:0;background:none;box-shadow:none;min-height:0}
    .ixmodal,.genemodal,.altpick,.infomodal{""",
    "Schlussblock: Regeln, die spaeter ueberschrieben wuerden", wo="style")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
assert s.count("function setMeine(") == 1, "setMeine fehlt"
assert s.count('class="msec ') == 2, "nicht beide Bereiche umgebaut"
assert s.count('class="msec-h"') == 2, "nicht beide Kopfzeilen da"
assert s.count("hb-l") == 3, "Beschriftung des Hinzufuegeknopfs unvollstaendig"  # Markup + 2 CSS-Regeln
assert "${PATIENT} tats" not in s, "dritte Person bei den Medikamenten"
assert "${PATIENT} nimmt derzeit" not in s, "dritte Person bei der Anzahl"
assert "bei ${PATIENT} gefunden" not in s, "dritte Person bei den Allelen"
assert "die ${PATIENT} besprechen" not in s, "dritte Person in der Merkliste"
assert s.index("let meineAuf=") < s.index("function setMeine("), "Zustand hinter der Funktion"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
