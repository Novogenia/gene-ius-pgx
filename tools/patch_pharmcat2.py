# -*- coding: utf-8 -*-
"""
Zweiter Teil: die Ansichten. Gen-Karten mit offenem Ergebnis, vierter
Filterknopf, vierte Kennzahl, Abdeckungsblock im Arztbericht.

Jede Ersetzung wird zugesichert.
"""
import io

APP = "pgx_app.html"
GEN = "patch_app_data.py"
s = io.open(APP, encoding="ascii").read()
orig = len(s)
n = 0

def sub(alt, neu, was, anzahl=1):
    global s, n
    c = s.count(alt)
    assert c == anzahl, "PATCH '%s': %d erwartet, %d gefunden" % (was, anzahl, c)
    s = s.replace(alt, neu)
    n += 1
    print("  ok  %s" % was)

def sub_gen(alt, neu, was):
    """Dieselbe Aenderung im Generator, sonst ist sie beim naechsten Lauf weg."""
    g = io.open(GEN, encoding="utf-8").read()
    assert g.count(alt) == 1, "GENERATOR '%s': nicht eindeutig" % was
    io.open(GEN, "w", encoding="utf-8", newline="\n").write(g.replace(alt, neu))
    print("  ok  %s (auch im Generator)" % was)

print("Patche %s (%d Zeichen)" % (APP, orig))

# =================================================== 1. DBSTATS um unk (2x!)
A = "  if(!_dbstat){const t={total:0,ok:0,warn:0,crit:0};"
B = "  if(!_dbstat){const t={total:0,ok:0,warn:0,crit:0,unk:0};"
sub(A, B, "DBSTATS um den offenen Fall erweitern")
sub_gen(A, B, "DBSTATS um den offenen Fall erweitern")

# ============================================ 2. Gen-Karte: offener Zustand
sub("""  const short=LVL[lvl].t;
  const colr=sv==='ultra'?'#0b6b36':sv==='ok'?'var(--ok-t)':sv==='warn'?'var(--warn-t)':'var(--crit-t)';""",
    """  const short=lvlLabel(g).t;
  const colr=sv==='ultra'?'#0b6b36':sv==='ok'?'var(--ok-t)':sv==='warn'?'var(--warn-t)'
    :sv==='unk'?'var(--unk-t)':'var(--crit-t)';
  /* Bei offenem Ergebnis gehoert der Grund auf die Karte. Ohne den steht dort
     nur "Nicht bestimmbar" und der Nutzer haelt es fuer einen Anzeigefehler. */
  const why=lvl<0?`<div class="gwhy">${gwhyText(g)}</div>`:'';""",
    "Gen-Karte: Farbe und Begruendung fuer den offenen Zustand")

# Begruendungstext + Rolle des Gens
sub("function geneCardHtml(g,opts){",
    """/* Warum ein Gen kein eindeutiges Ergebnis hat - direkt aus dem PharmCAT-Lauf */
function gwhyText(g){
  const p=PHENO[g], gn=GENO[g]||{};
  if(!p)return 'Dieses Gen war nicht Teil der Auswertung.';
  if(p.mehr)return '<b>Mehrere Varianten m&ouml;glich.</b> Die gelesenen Stellen schlie&szlig;en '
    +'sich nicht auf ein Ergebnis ein &mdash; es bleiben <b>'+p.kand+'</b> Kombinationen offen. '
    +'Daf&uuml;r fehlen '+gn.fehlt+' der insgesamt '+(gn.pos+gn.fehlt)+' Stellen, die dieses Gen '
    +'braucht.';
  return '<b>Kein Ergebnis.</b> Von den '+(gn.pos+gn.fehlt)+' Stellen, die dieses Gen braucht, '
    +'konnten '+gn.fehlt+' nicht gelesen werden'
    +(gn.pos?' &mdash; die '+gn.pos+' gelesenen reichen nicht aus.':'.');
}
function geneCardHtml(g,opts){""",
    "Begruendungstext fuer offene Gene")

sub("""  if(opts.flat)return `<div class="genebox flat b-${sv}">
    <div class="gb-top"><div class="gb-ic gi-${sv}">${helix(lvl)}</div>
      <div class="gb-tx"><div class="gn">${g}</div><div class="gs" style="color:${colr}">${short}</div></div></div>
    <div class="gsrow"><div class="genepair">${genePair(lvl)}</div>
      <div class="gsbar"><div class="gscale">${segs}</div><div class="gs-lab">${labs}</div></div></div></div>`;""",
    """  if(opts.flat)return `<div class="genebox flat b-${sv}">
    <div class="gb-top"><div class="gb-ic gi-${sv}">${helix(lvl)}</div>
      <div class="gb-tx"><div class="gn">${g}</div><div class="gs" style="color:${colr}">${short}</div></div></div>
    <div class="gsrow"><div class="genepair">${genePair(lvl)}</div>
      <div class="gsbar"><div class="gscale">${segs}</div><div class="gs-lab">${labs}</div></div></div>
    ${why}</div>`;""",
    "Gen-Karte flach: Begruendung anhaengen")

sub("""    <div class="gsrow"><div class="genepair">${genePair(lvl)}</div>
      <div class="gsbar"><div class="gscale">${segs}</div><div class="gs-lab">${labs}</div></div></div>
    <div class="gexp" onclick="event.stopPropagation()">""",
    """    <div class="gsrow"><div class="genepair">${genePair(lvl)}</div>
      <div class="gsbar"><div class="gscale">${segs}</div><div class="gs-lab">${labs}</div></div></div>
    ${why}
    <div class="gexp" onclick="event.stopPropagation()">""",
    "Gen-Karte aufklappbar: Begruendung anhaengen")

# copiesHtml: statt "keine Kopien hinterlegt" den echten Grund nennen
sub("""  if(!cps.length)return `<div class="anno">F&uuml;r dieses Gen sind keine Einzelkopien hinterlegt.</div>`;""",
    """  if(!cps.length){
    const gn=GENO[g]||{};
    const kand=(gn.alt&&gn.alt.length)
      ? `<div class="anno" style="margin-top:7px">M&ouml;gliche Kombinationen (Auszug):
           <b class="mono">${gn.alt.slice(0,8).join(' &middot; ')}</b>${gn.kand>8?' &hellip;':''}</div>`
      : '';
    return `<div class="anno">${gwhyText(g)}</div>${kand}`;
  }""",
    "Genkopien: echten Grund statt Platzhalter")

# plainSentence: offener Fall zuerst
sub("""function plainSentence(g){
  const cps=geneCopies(g), fns=cps.map(c=>c[1]);""",
    """function plainSentence(g){
  const p=PHENO[g];
  if(p&&p.lvl<0)return 'Von jedem Elternteil hast du eine Kopie des Gens <b>'+g+'</b> geerbt. '
    +'Welche genau, l&auml;sst sich aus dieser Analyse nicht sicher sagen &mdash; '
    +(p.mehr?'es bleiben mehrere Varianten m&ouml;glich':'die daf&uuml;r n&ouml;tigen Stellen wurden nicht gelesen')
    +'. Deshalb steht hier bewusst kein Ergebnis statt einer Vermutung.'
    +(p.rolle?' Dieses Gen ist zust&auml;ndig f&uuml;r: '+p.rolle+'.':'');
  const cps=geneCopies(g), fns=cps.map(c=>c[1]);""",
    "Klartext: offener Fall vorweg")

# techToggleHtml: gelesene Positionen und nicht rufbare Allele zeigen
sub("""      <div class="achips">${chips}</div></div>`;
}
function toggleTech(k){""",
    """      <div class="achips">${chips}</div>
      ${(GENO[g]&&GENO[g].var&&GENO[g].var.length)?`<div class="anno" style="margin-top:9px">
        Gelesene Stellen (${GENO[g].var.length}):
        ${GENO[g].var.slice(0,24).map(v=>`<b class="mono">${v[0]} ${v[1]}</b>`).join(' &middot; ')}
        ${GENO[g].var.length>24?' &hellip;':''}</div>`:''}
      ${(GENO[g]&&GENO[g].unc&&GENO[g].unc.length)?`<div class="anno" style="margin-top:7px;color:var(--unk-t)">
        Nicht pr&uuml;fbar, weil Stellen fehlen (${GENO[g].unc.length}):
        <b class="mono">${GENO[g].unc.slice(0,24).join(', ')}</b>${GENO[g].unc.length>24?' &hellip;':''}</div>`:''}
      </div>`;
}
function toggleTech(k){""",
    "Fachdetails: gelesene Stellen und Luecken")

# geneReportCard: lvlLabel benutzen
sub("""      <div class="rg-type t-${sv==='ultra'?'ok':sv}">${LVL[lvl].t}
        <span class="rg-kuerzel">${LVL[lvl].k}</span></div>""",
    """      <div class="rg-type t-${sv==='ultra'?'ok':sv}">${lvlLabel(g).t}
        <span class="rg-kuerzel">${lvlLabel(g).k}</span></div>
      ${PHENO[g]&&PHENO[g].rolle?`<div class="rg-sub" style="margin-top:2px">Zust&auml;ndig f&uuml;r
        ${PHENO[g].rolle}</div>`:''}""",
    "Arztbericht-Genkarte: Bezeichnung und Rolle")

# geneItemHtml: offener Fall
sub("""  const lvl=PHENO[g]?PHENO[g].lvl:2, sev=lvl===2||lvl===3?'ok':lvl===1?'warn':'crit';
  const key=ctx+":"+g,open=openGenes[key],gn=GENO[g];""",
    """  const lvl=PHENO[g]?PHENO[g].lvl:2;
  const sev=lvl<0?'unk':lvl===2||lvl===3?'ok':lvl===1?'warn':'crit';
  const key=ctx+":"+g,open=openGenes[key],gn=GENO[g];""",
    "Gen-Eintrag: offener Fall")

sub("""      <span class="gstat t-${sev}">${LVL[lvl].t}</span>""",
    """      <span class="gstat t-${sev}">${lvlLabel(g).t}</span>""",
    "Gen-Eintrag: Bezeichnung aus lvlLabel")

# =============================================== 3. Filter und Kennzahlen
sub("""    {k:'ok',    sev:'ok',   cls:'bf-ok',   lab:'Unauff&auml;llig', cnt:n('ok'),    txt:'Standarddosis ist f&uuml;r dich passend.'}
  ];""",
    """    {k:'ok',    sev:'ok',   cls:'bf-ok',   lab:'Unauff&auml;llig', cnt:n('ok'),    txt:'Standarddosis ist f&uuml;r dich passend.'},
    {k:'unk',   sev:'unk',  cls:'bf-unk',  lab:'Offen',            cnt:n('unk'),   txt:'Ein n&ouml;tiges Gen ist nicht bestimmbar.'}
  ];""",
    "Grosser Filterknopf fuer den offenen Fall")

sub("""      <button class="sfb sf-ok" aria-pressed="${!fWatch&&fSev==='ok'}" onclick="setSev('ok')">
        ${ico('st-ok','',16)} OK</button>""",
    """      <button class="sfb sf-ok" aria-pressed="${!fWatch&&fSev==='ok'}" onclick="setSev('ok')">
        ${ico('st-ok','',16)} OK</button>
      <button class="sfb sf-unk" aria-pressed="${!fWatch&&fSev==='unk'}" onclick="setSev('unk')">
        ${ico('c-search','',16)} Offen</button>""",
    "Ampelfilter fuer den offenen Fall")

# Einleitung: vierte Kachel mit den gerufenen Positionen
sub("""  const auff=Object.keys(PHENO).filter(g=>PHENO[g].lvl!==2).length;""",
    """  /* auffaellig = weicht vom Normalen ab. Offene Gene sind NICHT auffaellig,
     die zaehlen getrennt - sonst wird eine Wissenslueke als Befund verkauft. */
  const auff=Object.keys(PHENO).filter(g=>PHENO[g].lvl>=0&&PHENO[g].lvl!==2).length;
  const offen=Object.keys(PHENO).filter(g=>PHENO[g].lvl<0).length;
  const nGene=Object.keys(PHENO).length;""",
    "Kennzahl: auffaellig und offen trennen")

sub("""      <div class="hstat">
        <div class="hsic">${ico('n-dna','',22)}</div>
        <div class="hsn">233</div>
        <div class="hsl">Gene analysiert</div>
        <div class="hsd">der komplette pharmakogenetische Satz</div>
      </div>
      <div class="hstat">
        <div class="hsic">${ico('c-search','',22)}</div>
        <div class="hsn">6.566</div>
        <div class="hsl">Genvariationen untersucht</div>
        <div class="hsd">einzelne Stellen im Erbgut, Punkt f&uuml;r Punkt gelesen</div>
      </div>
      <div class="hstat hs-mark">
        <div class="hsic">${ico('st-excl','',22)}</div>
        <div class="hsn">${auff}</div>
        <div class="hsl">Gene arbeiten anders${ihelp('gene')}</div>
        <div class="hsd">bei dir weicht die Funktion vom Durchschnitt ab</div>
      </div>""",
    """      <div class="hstat">
        <div class="hsic">${ico('n-dna','',22)}</div>
        <div class="hsn">${nGene}</div>
        <div class="hsl">Gene ausgewertet</div>
        <div class="hsd">die pharmakogenetisch entscheidenden Gene</div>
      </div>
      <div class="hstat">
        <div class="hsic">${ico('c-search','',22)}</div>
        <div class="hsn">${nf(P_META.posda)}</div>
        <div class="hsl">Stellen im Erbgut gelesen</div>
        <div class="hsd">einzeln bestimmt, Position f&uuml;r Position</div>
      </div>
      <div class="hstat hs-mark">
        <div class="hsic">${ico('st-excl','',22)}</div>
        <div class="hsn">${auff}</div>
        <div class="hsl">Gene arbeiten anders${ihelp('gene')}</div>
        <div class="hsd">bei dir weicht die Funktion vom Durchschnitt ab</div>
      </div>
      <div class="hstat">
        <div class="hsic">${ico('c-search','',22)}</div>
        <div class="hsn">${offen}</div>
        <div class="hsl">Gene noch offen${ihelp('offen')}</div>
        <div class="hsd">hier reichen die gelesenen Stellen nicht f&uuml;r ein Ergebnis</div>
      </div>""",
    "Einleitung: vier echte Kennzahlen")

sub("""        <span class="hb-t">Medikamente gegen dein Profil gepr&uuml;ft${ihelp('ampel')}<br>
          <span>so verteilen sie sich auf die drei Bewertungen</span></span>""",
    """        <span class="hb-t">Medikamente gegen dein Profil gepr&uuml;ft${ihelp('ampel')}<br>
          <span>so verteilen sie sich auf die Bewertungen</span></span>""",
    "Kennzahlenband: Text auf vier Gruppen")

sub("""        <div class="hbb crit" style="width:${pct(D.crit)}%" title="${nf(D.crit)} mit Alarm"></div>
      </div>""",
    """        <div class="hbb unk"  style="width:${pct(D.unk)}%"  title="${nf(D.unk)} offen"></div>
        <div class="hbb crit" style="width:${pct(D.crit)}%" title="${nf(D.crit)} mit Alarm"></div>
      </div>""",
    "Kennzahlenband: Balken fuer den offenen Fall")

sub("""        <button class="hbk k-crit" onclick="goFilter('crit')">
          <span class="hbkn">${nf(D.crit)}</span>
          <span class="hbkl">mit Alarm</span>
          <span class="hbkd">hier gibt es eine offizielle Handlungsempfehlung</span></button>""",
    """        <button class="hbk k-crit" onclick="goFilter('crit')">
          <span class="hbkn">${nf(D.crit)}</span>
          <span class="hbkl">mit Alarm</span>
          <span class="hbkd">hier gibt es eine offizielle Handlungsempfehlung</span></button>
        <button class="hbk k-unk" onclick="goFilter('unk')">
          <span class="hbkn">${nf(D.unk)}</span>
          <span class="hbkl">noch offen</span>
          <span class="hbkd">ein daf&uuml;r n&ouml;tiges Gen ist nicht bestimmbar</span></button>""",
    "Kennzahlenband: Knopf fuer den offenen Fall")

sub("""    <button class="lg lg-ix" onclick="go('meine')">""",
    """    <button class="lg lg-unk" onclick="goFilter('unk')">
      <div class="lgbox"><span class="lgn">${DBSTATS().unk.toLocaleString('de-DE')}</span><span class="lgl">Offen</span></div>
      <div class="lgtx"><h4>Medikamente, bei denen die Antwort offen bleibt</h4>
        <p>F&uuml;r diese Wirkstoffe gibt es sehr wohl eine Leitlinie &mdash; sie h&auml;ngt aber an
          einem Gen, das <b>in dieser Analyse nicht eindeutig bestimmt werden konnte</b>.
          Statt zu raten wird das offen gelassen. Eine gezielte Nachbestimmung schlie&szlig;t
          diese L&uuml;cke.${ihelp('offen')}</p>
        <span class="lgmore">In der Datenbank ansehen ${ico('arr','',14)}</span></div>
    </button>
    <button class="lg lg-ix" onclick="go('meine')">""",
    "Legende: Box fuer den offenen Fall")

# =============================================== 4. Abdeckungsblock Arztbericht
sub("""  return `<div class="sec-title">F&uuml;r deinen Arzt &mdash; pharmakogenetischer Bericht</div>""",
    """  const nOffen=genes.filter(g=>PHENO[g].lvl<0);
  return `<div class="sec-title">F&uuml;r deinen Arzt &mdash; pharmakogenetischer Bericht</div>
  ${covBlock(nOffen)}""",
    "Arztbericht: Abdeckungsblock einsetzen")

sub("""/* ================= ARZTBERICHT (\"F&uuml;r deinen Arzt\") ================= */""",
    """/* ================= ARZTBERICHT (\"F&uuml;r deinen Arzt\") ================= */
/* Was der Test wirklich lesen konnte. Diese Angaben gehoeren an den Anfang des
   Arztberichts, weil jede Aussage darunter nur so weit tragt wie die Abdeckung. */
function covBlock(offen){
  const M=P_META, ges=M.posda+M.posfehlt;
  const pct=(100*M.posda/ges).toFixed(0);
  const rows=P_GENES.slice().sort((a,b)=>(a.ok===b.ok?0:a.ok?1:-1)||a.g.localeCompare(b.g))
    .map(g=>{
      const zu=g.pos+g.fehlt;
      const st=g.ok?'gerufen':(g.mehr?g.kand+' Varianten offen':'kein Ergebnis');
      return `<tr class="${g.ok?'':'miss'}">
        <td class="mono"><b>${g.g}</b></td>
        <td class="mono">${g.dip||'&mdash;'}</td>
        <td>${g.de||g.phen||'&mdash;'}</td>
        <td class="mono">${g.score||'&mdash;'}</td>
        <td>${g.pos} / ${zu}</td>
        <td>${g.ok?st:`<span class="warnpin">${st}</span>`}</td></tr>`;
    }).join('');
  return `<div class="cov">
    <div class="cov-h">${ico('c-pillbox','',17)} Grundlage dieser Auswertung</div>
    <div class="cov-b">
      <div class="cov-g">
        <div class="cov-k"><span class="n">${P_GENES.length}</span><span class="l">Gene im Panel</span></div>
        <div class="cov-k"><span class="n">${M.posda.toLocaleString('de-DE')}</span><span class="l">Stellen gelesen</span></div>
        <div class="cov-k"><span class="n">${pct}&thinsp;%</span><span class="l">Abdeckung der ben&ouml;tigten Stellen</span></div>
        <div class="cov-k"><span class="n">${offen.length}</span><span class="l">Gene ohne eindeutiges Ergebnis</span></div>
      </div>
      <p class="cov-p">Probe <b>${M.probe}</b> &middot; Referenz <b>${M.build}</b> &middot;
        Allel-Definitionen <b>ClinPGx</b> &middot; Auswertung <b>PharmCAT ${M.ver}</b> &middot;
        Stand <b>${M.stand}</b>.
        ${offen.length?`Bei <b>${offen.map(g=>g).join(', ')}</b> reichen die gelesenen Stellen
          nicht f&uuml;r ein eindeutiges Ergebnis. Diese Gene sind unten als offen gekennzeichnet und
          flie&szlig;en in keine Empfehlung ein.`:''}</p>
      <table class="cov-tab">
        <thead><tr><th>Gen</th><th>Diplotyp</th><th>Ph&auml;notyp</th><th>Score</th>
          <th>Stellen</th><th>Status</th></tr></thead>
        <tbody>${rows}</tbody></table>
    </div></div>`;
}""",
    "Abdeckungsblock als Funktion")

# =============================================== 5. Beurteilungsbox
sub("""    <div class="ab-h">${ico(sev==='ok'?'st-ok':'st-excl','',18)}""",
    """    <div class="ab-h">${ico(sev==='ok'?'st-ok':sev==='unk'?'c-search':'st-excl','',18)}""",
    "Beurteilungsbox: Symbol fuer den offenen Fall")

sub("""        <div class="ab-gs">${rc.gl.length?rc.gl.join(' &middot; '):'PharmGKB'} &middot; Originaltext englisch${ihelp('leit')}</div>
      </div>`""",
    """        <div class="ab-gs">${rc.gl.length?rc.gl.join(' &middot; '):'PharmGKB'} &middot; Originaltext englisch${ihelp('leit')}${rc.om?' &middot; OM '+rc.om:''}</div>
      </div>`""",
    "Beurteilungsbox: OM-Kennung mitgeben")

print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
assert all(ord(c) < 128 for c in s), "Datei ist nicht mehr rein ASCII"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("geschrieben.")
