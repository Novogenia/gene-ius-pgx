# -*- coding: utf-8 -*-
"""
Offene Gene und offene Wirkstoffe ausblenden, Liste mehrspaltig, Genansicht
entruempelt.

Vorgaben Daniel, 2026-08-05:
  1. Gene, die wir nicht analysieren koennen, nicht mehr anzeigen.
  2. Wirkstoffe, die wir mangels Gen nicht bewerten koennen, nicht mehr
     anzeigen.
  3. Unter "Deine Medikamente" die gefilterte Liste mehrspaltig, wenn Platz
     ist.
  4. Insgesamt uebersichtlicher und einfacher verstaendlich.

Betroffen sind 6 der 23 Gene (CYP4F2 mehrdeutig, HLA-A, HLA-B, IFNL3,
MT-RNR1, UGT1A1 ohne Ergebnis) und 2 der 2.697 Wirkstoffe (Atazanavir und
Irinotecan, beide ueber UGT1A1).

WICHTIG - der Abdeckungsnachweis im Arztbericht bleibt vollstaendig.
covBlock() rechnet direkt auf P_GENES und ist bewusst nicht gefiltert: das
ist der Nachweis, was der Test lesen konnte, und ohne ihn traegt keine
Aussage darunter. Ausgeblendet wird nur in den Patientenansichten
(sortedGenes) - also "Deine Gene" und die Genkarten im Bericht.

Zu Punkt 4 - drei Dinge, die in der Genansicht schlicht falsch waren
(aufgefallen an ABCG2, siehe Screenshot):

  a) Die "Empfehlungsmatrix" war eine fest verdrahtete Metabolisierer-Skala,
     unabhaengig davon, was das Gen tut. ABCG2 ist ein Transporter und
     metabolisiert nichts; RYR1 und CACNA1S sind Risikogene, CFTR ist ein
     Zielgen. Fuer die stand dort trotzdem "Langsamer Metabolisierer".
     Jetzt haengt die Skala an PHENO[g].art; Ziel- und Risikogene bekommen
     statt einer Skala ihren tatsaechlichen Befund.

  b) Die Prozentzahlen (100 %, ca. 50 %, ca. 200 %, ca. 0 %) standen so in
     keiner Quelle - erfundene Zahlen in einem Kasten, der nach Datenauszug
     aussieht. Ersetzt durch Klartext, was die Stufe bedeutet.

  c) Die Spalte "Empfehlung" behauptete pauschal "Anderes Medikament" fuer
     jede Poor-Stufe - genau der unbegruendete Alarm, der in v60 aus der
     Ampel geflogen ist, nur eine Ebene tiefer. Spalte entfernt; was zu tun
     ist, steht auf der Wirkstoffkarte, wo es hingehoert.

  d) "Beeinflusst 0 Medikamente in der Datenbank" bei ABCG2 war falsch.
     GENE_DRUGS zaehlte nur das Feld gene/genes im Wirkstoff-Datenblock und
     kannte die PharmCAT-Genotypen nicht. ABCG2 steuert ueber PharmCAT
     Rosuvastatin und Allopurinol. Jetzt zaehlt geneDrugCount() beide Wege.

Die Matrix stand zweimal fast identisch im Code (geneItemHtml und
geneDetailHtml). Beide rufen jetzt dieselbe Funktion - zwei Kopien waren
schon bei den Wortgruppen der Grund fuer Abweichungen.
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

# ============================================================ CSS (<style>)
# Die gefilterte Liste unter "Deine Medikamente" war einspaltig. Die Karten
# sind 352px breit; ab etwa 620px Spaltenbreite passen zwei nebeneinander.
sub("""  .col-scroll{max-height:78vh;overflow:auto;padding-right:4px}""",
    """  .col-scroll{max-height:78vh;overflow:auto;padding-right:4px;
    display:grid;grid-template-columns:repeat(auto-fill,minmax(292px,1fr));
    gap:0 12px;align-items:start;align-content:start}
  .col-scroll>.ws-empty,.col-scroll>.moreb{grid-column:1/-1}""",
    "Liste unter 'Deine Medikamente' mehrspaltig", wo="style")

# Der Ampelfilter hatte fuenf Knoepfe, "Offen" faellt weg
sub("""  .sevfilters{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:6px;margin-top:11px}""",
    """  .sevfilters{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px;margin-top:11px}""",
    "Ampelfilter auf vier Knoepfe", wo="style")

# Die Matrix hat eine Spalte weniger (Empfehlung raus)
sub("""  .mx{display:grid;grid-template-columns:26px 1.1fr 1.4fr 1fr 108px;""",
    """  .mx{display:grid;grid-template-columns:26px 1.2fr 1.9fr 108px;""",
    "Matrix ohne Empfehlungsspalte", wo="style")

# ========================================================= Wirkstoffe filtern
sub("""function filtered(){
  let ids=Object.keys(DRUGS);""",
    """function filtered(){
  /* Wirkstoffe, deren Bewertung an einem nicht bestimmbaren Gen haengt,
     werden nicht mehr angezeigt (Vorgabe Daniel, 2026-08-05). Sie stehen
     weiterhin im Datenblock - nur eben nicht in der Liste. */
  let ids=Object.keys(DRUGS).filter(i=>listSev(i)!=='unk');""",
    "filtered: offene Wirkstoffe ausblenden", wo="script")

sub("""  const all=Object.keys(DRUGS);
  const n=s=>all.filter(i=>listSev(i)===s).length;""",
    """  const all=Object.keys(DRUGS).filter(i=>listSev(i)!=='unk');
  const n=s=>all.filter(i=>listSev(i)===s).length;""",
    "Filterzaehlung ohne offene Wirkstoffe", wo="script")

sub("""    {k:'ok',    sev:'ok',   cls:'bf-ok',   lab:'Unauff&auml;llig', cnt:n('ok'),    txt:'Standarddosis ist f&uuml;r dich passend.'},
    {k:'unk',   sev:'unk',  cls:'bf-unk',  lab:'Offen',            cnt:n('unk'),   txt:'Ein n&ouml;tiges Gen ist nicht bestimmbar.'}
  ];""",
    """    {k:'ok',    sev:'ok',   cls:'bf-ok',   lab:'Unauff&auml;llig', cnt:n('ok'),    txt:'Standarddosis ist f&uuml;r dich passend.'}
  ];""",
    "Filterkachel 'Offen' entfernen", wo="script")

sub("""      <button class="sfb sf-unk" aria-pressed="${!fWatch&&fSev==='unk'}" onclick="setSev('unk')">
        ${ico('c-search','',16)} Offen</button>
""", "", "Ampelfilter-Knopf 'Offen' entfernen", wo="script")

sub("""  if(!_dbstat){const t={total:0,ok:0,warn:0,crit:0,unk:0};
    Object.keys(DRUGS).forEach(k=>{t.total++;t[listSev(k)]++;});_dbstat=t;}""",
    """  if(!_dbstat){const t={total:0,ok:0,warn:0,crit:0,unk:0};
    Object.keys(DRUGS).forEach(k=>{const v=listSev(k);t[v]++;if(v!=='unk')t.total++;});_dbstat=t;}""",
    "DBSTATS: offene Wirkstoffe nicht mitzaehlen", wo="script")

# ============================================================== Gene filtern
sub("""function sortedGenes(){
  return Object.keys(PHENO).sort((a,b)=>
    GORDER.indexOf(PHENO[a].lvl)-GORDER.indexOf(PHENO[b].lvl)||a.localeCompare(b));
}""",
    """function sortedGenes(){
  /* Gene ohne eindeutiges Ergebnis werden nicht mehr angezeigt (Vorgabe
     Daniel, 2026-08-05). Der Abdeckungsnachweis im Arztbericht (covBlock)
     rechnet weiter auf P_GENES und bleibt vollstaendig - er ist der Beleg,
     was der Test lesen konnte. */
  return Object.keys(PHENO).filter(g=>PHENO[g].lvl>=0).sort((a,b)=>
    GORDER.indexOf(PHENO[a].lvl)-GORDER.indexOf(PHENO[b].lvl)||a.localeCompare(b));
}""",
    "sortedGenes: offene Gene ausblenden", wo="script")

# ------------------------------------------------- Startseite: Kachel tauschen
sub("""  const auff=Object.keys(PHENO).filter(g=>PHENO[g].lvl>=0&&PHENO[g].lvl!==2).length;
  const offen=Object.keys(PHENO).filter(g=>PHENO[g].lvl<0).length;
  const nGene=Object.keys(PHENO).length;""",
    """  const auff=Object.keys(PHENO).filter(g=>PHENO[g].lvl>=0&&PHENO[g].lvl!==2).length;
  const nGene=Object.keys(PHENO).filter(g=>PHENO[g].lvl>=0).length;""",
    "Startseite: offene Gene nicht mehr zaehlen", wo="script")

# Die Kachel "Gene noch offen" faellt weg. An ihre Stelle die Wirkstoffzahl -
# das ist die Groesse, die den Nutzer betrifft.
sub("""      <div class="hstat">
        <div class="hsic">${ico('c-search','',22)}</div>
        <div class="hsn">${offen}</div>
        <div class="hsl">Gene noch offen${ihelp('offen')}</div>
        <div class="hsd">hier reichen die gelesenen Stellen nicht f&uuml;r ein Ergebnis</div>
      </div>""",
    """      <div class="hstat">
        <div class="hsic">${ico('n-pill','',22)}</div>
        <div class="hsn">${nf(D.crit+D.warn)}</div>
        <div class="hsl">Wirkstoffe ung&uuml;nstig verarbeitet</div>
        <div class="hsd">hier lohnt sich ein Blick vor der Verordnung</div>
      </div>""",
    "Startseite: Kachel 'Gene noch offen' durch Wirkstoffzahl ersetzen", wo="script")

# Die Aussage stimmt nicht - 611 gelesene und 437 fehlende Stellen auf einem
# Zielpanel sind keine vollstaendige Auswertung. Vom Kunden angemerkt.
sub("""    <p>Deine Erbinformation wurde vollst&auml;ndig ausgewertet. Daraus wissen wir, wie dein K&ouml;rper
      Medikamente verarbeitet &mdash; und das gilt f&uuml;r den Rest deines Lebens, denn deine Gene
      &auml;ndern sich nicht mehr.${ihelp('pgx')}</p>""",
    """    <p>Die pharmakogenetisch entscheidenden Gene wurden ausgewertet. Daraus wissen wir, wie dein
      K&ouml;rper diese Medikamente verarbeitet &mdash; und das gilt f&uuml;r den Rest deines Lebens,
      denn deine Gene &auml;ndern sich nicht mehr.${ihelp('pgx')}</p>""",
    "Startseite: 'vollstaendig ausgewertet' richtiggestellt", wo="script")

sub("""    <div><b>Das ist die vollst&auml;ndige Medikamenten-Datenbank</b>, ausgewertet gegen dein Genprofil &mdash;""",
    """    <div><b>Das ist die Medikamenten-Datenbank</b>, ausgewertet gegen dein Genprofil &mdash;""",
    "Liste: 'vollstaendige Datenbank' richtiggestellt", wo="script")

# ================================================== Wirkstoffzahl je Gen
# GENE_DRUGS kannte nur den Wirkstoff-Datenblock. Ueber PharmCAT steuern aber
# Gene Wirkstoffe, die dort gar nicht eingetragen sind - ABCG2 zeigte deshalb 0,
# obwohl es Rosuvastatin und Allopurinol bestimmt. Lazy, weil PDRUGBY weiter
# unten steht (TDZ, siehe Fallstrick 5).
sub("""/* 5) Anzahl betroffener Medikamente je Gen aus den echten Daten */
const GENE_DRUGS={};
Object.keys(PHENO).forEach(g=>{GENE_DRUGS[g]=0;});
Object.keys(DRUGS).forEach(k=>{
  const d=DRUGS[k];
  const gs=new Set([d.gene].concat(d.genes||[]).filter(Boolean));
  gs.forEach(g=>{if(GENE_DRUGS[g]!==undefined)GENE_DRUGS[g]++;});
});
""", "", "alte GENE_DRUGS-Berechnung entfernen", wo="script")

sub("""/* Kennzahlen der Startseite - erst beim ersten Aufruf berechnet, weil der
   Bewertungs-Zwischenspeicher weiter unten im Skript steht */""",
    """/* Wirkstoffe je Gen. Zaehlt beide Wege: das Feld gene/genes im
   Wirkstoff-Datenblock UND den Genotyp, auf den sich eine
   PharmCAT-Empfehlung stuetzt. Nur der erste Weg gezaehlt hiess bei ABCG2
   "0 Medikamente", obwohl es Rosuvastatin und Allopurinol steuert. */
var _gdc=null;
function geneDrugCount(g){
  if(!_gdc){
    const t={};
    Object.keys(PHENO).forEach(x=>{t[x]=new Set();});
    Object.keys(DRUGS).forEach(k=>{
      const d=DRUGS[k];
      new Set([d.gene].concat(d.genes||[]).filter(Boolean)).forEach(x=>{if(t[x])t[x].add(k);});
      const pr=pharmRec(k);
      if(pr)pr.alle.forEach(r=>Object.keys(t).forEach(x=>{if((r.gt||'').indexOf(x)>=0)t[x].add(k);}));
    });
    _gdc={};
    Object.keys(t).forEach(x=>{_gdc[x]=t[x].size;});
  }
  return _gdc[g]||0;
}
/* Kennzahlen der Startseite - erst beim ersten Aufruf berechnet, weil der
   Bewertungs-Zwischenspeicher weiter unten im Skript steht */""",
    "geneDrugCount: PharmCAT-Gene mitzaehlen", wo="script")

# ============================================ Die Matrix, einmal statt zweimal
sub("""function geneDetailHtml(g){
  const lvl=PHENO[g]?PHENO[g].lvl:2, gn=GENO[g];
  const rows=[
    {lvl:2,sev:'ok',t:"Normaler Metabolisierer",e:"Abbau bzw. Aktivierung wie erwartet (100 %)",d:"Standarddosis"},
    {lvl:1,sev:'warn',t:"Intermedi&auml;rer Metabolisierer",e:"Abbau bzw. Aktivierung vermindert (ca. 50 %)",d:"Dosis reduzieren"},
    {lvl:3,sev:'warn',t:"Ultraschneller Metabolisierer",e:"Abbau bzw. Aktivierung beschleunigt (ca. 200 %)",d:"Dosis erh&ouml;hen"},
    {lvl:0,sev:'crit',t:"Langsamer Metabolisierer",e:"Kaum Abbau bzw. Aktivierung (ca. 0 %)",d:"Anderes Medikament"}
  ];
  const src=(ANNOS[g]&&ANNOS[g].length)?"CPIC + DPWG":"&mdash;";
  return `<div class="subh" style="margin-top:0">Empfehlungsmatrix</div>
    <div class="mx h"><div></div><div>Metabolisierertyp</div><div>Wirkung auf das Medikament</div><div>Empfehlung</div><div class="mxs" style="text-align:right">Leitlinie</div></div>
    ${rows.map(r=>`<div class="mx m-${r.sev} ${r.lvl===lvl?'you':''}">
      <div>${ico(r.sev==='ok'?'st-ok':'st-excl','s-'+r.sev,20)}</div>
      <div><b>${r.t}</b>${r.lvl===lvl?'<span class="yb">Dein Ergebnis</span>':''}</div>
      <div>${r.e}</div><div class="mxd t-${r.sev}"><b>${r.d}</b></div>
      <div class="mxs" style="text-align:right;color:var(--muted);font-size:10.5px">${src}</div></div>`).join('')}
    <div class="subh">Regulatorische Annotationen</div>
    ${(ANNOS[g]||[["&mdash;","Keine Annotation hinterlegt."]]).map(a=>`<div class="anno"><b>${a[0]}</b> &mdash; ${a[1]}</div>`).join('')}
    <div class="subh">Quellen und Evidenz</div>
    <div class="anno">Genotyp <b>${gn?gn.genotyp:'&mdash;'}</b> &middot; untersuchte Allele: ${gn?gn.allele:'&mdash;'}<br>
      Beeinflusst <b>${GENE_DRUGS[g]||0}</b> Medikamente in der Datenbank.</div>
    <div class="srcrow"><a class="srclink" href="https://www.pharmgkb.org/search?query=${encodeURIComponent(g)}" target="_blank" rel="noopener">Zur Quelle</a></div>`;
}""",
    """/* Die Skala haengt davon ab, was das Gen tut. Ein Transporter
   metabolisiert nichts, ein Ziel- oder Risikogen erst recht nicht - dort
   stand vorher trotzdem "Langsamer Metabolisierer". Keine Prozentzahlen
   mehr: die frueheren 100/50/200/0 % standen in keiner Quelle. */
const MXSKALA={
  enz:[{lvl:2,sev:'ok',  t:"Normaler Metabolisierer",       e:"baut den Wirkstoff wie erwartet ab"},
       {lvl:1,sev:'warn',t:"Intermedi&auml;rer Metabolisierer", e:"baut langsamer ab, der Wirkstoff reichert sich an"},
       {lvl:3,sev:'warn',t:"Ultraschneller Metabolisierer",  e:"baut schneller ab, der Wirkstoff ist frueher wieder weg"},
       {lvl:0,sev:'crit',t:"Langsamer Metabolisierer",       e:"baut kaum ab, der Wirkstoff bleibt lange im Koerper"}],
  trans:[{lvl:2,sev:'ok',  t:"Normale Transportfunktion",       e:"schleust den Wirkstoff wie erwartet durch"},
       {lvl:1,sev:'warn',t:"Verminderte Transportfunktion",   e:"schleust langsamer durch, der Wirkstoff bleibt laenger"},
       {lvl:3,sev:'warn',t:"Erhoehte Transportfunktion",      e:"schleust schneller durch"},
       {lvl:0,sev:'crit',t:"Stark verminderte Transportfunktion", e:"schleust kaum durch, der Wirkstoff bleibt deutlich laenger"}]
};
/* Die Einordnung des Gens - fuer Stoffwechsel- und Transportgene als Skala
   mit der eigenen Stufe hervorgehoben, fuer Ziel- und Risikogene als
   schlichter Befund, weil es dort keine Skala gibt. */
function mxHtml(g){
  const p=PHENO[g]||{}, lvl=p.lvl===undefined?2:p.lvl;
  const skala=MXSKALA[p.art];
  const src=(ANNOS[g]&&ANNOS[g].length)?"CPIC / DPWG":"&mdash;";
  if(!skala){
    const sev=lvl===2?'ok':lvl===1?'warn':lvl===0?'crit':'ok';
    return `<div class="subh" style="margin-top:0">Dein Befund</div>
      <div class="mx m-${sev} you" style="grid-template-columns:26px 1.2fr 1.9fr 108px">
        <div>${ico(sev==='ok'?'st-ok':'st-excl','s-'+sev,20)}</div>
        <div><b>${p.de||p.phen||'&mdash;'}</b><span class="yb">Dein Ergebnis</span></div>
        <div>${p.rolle?'Zust&auml;ndig f&uuml;r '+p.rolle:'&mdash;'}</div>
        <div class="mxs" style="text-align:right;color:var(--muted);font-size:10.5px">${src}</div></div>`;
  }
  return `<div class="subh" style="margin-top:0">Wo du auf der Skala stehst</div>
    <div class="mx h"><div></div><div>Stufe</div><div>was das hei&szlig;t</div><div class="mxs" style="text-align:right">Leitlinie</div></div>
    ${skala.map(r=>`<div class="mx m-${r.sev} ${r.lvl===lvl?'you':''}">
      <div>${ico(r.sev==='ok'?'st-ok':'st-excl','s-'+r.sev,20)}</div>
      <div><b>${r.t}</b>${r.lvl===lvl?'<span class="yb">Dein Ergebnis</span>':''}</div>
      <div>${r.e}</div>
      <div class="mxs" style="text-align:right;color:var(--muted);font-size:10.5px">${src}</div></div>`).join('')}`;
}
/* Herkunft und Belege - unter der Einordnung, in beiden Ansichten gleich */
function mxQuellen(g){
  const gn=GENO[g], nd=geneDrugCount(g);
  return `${(ANNOS[g]&&ANNOS[g].length)?`<div class="subh">Regulatorische Annotationen</div>
    ${ANNOS[g].map(a=>`<div class="anno"><b>${a[0]}</b> &mdash; ${a[1]}</div>`).join('')}`:''}
    <div class="subh">Quellen und Evidenz</div>
    <div class="anno">Genotyp <b>${gn?gn.genotyp:'&mdash;'}</b>${gn&&gn.allele?' &middot; untersuchte Allele: '+gn.allele:''}<br>
      ${nd?`Bestimmt die Bewertung von <b>${nd}</b> Wirkstoff${nd===1?'':'en'} dieser Datenbank.`
          :'Kein Wirkstoff dieser Datenbank haengt an diesem Gen.'}</div>
    <div class="srcrow"><a class="srclink" href="https://www.pharmgkb.org/search?query=${encodeURIComponent(g)}" target="_blank" rel="noopener">Zur Quelle</a></div>`;
}
function geneDetailHtml(g){
  return mxHtml(g)+mxQuellen(g);
}""",
    "Genansicht: rollenabhaengige Skala statt fester Metabolisierer-Matrix", wo="script")

# Der zweite, fast gleiche Block im aufklappbaren Gen-Eintrag
sub("""  const key=ctx+":"+g,open=openGenes[key],gn=GENO[g];
  const rows=[
    {lvl:2,sev:'ok',t:"Normaler Metabolisierer",e:"Abbau bzw. Aktivierung wie erwartet (100 %)",d:"Standarddosis"},
    {lvl:1,sev:'warn',t:"Intermedi&auml;rer Metabolisierer",e:"Abbau bzw. Aktivierung vermindert (ca. 50 %)",d:"Dosis reduzieren"},
    {lvl:3,sev:'warn',t:"Ultraschneller Metabolisierer",e:"Abbau bzw. Aktivierung beschleunigt (ca. 200 %)",d:"Dosis erh&ouml;hen"},
    {lvl:0,sev:'crit',t:"Langsamer Metabolisierer",e:"Kaum Abbau bzw. Aktivierung (ca. 0 %)",d:"Anderes Medikament"}
  ];
  const src=(ANNOS[g]&&ANNOS[g].length)?"CPIC + DPWG":"&mdash;";
  return `<div class="gitem ${open?'open':''}">""",
    """  const key=ctx+":"+g,open=openGenes[key],gn=GENO[g];
  return `<div class="gitem ${open?'open':''}">""",
    "Gen-Eintrag: doppelte Matrix entfernen", wo="script")

sub("""    <div class="gitem-b">
      <div class="subh">Empfehlungsmatrix</div>
      <div class="mx h"><div></div><div>Metabolisierertyp</div><div>Wirkung auf das Medikament</div><div>Empfehlung</div><div class="mxs" style="text-align:right">Leitlinie</div></div>
      ${rows.map(r=>`<div class="mx m-${r.sev} ${r.lvl===lvl?'you':''}">
        <div>${ico(r.sev==='ok'?'st-ok':'st-excl','s-'+r.sev,20)}</div>
        <div><b>${r.t}</b>${r.lvl===lvl?'<span class="yb">Dein Ergebnis</span>':''}</div>
        <div>${r.e}</div><div class="mxd t-${r.sev}"><b>${r.d}</b></div>
        <div class="mxs" style="text-align:right;color:var(--muted);font-size:10.5px">${src}</div></div>`).join('')}
      <div class="subh">Regulatorische Annotationen</div>
      ${(ANNOS[g]||[["&mdash;","Keine Annotation hinterlegt."]]).map(a=>`<div class="anno"><b>${a[0]}</b> &mdash; ${a[1]}</div>`).join('')}
      <div class="subh">Quellen und Evidenz</div>
      <div class="anno">Genotyp <b>${gn?gn.genotyp:'&mdash;'}</b> &middot; untersuchte Allele: ${gn?gn.allele:'&mdash;'}<br>
        Beeinflusst <b>${GENE_DRUGS[g]||0}</b> Medikamente in der Datenbank.</div>
      <div class="srcrow"><a class="srclink" href="https://www.pharmgkb.org/search?query=${encodeURIComponent(g)}" target="_blank" rel="noopener">Zur Quelle</a></div>
    </div></div>`;""",
    """    <div class="gitem-b">${mxHtml(g)}${mxQuellen(g)}</div></div>`;""",
    "Gen-Eintrag: gemeinsame Skala verwenden", wo="script")

# Im Bericht steht die Zahl ebenfalls
sub("""        &middot; beeinflusst <b>${GENE_DRUGS[g]||0}</b> Wirkstoffe der Datenbank""",
    """        &middot; beeinflusst <b>${geneDrugCount(g)}</b> Wirkstoffe der Datenbank""",
    "Arztbericht: Wirkstoffzahl je Gen korrigiert", wo="script")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
assert "GENE_DRUGS" not in s, "GENE_DRUGS ist noch im Code"
for name in ("function mxHtml(", "function mxQuellen(", "function geneDrugCount("):
    assert s.count(name) == 1, "%s nicht genau einmal definiert" % name
assert "Empfehlungsmatrix" not in s, "alte Matrix-Ueberschrift noch vorhanden"
assert s.count("sf-unk") == 1, "Ampelfilter 'Offen' nicht sauber entfernt"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
