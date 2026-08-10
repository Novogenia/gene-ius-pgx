# -*- coding: utf-8 -*-
"""
"Deine Medikamente" wird eine reine Liste, Hinzufuegen laeuft ueber ein Popup.

Vorgabe Daniel, 2026-08-08: "Wenn du auf deine Medikamente klickst, solltest
du eine Auflistung deiner derzeit genommenen Medikamente sehen. Der ganze
Ballast oben: Die Bewertungen und diese Zusatzinfos gehoeren dann unten
dran, aber auf dieser Seite sieht man wirklich nur die eingenommenen
Medikamente mit den Interaktionen und den Warnungen. Wenn ich dann
'Medikament hinzufuegen' sage, dann oeffnet sich ein Popup, das dann die
Medikamentenliste zeigt, wo ich filtern, auswaehlen und hinzufuegen kann."

NEUE REIHENFOLGE auf der Seite:

  1. Ueberschrift, Zahl der Medikamente, Knopf "Medikament hinzufuegen"
  2. die Karten - mit Wechselwirkungen und Warnungen, sonst nichts
  3. darunter erst: Bilanz, Ampel-Legende, Erklaerkasten

Vorher stand die Bilanz zwischen Ueberschrift und Karten und der
Erklaerkasten ganz oben; man scrollte an beidem vorbei, um zu sehen, was man
nimmt.

DAS POPUP nutzt dieselbe Suche und dieselben Filter wie die
Medikamentliste. Damit das ohne zweite Liste geht, waehlt renderList() sein
Ziel nach dem Zustand: ist das Popup offen, rendert es in dessen Behaelter,
sonst in den der Ansicht. Ein zweiter Satz Funktionen fuer Suche und Filter
haette sonst zwangslaeufig auseinandergelebt.

Filter und Suche loesen render() aus, und render() baut nur #main neu - das
Popup liegt ausserhalb und ueberlebt. Sein Inhalt muss aber mitgezeichnet
werden, sonst zeigen die Filterknoepfe darin den alten Zustand. Deshalb ruft
render() am Ende renderAddBody(), wenn das Popup offen ist.
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

# Zustand zu den uebrigen, damit er vor renderList deklariert ist.
sub("""let openCards={}, openBoxes={dose:false,gene:false,alt:false}, openGenes={}, altChoice={}, altMenuOpen=null;""",
    """let openCards={}, openBoxes={dose:false,gene:false,alt:false}, openGenes={}, altChoice={}, altMenuOpen=null;
/* Ist das Popup zum Hinzufuegen offen? Steht hier und nicht bei seinen
   Funktionen, weil renderList() weiter oben im Skript darauf zugreift -
   const/let kennen kein Hoisting (Fallstrick 5). */
let addOpen=false;""",
    "Zustand des Popups", wo="script")

# ==================================================== 1. Das Popup im Markup
sub("""<div class="altpick" id="altpick" role="dialog" aria-modal="true"><div id="apbody"></div></div>""",
    """<div class="altpick" id="altpick" role="dialog" aria-modal="true"><div id="apbody"></div></div>
<div class="addmodal" id="addmodal" role="dialog" aria-modal="true"><div id="addbody"></div></div>""",
    "Popup im Markup", wo="script")

sub("""<div class="scrim" id="scrim" onclick="closeIx();closeAltPick();closeGene();closeInfo()"></div>""",
    """<div class="scrim" id="scrim" onclick="closeIx();closeAltPick();closeGene();closeInfo();closeAdd()"></div>""",
    "Popup schliesst beim Klick daneben", wo="script")

# ================================================== 2. Seite neu ordnen
sub("""  return `<div class="sec-title">Deine Medikamente</div>
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
  </div>`;""",
    """  /* Oben nur die Liste. Bilanz, Legende und Erklaerkasten stehen unter den
     Karten - man oeffnet diese Seite, um zu sehen was man nimmt, nicht um
     Kennzahlen zu lesen. Vorgabe Daniel, 2026-08-08. */
  return `<div class="sec-title">Deine Medikamente</div>
  <div class="wsurface" id="ws">
    <svg id="wsvg"></svg>
    <div class="wshead2">
      <div>
        <h2 class="wstitle">${PATIENT}, das sind <em>deine</em> Medikamente</h2>
        <p class="wssub">${workspace.length} aktiv eingenommene Medikamente &middot; nach Bewertung sortiert</p>
      </div>
      <button class="btn btn-plum addbtn" onclick="openAdd()">
        ${ico('c-search','',16)} Medikament hinzuf&uuml;gen</button>
    </div>
    <div id="wsrows"></div>
  </div>`;""",
    "vMeine: nur die Liste oben", wo="script")

sub("""  host.innerHTML=`<div class="wscols">${sortedWorkspace().map(id=>wsCard(id)).join('')}</div>
    <div class="wslegend">${leg}</div>`;""",
    """  /* Erst die Karten, dann die Auswertung. */
  host.innerHTML=`<div class="wscols">${sortedWorkspace().map(id=>wsCard(id)).join('')}</div>
    ${ixScoreHtml()}
    <div class="wslegend">${leg}</div>
    <div class="scope scope-me" style="margin:18px 0 0">${ico('n-pill','',18)}
      <div><b>${PATIENT}, das sind die Medikamente, die du tats&auml;chlich einnimmst.</b>
        Verbundene Karten beeinflussen sich gegenseitig.${ihelp("ix")}</div></div>`;""",
    "Bilanz und Erklaerkasten unter die Karten", wo="script")

sub("""      <button class="btn btn-plum" style="margin-top:14px"
        onclick="go('liste')">${ico('c-search','',16)} Zur Medikamentliste</button>""",
    """      <button class="btn btn-plum" style="margin-top:14px"
        onclick="openAdd()">${ico('c-search','',16)} Medikament hinzuf&uuml;gen</button>""",
    "Leerer Zustand oeffnet das Popup", wo="script")

# ================================================== 3. Popup-Logik
sub("""function closeAltPick(){altPickId=null;document.getElementById('scrim').classList.remove('open');document.getElementById('altpick').classList.remove('open');}""",
    """function closeAltPick(){altPickId=null;document.getElementById('scrim').classList.remove('open');document.getElementById('altpick').classList.remove('open');}

/* Medikament hinzufuegen: dasselbe Suchen und Filtern wie in der
   Medikamentliste, nur im Popup. renderList() waehlt sein Ziel nach dem
   Zustand addOpen - ein zweiter Satz Funktionen fuer Suche und Filter waere
   zwangslaeufig auseinandergelaufen. addOpen steht weiter oben bei den
   uebrigen Zustaenden, weil renderList frueher im Skript steht (Fallstrick 5). */
function openAdd(){
  addOpen=true;
  document.getElementById('scrim').classList.add('open');
  document.getElementById('addmodal').classList.add('open');
  renderAddBody();
}
function closeAdd(){
  if(!addOpen)return;
  addOpen=false;
  document.getElementById('scrim').classList.remove('open');
  document.getElementById('addmodal').classList.remove('open');
  render();
}
function renderAddBody(){
  const el=document.getElementById('addbody');if(!el)return;
  el.innerHTML=`
    <div class="ix-h">
      <div class="ixic">${ico('n-list','',20)}</div>
      <h2>Medikament hinzuf&uuml;gen</h2>
      <button class="x" onclick="closeAdd()" aria-label="Schlie&szlig;en">${ico('x','',16)}</button>
    </div>
    <div class="add-b">
      <p class="add-h">${workspace.length} auf deiner Liste &mdash; such ein Medikament und
        nimm es mit <b>Auf meine Liste</b> dazu.</p>
      ${toolbarHtml()}
      <div class="listcount" id="addcount"></div>
      <div id="addcol" class="grid3 compact"></div>
    </div>`;
  renderList();
  const inp=document.getElementById('q');
  if(inp){inp.focus();if(q)inp.setSelectionRange(q.length,q.length);}
}""",
    "Popup-Logik", wo="script")

# ---------------------------------------- 4. renderList schreibt ins Popup
sub("""function renderList(){
  const el=document.getElementById('listcol');if(!el)return;""",
    """function renderList(){
  /* Ist das Popup offen, gehoert die Liste dorthin - sonst in die Ansicht. */
  const imPopup=addOpen&&document.getElementById('addcol');
  const el=imPopup?document.getElementById('addcol'):document.getElementById('listcol');
  if(!el)return;""",
    "renderList: Ziel nach Zustand", wo="script")

sub("""  const cnt=document.getElementById('listcount');""",
    """  const cnt=document.getElementById(imPopup?'addcount':'listcount');""",
    "Trefferzahl ins richtige Ziel", wo="script")

# --------------------------------- 5. render zeichnet das Popup mit
sub("""  if(view==='liste'){const inp=document.getElementById('q');if(inp&&q){inp.focus();inp.setSelectionRange(q.length,q.length);}}
}""",
    """  if(view==='liste'){const inp=document.getElementById('q');if(inp&&q){inp.focus();inp.setSelectionRange(q.length,q.length);}}
  /* render() baut nur #main neu; das Popup liegt ausserhalb und ueberlebt.
     Sein Inhalt muss trotzdem mit, sonst zeigen die Filterknoepfe darin den
     alten Zustand. */
  if(addOpen)renderAddBody();
}""",
    "render zeichnet das Popup mit", wo="script")

sub("""document.addEventListener('keydown',e=>{if(e.key==='Escape'){closeIx();closeAltPick();closeGene();closeInfo();}});""",
    """document.addEventListener('keydown',e=>{if(e.key==='Escape'){closeIx();closeAltPick();closeGene();closeInfo();closeAdd();}});""",
    "Escape schliesst das Popup", wo="script")

# ------------------------------------------------------------------- 6. CSS
sub("""  .altpick{position:fixed;left:50%;top:50%;transform:translate(-50%,-46%) scale(.97);width:min(680px,94vw);max-height:90vh;overflow:auto;""",
    """  /* Popup zum Hinzufuegen - breiter als die Alternativenwahl, weil es die
     ganze Medikamentliste mit Filtern zeigt. */
  .addmodal{position:fixed;left:50%;top:50%;transform:translate(-50%,-46%) scale(.97);
    width:min(1080px,94vw);max-height:90vh;overflow:auto;background:#fff;border-radius:22px;
    box-shadow:var(--sh-lg);z-index:90;opacity:0;pointer-events:none;transition:.24s}
  .addmodal.open{opacity:1;pointer-events:auto;transform:translate(-50%,-50%) scale(1)}
  .addmodal .add-b{padding:18px 22px 24px}
  .addmodal .add-h{margin:0 0 14px;font-size:13.5px;color:var(--muted)}
  .altpick{position:fixed;left:50%;top:50%;transform:translate(-50%,-46%) scale(.97);width:min(680px,94vw);max-height:90vh;overflow:auto;""",
    "CSS: Popup", wo="style")

sub("""    .ixmodal,.genemodal,.altpick,.infomodal{
      left:0;right:0;top:auto;bottom:0;width:auto;max-width:none;
      max-height:88vh;border-radius:22px 22px 0 0;
      transform:translateY(18px) scale(1)}""",
    """    /* inset statt einzelner Kanten: die Einzelangaben werden vom Browser
       ohnehin zu inset zusammengefasst, und in dieser Form ist eindeutig,
       dass alle vier Kanten gesetzt sind. Hoehe ueber dvh, damit die
       Adressleiste mobiler Browser nicht hineinragt; vh faellt als
       Rueckfall davor. */
    .ixmodal,.genemodal,.altpick,.infomodal,.addmodal{
      inset:auto 0 0 0;width:auto;max-width:none;
      max-height:88vh;max-height:88dvh;border-radius:22px 22px 0 0;
      transform:translateY(18px) scale(1)}""",
    "Popup am Telefon als Bottom-Sheet", wo="style")

sub("""    .ixmodal.open,.genemodal.open,.altpick.open,.infomodal.open{
      transform:translateY(0) scale(1)}""",
    """    .ixmodal.open,.genemodal.open,.altpick.open,.infomodal.open,.addmodal.open{
      transform:translateY(0) scale(1)}""",
    "Popup am Telefon: offener Zustand", wo="style")

sub("""    .ixmodal .ix-b,.genemodal .gm-b,.altpick .ap-b,.infomodal .if-b{""",
    """    .ixmodal .ix-b,.genemodal .gm-b,.altpick .ap-b,.infomodal .if-b,.addmodal .add-b{""",
    "Popup am Telefon: sicherer Bereich unten", wo="style")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
for name in ("function openAdd(", "function closeAdd(", "function renderAddBody("):
    assert s.count(name) == 1, "%s nicht genau einmal vorhanden" % name
assert s.count('id="addmodal"') == 1 and s.count('id="addbody"') == 1, "Popup fehlt im Markup"
assert s.count("id=\"addcol\"") == 1 and s.count("id=\"addcount\"") == 1, "Behaelter fehlen"
assert "let addOpen=false;" in s, "Zustand fehlt"
assert s.index("let addOpen=false;") < s.index("const imPopup=addOpen"), "addOpen steht hinter der Nutzung"
assert s.count("closeAdd()") >= 4, "Popup wird nicht ueberall geschlossen"
# ixScoreHtml darf nur noch unter den Karten stehen
i_m = s.index("function vMeine(")
assert "ixScoreHtml" not in s[i_m:s.index("function vListe(")], "Bilanz steht noch oben"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
