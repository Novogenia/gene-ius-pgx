# -*- coding: utf-8 -*-
"""
Einzelpositionen mit Studienhinweis - eigene Ebene unter "Deine Gene".

Vorgaben Daniel, 2026-08-06:
  1. Die Darstellung soll ein MOEGLICHES Problem signalisieren, kein
     garantiertes.
  2. Alle Evidenzstufen aufnehmen, nicht nur 1A.

Datengrundlage: data/rs_befunde.js aus tools/30_rs_befunde.py - 39 Positionen
in 16 Genen, jede mit belegtem Genotyp der Probe. Was PharmCAT nicht gelesen
hat, ist gar nicht erst drin.

WIE DAS "MOEGLICH" TRANSPORTIERT WIRD - vier Mittel, die zusammenspielen:

  a) Eigene Farbwelt. Die Ampelfarben sind fuer die graduierte Bewertung
     reserviert und tauchen hier NICHT auf. Die Zeilen sind neutral
     umrandet statt gefuellt; die Richtung traegt ein Pfeil und das Wort,
     nicht die Farbe. Ein Stufe-3-Befund zu Koffein kann damit gar nicht
     wie ein ALARM aussehen.

  b) Wortlaut im Beobachtungsmodus. "H&ouml;heres Risiko beobachtet bei
     Isoniazid" statt "H&ouml;heres Risiko bei Isoniazid". Die
     Rahmenzeile sagt ausdruecklich, was das hier NICHT ist.

  c) Evidenzpunkte auf jeder Zeile, dieselbe .dots-Komponente wie bei den
     Wirkstoffkarten. 1A fuellt vier Punkte, Stufe 3 zwei, Stufe 4 einen.
     Ein schwacher Befund SIEHT schwach aus, ohne dass an jeder Zeile ein
     Disclaimer haengen muss. Das ist der Grund, warum alle Evidenzstufen
     mitkoennen, ohne dass Rauschen entsteht.

  d) Strukturelle Zusicherung: diese Ebene fasst die Ampel nicht an. Kein
     Befund von hier veraendert je eine Wirkstoffkarte. Das ist der
     eigentliche Unterschied zwischen "Hinweis" und "Bewertung" - und es
     ist eine Eigenschaft des Codes, nicht der Formulierung.

Sortiert wird nach Evidenz absteigend, innerhalb der Stufe zuerst die
unguenstigen Signale. Die Stufen 3 und 4 stehen hinter einem Aufklapper,
damit die 22 schwachen Befunde die 16 starken nicht zudecken.

Richtung gilt je Wirkstoff, nie je Gen: SLCO1B1 rs4149056 T/T ist die
normale Funktion - die Genkarte sagt das zu Recht - und steht trotzdem bei
Cyclophosphamid als unguenstiges Signal. Es wird deshalb nirgends ein
Gen-Verdikt gebildet.

Nebeneffekt: drei Gene, die seit v61 ausgeblendet sind, haben einen
belegten Genotyp und tauchen hier wieder auf - IFNL3 (rs12979860 C/T, 1A,
schwaecheres Ansprechen auf sieben Hepatitis-C-Wirkstoffe), CYP4F2
(rs2108622 C/T, 1A, Aspirin) und UGT1A1 (rs887829 C/T). Sie bekommen
bewusst KEINE Genkarte und keine Skala - es gibt dort keinen
Metabolisierer-Status. Nur Position, Genotyp und Signal.
"""
import io, os

APP = "index.html"
DATA = os.path.join("data", "rs_befunde.js")
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
sub("""/* ===== END PHARMCAT PROFIL ===== */
""",
    """/* ===== END PHARMCAT PROFIL ===== */
/* ===== BEGIN RS-BEFUNDE (erzeugt, nicht von Hand aendern) ===== */
""" + blk + """/* ===== END RS-BEFUNDE ===== */
""",
    "Datenblock rs_befunde einsetzen", wo="script")

# ------------------------------------------------------------------- 2. CSS
sub("""/* Abdeckungsblock im Arztbericht: was der Test wirklich lesen konnte */""",
    """  /* Einzelpositionen mit Studienhinweis. Bewusst OHNE Ampelfarben - das
     ist eine Beobachtung, keine Bewertung, und darf nie wie eine aussehen. */
  .rsband{background:#fff;border-radius:18px;box-shadow:var(--sh);padding:22px 24px;margin-top:22px}
  .rs-intro{font-size:13px;color:var(--muted);line-height:1.55;margin:6px 0 16px;max-width:78ch}
  .rs-intro b{color:var(--ink)}
  .rsgene{border:1.5px solid var(--line2);border-radius:14px;padding:13px 15px;margin-bottom:10px;background:var(--panel)}
  .rsgene>.rsg-h{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;margin-bottom:9px}
  .rsg-n{font-weight:800;font-size:14px;letter-spacing:.01em}
  .rsg-sub{font-size:11.5px;color:var(--faint)}
  .rspos{border-top:1px solid var(--line);padding-top:9px;margin-top:9px}
  .rspos:first-of-type{border-top:0;padding-top:0;margin-top:0}
  .rsp-h{display:flex;align-items:center;gap:9px;flex-wrap:wrap;font-size:12.5px;margin-bottom:6px}
  .rsp-rs{font-family:var(--mono,monospace);font-weight:700}
  .rsp-rs a{color:var(--blue);text-decoration:none}.rsp-rs a:hover{text-decoration:underline}
  .rsp-gt{font-family:var(--mono,monospace);background:#fff;border:1.5px solid var(--line2);
    border-radius:7px;padding:1px 7px;font-weight:700}
  /* 11px ist die Untergrenze der Pruefroutine (Abschnitt 7) - nicht darunter */
  .rsp-ev{margin-left:auto;display:flex;align-items:center;gap:7px;font-size:11px;color:var(--faint)}
  .rsp-ev b{font-weight:700;color:var(--muted);font-size:11px}
  /* Signalzeile: Umriss statt Fuellung. Kein Rot, kein Gruen. */
  .rssig{display:flex;gap:9px;align-items:flex-start;font-size:12.5px;line-height:1.5;
    border:1.5px solid var(--line2);border-radius:10px;padding:7px 10px;margin-bottom:5px;background:#fff}
  .rssig .rsi{flex:none;width:17px;height:17px;color:var(--muted);margin-top:1px}
  .rssig.neg{border-color:#C9B9C9}
  .rssig.neg .rsi{color:var(--plum)}
  .rssig-t{font-weight:750}
  .rssig-d{color:var(--muted)}
  .rsmore{background:none;border:0;font:inherit;font-size:12.5px;font-weight:750;color:var(--plum);
    cursor:pointer;padding:6px 0;display:flex;align-items:center;gap:7px}
  .rsmore svg{transition:.16s}.rsmore[aria-expanded="true"] svg{transform:rotate(180deg)}
/* Abdeckungsblock im Arztbericht: was der Test wirklich lesen konnte */""",
    "CSS fuer die Hinweis-Ebene", wo="style")

# ------------------------------------------------------------- 3. Renderer
sub("""function variantenHtml(){""",
    """/* ---- Einzelpositionen mit Studienhinweis ----------------------------
   Bewusst eine eigene Ebene: diese Befunde veraendern NIE eine
   Wirkstoffkarte und nie die Ampel. Sie zeigen, wo ein Zusammenhang
   beobachtet wurde - nicht, dass er bei dieser Person eintritt. */
const RS_BY={};
R_POS.forEach(p=>{(RS_BY[p[1]]=RS_BY[p[1]]||[]).push(p);});
const RSRANG={"1A":0,"1B":1,"2A":2,"2B":3,"3":4,"4":5};
/* unguenstig = hoeheres Risiko oder schwaecheres Ansprechen */
function rsNeg(sig){return sig.some(x=>x[0]===1||x[0]===3);}
function rsDots(lv){
  const e=R_EV[lv]||[1,lv]; let d="";
  for(let i=1;i<=4;i++)d+=`<i class="${i<=e[0]?'on':''}"></i>`;
  return `<span class="dots">${d}</span> <b>${e[1]}</b>`;
}
function rsPosHtml(p){
  const [rs,gen,gt,lv,sig]=p;
  const zeilen=sig.slice().sort((a,b)=>(a[0]===1||a[0]===3?0:1)-(b[0]===1||b[0]===3?0:1))
    .map(([code,idx])=>{
      const r=R_RICHT[code]||["ver&auml;ndert","s-up"];
      const neg=(code===1||code===3);
      const namen=idx.map(i=>R_DRUGS[i]).join(', ');
      return `<div class="rssig ${neg?'neg':''}">
        ${ico(r[1],'rsi',17)}
        <div><span class="rssig-t">${r[0]}</span>
          <span class="rssig-d">beobachtet bei ${namen}</span></div></div>`;
    }).join('');
  return `<div class="rspos">
    <div class="rsp-h">
      <span class="rsp-rs"><a href="https://www.ncbi.nlm.nih.gov/snp/${rs}" target="_blank" rel="noopener">${rs}</a></span>
      <span class="rsp-gt">${gt}</span>
      <span class="rsp-ev">${rsDots(lv)}</span>
    </div>${zeilen}</div>`;
}
function rsGeneHtml(g,liste){
  const p=PHENO[g];
  const sub=p?(p.lvl>=0?'erg&auml;nzend zum Ergebnis oben':'kein Metabolisierer-Status bestimmbar &mdash; nur diese Positionen')
             :'nur diese Positionen';
  return `<div class="rsgene">
    <div class="rsg-h"><span class="rsg-n">${g}</span><span class="rsg-sub">${sub}</span></div>
    ${liste.map(rsPosHtml).join('')}</div>`;
}
var rsOffen=false;
function toggleRs(){rsOffen=!rsOffen;render();}
function rsBefundeHtml(){
  const gene=Object.keys(RS_BY);
  if(!gene.length)return '';
  const stark=[], schwach=[];
  gene.forEach(g=>{
    const s=RS_BY[g].filter(p=>RSRANG[p[3]]<=3), w=RS_BY[g].filter(p=>RSRANG[p[3]]>3);
    if(s.length)stark.push([g,s]);
    if(w.length)schwach.push([g,w]);
  });
  const srt=a=>a.sort((x,y)=>(rsNeg(y[1][0][4])?1:0)-(rsNeg(x[1][0][4])?1:0)||x[0].localeCompare(y[0]));
  const nW=schwach.reduce((s,x)=>s+x[1].length,0);
  return `<div class="rsband">
    <div class="sec-title" style="margin:0">Einzelne Positionen mit Studienhinweis</div>
    <p class="rs-intro">Hier stehen einzelne Stellen deines Erbguts, zu denen es
      Ver&ouml;ffentlichungen gibt. <b>Das ist keine Bewertung.</b> Sie sagen, wo ein
      Zusammenhang <b>beobachtet</b> wurde &mdash; nicht, dass er bei dir eintritt. Sie
      ver&auml;ndern deshalb keine der Medikamentenkarten. Wie belastbar ein Hinweis ist,
      zeigen die Punkte rechts: vier Punkte hei&szlig;t Leitlinie oder Beipackzettel,
      ein Punkt hei&szlig;t Einzelfallbericht.</p>
    ${srt(stark).map(([g,l])=>rsGeneHtml(g,l)).join('')}
    ${nW?`<button class="rsmore" aria-expanded="${rsOffen}" onclick="toggleRs()">
      ${rsOffen?'Schw&auml;chere Hinweise ausblenden':'Auch die '+nW+' schw&auml;cheren Hinweise zeigen'}
      ${ico('chev','',16)}</button>
      ${rsOffen?srt(schwach).map(([g,l])=>rsGeneHtml(g,l)).join(''):''}`:''}
  </div>`;
}
function variantenHtml(){""",
    "Renderer fuer die Hinweis-Ebene", wo="script")

# ------------------------------------------------------- 4. In die Genansicht
sub("""  ${variantenHtml()}`;
}""",
    """  ${rsBefundeHtml()}
  ${variantenHtml()}`;
}""",
    "Hinweis-Ebene in 'Deine Gene' einhaengen", wo="script")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
for name in ("function rsBefundeHtml(", "function rsPosHtml(", "function rsGeneHtml(",
             "const R_POS=", "const R_DRUGS="):
    assert s.count(name) == 1, "%s nicht genau einmal vorhanden" % name
assert s.index("const R_POS=") < s.index("R_POS.forEach"), "Datenblock steht nach der Nutzung"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
