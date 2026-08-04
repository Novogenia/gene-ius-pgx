# -*- coding: utf-8 -*-
"""
Ein ALARM muss sich auf einen Befund am Patienten stuetzen.

PharmCAT setzt alternateDrugAvailable auch dort, wo die Alternative nur
bedingt gilt: Fluvastatin heisst "hoechstens 40mg als Startdosis; falls mehr
noetig, eine Alternative erwaegen". Das Flag steht, die Karte zeigt ALARM -
und darunter stehen "Wirkung: Normal" und "Toxizitaet: Normales Risiko".

Entscheidung Daniel, 2026-08-04: dass es eine Alternative gibt, ist keine
Eigenschaft des Patienten und darf die Ampel nicht allein tragen. Wo Wirkung
UND Risiko belegt normal sind, kann keine Karte ALARM zeigen.

Umgesetzt als Deckel, nicht als Neuableitung. Die Flag-Regel bleibt, was sie
ist. Der Versuch, die Ampel stattdessen ganz aus dem Implikationstext zu
ziehen, wurde vorher gegen die Daten gerechnet und verworfen: er stuft 39
Wirkstoffe hoch (Clopidogrel von OK auf ACHTUNG, Acenocoumarol auf ALARM),
weil der Text ueber Wirkung und Risiko oft gar nichts sagt. Genau davor warnt
DOKUMENTATION.md 11 - classification und Freitext taugen nicht als Ampel.

"Nicht angegeben" zaehlt deshalb NICHT als normal. Eine Luecke ist kein
Freispruch; sonst wuerde aus fehlender Information ein Entwarnungssignal.

Wirkung: an den 94 Wirkstoffen mit PharmCAT-Empfehlung bewegen sich genau
zwei, beide nach unten:

  fluvastatin   ALARM -> ACHTUNG   (Wirkung normal, Risiko normal, dosingInformation)
  rosuvastatin  ALARM -> ACHTUNG   (dito)

Nichts wird hochgestuft. Codein, Tramadol (Wirkung verstaerkt, Risiko hoch),
die Trizyklika, Ondansetron, Paroxetin (Wirkung zu schwach) bleiben ALARM -
sie stehen auf einem Befund, nicht auf der Alternative.

Offen bleibt: bei 12 Wirkstoffen (Metoprolol, Flecainid, Haloperidol,
Risperidon, Propafenon, Ivacaftor, Eliglustat, Succinylcholin, den
Inhalationsnarkotika und dem Dihydrocodein-Kombipraeparat) sagt der
Implikationstext weder etwas ueber Wirkung noch ueber Risiko. Dort haengt
ALARM weiter allein am Flag. Ohne Beleg wird nicht heruntergestuft - das
waere geraten.
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

# ------------------------------------------------------------------ 1. Helfer
# Die Wortgruppen standen bisher inline in pharmMetrics. Sie werden jetzt auch
# von der Ampel gebraucht - zwei Kopien wuerden auseinanderlaufen.
ALT = """/* Die massgebliche Empfehlung: schaerfste Ampel, bei Gleichstand die
   hoeherwertige Quelle. Alle uebrigen bleiben als Zusatz erhalten. */
const _pharmCache={};"""
NEU = """/* Wortgruppen, an denen sich Wirkung und Risiko ablesen lassen. Sie stehen
   hier oben, weil sowohl die Ampel als auch die Boxen sie brauchen; zwei
   Kopien wuerden mit der Zeit auseinanderlaufen. Kein /g - .test() waere
   sonst zustandsbehaftet und liefert bei jedem zweiten Aufruf false. */
const PW_SCHWACH=/less active|lower plasma|lower systemic|decreased plasma|decreased systemic|ineffectiveness|therapeutic failure|lack of efficacy|reduced efficacy|decreased concentration|decreased exposure/;
const PW_STARK=/increased formation|higher systemic|higher plasma|increased plasma|increased systemic|increased exposure|higher dose-adjusted|increased concentration/;
const PW_NORMAL=/normal metabolism|normal .*activity|typical |low risk|normal risk|normal .*formation/;
const PT_HOCH=/higher risk|increased risk|risk .*is increased|death has|serious toxicity|increased .*side effects|increased .*adverse/;
const PT_NORMAL=/low risk|normal risk|typical .*risk|does not appear to translate/;
/* Genau der Text, den auch die Boxen auswerten: erst die massgebliche Zeile,
   sonst die erste Quelle, die ueberhaupt etwas sagt. 13 der 94 Wirkstoffe
   haben in der massgeblichen Zeile keine Implikation - rechnete der Deckel
   auf einem anderen String als die Boxen, stuenden sie wieder im
   Widerspruch. */
function pImpOf(pr){return pr.haupt.imp || (pr.alle.find(x=>x.imp)||{}).imp || '';}
/* Belegt normale Wirkung UND belegt normales Risiko. "Nicht angegeben" zaehlt
   ausdruecklich nicht als normal - eine Luecke ist kein Freispruch. */
function pImplNormal(imp){
  const t=(imp||'').toLowerCase();
  if(!t)return false;
  const w=!PW_SCHWACH.test(t)&&!PW_STARK.test(t)&&PW_NORMAL.test(t);
  const x=!PT_HOCH.test(t)&&PT_NORMAL.test(t);
  return w&&x;
}
/* Der Deckel. Dass ein anderer Wirkstoff verfuegbar waere, ist kein Befund am
   Patienten: PharmCAT setzt alternateDrugAvailable auch bei "falls mehr
   noetig, Alternative erwaegen". Sind Wirkung und Risiko normal, bleibt als
   Grund fuer ALARM nur die Alternative uebrig - und die traegt ihn nicht.
   Uebrig bleibt, was die Quelle sonst noch verlangt: Dosis anpassen oder
   ueberwachen, sonst nichts. */
function pDeckel(sev,flags,imp){
  if(sev!=='crit'||!pImplNormal(imp))return sev;
  return (flags&6)?'warn':'ok';
}
function pEffSev(r){return pDeckel(r.sev,r.flags,r.imp);}
/* Die massgebliche Empfehlung: schaerfste Ampel, bei Gleichstand die
   hoeherwertige Quelle. Alle uebrigen bleiben als Zusatz erhalten. */
const _pharmCache={};"""
sub(ALT, NEU, "Wortgruppen und Deckel als gemeinsame Grundlage", wo="script")

# --------------------------------------------------- 2. Rangfolge der Quellen
# "Schaerfste gewinnt" muss die gedeckelte Stufe vergleichen, sonst wird eine
# heruntergestufte Zeile weiter vor eine echte ACHTUNG-Zeile sortiert.
sub("""  const best=rs.slice().sort((a,b)=>
    PSEV.indexOf(b.sev)-PSEV.indexOf(a.sev) || PQRANG[b.q]-PQRANG[a.q])[0];""",
    """  const best=rs.slice().sort((a,b)=>
    PSEV.indexOf(pEffSev(b))-PSEV.indexOf(pEffSev(a)) || PQRANG[b.q]-PQRANG[a.q])[0];""",
    "pharmRec: Rangfolge ueber die gedeckelte Stufe", wo="script")

# ------------------------------------------------------------- 3. Die Ampel
sub("""    const wirkung=h.sev==='crit'
      ? "Fuer dich ist ein anderer Wirkstoff angezeigt."
      : h.sev==='warn'
        ? "Die Dosis muss angepasst oder die Wirkung ueberwacht werden."
        : "Es ist keine Anpassung noetig.";
    return{sev:h.sev, lvl:plvl, pharm:true, flags:h.flags, gt:h.gt,""",
    """    /* Deckel, siehe pDeckel: eine belegt normale Wirkung bei normalem
       Risiko kann nie ALARM sein. Entscheidung Daniel, 2026-08-04. */
    const sev=pDeckel(h.sev,h.flags,pImpOf(pr)), gekappt=sev!==h.sev;
    const wirkung=sev==='crit'
      ? "Fuer dich ist ein anderer Wirkstoff angezeigt."
      : sev==='warn'
        ? "Die Dosis muss angepasst oder die Wirkung ueberwacht werden."
        : "Es ist keine Anpassung noetig.";
    return{sev:sev, lvl:plvl, pharm:true, gekappt:gekappt, flags:h.flags, gt:h.gt,""",
    "statusFor: Ampel gedeckelt", wo="script")

# ------------------------------------- 4. Boxen auf dieselben Wortgruppen
sub("""  const q=pr.haupt.imp || (pr.alle.find(x=>x.imp)||{}).imp || '';
  const t=q.toLowerCase();""",
    """  const t=pImpOf(pr).toLowerCase();""",
    "pharmMetrics: denselben Text wie der Deckel auswerten", wo="script")

sub("""  /* 1. Wirkung */
  let wirk;
  if(hat(/less active|lower plasma|lower systemic|decreased plasma|decreased systemic|ineffectiveness|therapeutic failure|lack of efficacy|reduced efficacy|decreased concentration|decreased exposure/))
    wirk=B("Wirkung","Zu schwach","warn","s-down");
  else if(hat(/increased formation|higher systemic|higher plasma|increased plasma|increased systemic|increased exposure|higher dose-adjusted|increased concentration/))
    wirk=B("Wirkung","Verst&auml;rkt","crit","s-dblup");
  else if(hat(/normal metabolism|normal .*activity|typical |low risk|normal risk|normal .*formation/))
    wirk=B("Wirkung","Normal","ok","s-check");
  else wirk=B("Wirkung","Nicht angegeben","unk","c-search");""",
    """  /* 1. Wirkung - dieselben Wortgruppen, die auch den Deckel setzen */
  let wirk;
  if(PW_SCHWACH.test(t))     wirk=B("Wirkung","Zu schwach","warn","s-down");
  else if(PW_STARK.test(t))  wirk=B("Wirkung","Verst&auml;rkt","crit","s-dblup");
  else if(PW_NORMAL.test(t)) wirk=B("Wirkung","Normal","ok","s-check");
  else wirk=B("Wirkung","Nicht angegeben","unk","c-search");""",
    "pharmMetrics: Wirkung aus den gemeinsamen Wortgruppen", wo="script")

sub("""  /* 3. Risiko */
  let tox;
  if(hat(/higher risk|increased risk|risk .*is increased|death has|serious toxicity|increased .*side effects|increased .*adverse/))
    tox=B("Toxizit&auml;t","Erh&ouml;htes Risiko","crit","s-up");
  else if(hat(/low risk|normal risk|typical .*risk|does not appear to translate/))
    tox=B("Toxizit&auml;t","Normales Risiko","ok","s-check");
  else tox=B("Toxizit&auml;t","Nicht angegeben","unk","c-search");""",
    """  /* 3. Risiko - dieselben Wortgruppen wie im Deckel */
  let tox;
  if(PT_HOCH.test(t))         tox=B("Toxizit&auml;t","Erh&ouml;htes Risiko","crit","s-up");
  else if(PT_NORMAL.test(t))  tox=B("Toxizit&auml;t","Normales Risiko","ok","s-check");
  else tox=B("Toxizit&auml;t","Nicht angegeben","unk","c-search");""",
    "pharmMetrics: Risiko aus den gemeinsamen Wortgruppen", wo="script")

# ----------------------------------------------- 5. Handlungsbox einfaerben
# Der Text bleibt - PharmCAT nennt die Alternative, das wird nicht verschwiegen.
# Nur die Farbe folgt der Karte, sonst steht ein roter Kasten auf ACHTUNG.
sub("""  const akt=(f&1) ? B("Handlung","Anderer Wirkstoff","crit","s-stop")""",
    """  const akt=(f&1) ? B("Handlung","Anderer Wirkstoff",st.gekappt?"warn":"crit","s-stop")""",
    "pharmMetrics: Handlungsbox folgt der gedeckelten Karte", wo="script")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
for name in ("function pDeckel(", "function pImplNormal(", "function pImpOf(",
             "function pEffSev("):
    assert s.count(name) == 1, "Helfer %s nicht genau einmal definiert" % name
assert "hat(/" in s, "Umsatz-Box sollte hat() weiter benutzen"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
