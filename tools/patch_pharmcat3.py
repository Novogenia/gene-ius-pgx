# -*- coding: utf-8 -*-
"""
Dritter Teil: PharmCATs eigene Wirkstoff-Empfehlungen werden zur ersten
Bewertungsquelle. Die Novogenia-Matrix bleibt als zweite Quelle darunter.

Jede Ersetzung wird zugesichert - und zwar mit Ortspruefung, nachdem ein
Anker schon einmal im Skript statt im Stylesheet gelandet ist.
"""
import io

APP = "pgx_app.html"
s = io.open(APP, encoding="ascii").read()
orig = len(s)
n = 0

def sub(alt, neu, was, anzahl=1, wo=None):
    """wo: 'style' oder 'script' - prueft, in welchem Bereich der Treffer liegt."""
    global s, n
    c = s.count(alt)
    assert c == anzahl, "PATCH '%s': %d erwartet, %d gefunden" % (was, anzahl, c)
    if wo:
        i = s.index(alt)
        si, se = s.index("<style>"), s.index("</style>")
        drin = si < i < se
        assert (wo == "style") == drin, "PATCH '%s': liegt im falschen Bereich" % was
    s = s.replace(alt, neu)
    n += 1
    print("  ok  %s" % was)

print("Patche %s (%d Zeichen)" % (APP, orig))

# ============================================ 1. Zuordnung und Bewertungsquelle
sub("""/* ---- Leitlinien-Matrix aus 'Pharmgkb drug recommendations V4' -------------""",
    """/* ---- PharmCATs eigene Empfehlungen ---------------------------------------
   Der Reporter von PharmCAT 3.2.0 liefert fuer dieses Genprofil fertige
   Empfehlungen aus CPIC, DPWG und den FDA-Beipackzetteln. Die Ampelstufe
   kommt aus PharmCATs eigenen Feldern, nicht aus einer Textdeutung:
     alternateDrugAvailable   -> ALARM   (ein anderer Wirkstoff ist angezeigt)
     dosingInformation        -> ACHTUNG (Dosis anpassen)
     otherPrescribingGuidance -> ACHTUNG (ueberwachen)
     nichts davon             -> OK      (kein Handlungsbedarf)
   Rangfolge der Quellen, wenn mehrere etwas sagen: CPIC vor DPWG vor FDA. */
const PSEV=['ok','warn','crit'];
const PQRANG={0:3,1:2,2:1,3:0};          /* CPIC, DPWG, FDA-Label, FDA-Assoz. */
const PDRUGBY={};
(function(){
  /* PharmCAT nennt Wirkstoffe englisch und klein. Verbundpraeparate stehen als
     "a / b / c" - jeder Bestandteil wird einzeln zugeordnet. */
  const loese=(name)=>{
    const teile=name.split('/').map(x=>x.trim().toLowerCase()).filter(Boolean);
    const out=[];
    teile.forEach(t=>{
      if(DRUGS[t]){out.push(t);return;}
      const a=(typeof ALIAS!=='undefined')?ALIAS[t]:null;
      if(a&&DRUGS[a]){out.push(a);return;}
      /* letzter Versuch: Name ohne Salzzusatz */
      const b=t.replace(/\\s+(sulfate|hydrochloride|hcl|sodium|maleate|tartrate|citrate|besylate|mesylate)$/,'');
      if(DRUGS[b])out.push(b);
    });
    return [...new Set(out)];
  };
  P_DRUGS.forEach(r=>{
    loese(r[0]).forEach(k=>{
      (PDRUGBY[k]=PDRUGBY[k]||[]).push({roh:r[0], q:r[1], txt:r[2]>=0?P_DTXT[r[2]]:'',
        imp:r[3]>=0?P_DIMP[r[3]]:'', kl:P_DKL[r[4]]||'', sev:PSEV[r[5]], flags:r[6], gt:r[7]});
    });
  });
})();
/* Die massgebliche Empfehlung: schaerfste Ampel, bei Gleichstand die
   hoeherwertige Quelle. Alle uebrigen bleiben als Zusatz erhalten. */
const _pharmCache={};
function pharmRec(id){
  let v=_pharmCache[id];
  if(v!==undefined)return v;
  const rs=PDRUGBY[id];
  if(!rs){ _pharmCache[id]=null; return null; }
  const best=rs.slice().sort((a,b)=>
    PSEV.indexOf(b.sev)-PSEV.indexOf(a.sev) || PQRANG[b.q]-PQRANG[a.q])[0];
  v={haupt:best, alle:rs};
  _pharmCache[id]=v;
  return v;
}
function pharmQuelle(q){return P_DQ[q]||'PharmCAT';}

/* ---- Leitlinien-Matrix aus 'Pharmgkb drug recommendations V4' -------------""",
    "PharmCAT-Empfehlungen zuordnen", wo="script")

# ====================================================== 2. statusFor umstellen
alt = """  /* 1. Vorrang: eine Leitlinienzeile, deren Genbedingungen exakt zutreffen.
        Der Schweregrad kommt dann aus der Quelle selbst (rot/gelb im
        Novogenia-Template), nicht aus einer Heuristik. */
  const rc=recFor(id);"""
neu = """  /* 1. Vorrang: PharmCAT hat fuer dieses Genprofil eine fertige Empfehlung.
        Das ist die Referenzimplementierung von CPIC/DPWG, genau auf den
        gerufenen Genotyp bezogen. */
  const pr=pharmRec(id);
  if(pr){
    const h=pr.haupt;
    const wirkung=h.sev==='crit'
      ? "Fuer dich ist ein anderer Wirkstoff angezeigt."
      : h.sev==='warn'
        ? "Die Dosis muss angepasst oder die Wirkung ueberwacht werden."
        : "Es ist keine Anpassung noetig.";
    return{sev:h.sev, lvl:2, pharm:true,
      text:"Zu "+d.name+" gibt es eine Empfehlung, die genau auf deinen Genotyp "
        +(h.gt||"")+" passt. "+wirkung+" Der Wortlaut steht unten."};
  }
  /* 2. Novogenias eigene Leitlinienzeile, wenn alle Genbedingungen zutreffen. */
  const rc=recFor(id);"""
sub(alt, neu, "statusFor: PharmCAT als erste Quelle", wo="script")

sub("""  /* 2. Eine Leitlinie existiert, laesst sich aber nicht anwenden, weil ein
        dafuer noetiges Gen nicht eindeutig bestimmt werden konnte. */""",
    """  /* 3. Eine Leitlinie existiert, laesst sich aber nicht anwenden, weil ein
        dafuer noetiges Gen nicht eindeutig bestimmt werden konnte. */""",
    "Nummerierung im Kommentar", wo="script")

sub("""  if(!PHENO[g])return{sev:"ok",lvl:2,nopgx:true,text:"F&uuml;r "+d.name+" ist &uuml;ber deine getesteten Gene kein relevanter genetischer Einfluss bekannt. Die Standarddosis ist f&uuml;r dich unauff&auml;llig."};
  const lvl=PHENO[g].lvl;let sev,text;
  /* 3. Gen ist im Panel, hat aber kein eindeutiges Ergebnis. */""",
    """  if(!PHENO[g])return{sev:"ok",lvl:2,nopgx:true,text:"F&uuml;r "+d.name+" ist &uuml;ber deine getesteten Gene kein relevanter genetischer Einfluss bekannt. Die Standarddosis ist f&uuml;r dich unauff&auml;llig."};
  const lvl=PHENO[g].lvl;let sev,text;
  /* 4. Gen ist im Panel, hat aber kein eindeutiges Ergebnis. */""",
    "Nummerierung im Kommentar 2", wo="script")

# ============================================ 3. Beurteilungsbox um PharmCAT
alt_ab = """    <div class="ab-plain">${st.text}</div>
    ${rc?`<div class="ab-sep"></div>"""
neu_ab = """    <div class="ab-plain">${st.text}</div>
    ${pharmBoxHtml(id)}
    ${rc?`<div class="ab-sep"></div>"""
sub(alt_ab, neu_ab, "Beurteilungsbox: PharmCAT-Block einsetzen", wo="script")

sub("function assessBox(id,sev){",
    """/* Alle Empfehlungen, die PharmCAT zu diesem Wirkstoff und Genotyp fuehrt.
   Mehrere Quellen koennen sich unterscheiden - das wird nicht geglaettet,
   sondern nebeneinander gezeigt, mit Quelle und Verbindlichkeit. */
function pharmBoxHtml(id){
  const pr=pharmRec(id); if(!pr)return '';
  const KL={'Strong':'verbindlich','Moderate':'abgewogen','Optional':'optional',
            'No recommendation':'keine Empfehlung','Unspecified':''};
  const rows=pr.alle.slice().sort((a,b)=>PQRANG[b.q]-PQRANG[a.q]).map(r=>`
    <div class="pw s-${r.sev}">
      <div class="pw-h">
        <span class="pw-q">${pharmQuelle(r.q)}</span>
        ${r.gt?`<span class="pw-gt">${r.gt}</span>`:''}
        ${KL[r.kl]?`<span class="pw-kl">${KL[r.kl]}</span>`:''}
        <span class="pw-b b-${r.sev}">${SLABEL[r.sev]}</span>
      </div>
      ${r.imp?`<div class="pw-i">${r.imp}</div>`:''}
      ${r.txt?`<div class="pw-t">${r.txt}</div>`:''}
    </div>`).join('');
  return `<div class="ab-sep"></div>
    <div class="ab-g">
      <div class="ab-gh">${ico('c-pillbox','',15)} Was die Leitlinien zu deinem Genotyp sagen
        <span class="ab-gt">PharmCAT ${P_META.ver}</span></div>
      ${rows}
      <div class="ab-gs">Originaltext englisch${ihelp('leit')} &middot;
        Datenstand ${P_META.daten}</div>
    </div>`;
}
function assessBox(id,sev){""",
    "PharmCAT-Block als Funktion", wo="script")

# ============================================================ 4. CSS dafuer
sub("  /* Befundzeile statt Metabolisierer-Skala bei Risiko- und Zielgenen */",
    """  /* Eine Leitlinien-Empfehlung von PharmCAT, je Quelle eine Zeile */
  .pw{border-left:3px solid var(--line2);padding:7px 0 7px 11px;margin:9px 0 0}
  .pw.s-crit{border-left-color:var(--crit)} .pw.s-warn{border-left-color:var(--warn)}
  .pw.s-ok{border-left-color:var(--ok)} .pw.s-unk{border-left-color:var(--unk)}
  .pw-h{display:flex;align-items:center;flex-wrap:wrap;gap:6px;margin-bottom:4px}
  .pw-q{font-size:11px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;color:var(--plum)}
  .pw-gt{font-family:var(--mono);font-size:10.5px;font-weight:700;color:var(--muted);
    background:var(--panel);border:1px solid var(--line);border-radius:5px;padding:1px 5px}
  .pw-kl{font-size:10.5px;font-weight:700;color:var(--muted)}
  .pw-b{margin-left:auto;font-size:10px;font-weight:800;letter-spacing:.06em;
    border-radius:5px;padding:2px 6px;border:1px solid}
  .pw-b.b-ok{background:var(--ok-bg);border-color:var(--ok-ln);color:var(--ok-t)}
  .pw-b.b-warn{background:var(--warn-bg);border-color:var(--warn-ln);color:var(--warn-t)}
  .pw-b.b-crit{background:var(--crit-bg);border-color:var(--crit-ln);color:var(--crit-t)}
  .pw-i{font-size:11.5px;font-weight:700;line-height:1.45;color:#3E3947;margin-bottom:3px}
  .pw-t{font-size:12px;line-height:1.55;color:#3c3540}
  /* Befundzeile statt Metabolisierer-Skala bei Risiko- und Zielgenen */""",
    "CSS fuer die Leitlinien-Zeilen", wo="style")

print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("geschrieben.")
