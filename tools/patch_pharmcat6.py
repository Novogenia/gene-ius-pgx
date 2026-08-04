# -*- coding: utf-8 -*-
"""
Die vier Sub-Bewertungen kommen bei PharmCAT-Faellen aus dem Implikationstext
der Quelle statt aus dem Prodrug-Schalter.

Warum: Amitriptylin ist in All Drugs V12 als aktivierungspflichtig markiert,
also haette die Heuristik "Wirkung stark verstaerkt, hohes Risiko" gezeigt.
CPIC sagt fuer CYP2D6 ultraschnell aber das Gegenteil: "Increased metabolism
of TCAs to less active compounds ... Lower plasma concentrations", also zu
SCHWACHE Wirkung. Codein dagegen: "Increased formation of morphine leading to
higher risk of toxicity". Beide sind CYP2D6-UM - der Unterschied steht nur im
Text, nicht im Genprofil.

Die Texte sind formelhaft. Wo sie nichts hergeben, steht "Nicht angegeben"
und nicht "Normal" - eine Luecke ist kein Normalbefund.
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

# Der bisherige Flag-Block wird durch die vollstaendige Ableitung ersetzt
ALT = """  /* Wenn PharmCAT die Bewertung liefert, kommt die letzte Box aus dessen
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
  }"""

NEU = """  /* Wenn PharmCAT die Bewertung liefert, werden alle vier Boxen aus dem
     Implikationstext der Quelle abgeleitet - der Prodrug-Schalter reicht
     nicht. Amitriptylin und Codein sind beide CYP2D6 ultraschnell, aber bei
     Codein entsteht MEHR Wirkstoff (Morphin, Toxizitaet), bei Amitriptylin
     WENIGER (Wirkungsverlust). Das steht nur im Text. */
  const pm=pharmMetrics(id,st);
  if(pm)return pm.concat(ixBox(id));"""
sub(ALT, NEU, "metrics: Ableitung aus dem Implikationstext", wo="script")

sub("""  const dd=ddisFor(id,workspace);
  if(dd.length){const c=dd.some(x=>x.sev==='crit');
    o.push(B("Interaktion",c?"Kritisch":"Zu beachten",c?"crit":"warn","c-ix"));}
  return o;""",
    """  return o.concat(ixBox(id));""",
    "metrics: Interaktionsbox auslagern", wo="script")

sub("function metrics(id){",
    """/* Wechselwirkungen in der eigenen Liste - unabhaengig von der Genetik */
function ixBox(id){
  const dd=ddisFor(id,workspace);
  if(!dd.length)return [];
  const c=dd.some(x=>x.sev==='crit');
  return [{l:"Interaktion",v:c?"Kritisch":"Zu beachten",sev:c?"crit":"warn",sym:"c-ix"}];
}
/* Die vier Boxen aus dem, was die Leitlinie ueber die Folge sagt.
   Die Texte von CPIC und DPWG sind formelhaft; erkannt wird an Wortgruppen,
   nicht geraten. Was der Text nicht hergibt, bleibt "Nicht angegeben". */
function pharmMetrics(id,st){
  const pr=pharmRec(id); if(!pr)return null;
  const t=pr.alle.map(x=>x.imp||'').join(' ').toLowerCase();
  const d=DRUGS[id], P=d.prodrug;
  const B=(l,v,sev,sym)=>({l,v,sev,sym});
  const hat=(re)=>re.test(t);

  /* 1. Wirkung */
  let wirk;
  if(hat(/less active|lower plasma|lower systemic|decreased plasma|decreased systemic|ineffectiveness|therapeutic failure|lack of efficacy|reduced efficacy|decreased concentration|decreased exposure/))
    wirk=B("Wirkung","Zu schwach","warn","s-down");
  else if(hat(/increased formation|higher systemic|higher plasma|increased plasma|increased systemic|increased exposure|higher dose-adjusted|increased concentration/))
    wirk=B("Wirkung","Verst&auml;rkt","crit","s-dblup");
  else if(hat(/normal metabolism|normal .*activity|typical |low risk|normal risk|normal .*formation/))
    wirk=B("Wirkung","Normal","ok","s-check");
  else wirk=B("Wirkung","Nicht angegeben","unk","c-search");

  /* 2. Umsatz im Koerper */
  let ums;
  if(hat(/increased metabolism|increased conversion|ultrarapid|rapid metaboli/))
    ums=B(P?"Aktivierung":"Abbau","Beschleunigt","warn","s-up");
  else if(hat(/decreased metabolism|reduced metabolism|poor metaboli|reduced .*activity|no .*activity|decreased .*activity/))
    ums=B(P?"Aktivierung":"Abbau","Verlangsamt","warn","s-down");
  else if(hat(/normal metabolism|normal .*activity|mildly reduced|slightly reduced/))
    ums=B(P?"Aktivierung":"Abbau","Normal","ok","s-check");
  else ums=B(P?"Aktivierung":"Abbau","Nicht angegeben","unk","c-search");

  /* 3. Risiko */
  let tox;
  if(hat(/higher risk|increased risk|risk .*is increased|death has|serious toxicity|increased .*side effects|increased .*adverse/))
    tox=B("Toxizit&auml;t","Erh&ouml;htes Risiko","crit","s-up");
  else if(hat(/low risk|normal risk|typical .*risk|does not appear to translate/))
    tox=B("Toxizit&auml;t","Normales Risiko","ok","s-check");
  else tox=B("Toxizit&auml;t","Nicht angegeben","unk","c-search");

  /* 4. Handlung - aus PharmCATs eigenen Feldern */
  const f=st.flags||0;
  const akt=(f&1) ? B("Handlung","Anderer Wirkstoff","crit","s-stop")
          : (f&2) ? B("Handlung","Dosis anpassen","warn","s-up")
          : (f&4) ? B("Handlung","&Uuml;berwachen","warn","s-up")
          :         B("Handlung","Keine Anpassung","ok","s-check");
  return [wirk,ums,tox,akt];
}
function metrics(id){""",
    "pharmMetrics als Funktion", wo="script")

# Graue Box braucht dieselbe Optik wie die anderen
sub("  .ibox.b-unk,.genebox.b-unk{background:var(--unk-bg);border-color:var(--unk-ln)}",
    "  .ibox.b-unk,.genebox.b-unk{background:var(--unk-bg);border-color:var(--unk-ln)}\n"
    "  .ibox.b-unk .il,.ibox.b-unk .iv{color:var(--unk-t)}",
    "CSS: graue Sub-Box lesbar", wo="style")

print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("geschrieben.")
