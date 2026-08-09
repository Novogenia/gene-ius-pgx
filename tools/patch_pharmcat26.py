# -*- coding: utf-8 -*-
"""
Echte Mobilbedienung: Viewport-Meta, Tableiste unten, groessere Schrift.

Vorgabe Daniel, 2026-08-08: "Die App ist noch nicht responsive. Am Handy
waeren die Texte viel zu klein, und es kann so nicht verwendet werden. Baue
es bei Handyeinstellung so um, dass es eine App aehnliche Experience ist und
am Handy gut bedienbar ist."

DIE URSACHE, und sie erklaert alles:

Die Datei hat gar keinen <head>. Sie beginnt direkt mit <style>, also gibt
es kein

    <meta name="viewport" content="width=device-width, initial-scale=1">

Ohne dieses Meta rendert jeder mobile Browser die Seite auf einer virtuellen
Breite von 980px und skaliert sie danach auf die Geraetebreite herunter.
Genau Daniels Symptom: alles korrekt angeordnet, aber winzig. Und genau der
Grund, warum der Browser-Pane dieser Umgebung nie unter 980px ging und
keine Media Query feuerte - v76 hat deshalb die Ueberlaeufe beseitigt, aber
am eigentlichen Problem nichts geaendert.

WAS DAZUKOMMT, damit es sich wie eine App anfuehlt:

  Tableiste unten     fuenf Ziele, feste Position, Daumenreichweite.
                      Die Seitenleiste blendet ihre Navigationsliste aus und
                      wird zur schmalen Kopfzeile.
  Kopfzeile           klebt oben, zeigt Marke und Patientin.
  Schrift             Basis 16px statt 15px, Kartennamen 17px, Statuszeilen
                      und Beschriftungen hoch auf mindestens 12px.
                      16px ist zugleich die Grenze, unterhalb derer iOS beim
                      Fokussieren eines Eingabefelds automatisch
                      hineinzoomt - das Suchfeld bekommt sie deshalb fest.
  Beruehrflaechen     mindestens 44px hoch fuer alle Knoepfe.
  Sichere Bereiche    env(safe-area-inset-bottom) fuer Geraete mit
                      Homebar.

Die Tableiste rendert aus derselben NAV-Liste wie die Seitenleiste, mit
Kurzbeschriftungen - "Deine Medikamente" passt auf einem Telefon nicht in
ein Fuenftel der Breite.
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

# ============================================== 1. Kopfbereich mit Viewport
# Ohne das Meta rendert jedes Telefon auf 980px und skaliert herunter.
assert not s.startswith("<meta"), "Kopfbereich schon vorhanden"
s = """<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>GENE-IUS PGx</title>
<meta name="description" content="Pharmakogenetik-Clickdummy - Prototyp zur Abstimmung, kein Medizinprodukt.">
<meta name="theme-color" content="#5E0047">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="GENE-IUS PGx">
""" + s
n += 1
print("  ok  Kopfbereich mit Viewport-Meta")

# ==================================================== 2. Tableiste im Markup
sub("""  <main id="main"></main>
</div>""",
    """  <main id="main"></main>
</div>
<nav class="tabbar" id="tabbar" aria-label="Hauptnavigation"></nav>""",
    "Tableiste im Markup", wo="script")

# ======================================================= 3. Tableiste rendern
sub("""const NAV=[
  {id:"dashboard",label:"Start",ic:"n-dash",group:"&Uuml;bersicht"},
  {id:"meine",label:"Deine Medikamente",ic:"n-pill",badge:"ws",group:"Deine Daten"},
  {id:"gene",label:"Deine Gene",ic:"n-dna"},
  {id:"merk",label:"F&uuml;r deinen Arzt",ic:"star",badge:"watch"},
  {id:"liste",label:"Alle Medikamente",ic:"n-list",group:"Datenbank"}
];""",
    """const NAV=[
  /* kurz = Beschriftung der Tableiste. "Deine Medikamente" passt auf einem
     Telefon nicht in ein Fuenftel der Breite. */
  {id:"dashboard",label:"Start",kurz:"Start",ic:"n-dash",group:"&Uuml;bersicht"},
  {id:"meine",label:"Deine Medikamente",kurz:"Medikamente",ic:"n-pill",badge:"ws",group:"Deine Daten"},
  {id:"gene",label:"Deine Gene",kurz:"Gene",ic:"n-dna"},
  {id:"merk",label:"F&uuml;r deinen Arzt",kurz:"Arzt",ic:"star",badge:"watch"},
  {id:"liste",label:"Alle Medikamente",kurz:"Datenbank",ic:"n-list",group:"Datenbank"}
];""",
    "NAV: Kurzbeschriftungen", wo="script")

sub("""      <span class="ni">${ico(n.ic,'',20)}</span> ${n.label} ${b}</button>`;}).join('');
}""",
    """      <span class="ni">${ico(n.ic,'',20)}</span> ${n.label} ${b}</button>`;}).join('');
  /* Dieselbe Liste als Tableiste unten - nur auf dem Telefon sichtbar. */
  const tb=document.getElementById('tabbar');
  if(tb)tb.innerHTML=NAV.map(n=>{
    const cnt=n.badge==='ws'?workspace.length:n.badge==='watch'?watchlist.size:null;
    return `<button class="tab ${view===n.id?'on':''}" aria-current="${view===n.id}"
      onclick="go('${n.id}')">
      <span class="tb-ic">${ico(n.ic,'',22)}${cnt?`<span class="tb-b">${cnt}</span>`:''}</span>
      <span class="tb-l">${n.kurz}</span></button>`;}).join('');
}""",
    "Tableiste rendern", wo="script")

# ============================================================== 4. Das CSS
sub("""  /* ---------- Telefon ----------------------------------------------""",
    """  /* ---------- Tableiste (nur Telefon) ---------- */
  .tabbar{display:none;position:fixed;left:0;right:0;bottom:0;z-index:60;
    background:#fff;border-top:1px solid var(--line2);
    padding:5px 4px calc(5px + env(safe-area-inset-bottom,0px));
    box-shadow:0 -3px 16px rgba(30,10,30,.10)}
  .tabbar .tab{flex:1 1 0;min-width:0;min-height:50px;display:flex;flex-direction:column;
    align-items:center;justify-content:center;gap:2px;border:0;background:none;font:inherit;
    color:var(--muted);cursor:pointer;padding:4px 2px;border-radius:12px;
    -webkit-tap-highlight-color:transparent}
  .tabbar .tab .tb-ic{position:relative;display:grid;place-items:center;line-height:0}
  .tabbar .tab svg{width:22px;height:22px}
  .tabbar .tab .tb-l{font-size:11px;font-weight:750;letter-spacing:-.01em;
    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%}
  .tabbar .tab.on{color:var(--plum)}
  .tabbar .tab.on .tb-l{font-weight:800}
  .tb-b{position:absolute;top:-5px;right:-9px;min-width:16px;height:16px;border-radius:999px;
    background:var(--plum);color:#fff;font-size:11px;font-weight:800;line-height:16px;
    text-align:center;padding:0 4px}
  /* ---------- Telefon ----------------------------------------------""",
    "CSS: Tableiste", wo="style")

sub("""  @media(max-width:430px){
    main#main{padding:14px 12px 56px}""",
    """  /* Ab hier ist es eine App: Seitenleiste zur Kopfzeile, Navigation nach
     unten in Daumenreichweite, Schrift groesser, Beruehrflaechen groesser. */
  @media(max-width:820px){
    .shell{grid-template-columns:minmax(0,1fr)}
    nav.rail{flex-direction:row;align-items:center;gap:12px;height:auto;
      padding:10px 14px calc(10px + env(safe-area-inset-top,0px));
      position:sticky;top:0;z-index:50}
    nav.rail .brand{padding:0;font-size:16px;gap:10px}
    nav.rail .brand .logo{width:32px;height:32px;font-size:15px}
    #rail{display:none}
    nav.rail .patient{margin:0 0 0 auto;padding:0;border-top:0;gap:9px}
    nav.rail .patient span{display:none}
    .tabbar{display:flex}
    main#main{padding:16px 14px calc(84px + env(safe-area-inset-bottom,0px))}
    /* Schrift: Basis 16px. Darunter zoomt iOS beim Fokussieren von
       Eingabefeldern automatisch hinein - deshalb bekommt die Suche sie fest. */
    body{font-size:16px}
    #q,input,select,textarea{font-size:16px}
    .cname{font-size:17px}
    .cbrands{font-size:13px}
    .cstate .sw{font-size:12px}
    .genebox .gn{font-size:17px}
    .genebox .gs{font-size:15px}
    .sec-sub{font-size:14.5px;max-width:none}
    .ab-plain,.plain{font-size:14.5px}
    .ixs-l{font-size:12.5px}
    .gpos-h,.gpos-s{font-size:13px}
    /* Beruehrflaechen: 44px ist die uebliche Untergrenze */
    .btn,.moreb,.bf,.sfb,.fchip,.heartbtn,.wbtn,.tab{min-height:44px}
    .heartbtn,.wbtn{width:44px}
    .fchip{padding:0 14px}
    .infogrid{grid-template-columns:1fr}
  }
  @media(max-width:430px){
    main#main{padding:14px 12px calc(84px + env(safe-area-inset-bottom,0px))}""",
    "CSS: Mobilschale", wo="style")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
assert s.count('name="viewport"') == 1, "Viewport-Meta fehlt oder doppelt"
assert s.index('name="viewport"') < s.index("<style>"), "Viewport-Meta steht nach dem Stylesheet"
assert s.count('id="tabbar"') == 1, "Tableiste nicht im Markup"
assert s.count("getElementById('tabbar')") == 1, "Tableiste wird nicht gerendert"
assert s.count("kurz:") == 5, "Kurzbeschriftungen unvollstaendig"
assert "@media(max-width:820px){\n    .shell{grid-template-columns:minmax(0,1fr)}" in s, \
    "Mobilschale nicht eingesetzt"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
