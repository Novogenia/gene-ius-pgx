# -*- coding: utf-8 -*-
"""
Die rs-Befunde wandern IN die Genkarte und faerben sie.

Vorgabe Daniel, 2026-08-06: "Ich moechte die Karten gen-fokussiert haben und
nicht RS-Nummern. Eine negative Auswirkung hat das Ganze? Gelb oder Rot
fahren."

Korrigiert damit v64, wo jede Position eine eigene Karte bekam - 611 Karten,
rs-fokussiert statt gen-fokussiert. Das war zu woertlich genommen;
tools/patch_pharmcat13.py ist entfernt.

Die Karte bleibt das Gen. Alles rs-Bezogene liegt darin:
  - vorne: eine Zeile "N Positionen mit Befund", wenn es welche gibt
  - aufgeklappt: die Signalzeilen mit Evidenzpunkten, danach die uebrigen
    gelesenen Positionen als kompakte Liste (Genotyp je Position)
Damit entfallen beide Sonderebenen - das Hinweis-Band aus v63 und die
aufklappbare Variantenliste. Nichts geht verloren, alles sitzt am Gen.

FARBE - das ist die eigentliche Aenderung. Bis v63 galt: die Hinweis-Ebene
fasst die Bewertung nie an. Diese Zusicherung wird hiermit aufgehoben, auf
ausdrueckliche Ansage. Neu:

    negativer Befund, Evidenz 1A/1B  -> ROT
    negativer Befund, Evidenz 2A-4   -> GELB
    kein negativer Befund            -> Farbe wie bisher aus dem Phaenotyp

Negativ heisst hoeheres Risiko oder schwaecheres Ansprechen (Codes 1 und 3).
Guenstige Befunde und reine Abbau-Hinweise faerben nicht.

Die Evidenzstufe entscheidet zwischen Gelb und Rot, weil sie die einzige
Groesse in den Daten ist, die "belegt" von "beobachtet" trennt. Damit bleibt
der Unterschied erhalten, den in v63 die Punkte getragen haben.

Die Karte nimmt immer die schaerfere der beiden Stufen - Phaenotyp oder
rs-Befund. Eine Karte wird also nie heruntergestuft.

WAS DAS KONKRET AENDERT (an NA17454, siehe Kopf der Doku):
  rot durch 1A-Befund : ABCG2, CYP2B6, CYP4F2, IFNL3, SLCO1B1, VKORC1
  gelb durch Stufe 3  : CYP2C19, CYP3A5, NAT2, RYR1, UGT1A1

Zwei davon sind erklaerungsbeduerftig und stehen so in der Doku:
  - SLCO1B1 meldet "Normale Transportfunktion" und wird trotzdem rot, weil
    rs4149056 T/T bei Cyclophosphamid, Docetaxel und Fluorouracil als
    ungueneriges Signal gefuehrt ist (1A). Die Karte sagt beides.
  - RYR1 meldet "Keine Risikovariante gefunden" und wird gelb wegen
    rs186983396 C/C - schwaecheres Ansprechen auf KOFFEIN, Evidenzstufe 3.
    Formal korrekt, inhaltlich duenn. Wenn das stoert, ist die Schwelle
    eine Zeile: in rsGeneSev() die Stufen 3 und 4 nicht mehr faerben lassen.
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

# ------------------------------------------------------------------- CSS
sub("""  /* Einzelpositionen mit Studienhinweis. Bewusst OHNE Ampelfarben - das
     ist eine Beobachtung, keine Bewertung, und darf nie wie eine aussehen. */""",
    """  /* Befundzeile auf der Genkarte */
  .gbef{display:flex;align-items:center;gap:7px;font-size:12px;font-weight:750;
    margin-top:9px;padding-top:9px;border-top:1px solid var(--line);color:var(--muted)}
  .gbef svg{width:15px;height:15px;flex:none}
  .gbef.neg{color:var(--plum)}
  /* Positionsblock im aufgeklappten Teil der Genkarte */
  .gpos{margin-top:4px}
  .gpos-r{border:1.5px solid var(--line2);border-radius:10px;padding:8px 10px;margin-bottom:6px;background:#fff}
  .gpos-h{display:flex;align-items:center;gap:8px;flex-wrap:wrap;font-size:12px;margin-bottom:5px}
  .gpos-rs{font-family:var(--mono,monospace);font-weight:700}
  .gpos-rs a{color:var(--blue);text-decoration:none}.gpos-rs a:hover{text-decoration:underline}
  .gpos-gt{font-family:var(--mono,monospace);background:var(--panel);border:1.5px solid var(--line2);
    border-radius:6px;padding:0 6px;font-weight:700}
  .gpos-ev{margin-left:auto;display:flex;align-items:center;gap:6px;font-size:11px;color:var(--faint)}
  .gpos-ev b{font-weight:700;color:var(--muted);font-size:11px}
  .gpos-s{display:flex;gap:7px;align-items:flex-start;font-size:12px;line-height:1.45;margin-top:4px}
  .gpos-s svg{width:15px;height:15px;flex:none;color:var(--muted);margin-top:1px}
  .gpos-s.neg svg{color:var(--plum)}
  .gpos-s b{font-weight:750}.gpos-s span{color:var(--muted)}
  .gpos-rest{font-size:11.5px;color:var(--faint);line-height:1.7;margin-top:6px}
  .gpos-rest code{font-family:var(--mono,monospace);background:var(--panel);border-radius:5px;
    padding:0 5px;color:var(--muted);font-size:11.5px}
  /* Einzelpositionen mit Studienhinweis. Bewusst OHNE Ampelfarben - das
     ist eine Beobachtung, keine Bewertung, und darf nie wie eine aussehen. */""",
    "CSS: Befunde auf der Genkarte", wo="style")

# ---------------------------------------------- Farbe und Karteninhalt
sub("""var rsOffen=false;
function toggleRs(){rsOffen=!rsOffen;render();}""",
    """/* Ab v65 faerben negative Befunde die Genkarte. Die Zusicherung aus v63,
   dass diese Ebene die Bewertung nie anfasst, ist damit aufgehoben -
   Ansage Daniel: "Eine negative Auswirkung hat das Ganze? Gelb oder Rot
   fahren." Die Evidenzstufe entscheidet zwischen Gelb und Rot, weil sie die
   einzige Groesse in den Daten ist, die belegt von beobachtet trennt.
   Guenstige Befunde und reine Abbau-Hinweise faerben nicht. */
function rsGeneSev(g){
  const l=RS_BY[g]; if(!l)return null;
  let sev=null;
  l.forEach(p=>{
    if(!p[4].some(x=>x[0]===1||x[0]===3))return;
    if(RSRANG[p[3]]<=1)sev='crit';
    else if(sev!=='crit')sev='warn';
  });
  return sev;
}
/* Die Stufe eines Gens: die schaerfere aus Phaenotyp und rs-Befund.
   EINE Stelle, weil Genkarte und Arztbericht sonst auseinanderlaufen -
   in der ersten Fassung war der Berichtsrahmen gelb und die Karte darin
   rot. */
const GSEVR={ok:0,ultra:0,none:0,unk:1,warn:2,crit:3};
function geneSev(g){
  const p=PHENO[g]; if(!p)return 'none';
  const psv=GSEV[p.lvl]||'unk', rsv=rsGeneSev(g);
  return (rsv&&GSEVR[rsv]>GSEVR[psv])?rsv:psv;
}
/* Positionen eines Gens ohne eigenen Befund - der Vollstaendigkeit halber,
   damit die Karte weiter belegt, was gelesen wurde. */
function gPosRest(g){
  const mitBefund={}; (RS_BY[g]||[]).forEach(p=>{mitBefund[p[0]]=1;});
  const pg=PGENE[g];
  return ((pg&&pg.var)||[]).filter(v=>!mitBefund[v[0]]);
}
/* Der Positionsblock im aufgeklappten Teil der Genkarte */
function gPosHtml(g){
  const bef=(RS_BY[g]||[]).slice().sort((a,b)=>
    (rsNeg(b[4])?1:0)-(rsNeg(a[4])?1:0)||RSRANG[a[3]]-RSRANG[b[3]]);
  const rest=gPosRest(g);
  if(!bef.length&&!rest.length)return '';
  const zeilen=bef.map(p=>{
    const sig=p[4].slice().sort((a,b)=>(a[0]===1||a[0]===3?0:1)-(b[0]===1||b[0]===3?0:1))
      .map(([code,idx])=>{
        const r=R_RICHT[code]||['ver&auml;ndert','s-up'];
        return `<div class="gpos-s ${(code===1||code===3)?'neg':''}">${ico(r[1],'',15)}
          <div><b>${r[0]}</b> <span>beobachtet bei ${idx.map(i=>R_DRUGS[i]).join(', ')}</span></div></div>`;
      }).join('');
    const isRs=/^rs\\d+$/.test(p[0]);
    return `<div class="gpos-r">
      <div class="gpos-h">
        <span class="gpos-rs">${isRs?`<a href="https://www.ncbi.nlm.nih.gov/snp/${p[0]}"
          target="_blank" rel="noopener">${p[0]}</a>`:p[0]}</span>
        <span class="gpos-gt">${p[2]}</span>
        <span class="gpos-ev">${rsDots(p[3])}</span>
      </div>${sig}</div>`;}).join('');
  const restHtml=rest.length
    ? `<div class="gpos-rest">Weitere gelesene Stellen ohne hinterlegte
        Ver&ouml;ffentlichung (${rest.length}):<br>
        ${rest.map(v=>`<code>${v[0]} ${v[1]}</code>`).join(' ')}</div>`
    : '';
  return `<div class="gsec sp">Einzelne gelesene Stellen</div>
    <div class="gpos">${zeilen}${restHtml}</div>`;
}""",
    "Farbregel und Positionsblock", wo="script")

# ------------------------------------------- Genkarte: Farbe uebersteuern
sub("""  const has=!!PHENO[g], lvl=has?PHENO[g].lvl:null, sv=has?GSEV[lvl]:'none', gn=GENO[g];""",
    """  const has=!!PHENO[g], lvl=has?PHENO[g].lvl:null, sv=geneSev(g), gn=GENO[g];""",
    "Genkarte: Farbe aus Phaenotyp oder Befund", wo="script")

# Der Arztbericht rahmt die Genkarte - sonst steht ein gelber Rahmen um eine
# rote Karte. Beide muessen dieselbe Stufe benutzen.
sub("""function geneReportCard(g){
  const lvl=PHENO[g].lvl, sv=GSEV[lvl], gn=GENO[g];""",
    """function geneReportCard(g){
  const lvl=PHENO[g].lvl, sv=geneSev(g), gn=GENO[g];""",
    "Arztbericht: dieselbe Stufe wie die Genkarte", wo="script")

# --------------------------------------- Genkarte: Befundzeile und Block
sub("""  const key='gene:'+g+(opts.ctx||''), open=openGenes[key];""",
    """  /* Befundzeile auf der Vorderseite - macht sichtbar, warum die Karte
     faerbt, ohne die Detailzeilen schon aufzuklappen. */
  const nBef=(RS_BY[g]||[]).filter(p=>rsNeg(p[4])).length;
  const nGes=(RS_BY[g]||[]).length;
  const befZeile=nGes
    ? `<div class="gbef ${nBef?'neg':''}">${ico(nBef?'st-excl':'st-ok','',15)}
        ${nBef?`${nBef} Position${nBef===1?'':'en'} mit negativem Befund`
              :`${nGes} Position${nGes===1?'':'en'} mit Studienhinweis`}</div>`
    : '';
  const key='gene:'+g+(opts.ctx||''), open=openGenes[key];""",
    "Genkarte: Befundzeile", wo="script")

sub("""  if(opts.flat)return `<div class="genebox flat b-${sv}">
    <div class="gb-top"><div class="gb-ic gi-${sv}">${helix(lvl)}</div>
      <div class="gb-tx"><div class="gn">${g}</div><div class="gs" style="color:${colr}">${short}</div></div></div>
    ${skala}
    ${why}</div>`;""",
    """  if(opts.flat)return `<div class="genebox flat b-${sv}">
    <div class="gb-top"><div class="gb-ic gi-${sv}">${helix(lvl)}</div>
      <div class="gb-tx"><div class="gn">${g}</div><div class="gs" style="color:${colr}">${short}</div></div></div>
    ${skala}
    ${why}${befZeile}</div>`;""",
    "Genkarte flach: Befundzeile", wo="script")

sub("""    ${skala}
    ${why}
    <div class="gexp" onclick="event.stopPropagation()">""",
    """    ${skala}
    ${why}${befZeile}
    <div class="gexp" onclick="event.stopPropagation()">""",
    "Genkarte: Befundzeile vor dem Aufklappbereich", wo="script")

sub("""      ${techToggleHtml(g,key+':tech')}
      <button class="btn btn-plum gmore" onclick="event.stopPropagation();openGene('${g}')">Alle Details und Empfehlungen ${ico('arr','',15)}</button>""",
    """      ${gPosHtml(g)}
      ${techToggleHtml(g,key+':tech')}
      <button class="btn btn-plum gmore" onclick="event.stopPropagation();openGene('${g}')">Alle Details und Empfehlungen ${ico('arr','',15)}</button>""",
    "Genkarte: Positionsblock aufgeklappt", wo="script")

# ------------------------------------- Genansicht: Sonderebenen aufloesen
sub("""  <div class="genegrid">${sortedGenes().map(g=>geneCardHtml(g)).join('')}</div>
  ${rsBefundeHtml()}
  ${variantenHtml()}`;
}""",
    """  <div class="genegrid">${geneListe().map(g=>geneCardHtml(g)).join('')}</div>`;
}""",
    "Genansicht: nur noch Genkarten", wo="script")

# Gene mit gelesenen Positionen, aber ohne Metabolisierer-Status, gehoeren dazu
sub("""function vGene(){""",
    """/* Gene mit Karte: alle mit Ergebnis plus alle mit gelesenen Positionen.
   Damit sind CYP4F2, IFNL3 und UGT1A1 wieder dabei - sie haben keinen
   Metabolisierer-Status, aber belegte Positionen mit Befund. */
function geneListe(){
  const mit={}; P_GENES.forEach(g=>{if((g.var||[]).length)mit[g.g]=1;});
  return Object.keys(PHENO).filter(g=>PHENO[g].lvl>=0||mit[g])
    .sort((a,b)=>GORDER.indexOf(PHENO[a].lvl)-GORDER.indexOf(PHENO[b].lvl)||a.localeCompare(b));
}
function vGene(){""",
    "Genliste inklusive der reinen Positionsgene", wo="script")

# --------------------------------- Genkarte ohne Phaenotyp: keine Skala
sub("""  const short=lvlLabel(g).t;""",
    """  /* Gen ohne Metabolisierer-Status, aber mit gelesenen Positionen. Muss VOR
     `why` und `skala` stehen, die beide darauf zugreifen - const kennt kein
     Hoisting (Fallstrick 5). */
  const nurPos=lvl<0&&PGENE[g]&&(PGENE[g].var||[]).length;
  const short=nurPos?'Nur Einzelpositionen':lvlLabel(g).t;""",
    "Genkarte: Statuszeile bei reinen Positionsgenen", wo="script")

sub("""  const skala=(PGENE[g]&&PGENE[g].flach)
    ? `<div class="gflat">${ico('st-ok','',15)} ${PGENE[g].de}</div>`
    : `<div class="gsrow"><div class="genepair">${genePair(lvl)}</div>
      <div class="gsbar"><div class="gscale">${segs}</div><div class="gs-lab">${labs}</div></div></div>`;""",
    """  /* Ohne Metabolisierer-Status keine Metabolisierer-Skala - die gibt es
     dort nicht, und "Kein Ergebnis" hat v62 aus der Oberflaeche geworfen. */
  const skala=nurPos
    ? `<div class="gflat">${ico('n-dna','',15)} Kein Metabolisierer-Status &mdash;
        ${(PGENE[g].var||[]).length} gelesene Position${(PGENE[g].var||[]).length===1?'':'en'}</div>`
    : (PGENE[g]&&PGENE[g].flach)
    ? `<div class="gflat">${ico('st-ok','',15)} ${PGENE[g].de}</div>`
    : `<div class="gsrow"><div class="genepair">${genePair(lvl)}</div>
      <div class="gsbar"><div class="gscale">${segs}</div><div class="gs-lab">${labs}</div></div></div>`;""",
    "Genkarte: keine Skala ohne Metabolisierer-Status", wo="script")

sub("""  const why=lvl<0?`<div class="gwhy">${gwhyText(g)}</div>`:'';""",
    """  const why=(lvl<0&&!nurPos)?`<div class="gwhy">${gwhyText(g)}</div>`:'';""",
    "Genkarte: Luecken-Text nur ohne Positionen", wo="script")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
assert "${rsBefundeHtml()}" not in s, "Hinweis-Band wird noch gerendert"
assert "${variantenHtml()}" not in s, "Variantenliste wird noch gerendert"
for name in ("function rsGeneSev(", "function gPosHtml(", "function geneListe(",
             "function geneSev("):
    assert s.count(name) == 1, "%s nicht genau einmal vorhanden" % name
assert s.count("geneSev(g)") == 3, "geneSev wird nicht an beiden Stellen benutzt"
# nurPos muss vor seiner ersten Verwendung deklariert sein
i_decl = s.index("const nurPos=")
assert i_decl < s.index("const why=(lvl<0&&!nurPos)"), "nurPos steht hinter why (TDZ)"
assert i_decl < s.index("const skala=nurPos"), "nurPos steht hinter skala (TDZ)"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
