# -*- coding: utf-8 -*-
"""
Wechselwirkungen am Telefon: Linien raus, antippbare Zeile rein.

Vorgabe Daniel, 2026-08-08, mit Screenshot: "schau mal, das funktioniert am
handy noch nicht".

WAS AUF DEM BILD ZU SEHEN WAR: rote Balken, die rechts aus den Karten
herausragen und am Bildrand abgeschnitten sind. Das ist die
Interaktionsebene #wsvg. Sie zeichnet Verbindungslinien zwischen zwei
Kartenmitten und legt den runden Knopf in den rechten Randstreifen - eine
Konstruktion, die eine zweispaltige Arbeitsflaeche mit 79px Rand
voraussetzt. Einspaltig auf dem Telefon gibt es weder das eine noch das
andere: die Linien laufen ins Leere, der Knopf liegt ausserhalb des Bildes.
Damit war die Wechselwirkung am Telefon nicht nur haesslich, sondern gar
nicht mehr aufrufbar.

LOESUNG: unter 820px wird die SVG-Ebene ausgeblendet und jede betroffene
Karte bekommt darunter eine eigene Zeile - Blitzsymbol, Partnername,
Antippen oeffnet dasselbe Fenster wie der runde Knopf am Desktop.

  [!] Wechselwirkung mit Omeprazol                    >

Geloeste Wechselwirkungen erscheinen dort ebenfalls, aber grau und mit
Haken - dieselbe Unterscheidung wie bei der Linie (v72).

Die Zeile steht bewusst nur am Telefon. Am Desktop bleibt die Linie: sie
zeigt, WELCHE zwei Karten zusammenhaengen, und das kann eine Textzeile nicht
leisten.

DAZU zwei Kleinigkeiten aus demselben Bild:
  - Die Aktionsknoepfe standen als eigener Block unter der Karte und
    rissen sie auseinander. Sie ruecken jetzt direkt an die Karte heran.
  - Die Karten hatten unten 14px Abstand plus den Knopfblock; das ergab
    einen unruhigen Rhythmus. Auf dem Telefon jetzt ein Abstand.
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

# ------------------------------------------------- 1. Die Zeile erzeugen
sub("""function wsActions(id,sev,replaced){""",
    """/* Am Telefon ersetzt diese Zeile die Verbindungslinie: die SVG-Ebene
   braucht zwei Spalten und einen 79px-Randstreifen, beides gibt es dort
   nicht. Antippen oeffnet dasselbe Fenster wie der runde Knopf am Desktop. */
function wsIxRows(id){
  const dd=ddisFor(id,workspace);
  if(!dd.length)return '';
  return `<div class="wsix">${dd.map(x=>{
    const other=DRUGS[x.a===id?x.b:x.a];
    const g=ixGeloest(x);
    return `<button class="wsix-r ${g?'done':x.sev}" onclick="event.stopPropagation();openIx('${x.a}','${x.b}')">
      ${ico(g?'s-check':'c-ix','',16)}
      <span class="wsix-t">${g?'Gel&ouml;st':'Wechselwirkung'} mit <b>${other.name}</b></span>
      ${ico('chev','wsix-c',15)}</button>`;}).join('')}</div>`;
}
function wsActions(id,sev,replaced){""",
    "Interaktionszeile fuer das Telefon", wo="script")

# ------------------------------------------------- 2. In beide Kartenformen
sub("""      ${wsActions(id,sev,true)}
    </div>`;""",
    """      ${wsActions(id,sev,true)}
      ${wsIxRows(id)}
    </div>`;""",
    "Austauschkarte: Interaktionszeile", wo="script")

sub("""  return `<div class="wrow" data-row="${id}">${cardHtml(id,'ws',{sevPool:workspace})}${wsActions(id,sev,false)}</div>`;""",
    """  return `<div class="wrow" data-row="${id}">${cardHtml(id,'ws',{sevPool:workspace})}${wsActions(id,sev,false)}${wsIxRows(id)}</div>`;""",
    "Normalkarte: Interaktionszeile", wo="script")

# ------------------------------------------------------------------- 3. CSS
sub("""  /* ---------- Tableiste (nur Telefon) ---------- */""",
    """  /* Wechselwirkungszeile - nur am Telefon, dort ersetzt sie die Linie */
  .wsix{display:none}
  .wsix-r{display:flex;align-items:center;gap:9px;width:100%;margin-top:8px;
    padding:11px 12px;min-height:46px;border-radius:12px;cursor:pointer;font:inherit;
    font-size:13.5px;text-align:left;border:1.5px solid var(--crit-ln);
    background:var(--crit-bg);color:var(--crit-t);-webkit-tap-highlight-color:transparent}
  .wsix-r.warn{border-color:var(--warn-ln);background:var(--warn-bg);color:var(--warn-t)}
  .wsix-r.done{border-color:var(--line2);background:var(--panel);color:var(--muted)}
  .wsix-r>svg:first-child{flex:none;width:16px;height:16px}
  .wsix-t{flex:1;min-width:0}
  .wsix-t b{font-weight:800}
  .wsix-c{flex:none;width:15px;height:15px;transform:rotate(-90deg);opacity:.6}
  /* ---------- Tableiste (nur Telefon) ---------- */""",
    "CSS: Interaktionszeile", wo="style")

sub("""    .tabbar{display:flex}""",
    """    .tabbar{display:flex}
    /* Die Verbindungslinien setzen zwei Spalten und einen 79px-Randstreifen
       voraus. Einspaltig laufen sie ins Leere und der runde Knopf liegt
       ausserhalb des Bildes - deshalb hier die Zeile statt der Linie. */
    #wsvg{display:none}
    .wsix{display:block}
    .wsactions{margin:-4px 0 0}
    .wrow{margin-bottom:20px}
    .wrow .card{margin-bottom:0}""",
    "Mobilschale: Linien aus, Zeile an", wo="style")

# Die Modalregeln muessen ans ENDE des Stylesheets. Die Basisregeln von
# .genemodal und .infomodal stehen weiter unten als der Mobilblock; bei
# gleicher Spezifitaet gewinnt die spaetere. Beim ersten Versuch blieb das
# Genmodal deshalb bei 356px, waehrend das frueher definierte ixmodal
# korrekt umsprang.
sub("""</style>""",
    """
  /* ---------- Modale am Telefon: Bottom-Sheets -----------------------
     Steht bewusst am Ende des Stylesheets: die Basisregeln von .genemodal
     und .infomodal kommen weiter oben nach dem Mobilblock, und bei gleicher
     Spezifitaet gewinnt die spaetere Regel.
     Aus dem unteren Rand herein, volle Breite, in Daumenreichweite. Zweiter
     Grund fuer den Umbau: die bisherige Breite haengt an 94vw, und vw loest
     in eingebetteten Ansichten nicht immer auf - gemessen kamen alle vier
     Fenster auf 0px. Mit left/right/bottom statt Breite plus Mittenversatz
     kann das nicht mehr passieren. */
  @media(max-width:820px){
    .ixmodal,.genemodal,.altpick,.infomodal{
      left:0;right:0;top:auto;bottom:0;width:auto;max-width:none;
      max-height:88vh;border-radius:22px 22px 0 0;
      transform:translateY(18px) scale(1)}
    .ixmodal.open,.genemodal.open,.altpick.open,.infomodal.open{
      transform:translateY(0) scale(1)}
    .ixmodal .ix-b,.genemodal .gm-b,.altpick .ap-b,.infomodal .if-b{
      padding-bottom:calc(22px + env(safe-area-inset-bottom,0px))}
    .ix-h{padding:16px}
  }
</style>""",
    # wo=None mit Absicht: der Anker IST die Bereichsgrenze, nicht etwas
    # darin - die Ortspruefung (si < i < se) kann hier gar nicht zutreffen.
    # Eindeutig ist er trotzdem, </style> kommt genau einmal vor.
    "Modale als Bottom-Sheet ans Stylesheet-Ende")
assert s.count("</style>") == 1, "</style> kommt nicht genau einmal vor"

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
assert s.count("function wsIxRows(") == 1, "wsIxRows nicht genau einmal definiert"
assert s.count("${wsIxRows(id)}") == 2, "Interaktionszeile nicht in beiden Kartenformen"
assert s.count("#wsvg{display:none}") == 1, "SVG-Ebene wird am Telefon nicht ausgeblendet"
assert s.index("function ixGeloest(") < s.index("function wsIxRows("), "ixGeloest steht hinter wsIxRows"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
