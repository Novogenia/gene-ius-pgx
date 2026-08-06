# -*- coding: utf-8 -*-
"""
Jede gelesene Position wird eine Karte - im selben Format wie die Genkarten.

Vorgabe Daniel, 2026-08-06: "RS-Nummern als Genkarten darstellen. Das
dazugehoerige Gen sollte genauso angezeigt werden, und RS-Nummern sollten
hier nicht separat anders gehandhabt werden."

Damit fallen die beiden Sonderbehandlungen weg:
  - das Hinweis-Band aus v63 (rsBefundeHtml)
  - die aufklappbare Variantenliste (variantenHtml)
Beide Inhalte stecken jetzt in den Karten selbst.

ZUR ERWARTUNG "mehrere hundert Gene": Karten ja, Gene nein. Die 611
gelesenen Positionen verteilen sich auf **19 Gene** - G6PD 146, RYR1 90,
DPYD 78, CFTR 61, CYP2C9 52, TPMT 38, CYP2C19 29, SLCO1B1 25, CYP2B6 24,
NAT2 24, CYP3A4 23, CYP3A5 5, CYP4F2 4, UGT1A1 4, NUDT15 3, CACNA1S 2,
ABCG2 1, IFNL3 1, VKORC1 1. Das Panel hat 23 Gene, mehr gibt es nicht.
Die Ansicht zeigt also 20 Genkarten und 611 Positionskarten, zusammen 631.
94 der 611 tragen keine rs-Nummer, sondern eine andere Notation
(Indels, HGVS) - sie werden gleich behandelt, nur ohne dbSNP-Link.

Reihenfolge: je Gen zuerst die Genkarte, dann ihre Positionen. So steht das
dazugehoerige Gen unmittelbar bei seinen Positionen. Innerhalb eines Gens
zuerst die Positionen mit Befund.

Drei Gene, die seit v61 keine Genkarte mehr hatten, bekommen wieder eine,
weil sie gelesene Positionen besitzen: CYP4F2, IFNL3, UGT1A1. Ihre Karte
sagt "kein Metabolisierer-Status" statt einer Skala - den gibt es dort
nicht.

STATUS EINER POSITIONSKARTE, nur aus den Daten:
  hoeheres Risiko / schwaecheres Ansprechen  -> warn
  geringeres Risiko / besseres Ansprechen    -> ok
  nur veraenderter Abbau                     -> schlicht
  keine Annotation (572 von 611)             -> schlicht,
                                                "keine Veroeffentlichung hinterlegt"
Das ist eine Aussage ueber die Literatur, nicht ueber unsere Analyse - der
Genotyp steht ja da. Deshalb ist das kein Rueckfall in den "Offen"-Zustand,
den v62 entfernt hat.

Die Evidenzpunkte bleiben auf jeder Karte mit Befund. Sie sind der Grund,
warum alle Evidenzstufen mitkoennen, ohne dass ein Stufe-3-Befund wie ein
Leitlinienbefund aussieht.

Leistung: 631 Karten auf einmal kosten zu viel (Fallstrick 6 - 2.697 Karten
brauchten 2,9 s). Deshalb dieselbe Loesung wie in der Wirkstoffliste:
zunaechst 150 Karten, Nachladeknopf fuer den Rest.
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
    """  /* Positionskarte - dieselbe Huelle wie die Genkarte (.genebox), damit
     rs-Nummern nicht anders gehandhabt aussehen als Gene. */
  .genebox.b-plain{border-color:var(--line2)}
  .gi-plain{background:var(--panel);color:var(--muted)}
  .pc-gen{display:flex;align-items:center;gap:8px;flex-wrap:wrap;font-size:12.5px;
    padding:9px 0 0;border-top:1px solid var(--line);margin-top:10px}
  .pc-gen .pc-gn{font-weight:800;letter-spacing:.01em}
  .pc-gt{font-family:var(--mono,monospace);background:var(--panel);border:1.5px solid var(--line2);
    border-radius:7px;padding:1px 7px;font-weight:700;font-size:12px}
  .pc-rolle{color:var(--faint);font-size:11.5px;width:100%}
  .pc-sig{display:flex;gap:8px;align-items:flex-start;font-size:12.5px;line-height:1.5;margin-top:9px}
  .pc-sig .rsi{flex:none;width:16px;height:16px;color:var(--muted);margin-top:1px}
  .pc-sig.neg .rsi{color:var(--plum)}
  .pc-sig b{font-weight:750}
  .pc-sig span{color:var(--muted)}
  .pc-ev{display:flex;align-items:center;gap:7px;margin-top:10px;font-size:11px;color:var(--faint)}
  .pc-ev b{font-weight:700;color:var(--muted);font-size:11px}
  .pc-none{font-size:12.5px;color:var(--faint);margin-top:9px}
  .genecount{font-size:12.5px;color:var(--muted);font-weight:700;margin:2px 0 12px}
  /* Einzelpositionen mit Studienhinweis. Bewusst OHNE Ampelfarben - das
     ist eine Beobachtung, keine Bewertung, und darf nie wie eine aussehen. */""",
    "CSS fuer die Positionskarte", wo="style")

# --------------------------------------------------------- Alte Ebenen raus
sub("""var rsOffen=false;
function toggleRs(){rsOffen=!rsOffen;render();}
function rsBefundeHtml(){""",
    """function rsBefundeHtml_UNUSED(){""",
    "Hinweis-Band-Zustand entfernen", wo="script")

# ------------------------------------------------------- Positionskarten
sub("""function vGene(){""",
    """/* ---- Positionen als Karten -----------------------------------------
   Eine gelesene Position ist eine Karte wie jede Genkarte. Der Genotyp
   steht aus dem PharmCAT-Lauf fest; ob dazu etwas veroeffentlicht ist,
   entscheidet R_POS. Ist nichts hinterlegt, sagt die Karte genau das -
   das ist eine Aussage ueber die Literatur, nicht ueber unsere Analyse. */
const RS_SIG={};
R_POS.forEach(p=>{RS_SIG[p[0]]=p;});
const POS_BY={};
P_GENES.forEach(g=>{(g.var||[]).forEach(v=>{
  (POS_BY[g.g]=POS_BY[g.g]||[]).push({rs:v[0],gt:v[1],gen:g.g,sig:RS_SIG[v[0]]||null});});});
function posNeg(p){return !!p.sig&&p.sig[4].some(x=>x[0]===1||x[0]===3);}
function posSev(p){
  if(!p.sig)return 'plain';
  if(posNeg(p))return 'warn';
  if(p.sig[4].some(x=>x[0]===2||x[0]===4))return 'ok';
  return 'plain';
}
/* Ueberschrift der Karte: das schaerfste Signal im Wortlaut */
function posKurz(p){
  if(!p.sig)return 'Genotyp bestimmt';
  const ord=[1,3,5,4,2];
  for(const c of ord){ const t=p.sig[4].find(x=>x[0]===c); if(t)return R_RICHT[c][0]; }
  return 'Genotyp bestimmt';
}
function posCardHtml(p){
  const sv=posSev(p), rs=/^rs\\d+$/.test(p.rs);
  const colr=sv==='ok'?'var(--ok-t)':sv==='warn'?'var(--warn-t)':'var(--muted)';
  const ph=PHENO[p.gen];
  const zeilen=p.sig?p.sig[4].slice()
    .sort((a,b)=>(a[0]===1||a[0]===3?0:1)-(b[0]===1||b[0]===3?0:1))
    .map(([code,idx])=>{
      const r=R_RICHT[code]||['ver&auml;ndert','s-up'];
      return `<div class="pc-sig ${(code===1||code===3)?'neg':''}">${ico(r[1],'rsi',16)}
        <div><b>${r[0]}</b> <span>beobachtet bei ${idx.map(i=>R_DRUGS[i]).join(', ')}</span></div></div>`;
    }).join(''):'';
  return `<div class="genebox b-${sv}">
    <div class="gb-top">
      <div class="gb-ic gi-${sv}">${ico('n-dna','',22)}</div>
      <div class="gb-tx">
        <div class="gn" style="font-family:var(--mono,monospace)">${rs
          ?`<a href="https://www.ncbi.nlm.nih.gov/snp/${p.rs}" target="_blank" rel="noopener"
             onclick="event.stopPropagation()" style="color:inherit">${p.rs}</a>`:p.rs}</div>
        <div class="gs" style="color:${colr}">${posKurz(p)}</div>
      </div>
    </div>
    <div class="pc-gen"><span class="pc-gn">${p.gen}</span><span class="pc-gt">${p.gt}</span>
      ${ph&&ph.rolle?`<span class="pc-rolle">Zust&auml;ndig f&uuml;r ${ph.rolle}</span>`:''}</div>
    ${zeilen}
    ${p.sig?`<div class="pc-ev">${rsDots(p.sig[3])}</div>`
           :`<div class="pc-none">Zu dieser Stelle ist keine Ver&ouml;ffentlichung hinterlegt.</div>`}
  </div>`;
}
/* Gene, die eine Karte bekommen: alle mit Ergebnis plus alle mit gelesenen
   Positionen. Damit sind CYP4F2, IFNL3 und UGT1A1 wieder dabei - sie haben
   keinen Metabolisierer-Status, aber belegte Positionen. */
function geneListe(){
  const mit=Object.keys(POS_BY);
  const alle=Object.keys(PHENO).filter(g=>PHENO[g].lvl>=0||mit.indexOf(g)>=0);
  return alle.sort((a,b)=>
    GORDER.indexOf(PHENO[a].lvl)-GORDER.indexOf(PHENO[b].lvl)||a.localeCompare(b));
}
/* Je Gen zuerst die Genkarte, dann ihre Positionen - Befunde zuerst. */
function genKarten(){
  const out=[];
  geneListe().forEach(g=>{
    out.push(geneCardHtml(g));
    (POS_BY[g]||[]).slice()
      .sort((a,b)=>(posNeg(b)?1:0)-(posNeg(a)?1:0)||(b.sig?1:0)-(a.sig?1:0)
                   ||a.rs.localeCompare(b.rs,'en',{numeric:true}))
      .forEach(p=>out.push(posCardHtml(p)));
  });
  return out;
}
let geneLimit=150;
function moreGene(){geneLimit+=300;render();}
function vGene(){""",
    "Positionskarten und Reihenfolge", wo="script")

# ------------------------------------------------------- Genansicht neu
sub("""  <div class="genegrid">${sortedGenes().map(g=>geneCardHtml(g)).join('')}</div>
  ${rsBefundeHtml()}
  ${variantenHtml()}`;
}""",
    """  ${(()=>{const k=genKarten(),nG=geneListe().length,nP=k.length-nG;
    const zeig=k.slice(0,geneLimit);
    return `<div class="genecount">${nG} Gene und ${nP.toLocaleString('de-DE')} gelesene
      Positionen${k.length>geneLimit?' &middot; '+geneLimit+' Karten angezeigt':''}</div>
    <div class="genegrid">${zeig.join('')}</div>
    ${k.length>geneLimit?`<button class="moreb" onclick="moreGene()">Weitere
      ${Math.min(300,k.length-geneLimit)} von ${(k.length-geneLimit).toLocaleString('de-DE')}
      anzeigen ${ico('chev','',16)}</button>`:''}`;})()}`;
}""",
    "Genansicht: Karten mit Nachladen statt Sonderebenen", wo="script")

# --------------------------------- Genkarte ohne Phaenotyp, aber mit Positionen
# CYP4F2, IFNL3 und UGT1A1 bekommen wieder eine Karte. Ungepatcht zeigt die
# Karte dort die Metabolisierer-Skala (die es dort nicht gibt) und den
# "Kein Ergebnis"-Text, den v62 aus der Oberflaeche geworfen hat. Beides
# waere ein Rueckfall: der Genotyp der Positionen steht ja fest.
sub("""  const skala=(PGENE[g]&&PGENE[g].flach)
    ? `<div class="gflat">${ico('st-ok','',15)} ${PGENE[g].de}</div>`
    : `<div class="gsrow"><div class="genepair">${genePair(lvl)}</div>
      <div class="gsbar"><div class="gscale">${segs}</div><div class="gs-lab">${labs}</div></div></div>`;""",
    """  /* Gene ohne Metabolisierer-Status, aber mit gelesenen Positionen: keine
     Skala (die gibt es dort nicht) und kein "Kein Ergebnis" - der Genotyp
     der Positionen steht fest, er ergibt nur keinen Typ. nurPos wird weiter
     oben deklariert, weil `why` es schon braucht (TDZ, Fallstrick 5). */
  const skala=nurPos
    ? `<div class="gflat">${ico('n-dna','',15)} Kein Metabolisierer-Status &mdash;
        ${POS_BY[g].length} gelesene Position${POS_BY[g].length===1?'':'en'}</div>`
    : (PGENE[g]&&PGENE[g].flach)
    ? `<div class="gflat">${ico('st-ok','',15)} ${PGENE[g].de}</div>`
    : `<div class="gsrow"><div class="genepair">${genePair(lvl)}</div>
      <div class="gsbar"><div class="gscale">${segs}</div><div class="gs-lab">${labs}</div></div></div>`;""",
    "Genkarte: keine Skala bei Genen ohne Metabolisierer-Status", wo="script")

sub("""  const why=lvl<0?`<div class="gwhy">${gwhyText(g)}</div>`:'';""",
    """  const why=(lvl<0&&!nurPos)?`<div class="gwhy">${gwhyText(g)}</div>`:'';""",
    "Genkarte: Luecken-Text nur ohne Positionen", wo="script")

sub("""  const short=lvlLabel(g).t;""",
    """  /* Gen ohne Metabolisierer-Status, aber mit gelesenen Positionen. Muss VOR
     `why` und `skala` stehen, die beide darauf zugreifen - const kennt kein
     Hoisting (Fallstrick 5). */
  const nurPos=lvl<0&&POS_BY[g]&&POS_BY[g].length;
  const short=nurPos?'Nur Einzelpositionen':lvlLabel(g).t;""",
    "Genkarte: Statuszeile bei reinen Positionsgenen", wo="script")

# ----------------------------------------------- Beschreibung anpassen
sub("""  <p class="sec-sub">${PATIENT}, das sind die Gene, die dar&uuml;ber entscheiden, wie du Medikamente verarbeitest. Jede Karte zeigt deine zwei Genkopien und was sie zusammen bewirken${ihelp("gene")} &mdash; anklicken f&uuml;r Klartext, Fachdetails und Quellen.${ihelp("metab")}</p>""",
    """  <p class="sec-sub">${PATIENT}, das sind die Gene, die dar&uuml;ber entscheiden, wie du Medikamente
    verarbeitest &mdash; und jede einzelne Stelle, die daf&uuml;r gelesen wurde${ihelp("gene")}. Eine Genkarte
    zeigt deine zwei Genkopien und was sie zusammen bewirken; die Karten darunter zeigen die
    Positionen, aus denen sich das zusammensetzt, mit deinem Genotyp und dem, was dazu
    ver&ouml;ffentlicht ist.${ihelp("metab")}</p>""",
    "Genansicht: Einleitung an die Positionskarten angepasst", wo="script")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
assert "${rsBefundeHtml()}" not in s, "Hinweis-Band wird noch gerendert"
assert "${variantenHtml()}" not in s, "Variantenliste wird noch gerendert"
for name in ("function posCardHtml(", "function genKarten(", "function geneListe(",
             "function posSev(", "const POS_BY="):
    assert s.count(name) == 1, "%s nicht genau einmal vorhanden" % name
assert s.index("const R_POS=") < s.index("R_POS.forEach(p=>{RS_SIG"), "Datenblock steht nach der Nutzung"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
