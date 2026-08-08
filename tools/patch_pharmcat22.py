# -*- coding: utf-8 -*-
"""
Vier Punkte aus Daniels Rueckmeldung vom 2026-08-08.

1. BILANZ PROMINENTER, UEBER DIE RECHTE SEITE

   Der schmale Kasten neben der Ueberschrift wird ein Band ueber die volle
   Breite der Einnahmeliste, mit grossen Zahlen.

2. MEHR ALS NUR WECHSELWIRKUNGEN ZAEHLEN

   Vorgabe: "wie viele Wechselwirkungen wir haben, wie viele Medikamente mit
   Alarm, wie viele mit Achtung und wie viele mit OK". Also zwei Gruppen -
   links die Medikamente nach Ampel, rechts die geprueften Paare. Die
   Medikamentenzahlen kommen aus overallSev(), also derselben Stelle wie die
   Kartenfarbe; ein ersetzter Wirkstoff zaehlt mit seiner Ersatzwahl.

3. UNTER "DEINE GENE" ALLES SOFORT ZEIGEN

   Der Nachladeknopf faellt weg, alle 488 Karten stehen sofort da. Gemessen
   hatte das erste Rendern rund 760 ms - vertretbar, und Fallstrick 6 zielte
   auf 2.697 Karten, nicht auf 488. geneLimit bleibt als Variable stehen,
   damit nichts anderes bricht, wird aber nicht mehr zum Abschneiden benutzt.

4. ARZTBERICHT: "17 GENE AUSGEWERTET" WAR FALSCH

   covBlock zaehlte nur die Panel-Gene mit Diplotyp. Ausgewertet werden
   inzwischen alle Gene der Genansicht. Die Tabelle darunter kann das nicht
   spiegeln - sie hat Spalten fuer Diplotyp, Phaenotyp und Score, die es nur
   bei den Panel-Genen gibt. Deshalb: Kennzahl auf die Gesamtzahl, und ueber
   der Tabelle ein Satz, der sagt, was sie zeigt und was nicht.

5. DER WIDERSPRUCH BEI CLOPIDOGREL

   Vorgabe: "auf den Genotyp des Kunden Ruecksicht nehmen und nur dann ein
   Medikament mit Alarm versehen, wenn der Genotyp, den der Patient hat, zu
   einer Anpassung fuehrt."

   Die Ampel tut das bereits - statusFor geht ueber PharmCAT (genotypgenau),
   dann die Matrix (alle Genbedingungen muessen zutreffen), dann den
   Rueckfall mit lvl>=0 auf beiden Seiten. Clopidogrel steht korrekt auf OK.

   Der Widerspruch stand im TEXT: faellt recFor() aus, weil keine Matrixzeile
   zum Genotyp passt, zeigte assessBox ersatzweise d.pro - einen allgemeinen
   Wirkstofftext, der einen ANDEREN Genotyp beschreibt. Bei Clopidogrel:
   "CYP2C19 intermediate metabolizers ... are at increased risk", waehrend
   die Patientin Normal Metabolizer ist. Das las sich wie eine Aussage ueber
   sie.

   24 Wirkstoffe sind betroffen, 6 davon nennen ausdruecklich einen
   Metabolisierertyp. Der Text bleibt erhalten - er ist richtig, nur nicht
   fuer diesen Genotyp -, wandert aber aus dem Kasten "Beurteilung fuer dein
   Genprofil" heraus und bekommt eine eigene Ueberschrift, die sagt, dass er
   andere Genotypen betrifft.
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

# =========================================================== 1+2. Bilanzband
sub("""  /* Bilanz der Wechselwirkungen im Kopf der Einnahmeliste */
  .wshead{display:flex;align-items:flex-start;gap:18px;flex-wrap:wrap;justify-content:space-between}
  .wshead>div:first-child{min-width:0;flex:1 1 260px}
  .ixscore{flex:none;background:var(--panel);border:1.5px solid var(--line2);border-radius:14px;
    padding:11px 14px;min-width:210px}
  /* 11px ist die Untergrenze der Pruefroutine (Abschnitt 7) - nicht darunter */
  .ixscore .ist{font-size:11px;font-weight:800;letter-spacing:.09em;text-transform:uppercase;
    color:var(--faint);margin-bottom:7px}
  .ixscore .isr{display:flex;align-items:center;gap:8px;font-size:12.5px;line-height:1.7}
  .ixscore .isn{flex:none;min-width:20px;font-weight:800;font-variant-numeric:tabular-nums;text-align:right}
  .ixscore .isd{flex:none;width:9px;height:9px;border-radius:50%}
  .ixscore .isr.crit .isn{color:var(--crit-t)} .ixscore .isr.crit .isd{background:var(--crit)}
  .ixscore .isr.warn .isn{color:var(--warn-t)} .ixscore .isr.warn .isd{background:var(--warn)}
  .ixscore .isr.done .isn{color:var(--muted)}  .ixscore .isr.done .isd{background:#9A93A3}
  .ixscore .isr.ok .isn{color:var(--ok-t)}     .ixscore .isr.ok .isd{background:var(--ok)}
  .ixscore .issum{margin-top:8px;padding-top:8px;border-top:1px solid var(--line);
    font-size:11.5px;color:var(--faint)}""",
    """  /* Bilanzband ueber die volle Breite der Einnahmeliste */
  .ixscore{background:var(--panel);border:1.5px solid var(--line2);border-radius:16px;
    padding:15px 18px;margin:2px 0 18px}
  .ixs-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px 26px}
  @media(max-width:760px){.ixs-grid{grid-template-columns:1fr}}
  /* 11px ist die Untergrenze der Pruefroutine (Abschnitt 7) - nicht darunter */
  .ixs-col>.ist{font-size:11px;font-weight:800;letter-spacing:.09em;text-transform:uppercase;
    color:var(--faint);margin-bottom:9px}
  .ixs-row{display:flex;gap:18px;flex-wrap:wrap}
  .ixs-k{display:flex;align-items:baseline;gap:7px;min-width:0}
  .ixs-n{font-size:26px;font-weight:800;line-height:1;font-variant-numeric:tabular-nums;
    letter-spacing:-.02em}
  .ixs-l{font-size:12px;font-weight:700;color:var(--muted);line-height:1.25}
  .ixs-k.crit .ixs-n{color:var(--crit-t)} .ixs-k.warn .ixs-n{color:var(--warn-t)}
  .ixs-k.ok .ixs-n{color:var(--ok-t)}     .ixs-k.done .ixs-n{color:#7A7382}
  .ixs-k.neutral .ixs-n{color:var(--ink)}
  .ixs-k.null .ixs-n{color:var(--faint)}  .ixs-k.null .ixs-l{color:var(--faint)}
  .ixs-sum{margin-top:10px;padding-top:9px;border-top:1px solid var(--line);
    font-size:11.5px;color:var(--faint)}""",
    "CSS: Bilanz als Band", wo="style")

sub("""function ixScoreHtml(){
  const z=ixScore();
  if(z.paare<1)return '';
  const zeile=(k,c,l)=>c?`<div class="isr ${k}"><span class="isd"></span>
    <span class="isn">${c}</span><span>${l}</span></div>`:'';
  return `<div class="ixscore">
    <div class="ist">Wechselwirkungen</div>
    ${zeile('crit',z.crit,z.crit===1?'Alarm':'mit Alarm')}
    ${zeile('warn',z.warn,z.warn===1?'Achtung':'mit Achtung')}
    ${zeile('done',z.done,z.done===1?'gel&ouml;st':'gel&ouml;st')}
    ${zeile('ok',z.ok,'unauff&auml;llig')}
    <div class="issum">${z.paare} Paar${z.paare===1?'':'e'} gepr&uuml;ft</div>
  </div>`;
}""",
    """/* Die Medikamente nach Ampel - aus overallSev(), also derselben Stelle wie
   die Kartenfarbe. Ein ersetzter Wirkstoff zaehlt mit seiner Ersatzwahl. */
function medScore(){
  const z={crit:0,warn:0,ok:0,unk:0};
  workspace.forEach(id=>{
    const ersatz=altChoice[id]?findDrug(altChoice[id]):null;
    const s=overallSev(ersatz||id,workspace);
    z[s]=(z[s]||0)+1;
  });
  return z;
}
function ixScoreHtml(){
  if(!workspace.length)return '';
  const z=ixScore(), m=medScore();
  const kachel=(k,c,l)=>`<div class="ixs-k ${c?k:'null'}">
    <span class="ixs-n">${c}</span><span class="ixs-l">${l}</span></div>`;
  return `<div class="ixscore">
    <div class="ixs-grid">
      <div class="ixs-col">
        <div class="ist">Deine Medikamente</div>
        <div class="ixs-row">
          ${kachel('neutral',workspace.length,'auf der Liste')}
          ${kachel('crit',m.crit,'mit Alarm')}
          ${kachel('warn',m.warn,'mit Achtung')}
          ${kachel('ok',m.ok,'unauff&auml;llig')}
        </div>
      </div>
      <div class="ixs-col">
        <div class="ist">Wechselwirkungen</div>
        <div class="ixs-row">
          ${kachel('crit',z.crit,'mit Alarm')}
          ${kachel('warn',z.warn,'mit Achtung')}
          ${kachel('done',z.done,'gel&ouml;st')}
          ${kachel('ok',z.ok,'unauff&auml;llig')}
        </div>
        <div class="ixs-sum">${z.paare} Paar${z.paare===1?'':'e'} gepr&uuml;ft &mdash;
          jede Kombination deiner Medikamente einzeln</div>
      </div>
    </div>
  </div>`;
}""",
    "Bilanz: Medikamente und Wechselwirkungen", wo="script")

sub("""      <div class="wshead">
        <div>
          <h2 class="wstitle">${PATIENT}, das sind <em>deine</em> Medikamente</h2>
          <p class="wssub">${workspace.length} aktiv eingenommene Medikamente &middot; nach Bewertung sortiert</p>
        </div>
        ${ixScoreHtml()}
      </div>""",
    """      <h2 class="wstitle">${PATIENT}, das sind <em>deine</em> Medikamente</h2>
      <p class="wssub">${workspace.length} aktiv eingenommene Medikamente &middot; nach Bewertung sortiert</p>
      ${ixScoreHtml()}""",
    "Bilanzband ueber die volle Breite", wo="script")

# ================================================ 3. Genansicht ohne Nachladen
sub("""  ${(()=>{const k=geneListe(),z=geneZahlen();
    const zeig=k.slice(0,geneLimit);
    return `<div class="genecount">${z.alle} Gene ausgewertet${
      k.length>geneLimit?' &middot; '+geneLimit+' angezeigt':''}</div>
    <div class="genegrid">${zeig.map(g=>geneCardHtml(g)).join('')}</div>
    ${k.length>geneLimit?`<button class="moreb" onclick="moreGene()">Weitere
      ${Math.min(240,k.length-geneLimit)} von ${(k.length-geneLimit).toLocaleString('de-DE')}
      anzeigen ${ico('chev','',16)}</button>`:''}`;})()}`;""",
    """  ${(()=>{const k=geneListe(),z=geneZahlen();
    /* Alle Karten sofort, kein Nachladeknopf (Vorgabe Daniel, 2026-08-08).
       488 Karten kosten rund 760 ms beim ersten Rendern - Fallstrick 6 zielte
       auf 2.697 Karten in der Wirkstoffliste, nicht auf diese Groessenordnung. */
    return `<div class="genecount">${z.alle} Gene ausgewertet</div>
    <div class="genegrid">${k.map(g=>geneCardHtml(g)).join('')}</div>`;})()}`;""",
    "Genansicht: alle Karten sofort", wo="script")

# ============================================ 4. Arztbericht: richtige Genzahl
sub("""        <div class="cov-k"><span class="n">${zeigbar.length}</span><span class="l">Gene ausgewertet</span></div>""",
    """        <div class="cov-k"><span class="n">${geneListe().length}</span><span class="l">Gene ausgewertet</span></div>""",
    "Arztbericht: alle ausgewerteten Gene zaehlen", wo="script")

sub("""      <table class="cov-tab">
        <thead><tr><th>Gen</th><th>Diplotyp</th><th>Ph&auml;notyp</th><th>Score</th>""",
    """      <p class="cov-p">Die Tabelle f&uuml;hrt die <b>${zeigbar.length} Gene mit
        Diplotyp-Auswertung</b> aus dem PharmCAT-Panel. Die &uuml;brigen Gene werden
        &uuml;ber einzelne Positionen bewertet und stehen unter &bdquo;Deine Gene&ldquo;.</p>
      <table class="cov-tab">
        <thead><tr><th>Gen</th><th>Diplotyp</th><th>Ph&auml;notyp</th><th>Score</th>""",
    "Arztbericht: Tabelle einordnen", wo="script")

# ====================================== 5. Kein fremder Genotyp als Beurteilung
sub("""    :(d.pro?`<div class="ab-sep"></div><div class="ab-g"><div class="ab-gx">${d.pro}</div>
        <div class="ab-gs">PharmGKB &middot; Originaltext englisch${ihelp('leit')}</div></div>`
      :`<div class="ab-sep"></div>
        <div class="ab-none">F&uuml;r diesen Wirkstoff liegt keine genotypspezifische
          Leitlinien-Empfehlung vor.</div>`)}""",
    """    :`<div class="ab-sep"></div>
        ${pharmRec(id)?'':`<div class="ab-none">F&uuml;r deinen Genotyp liegt zu diesem
          Wirkstoff keine Leitlinien-Empfehlung vor.</div>`}
        ${d.pro?`<div class="ab-g ab-fremd">
          <div class="ab-gh">${ico('c-search','',15)} Gilt f&uuml;r andere Genotypen
            <span class="ab-gt">nicht auf dich zutreffend</span></div>
          <div class="ab-gx">${d.pro}</div>
          <div class="ab-gs">PharmGKB &middot; Originaltext englisch${ihelp('leit')}</div></div>`:''}`}""",
    "assessBox: fremder Genotyp klar abgesetzt", wo="script")

sub("""  .abox{""",
    """  /* Text, der einen anderen Genotyp beschreibt als den des Patienten. Steht
     bewusst blass und mit eigener Ueberschrift, damit er nicht als Aussage
     ueber diese Person gelesen wird - genau das war bei Clopidogrel der Fall. */
  .ab-fremd{opacity:.72;border-left:3px solid var(--line2);padding-left:11px;margin-top:10px}
  .ab-fremd .ab-gh{color:var(--faint)}
  .abox{""",
    "CSS: fremder Genotyp abgesetzt", wo="style")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
assert s.count("function medScore(") == 1, "medScore nicht genau einmal vorhanden"
assert "moreGene()" not in s.split("function vGene(")[1].split("function ")[0], \
    "Nachladeknopf steht noch in der Genansicht"
assert "ab-fremd" in s, "Absetzung des fremden Genotyps fehlt"
assert s.count("${d.pro}") == 1, "d.pro wird an mehreren Stellen gezeigt"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
