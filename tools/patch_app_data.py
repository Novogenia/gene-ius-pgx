# -*- coding: utf-8 -*-
"""Baut den erzeugten Datenblock in pgx_app.html ein."""
import re, io, os

APP = "pgx_app.html"
DATA = "pgx_data.js"

s = open(APP, encoding="utf-8").read()
data = open(DATA, encoding="utf-8").read()

# Bereits eingebaut? Dann alten Block herausschneiden und neu setzen.
MARK_A = "/* ===== BEGIN ECHTE WIRKSTOFFDATEN ===== */"
MARK_E = "/* ===== END ECHTE WIRKSTOFFDATEN ===== */"
if MARK_A in s:
    s = s[:s.index(MARK_A)] + s[s.index(MARK_E)+len(MARK_E):]

BUILDER = r"""
/* ---- Aufbau: echte Wirkstoffe + handgepflegte Demo-Wirkstoffe ---------- */
/* Deutsche Schreibweisen der Demo-Wirkstoffe auf die englischen Quellnamen */
const ALIAS={omeprazol:"omeprazole",pantoprazol:"pantoprazole",codein:"codeine",
  amitriptylin:"amitriptyline",azathioprin:"azathioprine",atorvastatin:"atorvastatin",
  allopurinol:"allopurinol",carbamazepin:"carbamazepine",diclofenac:"diclofenac",
  metformin:"metformin",morphin:"morphine",sertralin:"sertraline",venlafaxin:"venlafaxine",
  letrozol:"letrozole",mycophenolat:"mycophenolate mofetil",amphotericinb:"amphotericin b",
  rosuvastatin:"rosuvastatin",pravastatin:"pravastatin",apixaban:"apixaban",
  rivaroxaban:"rivaroxaban",ticagrelor:"ticagrelor",prasugrel:"prasugrel",
  oxaliplatin:"oxaliplatin",cisplatin:"cisplatin",azithromycin:"azithromycin",
  phenytoin:"phenytoin",voriconazol:"voriconazole",tamoxifen:"tamoxifen",
  irinotecan:"irinotecan",clarithromycin:"clarithromycin",simvastatin:"simvastatin",
  warfarin:"warfarin",ibuprofen:"ibuprofen",citalopram:"citalopram",
  fluorouracil:"fluorouracil",clopidogrel:"clopidogrel",metoprolol:"metoprolol",
  bisoprolol:"bisoprolol",ondansetron:"ondansetron",tramadol:"tramadol"};

/* Kategorien = ATC-Hauptgruppen aus All Drugs V12 */
const CATS={};
D_ATC1DE.forEach((n,i)=>{CATS['a'+i]=n;});
/* Demo-Wirkstoffe auf dieselben Hauptgruppen umhaengen */
const DEMOCAT={psyche:9,herz:5,magen:0,infekt:1,schmerz:9,onko:2,immun:2};

const DRUGS={};
/* 1) handgepflegte Wirkstoffe zuerst - sie behalten Markennamen und Alternativen */
Object.keys(DEMO_DRUGS).forEach(k=>{
  const d=Object.assign({},DEMO_DRUGS[k]);
  if(DEMOCAT[d.cat]!==undefined)d.cat='a'+DEMOCAT[d.cat];
  d.src='demo';
  DRUGS[k]=d;
});
/* 2) alle Wirkstoffe der Datenbank dazu, Doubletten anhand des Namens auslassen */
const _seen=new Set();
Object.keys(DEMO_DRUGS).forEach(k=>{
  _seen.add(DEMO_DRUGS[k].name.toLowerCase());
  if(ALIAS[k])_seen.add(ALIAS[k]);
});
const IDX2KEY={};
D_ROWS.forEach((r,i)=>{
  const nm=r[0], low=nm.toLowerCase();
  if(_seen.has(low)){
    const ex=Object.keys(DRUGS).find(k=>DRUGS[k].name.toLowerCase()===low||ALIAS[k]===low);
    if(ex){IDX2KEY[i]=ex; enrich(DRUGS[ex],r); return;}
  }
  const key='w'+i; IDX2KEY[i]=key;
  const gene=r[3]>=0?D_GENES[r[3]]:null;
  DRUGS[key]={name:nm, brands:[], cat:r[1]>=0?('a'+r[1]):'a13',
    sub:r[2]>=0?D_ATC2[r[2]]:'',
    atc3:r[10]>=0?D_ATC3[r[10]]:'', atc4:r[11]>=0?D_ATC4[r[11]]:'', gene:gene,
    genes:(r[9]||[]).map(g=>D_GENES[g]).filter(g=>PHENO[g]),
    prodrug:!!r[4], ev:D_EV[r[5]]||'', gl:glFrom(r[6]),
    recs:r[8]||0, alts:[], pro:r[7]>=0?D_TXT[r[7]]:'', src:'db'};
});
function glFrom(mask){const o=[];D_GL.forEach((g,i)=>{if(mask&(1<<i))o.push(g);});return o;}
function enrich(d,r){                    /* Demo-Karte um Datenbankwerte ergaenzen */
  if(!d.sub&&r[2]>=0)d.sub=D_ATC2[r[2]];
  if(!d.atc3&&r[10]>=0)d.atc3=D_ATC3[r[10]];
  if(!d.atc4&&r[11]>=0)d.atc4=D_ATC4[r[11]];
  if(!d.recs&&r[8])d.recs=r[8];
  if((!d.gl||!d.gl.length)&&r[6])d.gl=glFrom(r[6]);
  if(!d.ev&&r[5])d.ev=D_EV[r[5]]||'';
}

/* 3) genotypabhaengige Leitlinien-Empfehlungen zuordnen */
const RECBY={};
D_REC.forEach(r=>{
  const k=IDX2KEY[r[0]]; if(!k)return;
  (RECBY[k]=RECBY[k]||[]).push({gen:D_RECGENES[r[1]], lvl:r[2], gt:r[3],
    txt:r[4]>=0?D_TXT[r[4]]:'', gl:glFrom(r[5])});
});
/* Rueckfall: Empfehlung aus dem Wirkstoff-Datenblock. Wird nur genommen, wenn
   die genauere Leitlinien-Matrix P_REC fuer diesen Wirkstoff nichts hat.
   Die Stufen muessen beide >= 0 sein - Stufe -1 heisst im Datenblock
   "Sondergenotyp", im Profil aber "nicht bestimmbar". Das darf sich nicht
   versehentlich treffen. */
function recForFallback(id){
  const rs=RECBY[id]; if(!rs)return null;
  for(const r of rs){ const p=PHENO[r.gen];
    if(p&&r.lvl>=0&&p.lvl>=0&&p.lvl===r.lvl)return r; }
  return null;
}

/* 4) Wechselwirkungen: DrugBank-Paare plus enzymatisch abgeleitete ------- */
const DDI=DEMO_DDI.slice();
const _ddiSeen=new Set(DDI.map(x=>[x.a,x.b].sort().join('|')));
D_IX.forEach(x=>{
  const a=IDX2KEY[x[0]], b=IDX2KEY[x[1]]; if(!a||!b||a===b)return;
  const sig=[a,b].sort().join('|'); if(_ddiSeen.has(sig))return; _ddiSeen.add(sig);
  const enz=x[3]>=0?D_GENES[x[3]]:null, eff=D_EFF[x[4]], risk=x[5]>=0?D_RISK[x[5]]:'';
  /* Verursacher und Betroffener stehen in den Quelldaten */
  const ausl=x[6]===0?a:b, betr=x[6]===0?b:a;
  const nA=DRUGS[ausl].name, nB=DRUGS[betr].name;
  let txt,mech,meas,src;
  if(eff==='enz'){
    mech=nA+' hemmt '+enz+' &mdash; das Enzym, &uuml;ber das '+nB+' abgebaut wird.';
    txt=nA+' bremst den Abbau von '+nB+'.';
    src='Novogenia Enzym-Datenbank (All Drugs V12)';
  }else{
    mech=enz?(nA+' beeinflusst '+enz+', den Abbauweg von '+nB+'.')
            :('Beide Wirkstoffe beeinflussen sich gegenseitig.');
    if(eff==='risk')      txt='Zusammen mit '+nA+' steigt bei '+nB+' das Risiko'+(risk?' f&uuml;r '+risk:' f&uuml;r Nebenwirkungen')+'.';
    else if(eff==='up')   txt=nA+' l&auml;sst den Spiegel von '+nB+' ansteigen.';
    else if(eff==='down') txt=nA+' schw&auml;cht die Wirkung von '+nB+' ab.';
    else                  txt=nA+' und '+nB+' beeinflussen sich gegenseitig.';
    src='DrugBank';
  }
  DDI.push({a:ausl,b:betr,sev:x[2]===2?'crit':'warn',txt:txt,mech:mech,
    eff:D_EFFDE[x[4]]+(risk?' &mdash; '+risk:''),
    meas:'Diese Kombination mit deiner &Auml;rztin oder deinem Arzt besprechen.',
    src:src});
});

/* 4b) Alternativen: gleiche ATC-Ebene-4-Gruppe, nach deiner Bewertung sortiert */
const ALTOF={};
D_ALT.forEach(row=>{
  const k=IDX2KEY[row[0]]; if(!k)return;
  ALTOF[k]=row.slice(1).map(i=>IDX2KEY[i]).filter(Boolean);
});
function altsFor(id){
  const base=(DRUGS[id].alts||[]).map(a=>findDrug(a[0])).filter(Boolean);
  const grp=(ALTOF[id]||[]).filter(k=>k!==id&&base.indexOf(k)<0);
  /* unauffaellige zuerst, danach nach Namen */
  grp.sort((x,y)=>RANK[listSev(x)]-RANK[listSev(y)]||DRUGS[x].name.localeCompare(DRUGS[y].name));
  return base.concat(grp).slice(0,12);
}
/* Die Gruppierung ist die ATC-Ebene 4. Bei Sammelgruppen ("Sonstige ...",
   Antidote, Antibiotika) stehen darin Wirkstoffe, die einander gerade NICHT
   ersetzen koennen - das wird gesondert ausgewiesen. */
function altGroupName(id){
  const d=DRUGS[id];
  return d.atc4||d.sub||'gleiche Wirkstoffgruppe';
}
function altGroupPath(id){
  const d=DRUGS[id], parts=[d.sub,d.atc3,d.atc4].filter(Boolean);
  return parts.join(' &rsaquo; ');
}
function altGroupMixed(id){
  const g=(DRUGS[id].atc4||'').toLowerCase();
  if(!g)return true;
  return /^(other|various|all other|antidotes|antibiotics|combinations)/.test(g)
      || /other/.test(g);
}

/* 5) Anzahl betroffener Medikamente je Gen aus den echten Daten */
const GENE_DRUGS={};
Object.keys(PHENO).forEach(g=>{GENE_DRUGS[g]=0;});
Object.keys(DRUGS).forEach(k=>{
  const d=DRUGS[k];
  const gs=new Set([d.gene].concat(d.genes||[]).filter(Boolean));
  gs.forEach(g=>{if(GENE_DRUGS[g]!==undefined)GENE_DRUGS[g]++;});
});
/* Kennzahlen der Startseite - erst beim ersten Aufruf berechnet, weil der
   Bewertungs-Zwischenspeicher weiter unten im Skript steht */
var _dbstat=null;
function DBSTATS(){
  if(!_dbstat){const t={total:0,ok:0,warn:0,crit:0,unk:0};
    Object.keys(DRUGS).forEach(k=>{t.total++;t[listSev(k)]++;});_dbstat=t;}
  return _dbstat;
}
"""

# 1) Demo-Daten umbenennen
s = s.replace("const DRUGS={\n", "const DEMO_DRUGS={\n", 1)
s = s.replace("const DDI=[\n", "const DEMO_DDI=[\n", 1)

# 2) alte CATS- und GENE_DRUGS-Definitionen entfernen (kommen jetzt aus den Daten)
s = re.sub(r"const CATS=\{[^\n]*\};\n", "", s, count=1)
s = re.sub(r"const GENE_DRUGS=\{[^\n]*\};\n", "", s, count=1)

# 3) Datenblock + Builder direkt hinter das Ende des Demo-DDI-Arrays setzen
i = s.index("const DEMO_DDI=[")
j = s.index("\n];", i) + 3
block = "\n" + MARK_A + "\n" + data + BUILDER + MARK_E + "\n"
s = s[:j] + block + s[j:]

open(APP, "w", encoding="utf-8", newline="\n").write(s)
print("eingebaut. Datei %.0f kB" % (os.path.getsize(APP)/1024))
na = sum(1 for c in s if ord(c) > 127)
print("nicht-ASCII Zeichen:", na)
