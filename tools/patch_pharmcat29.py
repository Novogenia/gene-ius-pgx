# -*- coding: utf-8 -*-
"""
Suche wandert in die Medikamentliste, "Deine Medikamente" wird reine Liste.

Vorgabe Daniel, 2026-08-08: "ich denke, es waere besser, wenn wir die
Medikamentliste mit der Medikamentsuche kombinieren und als separaten
Reiter die eigenen Medikamente machen und eher mit Kennzeichnen und zur
Liste hinzufuegen arbeiten, statt das Ganze links und rechts zu haben und
Drag and Drop zu machen - fuer HTML-Ansicht und auch grosse Ansicht."

Also fuer BEIDE Groessen, nicht nur fuers Telefon.

WAS SICH AENDERT

  Medikamentliste   ist ab jetzt der Ort zum Suchen UND Hinzufuegen. Die
                    Karten haben den Knopf laengst; er bekommt nur eine
                    Beschriftung, damit erkennbar ist, was er tut.
  Deine Medikamente enthaelt nur noch deine Liste. Die Suchspalte, der
                    Ziehpfeil und die zweispaltige Aufteilung entfallen.
  Drag and Drop     entfaellt. Die vier Handler (wsOver, wsLeave, wsDrop,
                    dragStart/dragEnd) und das draggable-Attribut fliegen
                    raus - eine Bedienung, die auf dem Telefon ohnehin nie
                    funktioniert hat und am Desktop eine zweite,
                    unauffindbare Art war, dasselbe zu tun.

Damit entfaellt auch der Aufklapp-Mechanismus aus v79: er loeste das
Nebeneinander von Suche und Liste am Telefon, und dieses Nebeneinander gibt
es nicht mehr. Zustand und Kopfzeilen sind entfernt.

DER LEERE ZUSTAND fuehrt jetzt weiter, statt auf eine Spalte zu verweisen,
die es nicht mehr gibt: ein Knopf, der in die Medikamentliste springt.
Dasselbe steht als Knopf ueber der Liste, damit man von dort aus weiter
Medikamente aufnehmen kann, ohne die Tableiste zu suchen.
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

# ==================================================== 1. vMeine ohne Suche
sub("""function vMeine(){
  return `<div class="sec-title">Deine Medikamente</div>
  <div class="scope scope-me">${ico('n-pill','',18)}
    <div><b>${PATIENT}, das sind die Medikamente, die du tats&auml;chlich einnimmst.</b>
      Such sie links und setz sie mit dem Knopf auf deine Liste. Verbundene Karten beeinflussen sich gegenseitig.${ihelp("ix")}</div></div>
  <div class="split">
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
    </div>
    <div class="dragarrow" aria-hidden="true">
      <div class="daline"></div>
      <div class="dahead">${ico('arr','',26)}</div>
      <div class="datx">Karte hier<br>her&uuml;berziehen<br><span>oder Herz klicken</span></div>
      <div class="daline"></div>
    </div>
    <div class="msec ${meineAuf==='liste'?'auf':''}">
    <button class="msec-h" onclick="setMeine('liste')" aria-expanded="${meineAuf==='liste'}">
      ${ico('n-pill','',17)}<span class="msec-t">Deine Liste</span>
      <span class="msec-n">${workspace.length}</span>
      ${ico('chev','msec-c',16)}</button>
    <div class="msec-b">
    <div class="wsurface" id="ws" ondragover="wsOver(event)" ondragleave="wsLeave(event)" ondrop="wsDrop(event)">
      <svg id="wsvg"></svg>
      <div class="colh">${ico('n-pill','',16)} Schritt 2 &mdash; deine Einnahmeliste</div>
      <h2 class="wstitle">${PATIENT}, das sind <em>deine</em> Medikamente</h2>
      <p class="wssub">${workspace.length} aktiv eingenommene Medikamente &middot; nach Bewertung sortiert</p>
      ${ixScoreHtml()}
      <div id="wsrows"></div>
    </div>
    </div></div>
  </div>`;
}""",
    """function vMeine(){
  /* Nur noch deine Liste. Gesucht und hinzugefuegt wird in der
     Medikamentliste - Vorgabe Daniel, 2026-08-08. Damit entfallen die
     zweispaltige Aufteilung, der Ziehpfeil und Drag and Drop. */
  return `<div class="sec-title">Deine Medikamente</div>
  <div class="scope scope-me">${ico('n-pill','',18)}
    <div><b>${PATIENT}, das sind die Medikamente, die du tats&auml;chlich einnimmst.</b>
      Verbundene Karten beeinflussen sich gegenseitig.${ihelp("ix")}</div></div>
  <div class="wsurface" id="ws">
    <svg id="wsvg"></svg>
    <div class="wshead2">
      <div>
        <h2 class="wstitle">${PATIENT}, das sind <em>deine</em> Medikamente</h2>
        <p class="wssub">${workspace.length} aktiv eingenommene Medikamente &middot; nach Bewertung sortiert</p>
      </div>
      <button class="btn btn-plum addbtn" onclick="go('liste')">
        ${ico('c-search','',16)} Medikament hinzuf&uuml;gen</button>
    </div>
    ${ixScoreHtml()}
    <div id="wsrows"></div>
  </div>`;
}""",
    "vMeine: nur noch die eigene Liste", wo="script")

# ============================================ 2. Medikamentliste als Suchort
sub("""function vListe(){
  return `<div class="sec-title">Alle Medikamente &mdash; Datenbank</div>
  <div class="scope scope-db">${ico('n-list','',18)}
    <div><b>Das ist die Medikamenten-Datenbank</b>, ausgewertet gegen dein Genprofil &mdash;
      <u>nicht</u> die Liste der Medikamente, die du einnimmst.
      Deine eigene Liste findest du unter <a href="javascript:go('meine')">Deine Medikamente</a>.${ihelp("ampel")}</div></div>""",
    """function vListe(){
  return `<div class="sec-title">Medikamentliste</div>
  <div class="scope scope-db">${ico('n-list','',18)}
    <div><b>${PATIENT}, hier suchst du Medikamente und setzt sie auf deine Liste.</b>
      Alle ${DBSTATS().total.toLocaleString('de-DE')} sind gegen dein Genprofil ausgewertet. Mit
      <b>Auf meine Liste</b> nimmst du eines auf &mdash; deine Auswahl steht unter
      <a href="javascript:go('meine')">Deine Medikamente</a>.${ihelp("ampel")}</div></div>""",
    "vListe: Suchen und Hinzufuegen", wo="script")

# ============================================== 3. Drag and Drop entfernen
sub("""      ${ctx==='list'?`draggable="true" ondragstart="dragStart(event,'${id}')" ondragend="dragEnd(event)"`:''}>""",
    """      >""",
    "Karte nicht mehr ziehbar", wo="script")

sub("""let dragId=null;
function dragStart(e,id){dragId=id;e.dataTransfer.setData('text/plain',id);e.dataTransfer.effectAllowed='copy';}
function dragEnd(){dragId=null;}
function wsOver(e){e.preventDefault();e.dataTransfer.dropEffect='copy';document.getElementById('ws').classList.add('hot');}
function wsLeave(e){if(e.currentTarget.contains(e.relatedTarget))return;document.getElementById('ws').classList.remove('hot');}
function wsDrop(e){e.preventDefault();document.getElementById('ws').classList.remove('hot');
  const id=e.dataTransfer.getData('text/plain')||dragId;
  if(id&&DRUGS[id]&&!workspace.includes(id))workspace.push(id);
  render();}""",
    """/* Drag and Drop ist entfallen (Vorgabe Daniel, 2026-08-08): auf dem Telefon
   hat es nie funktioniert, am Desktop war es eine zweite, unauffindbare Art,
   dasselbe zu tun wie der Knopf auf der Karte. */""",
    "Drag-and-Drop-Handler entfernen", wo="script")

# ============================================ 4. Aufklapp-Zustand entfaellt
sub("""/* Am Telefon ist unter "Deine Medikamente" immer genau einer der beiden
   Bereiche offen. Voreingestellt die eigene Liste - das ist die Ansicht,
   die man oeffnet um nachzusehen, nicht um zu suchen. Am Desktop ohne
   Wirkung, dort sind beide Bereiche offen. */
let meineAuf='liste';
function setMeine(t){meineAuf=t;render();}""",
    """/* Der Aufklapp-Mechanismus aus v79 ist entfallen: er loeste das
   Nebeneinander von Suche und eigener Liste am Telefon, und dieses
   Nebeneinander gibt es seit v80 nicht mehr. */""",
    "Aufklapp-Zustand entfernen", wo="script")

# =================================================== 5. Leerer Zustand
sub("""    host.innerHTML=`<div class="ws-empty">Noch nichts auf deiner Liste.<br>
      <span style="font-size:12.5px">Links ein Medikament suchen und auf das <b>Herz</b> klicken &mdash;
      oder die Karte hierher ziehen.</span></div>`;drawLinks();return;}""",
    """    host.innerHTML=`<div class="ws-empty">Noch nichts auf deiner Liste.<br>
      <span style="font-size:13px">In der Medikamentliste suchen und mit
      <b>Auf meine Liste</b> aufnehmen.</span><br>
      <button class="btn btn-plum" style="margin-top:14px"
        onclick="go('liste')">${ico('c-search','',16)} Zur Medikamentliste</button>
      </div>`;drawLinks();return;}""",
    "Leerer Zustand fuehrt weiter", wo="script")

# ====================================================== 6. Beschriftung ueberall
# Die .msec-Regeln des Aufklappers und .hb-l stehen verschachtelt - deshalb
# der ganze Bereich in einem Zug.
sub("""  /* Aufklappbare Bereiche - Kopfzeilen nur am Telefon sichtbar */
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
  .hb-l{display:none}
  .msec.auf .msec-c{transform:rotate(180deg)}""",
    """  /* Der Knopf traegt jetzt ueberall Text - die Medikamentliste ist der Ort
     zum Hinzufuegen, da muss erkennbar sein, was der Knopf tut. */
  .hb-l{display:inline;font-size:12.5px;font-weight:800;letter-spacing:-.01em}""",
    "Aufklapper-CSS raus, Knopfbeschriftung ueberall", wo="style")

sub("""    /* Immer genau ein Bereich offen - sonst steht die eigene Liste hinter
       150 Suchtreffern und ist nicht auffindbar. */
    .msec-h{display:flex}
    .msec>.msec-b{display:none}
    .msec.auf>.msec-b{display:block}
""", "", "Aufklapper-Mobilregeln raus", wo="style")

sub("""  .heartbtn{position:absolute;top:9px;right:9px;z-index:3;width:32px;height:32px;border-radius:50%;""",
    """  .heartbtn{position:absolute;top:9px;right:9px;z-index:3;height:32px;border-radius:999px;
    padding:0 12px;gap:7px;""",
    "Hinzufuegeknopf als Pille", wo="style")

# ================================================== 7. Kopf der eigenen Liste
sub("""  .hb-l{display:inline;font-size:12.5px;font-weight:800;letter-spacing:-.01em}""",
    """  .hb-l{display:inline;font-size:12.5px;font-weight:800;letter-spacing:-.01em}
  /* Kopf der eigenen Liste: Ueberschrift links, Knopf zur Medikamentliste
     rechts - der Weg zum Hinzufuegen muss von hier aus sichtbar sein. */
  .wshead2{display:flex;align-items:flex-start;gap:16px;justify-content:space-between;
    flex-wrap:wrap;margin-bottom:4px}
  .wshead2>div:first-child{min-width:0;flex:1 1 240px}
  .addbtn{flex:none;white-space:nowrap}""",
    "CSS: Kopf der eigenen Liste", wo="style")

# Das zweispaltige Raster und der Ziehpfeil werden nirgends mehr benutzt.
sub("""  .split{display:grid;grid-template-columns:minmax(0,1fr) 92px minmax(0,1fr);gap:14px;align-items:start}
  .dragarrow{position:sticky;top:24px;display:flex;flex-direction:column;align-items:center;gap:8px;padding-top:96px}
  .dragarrow .daline{flex:1;width:2px;min-height:26px;background:linear-gradient(var(--line2),transparent)}
  .dragarrow .dahead{width:48px;height:48px;border-radius:50%;background:var(--plum);color:#fff;
    display:grid;place-items:center;box-shadow:0 8px 20px -8px rgba(94,0,71,.7);animation:danudge 2.4s ease-in-out infinite}
  .dragarrow .dahead svg{color:#fff}
  .dragarrow .datx{font-size:11.5px;font-weight:800;line-height:1.35;text-align:center;color:var(--plum);letter-spacing:.01em}
  .dragarrow .datx span{font-weight:600;color:var(--muted)}
  @keyframes danudge{0%,100%{transform:translateX(-4px)}50%{transform:translateX(4px)}}
  @media(prefers-reduced-motion:reduce){.dragarrow .dahead{animation:none}}
  @media(max-width:1180px){.split{grid-template-columns:minmax(0,1fr)} .dragarrow{display:none}}
""", "", "Raster und Ziehpfeil aus dem Stylesheet", wo="style")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
for weg in ("wsOver", "wsLeave", "wsDrop", "dragStart", "dragEnd", "draggable",
            "meineAuf", "setMeine", "msec-h", "dragarrow"):
    assert weg not in s, "'%s' ist noch im Code" % weg
assert s.count('class="split"') == 0, "die zweispaltige Aufteilung steht noch"
assert s.count('id="ws"') == 1 and s.count('id="wsrows"') == 1, "Arbeitsflaeche beschaedigt"
assert s.count('id="listcol"') == 1, "Liste kommt nur noch einmal vor"
assert s.count("go('liste')") >= 2, "Weg zur Medikamentliste fehlt"
# nf() ist eine lokale Konstante in vDashboard - ausserhalb nicht verfuegbar.
# node --check findet das nicht, es ist ein Laufzeitfehler.
i_l = s.index("function vListe(")
assert "nf(" not in s[i_l:s.index("}", s.index("`;", i_l))], "vListe benutzt nf() ausserhalb seines Gueltigkeitsbereichs"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
