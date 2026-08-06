# -*- coding: utf-8 -*-
"""
Demo-Genotypen verdrahten - 482 zusaetzliche Genkarten aus erfundenen Werten.

Vorgabe Daniel, 2026-08-06: "Mal einen Dummy-Genotyp und gehe davon aus,
dass du diese in Zukunft ueber als Input fuer die App bekommst."

Damit wird Regel 1 fuer den Clickdummy ausgesetzt. Die Gegenmassnahme ist
Sichtbarkeit, an vier Stellen:

  1. Die Daten selbst: jede Demo-Position traegt ein sechstes Feld = 1.
  2. Die Genkarte: Statuszeile "Demo-Genotyp" und ein Streifen im
     aufgeklappten Teil.
  3. Die Genansicht: Hinweisbanner ueber dem Kartenraster.
  4. Die Zaehlzeile: getrennte Zahlen fuer gemessen und Demo.

Die 611 echten PharmCAT-Positionen bleiben unberuehrt und sind an keiner
Stelle markiert - sie sind echt. Ein Gen kann beides haben; dann steht der
Demo-Hinweis an der einzelnen Position, nicht an der Karte.

ZUSAMMENFUEHRUNG: D_DRUGS wird an R_DRUGS angehaengt und die Indizes der
Demo-Positionen werden um den Versatz verschoben. Danach sind Demo- und
Echtpositionen strukturgleich und laufen durch dieselbe Darstellung - bis
auf das Markierungsfeld. Genau so soll es sein, wenn spaeter echte Werte
nachruecken: dann faellt nur der Generator weg.

LEISTUNG: 502 Karten auf einmal sind zu viel (Fallstrick 6). 120 vorab,
Nachladeknopf fuer den Rest.
"""
import io, os

APP = "index.html"
DATA = os.path.join("data", "dummy_genotypen.js")
s = io.open(APP, encoding="ascii").read()
blk = io.open(DATA, encoding="ascii").read()
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

# ------------------------------------------------------------ 1. Datenblock
sub("""/* ===== END RS-BEFUNDE ===== */
""",
    """/* ===== END RS-BEFUNDE ===== */
/* ===== BEGIN DEMO-GENOTYPEN (erzeugt, KEINE MESSWERTE) ===== */
""" + blk + """/* ===== END DEMO-GENOTYPEN ===== */
""",
    "Datenblock dummy_genotypen einsetzen", wo="script")

# ------------------------------------------------------------------- 2. CSS
sub("""  /* Befundzeile auf der Genkarte */""",
    """  /* Demo-Genotypen: muss auf den ersten Blick als solche erkennbar sein */
  .demoband{display:flex;align-items:flex-start;gap:11px;background:#FFF8E6;
    border:1.5px solid #E8CE7A;border-radius:14px;padding:13px 16px;margin-bottom:16px}
  .demoband svg{flex:none;width:20px;height:20px;color:#8A6D1F;margin-top:1px}
  .demoband b{color:#6B540F}
  .demoband .dbt{font-size:13px;line-height:1.55;color:#6B540F;max-width:82ch}
  .demopill{display:inline-flex;align-items:center;gap:5px;background:#FFF3D1;color:#6B540F;
    border:1.5px solid #E8CE7A;border-radius:999px;padding:1px 9px;font-size:11px;font-weight:800;
    letter-spacing:.02em;vertical-align:middle}
  .gdemo{display:flex;align-items:center;gap:7px;font-size:11.5px;font-weight:750;color:#6B540F;
    background:#FFF8E6;border:1.5px solid #E8CE7A;border-radius:9px;padding:6px 9px;margin-top:9px}
  .gdemo svg{flex:none;width:14px;height:14px}
  /* Befundzeile auf der Genkarte */""",
    "CSS fuer die Demo-Kennzeichnung", wo="style")

# ------------------------------------------- 3. Demo-Positionen einmischen
sub("""const RS_BY={};
R_POS.forEach(p=>{(RS_BY[p[1]]=RS_BY[p[1]]||[]).push(p);});""",
    """const RS_BY={};
R_POS.forEach(p=>{(RS_BY[p[1]]=RS_BY[p[1]]||[]).push(p);});
/* Demo-Genotypen anhaengen. Sie sind strukturgleich zu den echten
   Positionen, tragen aber ein sechstes Feld = 1. Die Wirkstoffindizes
   werden um die Laenge von R_DRUGS verschoben, danach zeigen beide
   Datensaetze in dasselbe Namensregister. Ruecken spaeter echte Werte nach,
   faellt nur der Generator weg - hier aendert sich nichts. */
const DEMO_GENE={};
if(typeof D_POS!=='undefined'){
  const off=R_DRUGS.length;
  D_DRUGS.forEach(d=>R_DRUGS.push(d));
  D_POS.forEach(p=>{
    const q=[p[0],p[1],p[2],p[3],p[4].map(x=>[x[0],x[1].map(i=>i+off)]),1];
    (RS_BY[p[1]]=RS_BY[p[1]]||[]).push(q);
    if(!PHENO[p[1]])DEMO_GENE[p[1]]=1;
  });
}
function istDemo(p){return p.length>5&&p[5]===1;}
function genIstDemo(g){return !!DEMO_GENE[g];}""",
    "Demo-Positionen in RS_BY einmischen", wo="script")

# --------------------------------------------- 4. Stufe fuer Gene ohne PHENO
sub("""function geneSev(g){
  const p=PHENO[g]; if(!p)return 'none';""",
    """function geneSev(g){
  const p=PHENO[g];
  /* Demo-Gene haben keinen Phaenotyp - sie haengen allein am Befund. */
  if(!p)return rsGeneSev(g)||'ok';""",
    "geneSev: Demo-Gene haengen allein am Befund", wo="script")

# ------------------------------------------------- 5. Genliste erweitern
sub("""function geneListe(){
  const mit={}; P_GENES.forEach(g=>{if((g.var||[]).length)mit[g.g]=1;});
  return Object.keys(PHENO).filter(g=>PHENO[g].lvl>=0||mit[g])
    .sort((a,b)=>GORDER.indexOf(PHENO[a].lvl)-GORDER.indexOf(PHENO[b].lvl)||a.localeCompare(b));
}""",
    """function geneListe(){
  const mit={}; P_GENES.forEach(g=>{if((g.var||[]).length)mit[g.g]=1;});
  const echt=Object.keys(PHENO).filter(g=>PHENO[g].lvl>=0||mit[g])
    .sort((a,b)=>GORDER.indexOf(PHENO[a].lvl)-GORDER.indexOf(PHENO[b].lvl)||a.localeCompare(b));
  /* Demo-Gene stehen hinter den gemessenen, auffaellige zuerst. */
  const demo=Object.keys(DEMO_GENE).sort((a,b)=>
    (geneSev(b)==='warn'?1:0)-(geneSev(a)==='warn'?1:0)||a.localeCompare(b));
  return echt.concat(demo);
}
function geneZahlen(){
  const alle=geneListe();
  const d=alle.filter(genIstDemo).length;
  return {alle:alle.length, echt:alle.length-d, demo:d};
}""",
    "Genliste um die Demo-Gene erweitern", wo="script")

# ------------------------------------------- 6. Genkarte fuer Gene ohne PHENO
sub("""  const has=!!PHENO[g], lvl=has?PHENO[g].lvl:null, sv=geneSev(g), gn=GENO[g];
  if(!has)return `<div class="genebox flat"><div class="gb-top">
    <div class="gb-ic" style="background:var(--panel);opacity:.45">${helix(2)}</div>
    <div class="gb-tx"><div class="gn">${g}</div><div class="gs" style="color:var(--muted)">nicht getestet</div></div></div></div>`;""",
    """  const has=!!PHENO[g], lvl=has?PHENO[g].lvl:null, sv=geneSev(g), gn=GENO[g];
  /* Demo-Gen: kein Phaenotyp, kein gemessener Wert - die Karte haengt allein
     am Befund und sagt das auch. */
  if(!has&&genIstDemo(g)){
    const key='gene:'+g+(opts.ctx||''), off=openGenes[key];
    const neg=(RS_BY[g]||[]).some(p=>rsNeg(p[4]));
    const nP=(RS_BY[g]||[]).length;
    const kopf=`<div class="gb-top">
        <div class="gb-ic gi-${sv}">${mtIcon(null,sv)}</div>
        <div class="gb-tx"><div class="gn">${g}</div>
          <div class="gs" style="color:${neg?'var(--warn-t)':'var(--ok-t)'}">${neg?'Auff&auml;llig':'Unauff&auml;llig'}</div></div>
        ${opts.flat?'':ico('chev','gchev')}</div>
      <div class="gdemo">${ico('c-search','',14)} Demo-Genotyp &mdash; kein gemessener Wert</div>`;
    if(opts.flat)return `<div class="genebox flat b-${sv}">${kopf}</div>`;
    return `<div class="genebox b-${sv} ${off?'open':''}" onclick="toggleGene('${key}')">
      ${kopf}
      <div class="gexp" onclick="event.stopPropagation()">
        <div class="gsec">Worauf das beruht</div>
        <div class="plain sm">F&uuml;r ${g} liegt in dieser Demo kein gemessener Genotyp vor.
          Die ${nP} Position${nP===1?'':'en'} unten sind <b>erfunden</b> und stehen nur, um zu
          zeigen, wie die Karte mit echten Werten aussehen wird.</div>
        ${gPosHtml(g)}
      </div></div>`;
  }
  if(!has)return `<div class="genebox flat"><div class="gb-top">
    <div class="gb-ic" style="background:var(--panel);opacity:.45">${helix(2)}</div>
    <div class="gb-tx"><div class="gn">${g}</div><div class="gs" style="color:var(--muted)">nicht getestet</div></div></div></div>`;""",
    "Genkarte fuer Demo-Gene", wo="script")

# ------------------------------------------- 7. Demo-Marke an der Position
sub("""    const isRs=/^rs\\d+$/.test(p[0]);
    return `<div class="gpos-r">
      <div class="gpos-h">
        <span class="gpos-rs">${isRs?`<a href="https://www.ncbi.nlm.nih.gov/snp/${p[0]}"
          target="_blank" rel="noopener">${p[0]}</a>`:p[0]}</span>
        <span class="gpos-gt">${p[2]}</span>""",
    """    const isRs=/^rs\\d+$/.test(p[0]);
    return `<div class="gpos-r">
      <div class="gpos-h">
        <span class="gpos-rs">${isRs?`<a href="https://www.ncbi.nlm.nih.gov/snp/${p[0]}"
          target="_blank" rel="noopener">${p[0]}</a>`:p[0]}</span>
        <span class="gpos-gt">${p[2]}</span>
        ${istDemo(p)?'<span class="demopill">Demo</span>':''}""",
    "Demo-Marke an der einzelnen Position", wo="script")

# --------------------------------------------------- 8. Genansicht: Banner
sub("""  <div class="genegrid">${geneListe().map(g=>geneCardHtml(g)).join('')}</div>`;
}""",
    """  ${(typeof DUMMY_AKTIV!=='undefined'&&DUMMY_AKTIV)?`<div class="demoband">
    ${ico('n-warn','',20)}
    <div class="dbt"><b>Ein Teil dieser Karten beruht auf Demo-Genotypen.</b>
      Gemessen wurden ${geneZahlen().echt} Gene aus dem PharmCAT-Lauf. Die weiteren
      ${geneZahlen().demo} Gene tragen <b>erfundene</b> Genotypen &mdash; sie zeigen, wie die
      Ansicht mit vollst&auml;ndigen Rohdaten aussehen wird, und sind einzeln als
      <span class="demopill">Demo</span> gekennzeichnet. Keine dieser Angaben ist ein
      Messergebnis.</div></div>`:''}
  ${(()=>{const k=geneListe(),z=geneZahlen();
    const zeig=k.slice(0,geneLimit);
    return `<div class="genecount">${z.echt} gemessene Gene${z.demo?' und '+z.demo+' mit Demo-Genotyp':''}${
      k.length>geneLimit?' &middot; '+geneLimit+' angezeigt':''}</div>
    <div class="genegrid">${zeig.map(g=>geneCardHtml(g)).join('')}</div>
    ${k.length>geneLimit?`<button class="moreb" onclick="moreGene()">Weitere
      ${Math.min(240,k.length-geneLimit)} von ${(k.length-geneLimit).toLocaleString('de-DE')}
      anzeigen ${ico('chev','',16)}</button>`:''}`;})()}`;
}""",
    "Genansicht: Banner, Zaehlzeile, Nachladen", wo="script")

sub("""function vGene(){""",
    """let geneLimit=120;
function moreGene(){geneLimit+=240;render();}
function vGene(){""",
    "Nachladezustand fuer die Genansicht", wo="script")

# CSS-Klasse fuer die Zaehlzeile
sub("""  /* Demo-Genotypen: muss auf den ersten Blick als solche erkennbar sein */""",
    """  .genecount{font-size:12.5px;color:var(--muted);font-weight:700;margin:2px 0 12px}
  /* Demo-Genotypen: muss auf den ersten Blick als solche erkennbar sein */""",
    "CSS fuer die Zaehlzeile", wo="style")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
for name in ("const D_POS=", "function istDemo(", "function genIstDemo(",
             "function geneZahlen(", "let geneLimit="):
    assert s.count(name) == 1, "%s nicht genau einmal vorhanden" % name
assert s.index("const D_POS=") < s.index("if(typeof D_POS!=='undefined')"), \
    "Datenblock steht nach der Nutzung"
assert s.index("let geneLimit=") < s.index("moreGene()"), "geneLimit steht hinter der Nutzung (TDZ)"
assert s.count("demopill") >= 3, "Demo-Marke fehlt"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
