# -*- coding: utf-8 -*-
"""
Drei Aenderungen:

1. Alphabetische Reihenfolge in der Liste. Bisher standen die schlimmsten
   Treffer oben, dadurch sah man auf der ersten Seite nur ALARM.

2. Die vier Sub-Bewertungen widersprachen dem Gesamtergebnis: Amitriptylin
   stand auf ALARM, darunter viermal "Normal". Ursache: statusFor hat bei
   einer PharmCAT-Empfehlung lvl fest auf 2 gesetzt, und metrics() verzweigt
   ueber lvl. Jetzt kommt lvl aus dem Genotyp, auf den sich die Empfehlung
   bezieht, und die Handlungs-Box aus PharmCATs Flags.
   Dabei faellt ein alter Fehler auf: bei ultraschnellem Abbau stand
   "Wirkung: Verstaerkt" - das gilt nur fuer Prodrugs. Bei einem normalen
   Wirkstoff bedeutet schneller Abbau eine ZU SCHWACHE Wirkung.

3. Die 611 gelesenen Einzelvarianten werden aufgelistet - nicht als
   Metabolisierertyp, sondern als das, was sie sind: bestimmte Positionen
   mit Genotyp.
"""
import io

APP = "pgx_app.html"
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

# ================================================= 1. Alphabetisch sortieren
sub("""  return ids.sort((a,b)=>{const r=RANK[listSev(b)]-RANK[listSev(a)];return r||DRUGS[a].name.localeCompare(DRUGS[b].name);});""",
    """  /* Alphabetisch. Vorher standen die schlimmsten oben - dann sieht man auf
     der ersten Seite nur ALARM und bekommt kein Gefuehl fuer das Verhaeltnis.
     Wer gezielt die Alarme will, nimmt den Ampelfilter darueber. */
  return ids.sort((a,b)=>DRUGS[a].name.localeCompare(DRUGS[b].name,'de'));""",
    "Liste alphabetisch sortieren", wo="script")

sub("""  const ids=[...watchlist].filter(k=>DRUGS[k])
    .sort((a,b)=>RANK[listSev(b)]-RANK[listSev(a)]||DRUGS[a].name.localeCompare(DRUGS[b].name));""",
    """  /* Im Arztbericht bleibt die Reihenfolge nach Dringlichkeit - dort ist
     genau das der Zweck. */
  const ids=[...watchlist].filter(k=>DRUGS[k])
    .sort((a,b)=>RANK[listSev(b)]-RANK[listSev(a)]||DRUGS[a].name.localeCompare(DRUGS[b].name,'de'));""",
    "Arztbericht behaelt Dringlichkeitsreihenfolge", wo="script")

# ============================== 2a. statusFor: lvl aus dem Empfehlungsgenotyp
sub("""  const pr=pharmRec(id);
  if(pr){
    const h=pr.haupt;""",
    """  const pr=pharmRec(id);
  if(pr){
    const h=pr.haupt;
    /* Die Stufe muss zum Genotyp passen, auf den sich die Empfehlung bezieht -
       sonst zeigen die Sub-Bewertungen "Normal", waehrend oben ALARM steht.
       Bei mehreren Genen zaehlt das am staerksten abweichende. */
    let plvl=2;
    Object.keys(PHENO).forEach(g=>{
      if((h.gt||'').indexOf(g)<0)return;
      const l=PHENO[g].lvl; if(l<0)return;
      if(Math.abs(l-2)>Math.abs(plvl-2))plvl=l;
    });""",
    "statusFor: Stufe aus dem Empfehlungsgenotyp", wo="script")

sub("""    return{sev:h.sev, lvl:2, pharm:true,
      text:"Zu "+d.name+" gibt es eine Empfehlung, die genau auf deinen Genotyp "
        +(h.gt||"")+" passt. "+wirkung+" Der Wortlaut steht unten."};""",
    """    return{sev:h.sev, lvl:plvl, pharm:true, flags:h.flags, gt:h.gt,
      text:"Zu "+d.name+" gibt es eine Empfehlung, die genau auf deinen Genotyp "
        +(h.gt||"")+" passt. "+wirkung+" Der Wortlaut steht unten."};""",
    "statusFor: Flags und Genotyp mitgeben", wo="script")

# ==================== 2b. metrics: Prodrug-Unterschied bei ultraschnellem Abbau
sub("""  }else{
    o.push(B("Wirkung","Verst&auml;rkt","ok","s-dblup"),B(P?"Aktivierung":"Abbau","Beschleunigt","warn","s-up"),
           B("Toxizit&auml;t","Erh&ouml;htes Risiko","warn","s-up"),B("Dosierung","Dosis reduzieren","warn","s-down"));
  }""",
    """  }else{
    /* Ultraschnell. Fuer ein Prodrug heisst das: mehr Wirkstoff entsteht,
       also staerkere Wirkung und hoeheres Risiko (Codein zu Morphin).
       Fuer einen normalen Wirkstoff das Gegenteil: er ist zu schnell weg,
       die Wirkung bleibt zu schwach. Das war bisher nicht unterschieden. */
    if(P){
      o.push(B("Wirkung","Stark verst&auml;rkt","crit","s-dblup"),
             B("Aktivierung","Beschleunigt","crit","s-up"),
             B("Toxizit&auml;t","Hohes Risiko","crit","s-up"),
             B("Dosierung","Anderes Medikament","crit","s-stop"));
    }else{
      o.push(B("Wirkung","Zu schwach","warn","s-down"),
             B("Abbau","Beschleunigt","warn","s-up"),
             B("Toxizit&auml;t","Normales Risiko","ok","s-check"),
             B("Dosierung","Dosis erh&ouml;hen","warn","s-up"));
    }
  }""",
    "metrics: Prodrug-Unterschied bei ultraschnellem Abbau", wo="script")

# ==================== 2c. Handlungs-Box aus PharmCATs Flags ueberschreiben
sub("""  const dd=ddisFor(id,workspace);
  if(dd.length){const c=dd.some(x=>x.sev==='crit');
    o.push(B("Interaktion",c?"Kritisch":"Zu beachten",c?"crit":"warn","c-ix"));}
  return o;""",
    """  /* Wenn PharmCAT die Bewertung liefert, kommt die letzte Box aus dessen
     Flags - das ist die Handlungsanweisung der Quelle selbst und darf der
     Gesamtampel nicht widersprechen. */
  if(st.pharm&&o.length>=4){
    const f=st.flags||0;
    o[3]= (f&1) ? B("Handlung","Anderer Wirkstoff","crit","s-stop")
        : (f&2) ? B("Handlung","Dosis anpassen","warn","s-up")
        : (f&4) ? B("Handlung","&Uuml;berwachen","warn","s-up")
        :         B("Handlung","Keine Anpassung","ok","s-check");
    /* Kein gruener Kasten, wenn oben ALARM steht. */
    if(st.sev==='crit')o.forEach(x=>{if(x.sev==='ok'&&x.l!=='Toxizit&auml;t')x.sev='warn';});
  }
  const dd=ddisFor(id,workspace);
  if(dd.length){const c=dd.some(x=>x.sev==='crit');
    o.push(B("Interaktion",c?"Kritisch":"Zu beachten",c?"crit":"warn","c-ix"));}
  return o;""",
    "metrics: Handlungs-Box aus den Flags", wo="script")

# ============================================ 3. Variantenliste in "Deine Gene"
sub("""  <div class="genegrid">${sortedGenes().map(g=>geneCardHtml(g)).join('')}</div>`;""",
    """  <div class="genegrid">${sortedGenes().map(g=>geneCardHtml(g)).join('')}</div>
  ${variantenHtml()}`;""",
    "Variantenliste an die Genansicht anhaengen", wo="script")

sub("function vGene(){",
    """/* Alle Positionen, die tatsaechlich gelesen wurden. Die meisten ergeben
   keinen Metabolisierertyp - sie sind Bausteine, aus denen der Diplotyp
   zusammengesetzt wird. Trotzdem gehoeren sie in den Bericht: sie belegen,
   was geprueft wurde und was nicht. */
let varOffen={};
function toggleVar(g){varOffen[g]=!varOffen[g];render();}
function variantenHtml(){
  const mit=P_GENES.filter(g=>(g.var||[]).length).sort((a,b)=>a.g.localeCompare(b.g));
  if(!mit.length)return '';
  const ges=mit.reduce((s,g)=>s+g.var.length,0);
  const bloecke=mit.map(g=>{
    const auf=varOffen[g.g];
    const zeilen=g.var.map(v=>{
      const rs=/^rs\\d+$/.test(v[0]);
      return `<div class="vrow">
        <span class="vrs">${rs?`<a href="https://www.ncbi.nlm.nih.gov/snp/${v[0]}" target="_blank" rel="noopener">${v[0]}</a>`:v[0]}</span>
        <span class="vgt">${v[1]}</span></div>`;}).join('');
    return `<div class="vgene ${auf?'open':''}">
      <button class="vhead" onclick="toggleVar('${g.g}')">
        ${ico('chev','vchev',15)}
        <span class="vg">${g.g}</span>
        <span class="vn">${g.var.length} Positionen</span>
        <span class="vd">${g.dip?('Ergebnis '+g.dip):'kein Diplotyp'}</span>
      </button>
      <div class="vbody"><div class="vgrid">${zeilen}</div>
        ${g.fehlt?`<div class="anno" style="margin-top:9px">Zus&auml;tzlich erwartet, aber
          nicht gelesen: <b>${g.fehlt}</b> Positionen.</div>`:''}</div>
    </div>`;}).join('');
  return `<div class="sec-title" style="margin-top:30px">Jede einzelne gelesene Stelle</div>
    <p class="sec-sub">Aus diesen <b>${ges}</b> Positionen setzt sich dein Ergebnis zusammen.
      Die meisten ergeben f&uuml;r sich genommen keinen Metabolisierertyp &mdash; sie sind die
      Bausteine, aus denen die Genvarianten oben zusammengesetzt werden. Aufgef&uuml;hrt sind
      sie, weil sie belegen, was gepr&uuml;ft wurde.${ihelp('offen')}</p>
    <div class="vlist">${bloecke}</div>`;
}
function vGene(){""",
    "Variantenliste als Funktion", wo="script")

sub("  /* Eine Leitlinien-Empfehlung von PharmCAT, je Quelle eine Zeile */",
    """  /* Liste aller gelesenen Positionen, je Gen aufklappbar */
  .vlist{display:flex;flex-direction:column;gap:8px}
  .vgene{border:1px solid var(--line);border-radius:12px;background:#fff;overflow:hidden}
  .vhead{display:flex;align-items:center;gap:9px;width:100%;padding:11px 14px;border:0;
    background:none;font:inherit;cursor:pointer;text-align:left}
  .vhead:hover{background:var(--plum-050)}
  .vchev{flex:none;color:var(--faint);transition:transform .2s}
  .vgene.open .vchev{transform:rotate(90deg)}
  .vg{font-family:var(--mono);font-size:13px;font-weight:800;color:var(--ink)}
  .vn{font-size:11.5px;font-weight:700;color:var(--plum);background:var(--plum-100);
    border-radius:6px;padding:2px 7px}
  .vd{margin-left:auto;font-family:var(--mono);font-size:11px;color:var(--muted);
    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:44%}
  .vbody{display:none;padding:0 14px 13px;border-top:1px solid var(--line)}
  .vgene.open .vbody{display:block}
  .vgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(184px,1fr));gap:4px 12px;
    margin-top:10px}
  .vrow{display:flex;align-items:baseline;gap:8px;font-size:11.5px;padding:2px 0;
    border-bottom:1px solid var(--line)}
  .vrs{font-family:var(--mono);color:var(--muted)}
  .vrs a{color:var(--plum);text-decoration:none}
  .vrs a:hover{text-decoration:underline}
  .vgt{margin-left:auto;font-family:var(--mono);font-weight:700;color:var(--ink)}
  /* Eine Leitlinien-Empfehlung von PharmCAT, je Quelle eine Zeile */""",
    "CSS fuer die Variantenliste", wo="style")

print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("geschrieben.")
