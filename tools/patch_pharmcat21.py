# -*- coding: utf-8 -*-
"""
Geloeste Wechselwirkungen ausgrauen und eine Bilanz danebenstellen.

Vorgabe Daniel, 2026-08-08: "Wir muessen, wenn wir eine Interaktion geloest
haben, das Ganze zwar noch zeigen, aber ausgegraut zeigen, damit man sieht,
dass es geloest ist. Wir sollten rechts daneben auch noch eine Bewertung von
fuenf Interaktionen, zweimal Alarm und sechsmal OK und dergleichen zeigen,
damit man sieht, wo man so steht."

GELOEST heisst hier: mindestens einer der beiden Partner wurde ersetzt
(altChoice gesetzt). Der urspruengliche Wirkstoff bleibt in der Liste
stehen - durchgestrichen unter "BISHER" -, also bleibt auch die Linie
stehen. Nur eben grau statt rot, mit Haken statt Ausrufezeichen und ohne
Pulsieren.

Drei Stellen, nicht nur die Linie:

  a) drawLinks  - graue Linie, Haken im Knopf, keine Animation
  b) overallSev - eine geloeste Interaktion faerbt die Karte nicht mehr.
     Ohne das steht Clopidogrel weiter auf ALARM, obwohl der Partner
     Omeprazol laengst durch Dexlansoprazol ersetzt ist. Genau das war im
     Screenshot zu sehen. Die Ampel muss der Loesung folgen, sonst ist das
     Ausgrauen nur Kosmetik.
  c) ixBox      - dasselbe fuer die Box auf der Karte.

DIE BILANZ zaehlt Paare, nicht Wirkstoffe. Bei 4 Medikamenten sind das
4*3/2 = 6 Paare. Jedes Paar ist genau eines von vier Dingen: Alarm,
Achtung, geloest oder unauffaellig. Die Summe ergibt immer die Paarzahl -
so sieht man, wovon die Zahl kommt, statt nur eine nackte Trefferzahl.

Sie steht im Kopf der Einnahmeliste, rechts neben der Ueberschrift. Der
rechte Randstreifen selbst - wo die runden Knoepfe sitzen - ist mit 79 px
zu schmal fuer Text.
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
sub("""  #wsvg{position:absolute;inset:0;pointer-events:none;z-index:2}""",
    """  #wsvg{position:absolute;inset:0;pointer-events:none;z-index:2}
  /* Bilanz der Wechselwirkungen im Kopf der Einnahmeliste */
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
    "CSS fuer die Interaktionsbilanz", wo="style")

# --------------------------------------- geloest: Begriff und Ampelwirkung
sub("""function ddisFor(id,pool){return DDI.filter(x=>(x.a===id&&pool.includes(x.b))||(x.b===id&&pool.includes(x.a)));}""",
    """function ddisFor(id,pool){return DDI.filter(x=>(x.a===id&&pool.includes(x.b))||(x.b===id&&pool.includes(x.a)));}
/* Geloest = einer der beiden Partner wurde ersetzt. Die Linie bleibt
   sichtbar, aber sie faerbt nichts mehr - sonst stuende Clopidogrel weiter
   auf ALARM, obwohl Omeprazol schon durch Dexlansoprazol ersetzt ist. */
function ixGeloest(x){return !!(altChoice[x.a]||altChoice[x.b]);}
function ddisOffen(id,pool){return ddisFor(id,pool).filter(x=>!ixGeloest(x));}""",
    "ixGeloest und ddisOffen", wo="script")

sub("""function overallSev(id,pool){
  const st=statusFor(id);let s=st.sev;
  const dd=ddisFor(id,pool||workspace);""",
    """function overallSev(id,pool){
  const st=statusFor(id);let s=st.sev;
  const dd=ddisOffen(id,pool||workspace);""",
    "overallSev: geloeste Interaktionen faerben nicht mehr", wo="script")

sub("""function ixBox(id){
  const dd=ddisFor(id,workspace);
  if(!dd.length)return [];
  const c=dd.some(x=>x.sev==='crit');
  return [{l:"Interaktion",v:c?"Kritisch":"Zu beachten",sev:c?"crit":"warn",sym:"c-ix"}];
}""",
    """function ixBox(id){
  const dd=ddisFor(id,workspace);
  if(!dd.length)return [];
  const offen=dd.filter(x=>!ixGeloest(x));
  if(!offen.length)return [{l:"Interaktion",v:"Gel&ouml;st",sev:"ok",sym:"c-ix"}];
  const c=offen.some(x=>x.sev==='crit');
  return [{l:"Interaktion",v:c?"Kritisch":"Zu beachten",sev:c?"crit":"warn",sym:"c-ix"}];
}""",
    "ixBox: geloeste Interaktion als geloest ausweisen", wo="script")

# --------------------------------------------------- Linie ausgrauen
sub("""    const crit=x.sev==='crit';
    const col=crit?'#D0021B':'#E08000';""",
    """    const geloest=ixGeloest(x);
    const crit=x.sev==='crit'&&!geloest;
    const col=geloest?'#9A93A3':(x.sev==='crit'?'#D0021B':'#E08000');""",
    "drawLinks: Farbe der geloesten Linie", wo="script")

sub("""    out+=`<path d="${d}" fill="none" stroke="${col}" stroke-width="20" stroke-linecap="round" stroke-linejoin="round" opacity=".16"/>`;
    out+=`<path d="${d}" fill="none" stroke="${col}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>`;
    out+=`<path d="${d}" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity=".38"/>`;
    out+=`<g class="ixbtn ${crit?'crit':''}" style="pointer-events:auto;cursor:pointer" onclick="openIx('${x.a}','${x.b}')">
      <circle cx="${cx}" cy="${cy}" r="27" fill="${col}" opacity=".2"/>
      <circle cx="${cx}" cy="${cy}" r="22" fill="#fff"/>
      <circle cx="${cx}" cy="${cy}" r="19" fill="${col}"/>
      <path d="M${cx} ${cy-10.5} L${cx+9.5} ${cy+7} H${cx-9.5} Z" fill="#fff"/>
      <path d="M${cx} ${cy-4.6}v5.6M${cx} ${cy+3.4}v1.1" stroke="${col}" stroke-width="2.4" stroke-linecap="round"/>
      <title>Interaktion ansehen</title></g>`;""",
    """    /* Geloest: duenner, blasser, gestrichelt - noch da, aber sichtbar
       erledigt. Im Knopf steht dann ein Haken statt des Ausrufezeichens. */
    const dick=geloest?5:9, du=geloest?' stroke-dasharray="1 9" stroke-opacity=".85"':'';
    out+=`<path d="${d}" fill="none" stroke="${col}" stroke-width="${geloest?12:20}" stroke-linecap="round" stroke-linejoin="round" opacity="${geloest?'.10':'.16'}"/>`;
    out+=`<path d="${d}" fill="none" stroke="${col}" stroke-width="${dick}" stroke-linecap="round" stroke-linejoin="round"${du}/>`;
    if(!geloest)out+=`<path d="${d}" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity=".38"/>`;
    const glyph=geloest
      ? `<path d="M${cx-7.5} ${cy+0.5} L${cx-2.5} ${cy+5.5} L${cx+7.5} ${cy-5.5}" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>`
      : `<path d="M${cx} ${cy-10.5} L${cx+9.5} ${cy+7} H${cx-9.5} Z" fill="#fff"/>
         <path d="M${cx} ${cy-4.6}v5.6M${cx} ${cy+3.4}v1.1" stroke="${col}" stroke-width="2.4" stroke-linecap="round"/>`;
    out+=`<g class="ixbtn ${crit?'crit':''}" style="pointer-events:auto;cursor:pointer" opacity="${geloest?'.72':'1'}" onclick="openIx('${x.a}','${x.b}')">
      <circle cx="${cx}" cy="${cy}" r="${geloest?21:27}" fill="${col}" opacity=".2"/>
      <circle cx="${cx}" cy="${cy}" r="${geloest?17:22}" fill="#fff"/>
      <circle cx="${cx}" cy="${cy}" r="${geloest?14.5:19}" fill="${col}"/>
      ${glyph}
      <title>${geloest?'Gel&ouml;st &mdash; Wechselwirkung ansehen':'Interaktion ansehen'}</title></g>`;""",
    "drawLinks: geloeste Linie ausgrauen", wo="script")

# ------------------------------------------------------------- Bilanz
sub("""function renderWorkspace(){""",
    """/* Bilanz der Wechselwirkungen. Gezaehlt werden PAARE, nicht Wirkstoffe:
   bei 4 Medikamenten sind das 6 Paare, und jedes ist genau eines von vier
   Dingen. Die Summe ergibt immer die Paarzahl - so sieht man, wovon die
   Zahl kommt, statt nur eine nackte Trefferzahl. */
function ixScore(){
  const n=workspace.length;
  const paare=n*(n-1)/2;
  let crit=0,warn=0,done=0;
  DDI.filter(x=>workspace.includes(x.a)&&workspace.includes(x.b)).forEach(x=>{
    if(ixGeloest(x))done++; else if(x.sev==='crit')crit++; else warn++;
  });
  return {paare,crit,warn,done,ok:Math.max(0,paare-crit-warn-done)};
}
function ixScoreHtml(){
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
}
function renderWorkspace(){""",
    "Bilanz der Wechselwirkungen", wo="script")

sub("""      <div class="colh">${ico('n-pill','',16)} Schritt 2 &mdash; deine Einnahmeliste</div>
      <h2 class="wstitle">${PATIENT}, das sind <em>deine</em> Medikamente</h2>
      <p class="wssub">${workspace.length} aktiv eingenommene Medikamente &middot; nach Bewertung sortiert</p>
      <div id="wsrows"></div>""",
    """      <div class="colh">${ico('n-pill','',16)} Schritt 2 &mdash; deine Einnahmeliste</div>
      <div class="wshead">
        <div>
          <h2 class="wstitle">${PATIENT}, das sind <em>deine</em> Medikamente</h2>
          <p class="wssub">${workspace.length} aktiv eingenommene Medikamente &middot; nach Bewertung sortiert</p>
        </div>
        ${ixScoreHtml()}
      </div>
      <div id="wsrows"></div>""",
    "Bilanz in den Kopf der Einnahmeliste", wo="script")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
for name in ("function ixGeloest(", "function ddisOffen(", "function ixScore(",
             "function ixScoreHtml("):
    assert s.count(name) == 1, "%s nicht genau einmal vorhanden" % name
assert "ddisOffen(id,pool||workspace)" in s, "overallSev nutzt ddisOffen nicht"
# ixGeloest muss vor overallSev stehen, sonst TDZ beim ersten Rendern
assert s.index("function ixGeloest(") < s.index("function overallSev("), \
    "ixGeloest steht hinter overallSev"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
