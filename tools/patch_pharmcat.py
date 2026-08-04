# -*- coding: utf-8 -*-
"""
Verdrahtet das echte PharmCAT-Profil in pgx_app.html.

Jede Ersetzung wird zugesichert. Ohne das laufen stille Fehlschlaege durch -
das ist in diesem Projekt schon zweimal passiert.

Aufruf:  python patch_pharmcat.py
"""
import io, os, re, sys

APP = "pgx_app.html"
DATA = "pharmcat_profil.js"

s = io.open(APP, encoding="ascii").read()
orig_len = len(s)
n_edits = 0

def sub(alt, neu, was, anzahl=1):
    """Ersetzen mit Zusicherung. alt muss genau <anzahl> mal vorkommen."""
    global s, n_edits
    c = s.count(alt)
    assert c == anzahl, "PATCH '%s': %d Treffer erwartet, %d gefunden" % (was, anzahl, c)
    s = s.replace(alt, neu)
    n_edits += 1
    print("  ok  %s" % was)

print("Patche %s (%d Zeichen)" % (APP, orig_len))

# ==================================================================== 1. CSS
sub("    --ok-ln:#C4E6D2; --warn-ln:#F3D9AE; --crit-ln:#F2C4C2;\n",
    "    --ok-ln:#C4E6D2; --warn-ln:#F3D9AE; --crit-ln:#F2C4C2;\n"
    "    --unk:#8E8896; --unk-t:#55505E; --unk-bg:#F3F2F6; --unk-ln:#D9D6E0;\n",
    "CSS-Variablen fuer den vierten Zustand")

sub("  .s-ok{color:var(--ok)}.s-warn{color:var(--warn)}.s-crit{color:var(--crit)}\n",
    """  .s-ok{color:var(--ok)}.s-warn{color:var(--warn)}.s-crit{color:var(--crit)}
  /* ---- vierter Zustand: nicht bestimmbar --------------------------------
     Wenn eine Genposition nicht gerufen werden kann oder mehrere Diplotypen
     moeglich bleiben, ist die Aussage weder gruen noch rot. Dafuer gibt es
     eine eigene, bewusst farblose Stufe. Eine erfundene Sicherheit waere
     schlimmer als eine sichtbare Luecke. */
  .s-unk{color:var(--unk)} .t-unk{color:var(--unk-t)}
  .mchip.b-unk,.pillbadge.b-unk{background:var(--unk-bg);border-color:var(--unk-ln);color:var(--unk-t)}
  .ibox.b-unk,.genebox.b-unk{background:var(--unk-bg);border-color:var(--unk-ln)}
  .abox.s-unk{border-color:var(--unk)} .abox.s-unk .ab-h{background:#6B6575}
  .rgene.s-unk,.rdrug.s-unk,.grow.s-unk,.mrow.s-unk{border-left-color:var(--unk)}
  .genebox.b-unk .gscale .gs-seg{background:rgba(255,255,255,.82)}
  .gi-unk{background:var(--unk-bg);color:var(--unk-t)}
  .bf-unk{background:#77717F} .bf-unk[aria-pressed="true"]{background:#5B5664}
  .sf-unk{background:#77717F}
  .hbb.unk{background:#8E8896}
  .hbk.k-unk{border-left-color:var(--unk)} .hbk.k-unk .hbkn,.hbk.k-unk .hbkl{color:var(--unk-t)}
  .lg-unk .lgbox{background:#77717F} .lg-unk .lgmore{color:var(--unk-t)}
  .wsleg.h-unk .lr1,.wsleg.h-unk .lr1 svg{color:var(--unk-t)} .wsleg.h-unk .n{background:var(--unk)}
  /* Hinweiszeile auf einer Genkarte, wenn PharmCAT nichts eindeutiges liefert */
  .gwhy{margin:8px 0 0;padding:8px 10px;border-radius:9px;background:rgba(255,255,255,.7);
    border:1px solid var(--unk-ln);font-size:11.5px;font-weight:600;line-height:1.45;color:var(--unk-t)}
  .gwhy b{color:#3E3947}
""",
    "CSS-Regeln fuer den vierten Zustand")

sub("  .sevfilters{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px;margin-top:11px}",
    "  .sevfilters{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:6px;margin-top:11px}",
    "Ampelfilter-Raster auf fuenf Spalten")

sub("  .hb-keys{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:14px}",
    "  .hb-keys{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-top:14px}",
    "Kennzahlenband auf vier Spalten")

# Vierte Kachel in der Einleitung - das Raster hat drei feste Spalten
sub("  .hstats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0;margin-top:24px;",
    "  .hstats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:0;margin-top:24px;",
    "Einleitungskacheln auf vier Spalten")

# Abdeckungsblock im Arztbericht
sub("/* ================= ERKL", """/* Abdeckungsblock im Arztbericht: was der Test wirklich lesen konnte */
  .cov{margin:0 0 18px;border:1px solid var(--line);border-radius:14px;background:#fff;overflow:hidden}
  .cov-h{display:flex;align-items:center;gap:9px;padding:11px 15px;background:var(--plum-050);
    border-bottom:1px solid var(--line);font-size:13px;font-weight:800;color:var(--plum)}
  .cov-h svg{flex:none;color:var(--plum)}
  .cov-b{padding:13px 15px 15px}
  .cov-g{display:grid;grid-template-columns:repeat(auto-fit,minmax(132px,1fr));gap:10px;margin-bottom:12px}
  .cov-k{border:1px solid var(--line);border-radius:11px;padding:9px 11px;background:var(--panel)}
  .cov-k .n{display:block;font-size:21px;font-weight:800;letter-spacing:-.03em;line-height:1.1;
    font-variant-numeric:tabular-nums;color:var(--ink)}
  .cov-k .l{display:block;font-size:10.5px;font-weight:700;color:var(--muted);line-height:1.35;margin-top:3px}
  .cov-p{margin:0;font-size:12.5px;line-height:1.6;color:#3c3540}
  .cov-p b{color:var(--plum)}
  .cov-tab{width:100%;border-collapse:collapse;margin-top:11px;font-size:11.5px}
  .cov-tab th{text-align:left;font-weight:800;color:var(--muted);padding:5px 8px;border-bottom:1px solid var(--line);
    font-size:10px;letter-spacing:.05em;text-transform:uppercase}
  .cov-tab td{padding:5px 8px;border-bottom:1px solid var(--line);vertical-align:top}
  .cov-tab td.mono{font-family:var(--mono);font-size:11px}
  .cov-tab tr.miss td{background:var(--unk-bg)}
  .cov-tab td .warnpin{color:var(--unk-t);font-weight:800}

/* ================= ERKL""",
    "CSS fuer den Abdeckungsblock")

# ============================================================ 2. Datenblock
blk = io.open(DATA, encoding="ascii").read()
sub("<script>\n/* ================= DATEN ================= */\n",
    "<script>\n/* ===== BEGIN PHARMCAT PROFIL (erzeugt, nicht von Hand aendern) ===== */\n"
    + blk +
    "/* ===== END PHARMCAT PROFIL ===== */\n"
    "/* ================= DATEN ================= */\n",
    "PharmCAT-Datenblock einsetzen")

# ==================================================== 3. PHENO / GENO / LVL
alt_pheno = 'const PHENO={CYP2C19:{lvl:1},CYP2D6:{lvl:2},CYP2C9:{lvl:0},VKORC1:{lvl:0},DPYD:{lvl:1},SLCO1B1:{lvl:1},TPMT:{lvl:2},UGT1A1:{lvl:1},CYP3A4:{lvl:2},NAT2:{lvl:1},ABCB1:{lvl:1},G6PD:{lvl:2},CYP1A2:{lvl:3}};'
neu_pheno = """/* Die Gendaten kommen nicht mehr aus der Hand, sondern aus dem PharmCAT-Lauf
   der Probe P_META.probe. lvl -1 heisst: PharmCAT konnte kein eindeutiges
   Ergebnis liefern - entweder fehlen Positionen im VCF oder es bleiben mehrere
   Diplotypen moeglich. Dieser Fall wird als eigener Zustand gefuehrt und
   NICHT zu "normal" geglaettet. */
const PGENE={}; P_GENES.forEach(g=>{PGENE[g.g]=g;});
const PHENO={};
P_GENES.forEach(g=>{PHENO[g.g]={lvl:g.lvl,code:g.code,art:g.kind,eind:!!g.ok,
  mehr:!!g.mehr,kand:g.kand,score:g.score,rolle:g.rolle,phen:g.phen,de:g.de};});"""
sub(alt_pheno, neu_pheno, "PHENO aus PharmCAT ableiten")

alt_lvl = 'const LVL={3:{t:"Ultraschneller Metabolisierer",k:"UM",s:"Sehr schnell",col:"var(--ok-t)"},2:{t:"Normaler Metabolisierer",k:"NM",s:"Normal",col:"var(--ok-t)"},1:{t:"Intermedi&auml;rer Metabolisierer",k:"IM",s:"Vermindert",col:"var(--warn-t)"},0:{t:"Langsamer Metabolisierer",k:"PM",s:"Stark vermindert",col:"var(--crit-t)"}};'
neu_lvl = """const LVL={3:{t:"Ultraschneller Metabolisierer",k:"UM",s:"Sehr schnell",col:"var(--ok-t)"},2:{t:"Normaler Metabolisierer",k:"NM",s:"Normal",col:"var(--ok-t)"},1:{t:"Intermedi&auml;rer Metabolisierer",k:"IM",s:"Vermindert",col:"var(--warn-t)"},0:{t:"Langsamer Metabolisierer",k:"PM",s:"Stark vermindert",col:"var(--crit-t)"},
"-1":{t:"Nicht bestimmbar",k:"?",s:"Offen",col:"var(--unk-t)"}};
/* Fuer Transporter und Zielproteine passt das Wort Metabolisierer nicht.
   PharmCAT liefert dort eigene Phaenotyp-Woerter, die im Datenblock schon
   uebersetzt sind - LVLFOR nimmt sie, wenn vorhanden. */
function lvlLabel(g){
  const p=PHENO[g];
  if(!p)return LVL[2];
  if(p.de)return {t:p.de,k:LVL[p.lvl]?LVL[p.lvl].k:"?",s:LVL[p.lvl]?LVL[p.lvl].s:"Offen",
                  col:LVL[p.lvl]?LVL[p.lvl].col:"var(--unk-t)"};
  return LVL[p.lvl]||LVL["-1"];
}"""
sub(alt_lvl, neu_lvl, "LVL um 'nicht bestimmbar' erweitern")

# GENO: den handgemachten Block komplett ersetzen
i0 = s.index("const GENO={\n")
i1 = s.index("};\n", s.index("CYP1A2:{genotyp:", i0)) + 3
alt_geno = s[i0:i1]
assert "CYP1A2" in alt_geno and len(alt_geno) < 2200, "GENO-Block nicht wie erwartet: %d Zeichen" % len(alt_geno)
neu_geno = """/* GENO wird aus dem PharmCAT-Profil gebaut. kopien = die beiden gerufenen
   Allele mit ihrer Funktion, wie PharmCAT sie meldet. Bei nicht eindeutigem
   Ergebnis bleibt kopien leer - dann zeigt die Karte den Grund statt zwei
   erfundene Kopien. */
const GENO={};
P_GENES.forEach(g=>{
  const kop=[];
  if(g.ok&&g.a1)kop.push([g.a1,g.f1]);
  if(g.ok&&g.a2)kop.push([g.a2,g.f2]);
  GENO[g.g]={genotyp:g.dip||"nicht bestimmbar",
    allele:(g.alle&&g.alle.length)?g.alle.join(", "):"&mdash;",
    kopien:kop, score:g.score, unc:g.unc||[], var:g.var||[],
    pos:g.pos, fehlt:g.fehlt, kand:g.kand, alt:g.alt||[]};
});
"""
s = s.replace(alt_geno, neu_geno)
n_edits += 1
print("  ok  GENO aus PharmCAT ableiten (%d Zeichen ersetzt)" % len(alt_geno))

# AFN: die gerufenen Allelfunktionen von PharmCAT dazumischen
sub("const AFNC={'normal':'ok',",
    """/* Die von PharmCAT gemeldeten Funktionen der gerufenen Allele haben Vorrang
   vor der hinterlegten Tabelle - sie stammen direkt aus der Allel-Definition
   der verwendeten ClinPGx-Version. */
P_GENES.forEach(g=>{
  AFN[g.g]=AFN[g.g]||{};
  if(g.a1&&g.f1)AFN[g.g][g.a1]=g.f1;
  if(g.a2&&g.f2)AFN[g.g][g.a2]=g.f2;
});
const AFNC={'normal':'ok',""",
    "Allelfunktionen aus PharmCAT nachtragen")

sub("'Empfindlichkeit erh&ouml;ht':'warn','ver&auml;nderter Transport':'warn'};",
    "'Empfindlichkeit erh&ouml;ht':'warn','ver&auml;nderter Transport':'warn',\n"
    "  'm&ouml;glicherweise reduziert':'warn','unklar':'warn','unbekannt':'warn'};",
    "AFNC um die PharmCAT-Funktionswoerter erweitern")

# ============================================== 4. Leitlinien-Matcher (P_REC)
# Der alte recFor liegt INNERHALB des generierten Blocks. Er wird umbenannt und
# bleibt Rueckfall. Dieselbe Aenderung geht in patch_app_data.py, sonst ist sie
# beim naechsten Generatorlauf verloren - dieser Fehler ist hier schon passiert.
ALT_FB = """/* Empfehlung, die zu Lisas Phaenotyp passt */
function recFor(id){
  const rs=RECBY[id]; if(!rs)return null;
  for(const r of rs){ const p=PHENO[r.gen]; if(p&&p.lvl===r.lvl)return r; }
  return null;
}"""
NEU_FB = """/* Rueckfall: Empfehlung aus dem Wirkstoff-Datenblock. Wird nur genommen, wenn
   die genauere Leitlinien-Matrix P_REC fuer diesen Wirkstoff nichts hat.
   Die Stufen muessen beide >= 0 sein - Stufe -1 heisst im Datenblock
   "Sondergenotyp", im Profil aber "nicht bestimmbar". Das darf sich nicht
   versehentlich treffen. */
function recForFallback(id){
  const rs=RECBY[id]; if(!rs)return null;
  for(const r of rs){ const p=PHENO[r.gen];
    if(p&&r.lvl>=0&&p.lvl>=0&&p.lvl===r.lvl)return r; }
  return null;
}"""
sub(ALT_FB, NEU_FB, "alten recFor zum Rueckfall umbenennen")

gen_py = "patch_app_data.py"
g = io.open(gen_py, encoding="utf-8").read()
assert g.count(ALT_FB) == 1, "Generator: alter recFor nicht eindeutig gefunden"
io.open(gen_py, "w", encoding="utf-8", newline="\n").write(g.replace(ALT_FB, NEU_FB))
print("  ok  dieselbe Umbenennung in %s" % gen_py)

# Der neue Matcher gehoert AUSSERHALB des generierten Blocks, in die Logik.
alt_rec = "/* ================= LOGIK ================= */"
neu_rec = """/* ---- Leitlinien-Matrix aus 'Pharmgkb drug recommendations V4' -------------
   Eine Zeile gilt nur, wenn ALLE ihre Genbedingungen zutreffen. 14 der 103
   Zeilen verlangen zwei Gene gleichzeitig (CYP2C19 und CYP2D6 bei
   Amitriptylin) - wer nur die erste Bedingung prueft, ordnet dem Kunden eine
   fremde Empfehlung zu. Das war beim ersten Abgleich genau der Fehler. */
const PRECBY={};
P_REC.forEach(r=>{
  const k=r[0].toLowerCase();
  (PRECBY[k]=PRECBY[k]||[]).push({drug:r[0],om:r[1],cond:r[2],
    txt:r[3]>=0?P_TXT[r[3]]:'', gl:pglFrom(r[4]), dose:r[5], sev:r[6]||'warn',
    dosis:r[7]});
});
function pglFrom(m){return P_GL.filter((_,i)=>m&(1<<i));}
/* Transporter- und Enzymvokabular treffen sich: das Spreadsheet schreibt
   POOR/INTERMEDIATE auch dort, wo PharmCAT PF/DF meldet. */
const PAEQ={NF:'NM',DF:'IM',PF:'PM',IF:'UM'};
/* Ergebnis je Bedingung: true trifft zu, false trifft nicht zu,
   null nicht entscheidbar (Gen fehlt, mehrdeutig oder ohne Ergebnis). */
function condTrifft(c){
  const gen=c[0], code=c[1], roh=c[2];
  const p=PHENO[gen];
  if(!p)return [null,gen+' ist nicht Teil des Panels'];
  if(p.mehr)return [null,gen+' ist mehrdeutig &mdash; '+p.kand+' Diplotypen bleiben m&ouml;glich'];
  if(!p.eind)return [null,'f&uuml;r '+gen+' liegt kein Ergebnis vor'];
  if(code){
    const mine=[p.code]; if(PAEQ[p.code])mine.push(PAEQ[p.code]);
    return [mine.indexOf(code)>=0, gen+' ist '+p.code+', die Zeile verlangt '+code];
  }
  /* Kein Phaenotyp-Code: das Spreadsheet vergleicht hier den Diplotyp
     direkt, etwa UGT1A1 *28/*28 oder VKORC1 TT. */
  const gn=GENO[gen];
  const a=(gn&&gn.genotyp||'').replace(/\\s/g,'').toUpperCase();
  const b=(roh||'').replace(/\\s/g,'').toUpperCase();
  if(!a||a==='NICHTBESTIMMBAR')return [null,'f&uuml;r '+gen+' liegt kein Diplotyp vor'];
  return [a===b, gen+' ist '+gn.genotyp+', die Zeile verlangt '+roh];
}
/* Die Zeile, die zum Profil passt. Zusaetzlich wird festgehalten, ob eine
   Zeile nur deshalb nicht greift, weil ein Gen nicht bestimmbar ist. */
function recMatch(id){
  const rs=PRECBY[id]; if(!rs)return {rec:null,offen:null};
  let offen=null;
  for(const r of rs){
    if(!r.cond.length)continue;                 /* Warfarin-Dosisformel, s.u. */
    let alle=true, unklar=null;
    for(const c of r.cond){
      const [ok,warum]=condTrifft(c);
      if(ok===false){alle=false;break;}
      if(ok===null){unklar=warum;alle=false;}
    }
    if(alle)return {rec:r,offen:null};
    if(unklar&&!offen)offen={grund:unklar,n:rs.length};
  }
  return {rec:null,offen:offen};
}
const _recCache={};
function _rc(id){
  let v=_recCache[id];
  if(v===undefined){v=recMatch(id);_recCache[id]=v;}
  return v;
}
function recFor(id){
  const v=_rc(id);
  if(v.rec)return{gen:v.rec.cond.map(c=>c[0]).join(' + '),
                  cgen:v.rec.cond[0]?v.rec.cond[0][0]:null,
                  gt:v.rec.cond.map(c=>c[2]).join(' + '),
                  txt:v.rec.txt, gl:v.rec.gl, sev:v.rec.sev,
                  dose:v.rec.dose, om:v.rec.om, quelle:'matrix'};
  /* nichts in der Matrix - dann der Rueckfall aus dem Wirkstoff-Datenblock */
  const fb=recForFallback(id);
  return fb?Object.assign({},fb,{sev:null,cgen:fb.gen,quelle:'datenblock'}):null;
}
/* Warum eine Leitlinie zwar existiert, aber nicht angewandt werden kann */
function recOffen(id){return _rc(id).offen;}

/* ================= LOGIK ================= */"""
sub(alt_rec, neu_rec, "Leitlinien-Matcher vor die Logik setzen")

# =============================================================== 5. statusFor
alt_st = """function statusFor(id){
  const d=DRUGS[id],g=d.gene;
  if(!PHENO[g])return{sev:"ok",lvl:2,nopgx:true,text:"F&uuml;r "+d.name+" ist &uuml;ber deine getesteten Gene kein relevanter genetischer Einfluss bekannt. Die Standarddosis ist f&uuml;r dich unauff&auml;llig."};
  const lvl=PHENO[g].lvl;let sev,text;"""
neu_st = """function statusFor(id){
  const d=DRUGS[id],g=d.gene;
  /* 1. Vorrang: eine Leitlinienzeile, deren Genbedingungen exakt zutreffen.
        Der Schweregrad kommt dann aus der Quelle selbst (rot/gelb im
        Novogenia-Template), nicht aus einer Heuristik. */
  const rc=recFor(id);
  if(rc&&rc.quelle==='matrix')return{sev:rc.sev, lvl:PHENO[rc.cgen]?PHENO[rc.cgen].lvl:2,
    leit:true,
    text:"F&uuml;r "+d.name+" gibt es eine offizielle Empfehlung, die genau auf deinen "
      +"Genotyp "+rc.gt+" passt. Sie steht unten im Wortlaut."};
  /* 2. Eine Leitlinie existiert, laesst sich aber nicht anwenden, weil ein
        dafuer noetiges Gen nicht eindeutig bestimmt werden konnte. */
  const off=recOffen(id);
  if(off)return{sev:"unk", lvl:-1, offen:off,
    text:"F&uuml;r "+d.name+" gibt es offizielle Empfehlungen &mdash; sie h&auml;ngen aber an "
      +"einem Gen, das in deiner Analyse nicht eindeutig bestimmt werden konnte "
      +"("+off.grund+"). Deshalb bleibt die Bewertung offen."};
  if(!PHENO[g])return{sev:"ok",lvl:2,nopgx:true,text:"F&uuml;r "+d.name+" ist &uuml;ber deine getesteten Gene kein relevanter genetischer Einfluss bekannt. Die Standarddosis ist f&uuml;r dich unauff&auml;llig."};
  const lvl=PHENO[g].lvl;let sev,text;
  /* 3. Gen ist im Panel, hat aber kein eindeutiges Ergebnis. */
  if(lvl<0)return{sev:"unk",lvl:-1,
    text:"Ob "+d.name+" zu dir passt, h&auml;ngt von "+g+" ab. Dieses Gen konnte in deiner "
      +"Analyse nicht eindeutig bestimmt werden &mdash; "
      +(PHENO[g].mehr?("es bleiben "+PHENO[g].kand+" m&ouml;gliche Varianten offen")
                     :"die daf&uuml;r n&ouml;tigen Positionen wurden nicht gelesen")
      +". Eine Aussage w&auml;re geraten, deshalb bleibt sie offen."};"""
sub(alt_st, neu_st, "statusFor: Leitlinie zuerst, dann offener Fall")

sub("  if(d.gene2&&PHENO[d.gene2]&&PHENO[d.gene2].lvl===0)sev=\"crit\";\n  return{sev,lvl,text};",
    "  if(d.gene2&&PHENO[d.gene2]&&PHENO[d.gene2].lvl===0)sev=\"crit\";\n  return{sev,lvl,text};",
    "statusFor-Ende unveraendert (Kontrolle)")

sub('const RANK={ok:0,warn:1,crit:2};\nconst SLABEL={ok:"OK",warn:"Achtung",crit:"ALARM"};',
    '/* unk liegt zwischen OK und Achtung: eine offene Frage ist ernster als\n'
    '   ein unauffaelliges Ergebnis, aber kein belegter Handlungsbedarf. */\n'
    'const RANK={ok:0,unk:1,warn:2,crit:3};\n'
    'const SLABEL={ok:"OK",unk:"Offen",warn:"Achtung",crit:"ALARM"};',
    "RANK und SLABEL um 'unk' erweitern")

# ==================================================== 6. Gensymbole und Skala
sub("""  if(lvl===2)return bar('on')+bar('on');
  if(lvl===1)return bar('on')+bar('off');
  if(lvl===0)return bar('off')+bar('off');
  return bar('ultra')+bar('ultra');""",
    """  if(lvl===2)return bar('on')+bar('on');
  if(lvl===1)return bar('on')+bar('off');
  if(lvl===0)return bar('off')+bar('off');
  if(lvl===3)return bar('ultra')+bar('ultra');
  /* nicht bestimmbar: zwei graue Balken mit Fragezeichen statt Haken */
  const q=(w,h)=>`<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">`
    +`<rect x="0" y="0" width="${w}" height="${h}" rx="${h/2}" fill="#8E8896"/>`
    +`<text x="31.5" y="${h/2+3.4}" text-anchor="middle" font-size="9.5" font-weight="800" fill="#fff"`
    +` font-family="var(--font)">?</text></svg>`;
  return q(44,12)+q(44,12);""",
    "genePair: grauer Zustand fuer nicht bestimmbar")

sub("const GSEV={0:'crit',1:'warn',2:'ok',3:'ultra'};\nconst GPCT={0:'0 %',1:'50 %',2:'100 %',3:'200 %'};\nconst GCOL={0:'#E12D2D',1:'#F08A00',2:'#12A150',3:'#0b6b36'};",
    "const GSEV={0:'crit',1:'warn',2:'ok',3:'ultra','-1':'unk'};\n"
    "const GPCT={0:'0 %',1:'50 %',2:'100 %',3:'200 %','-1':'nicht bestimmbar'};\n"
    "const GCOL={0:'#E12D2D',1:'#F08A00',2:'#12A150',3:'#0b6b36','-1':'#8E8896'};",
    "GSEV / GPCT / GCOL um 'nicht bestimmbar' erweitern")

# helix: lvl -1 darf nicht in ok[undefined] laufen
sub("  const rungs=[[7.5,5.4],[12,7.6],[16.5,5.4],[27.5,5.4],[32,7.6],[36.5,5.4]];\n  const ok={0:[],1:[0,1,2],2:[0,1,2,3,4,5],3:[0,1,2,3,4,5]}[lvl];",
    "  const rungs=[[7.5,5.4],[12,7.6],[16.5,5.4],[27.5,5.4],[32,7.6],[36.5,5.4]];\n"
    "  /* -1: alle Sprossen gebrochen zeichnen - offen, nicht ausgefallen */\n"
    "  const ok={0:[],1:[0,1,2],2:[0,1,2,3,4,5],3:[0,1,2,3,4,5],'-1':[]}[lvl];",
    "helix: lvl -1 abfangen")

# Genreihenfolge: schlechteste zuerst, offene Faelle vor den normalen
sub("const GORDER=[0,1,2,3];",
    "/* schlechteste Gene zuerst, danach die offenen Faelle, zuletzt die normalen */\n"
    "const GORDER=[0,1,-1,3,2];",
    "Genreihenfolge um 'nicht bestimmbar' erweitern")

print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n_edits, orig_len, len(s)))
assert all(ord(c) < 128 for c in s), "Datei ist nicht mehr rein ASCII"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("geschrieben.")
