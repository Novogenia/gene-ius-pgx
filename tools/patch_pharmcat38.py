# -*- coding: utf-8 -*-
"""
Zwei Ansichten: Einfach und Experte, umschaltbar.

Vorgabe Daniel, 2026-08-25: "Toll waere, wenn wir diese Webseite nun in eine
Simple View und Expert View umwandeln koennten. Also, es sollte einen Toggle
geben. Bei Simple View wollen wir wirklich die Informationen auf das Minimum,
das notwendig ist, herunterbrechen. Bei Expert View gibt es die ganzen
technischen Details."

MECHANIK: eine Klasse am <body> (m-einfach / m-experte) plus zwei
Markierungsklassen an den Bausteinen:

    .x-only   nur in der Expertenansicht
    .s-only   nur in der einfachen Ansicht

Damit gibt es EINEN Renderpfad, nicht zwei. Zwei getrennte Renderfunktionen
waeren bei 4.000 Zeilen die sichere Quelle fuer Ansichten, die auseinander
laufen. Beim Umschalten wird trotzdem neu gerendert, weil einzelne Texte sich
unterscheiden (nicht nur Sichtbarkeit) und weil Zaehler stimmen muessen.

Die beiden Regeln stehen am ENDE des Stylesheets. Frueher platziert verlieren
sie gegen spaetere Grundregeln - das ist in diesem Projekt schon viermal
passiert (Fallstricke: Modale, .heartbtn, .scope, .addbtn).

EINTEILUNG - was in der einfachen Ansicht verschwindet:

  Medikamentenkarte   das Feld "Abbau"/"Aktivierung". Das ist reine Mechanik:
                      es erklaert, WARUM etwas passiert, nicht WAS zu tun ist.
  Genkarte            die Metabolisierer-Skala mit PM/IM/NM/UM, der Block
                      "Deine zwei Genkopien", die Einzelpositionen mit
                      rs-Nummer, Genotyp und Evidenzstufe, der Knopf
                      "Fachdetails fuer den Arzt".
  Genansicht          alle Gene ohne Phaenotyp UND ohne Befund. Aus 488 Karten
                      werden die, die etwas aussagen. Eine Zeile nennt die
                      Zahl der ausgeblendeten.
  Quellenzeile        Referenzgenom, Allel-Definitionen, PharmCAT-Version.

WAS NICHT VERSCHWINDET, obwohl es technisch klingt:

  "Toxizitaet"        wird zu "Risiko" UMBENANNT statt versteckt. Eine Warnung
                      vor erhoehtem Risiko ist sicherheitsrelevant - so etwas
                      blendet man nicht aus, um es einfacher zu machen. Nur
                      Mechanik wird versteckt, nie eine Konsequenz.
  Arztbericht         bleibt in BEIDEN Ansichten vollstaendig technisch. Er ist
                      ausdruecklich fuer den Arzt; dort ist Dichte der Zweck.
                      Die Ansicht steuert, was DU ueber dich siehst, nicht was
                      der Arzt bekommt. In der einfachen Ansicht steht dazu
                      eine erklaerende Zeile.

VOREINSTELLUNG: einfach. Das ist die Verbraucheransicht; die Expertenansicht
ist die bewusste Zuschaltung. Die Wahl liegt im localStorage.
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

# =========================================================== 1. Zustand
# MODE muss vor jedem Rendern stehen - const/let kennen kein Hoisting
# (Fallstrick 5). Deshalb direkt zu den uebrigen Zustandsvariablen.
sub("""let view="dashboard", detailId=null;""",
    """let view="dashboard", detailId=null;
/* Einfach oder Experte. Voreinstellung "einfach": das ist die Ansicht fuer
   Nutzerinnen und Nutzer, die Expertenansicht wird bewusst zugeschaltet. */
let MODE=(function(){try{return localStorage.getItem('ndr-mode')||'einfach';}
  catch(e){return 'einfach';}})();
function istEinfach(){return MODE==='einfach';}
function setMode(m){
  if(m===MODE)return;
  MODE=m;
  try{localStorage.setItem('ndr-mode',m);}catch(e){}
  document.body.className='m-'+m;
  /* Neu rendern statt nur ein-/auszublenden: einzelne Texte unterscheiden
     sich, und die Zaehler ("x Gene ausgewertet") muessen mitwandern. */
  render();
}""",
    "Zustand und Umschalter", wo="script")

# =========================================================== 2. Umschalter
sub("""    <div class="brand"><div class="logo">N</div><div>NOVO<small>Drug Response</small></div></div>
    <div id="rail"></div>""",
    """    <div class="brand"><div class="logo">N</div><div>NOVO<small>Drug Response</small></div></div>
    <div class="modesw" role="group" aria-label="Ansicht">
      <button type="button" class="msw-b" data-m="einfach" onclick="setMode('einfach')">Einfach</button>
      <button type="button" class="msw-b" data-m="experte" onclick="setMode('experte')">Experte</button>
    </div>
    <div id="rail"></div>""",
    "Umschalter in die Kopfleiste")

# =========================================================== 3. CSS
sub("""    .ix-h{padding:16px}
  }
</style>""",
    """    .ix-h{padding:16px}
  }

  /* ============================================================
     EINFACH / EXPERTE
     Diese beiden Regeln stehen bewusst am ENDE des Stylesheets.
     Frueher platziert verlieren sie gegen spaetere Grundregeln -
     in diesem Projekt schon viermal passiert.
     ============================================================ */
  body.m-einfach .x-only{display:none!important}
  body.m-experte .s-only{display:none!important}

  /* Der Umschalter. In der Seitenleiste steht er unter der Marke, am
     Telefon wird die Leiste waagrecht und er rueckt in die Luecke
     zwischen Marke und Patientenblock. */
  .modesw{display:flex;gap:2px;padding:3px;margin:0 6px 14px;border-radius:11px;
    background:rgba(0,0,0,.22);border:1px solid rgba(255,255,255,.13)}
  .msw-b{flex:1;min-height:32px;padding:0 10px;border:0;border-radius:8px;cursor:pointer;
    background:transparent;color:#d8b6cd;font:inherit;font-size:12.5px;font-weight:750;
    letter-spacing:.01em;transition:.14s;-webkit-tap-highlight-color:transparent}
  .msw-b:hover{color:#fff}
  body.m-einfach .msw-b[data-m="einfach"],
  body.m-experte .msw-b[data-m="experte"]{background:#fff;color:var(--plum)}

  /* Hinweiszeile, die nur in der einfachen Ansicht erscheint. */
  .s-hint{display:flex;align-items:flex-start;gap:9px;margin:0 0 16px;padding:11px 13px;
    border:1px solid var(--line);border-radius:12px;background:var(--plum-050);
    color:var(--muted);font-size:12.5px;line-height:1.5}
  .s-hint b{color:var(--ink)}
  .s-hint svg{flex:none;width:16px;height:16px;margin-top:1px;color:var(--plum)}

  @media(max-width:1080px){
    /* Waagrechte Kopfleiste: der Umschalter sitzt zwischen Marke und
       Patientenblock und wird kompakt. */
    .modesw{margin:0;flex:none}
    .msw-b{min-height:30px;padding:0 11px;font-size:12px}
  }
  @media(max-width:430px){
    /* Bei 375px ist zwischen Marke und Patientenblock kein Platz mehr fuer
       zwei Woerter. Der Patientenblock gibt seinen Text ab und behaelt das
       Kuerzel - der Name steht ohnehin gross auf der Startseite. */
    .patient>div:last-child{display:none}
    .msw-b{padding:0 9px;font-size:11.5px}
  }
</style>""",
    "CSS fuer beide Ansichten", wo="style")

# ===================================================== 4. Medikamentenkarte
# Nur metricBoxes anfassen, nicht metrics() - so bleibt die Herleitung der
# Werte an einer Stelle und die Ansicht entscheidet allein ueber die Anzeige.
sub("""function metricBoxes(id){
  return metrics(id).map(m=>`<div class="ibox b-${m.sev}">
    <div class="ic s-${m.sev}">${ico(m.sym)}</div>
    <div class="itx"><div class="il">${m.l}</div><div class="iv t-${m.sev}">${m.v}</div></div>
  </div>`).join('');
}""",
    """function metricBoxes(id){
  return metrics(id).map(m=>{
    /* "Abbau" und "Aktivierung" erklaeren die Mechanik - warum etwas
       passiert, nicht was zu tun ist. Das ist der einzige Wert, der in der
       einfachen Ansicht faellt. */
    const mechanik=(m.l==='Abbau'||m.l==='Aktivierung');
    /* "Toxizitaet" wird umbenannt, NICHT versteckt: ein erhoehtes Risiko ist
       sicherheitsrelevant. Versteckt wird nur Mechanik, nie eine Folge. */
    const lab=(istEinfach()&&m.l==='Toxizit&auml;t')?'Risiko':m.l;
    return `<div class="ibox b-${m.sev}${mechanik?' x-only':''}">
    <div class="ic s-${m.sev}">${ico(m.sym)}</div>
    <div class="itx"><div class="il">${lab}</div><div class="iv t-${m.sev}">${m.v}</div></div>
  </div>`;}).join('');
}""",
    "Medikamentenkarte: Mechanikfeld und Umbenennung", wo="script")

# =============================================================== 5. Genkarte
sub("""    <div class="gexp" onclick="event.stopPropagation()">
      <div class="gsec">Was heisst das f&uuml;r dich?</div>
      <div class="plain sm">${plainSentence(g)}</div>
      <div class="gsec sp">Deine zwei Genkopien</div>
      <div class="gcopies">${copiesHtml(g)}</div>
      ${gPosHtml(g)}
      ${techToggleHtml(g,key+':tech')}
      <button class="btn btn-plum gmore" onclick="event.stopPropagation();openGene('${g}')">Alle Details und Empfehlungen ${ico('arr','',15)}</button>
    </div>""",
    """    <div class="gexp" onclick="event.stopPropagation()">
      <div class="gsec">Was heisst das f&uuml;r dich?</div>
      <div class="plain sm">${plainSentence(g)}</div>
      <div class="x-only">
        <div class="gsec sp">Deine zwei Genkopien</div>
        <div class="gcopies">${copiesHtml(g)}</div>
        ${gPosHtml(g)}
        ${techToggleHtml(g,key+':tech')}
      </div>
      <button class="btn btn-plum gmore" onclick="event.stopPropagation();openGene('${g}')">Alle Details und Empfehlungen ${ico('arr','',15)}</button>
    </div>""",
    "Genkarte: Genkopien, Positionen und Fachdetails", wo="script")

# Die Metabolisierer-Skala mit den Stufen Langsam/Vermindert/Normal/Schnell
# ist Fachsprache. Der Zustand steht ohnehin schon als Wort in der Kopfzeile.
sub("""    <div class="gb-tx"><div class="gn">${g}</div><div class="gs" style="color:${colr}">${short}</div></div>
      ${ico('chev','gchev')}
    </div>
    ${skala}""",
    """    <div class="gb-tx"><div class="gn">${g}</div><div class="gs" style="color:${colr}">${short}</div></div>
      ${ico('chev','gchev')}
    </div>
    <div class="x-only">${skala}</div>""",
    "Genkarte: Metabolisierer-Skala", wo="script")

# Auch die flache Fassung (im Gen-Fenster und im Arztbericht) - dort aber
# NICHT ausblenden: der Arztbericht bleibt vollstaendig. Die flache Karte
# wird nur dort benutzt, also bleibt sie unveraendert.

# ============================================================ 6. Genansicht
sub("""  ${(()=>{const k=geneListe(),z=geneZahlen();""",
    """  ${(()=>{const kAlle=geneListe(),z=geneZahlen();
    /* In der einfachen Ansicht nur die Gene, die etwas aussagen: solche mit
       Metabolisierertyp oder mit mindestens einem Befund. Aus 488 Karten
       werden damit die, zu denen es ueberhaupt eine Aussage gibt. */
    const k=istEinfach()
      ? kAlle.filter(g=>!!PHENO[g]||(RS_BY[g]||[]).some(p=>rsNeg(p[4])))
      : kAlle;
    const versteckt=kAlle.length-k.length;""",
    "Genansicht: nur aussagekraeftige Gene", wo="script")

sub("""    return `<div class="genecount">${z.alle} Gene ausgewertet</div>
    <div class="genegrid">${k.map(g=>geneCardHtml(g)).join('')}</div>`;})()}`;""",
    """    return `<div class="genecount">${z.alle} Gene ausgewertet</div>
    ${versteckt?`<div class="s-hint">${ico('info','',16)}<div>Hier stehen die
      <b>${k.length} Gene, zu denen es eine Aussage gibt</b>. Die uebrigen
      ${versteckt} wurden ebenfalls untersucht und waren unauff&auml;llig &mdash;
      mit <b>Experte</b> oben siehst du alle.</div></div>`:''}
    <div class="genegrid">${k.map(g=>geneCardHtml(g)).join('')}</div>`;})()}`;""",
    "Genansicht: Hinweis auf die ausgeblendeten", wo="script")

# ======================================================= 7. Quellenzeile
sub("""      <p class="cov-p">Probe <b>${M.probe}</b> &middot; Referenz <b>${M.build}</b> &middot;""",
    """      <p class="cov-p x-only">Probe <b>${M.probe}</b> &middot; Referenz <b>${M.build}</b> &middot;""",
    "Quellenzeile nur fuer Fachleute", wo="script")

# ============================================ 8. Klasse am body von Anfang an
sub("""<div class="shell">""",
    """<script>document.body.className='m-'+((function(){try{return localStorage.getItem('ndr-mode')||'einfach';}catch(e){return 'einfach';}})());</script>
<div class="shell">""",
    "Ansichtsklasse setzen, bevor gezeichnet wird")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
assert s.count("body.m-einfach .x-only{display:none!important}") == 1, "Regel fuer x-only fehlt"
assert s.count("body.m-experte .s-only{display:none!important}") == 1, "Regel fuer s-only fehlt"
assert s.count('class="modesw"') == 1, "Umschalter nicht genau einmal"
assert s.count("function setMode(") == 1, "setMode fehlt"
assert s.count("function istEinfach(") == 1, "istEinfach fehlt"
# MODE muss VOR seiner ersten Benutzung stehen (Fallstrick 5: kein Hoisting).
iDecl = s.index("let MODE=")
for name in ("istEinfach()", "MODE==="):
    for j in range(len(s)):
        j = s.find(name, j)
        if j < 0:
            break
        assert j > iDecl or s[j-9:j] == "function ", \
            "%s wird vor der Deklaration von MODE benutzt" % name
        j += 1
        break
assert s.count('class="x-only"') >= 2, "x-only wird kaum verwendet"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
