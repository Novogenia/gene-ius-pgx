# -*- coding: utf-8 -*-
"""
rs-Befunde faerben nur noch Gelb, nie Rot - und heissen auffaellig bzw.
unauffaellig.

Vorgabe Daniel, 2026-08-06: "Wenn eine RS-Nummer mit einem Gen assoziiert
ist, dann sollte die Karte fuer das Gen existieren. Der Name des Gens sollte
oben sein, und es sollte in einer Farbe gekennzeichnet werden: unauffaellig
oder auffaellig, in Gruen oder Gelb. Nur beim Ausklappen sieht man dann die
RS-Nummern, die dahinter stecken."

Drei der vier Punkte standen schon seit v65: die Karte ist das Gen, der
Genname steht oben, die rs-Nummern erscheinen erst beim Aufklappen.
Geaendert wird die Farbe.

  v65:  negativer Befund + Evidenz 1A  -> ROT
        negativer Befund + schwaecher  -> GELB
  v66:  negativer Befund               -> GELB, unabhaengig von der Evidenz
        kein negativer Befund          -> GRUEN

Rot vergibt ab jetzt nur noch der Phaenotyp selbst. Bei NA17454 bleibt
genau ein Gen rot: ABCG2 mit "Stark verminderte Transportfunktion" - das ist
ein Metabolisierer- bzw. Transporterbefund, keine rs-Assoziation, und wird
deshalb nicht heruntergestuft. Wenn auch das weg soll, ist es eine Zeile in
geneSev().

Damit loest sich der Fall, der in v65 erklaerungsbeduerftig war: SLCO1B1
meldet "Normale Transportfunktion" und stand trotzdem auf Rot. Jetzt gelb -
auffaellig, aber nicht alarmierend.

Die Evidenzstufe faellt als Farbgeber weg, bleibt aber vollstaendig
erhalten, wo sie hingehoert: als Punkte an jeder aufgeklappten rs-Zeile.
Genau das meint "nur beim Ausklappen sieht man die RS-Nummern".

Wortlaut auf der Karte folgt der Vorgabe:
  negativer Befund      -> "Auffaellig - N Position(en) mit Befund"
  nur guenstig/neutral  -> "Unauffaellig - N Position(en) gepruefte Stelle"
Gene ohne Metabolisierer-Status (CYP4F2, IFNL3, UGT1A1) tragen als
Statuszeile jetzt ebenfalls "Auffaellig" bzw. "Unauffaellig" statt "Nur
Einzelpositionen" - sie haben keine andere Aussage, und genau danach wurde
gefragt.
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

# --------------------------------------------------------------- Farbregel
sub("""function rsGeneSev(g){
  const l=RS_BY[g]; if(!l)return null;
  let sev=null;
  l.forEach(p=>{
    if(!p[4].some(x=>x[0]===1||x[0]===3))return;
    if(RSRANG[p[3]]<=1)sev='crit';
    else if(sev!=='crit')sev='warn';
  });
  return sev;
}""",
    """function rsGeneSev(g){
  const l=RS_BY[g]; if(!l)return null;
  /* Ein rs-Befund faerbt hoechstens gelb, nie rot (Vorgabe Daniel,
     2026-08-06: "unauffaellig oder auffaellig, in Gruen oder Gelb"). Rot
     vergibt nur der Phaenotyp selbst. Die Evidenzstufe faellt als Farbgeber
     weg - sie steht weiter als Punkte an jeder aufgeklappten rs-Zeile, und
     genau dort gehoert die Abstufung hin. */
  return l.some(p=>p[4].some(x=>x[0]===1||x[0]===3))?'warn':'ok';
}""",
    "rs-Befund faerbt hoechstens gelb", wo="script")

# Ein Gen ohne Metabolisierer-Status hat sonst gar keine Stufe - es haengt
# dann allein am Befund, gruen oder gelb.
sub("""function geneSev(g){
  const p=PHENO[g]; if(!p)return 'none';
  const psv=GSEV[p.lvl]||'unk', rsv=rsGeneSev(g);
  return (rsv&&GSEVR[rsv]>GSEVR[psv])?rsv:psv;
}""",
    """function geneSev(g){
  const p=PHENO[g]; if(!p)return 'none';
  const rsv=rsGeneSev(g);
  /* Ohne Metabolisierer-Status traegt der Befund die Karte allein: gruen,
     wenn nichts Negatives dabei ist, sonst gelb. Kein Grau - das war der
     "Offen"-Zustand, den v62 entfernt hat. */
  if(p.lvl<0)return rsv||'ok';
  const psv=GSEV[p.lvl]||'unk';
  return (rsv&&GSEVR[rsv]>GSEVR[psv])?rsv:psv;
}""",
    "Gene ohne Phaenotyp haengen allein am Befund", wo="script")

# ------------------------------------------------------------- Wortlaut
sub("""  const befZeile=nGes
    ? `<div class="gbef ${nBef?'neg':''}">${ico(nBef?'st-excl':'st-ok','',15)}
        ${nBef?`${nBef} Position${nBef===1?'':'en'} mit negativem Befund`
              :`${nGes} Position${nGes===1?'':'en'} mit Studienhinweis`}</div>`
    : '';""",
    """  /* Bei Genen ohne Metabolisierer-Status traegt schon die Statuszeile
     "Auffaellig"/"Unauffaellig" - dann nur die Zahl, sonst steht es zweimal
     auf derselben Karte. */
  const befZeile=nGes
    ? `<div class="gbef ${nBef?'neg':''}">${ico(nBef?'st-excl':'st-ok','',15)}
        ${nurPos?`${nGes} gepr&uuml;fte Position${nGes===1?'':'en'}${nBef?`, ${nBef} mit Befund`:''}`
          :nBef?`Auff&auml;llig &mdash; ${nBef} Position${nBef===1?'':'en'} mit Befund`
               :`Unauff&auml;llig &mdash; ${nGes} gepr&uuml;fte Position${nGes===1?'':'en'}`}</div>`
    : '';""",
    "Befundzeile: auffaellig / unauffaellig", wo="script")

# Statuszeile der Gene ohne Metabolisierer-Status
sub("""  const short=nurPos?'Nur Einzelpositionen':lvlLabel(g).t;""",
    """  /* Ohne Metabolisierer-Status gibt es keine andere Aussage als
     auffaellig/unauffaellig - genau danach wurde gefragt. */
  const short=nurPos
    ? ((RS_BY[g]||[]).some(p=>rsNeg(p[4]))?'Auff&auml;llig':'Unauff&auml;llig')
    : lvlLabel(g).t;""",
    "Statuszeile der Gene ohne Metabolisierer-Status", wo="script")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
assert "sev='crit'" not in s.split("function rsGeneSev(")[1].split("}")[0], \
    "rsGeneSev vergibt noch crit"
assert "RSRANG[p[3]]<=1" not in s, "Evidenzstufe faerbt noch"
assert s.count("function rsGeneSev(") == 1 and s.count("function geneSev(") == 1
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
