# -*- coding: utf-8 -*-
"""
Alarm aus der Genetik und Alarm aus einer Wechselwirkung auseinanderhalten.

Vorgabe Daniel, 2026-08-08: "wir wollten zwischen Alarm wegen
Pharmakogenetik und Alarm wegen Interaktionen unterscheiden. Wir brauchen
ein anderes rotes Icon und einen anderen Begriff, wie zum Beispiel
Interaktion."

Bisher stand auf beiden Faellen ALARM mit demselben Ausrufezeichen. Bei
Clopidogrel fuehrte das zu Daniels Rueckfrage: genetisch unauffaellig,
trotzdem ALARM - die Ursache war die Wechselwirkung mit Omeprazol, aber am
Etikett nicht zu erkennen. v74 hat den Grund im Beurteilungskasten benannt;
hier bekommt er ein eigenes Etikett.

  Stufe aus dem Genprofil        -> ALARM / Achtung, Ausrufezeichen
  Stufe aus einer Wechselwirkung -> INTERAKTION, Blitzsymbol (c-ix)

Beides bleibt rot bzw. gelb - die Dringlichkeit ist dieselbe, nur die
Ursache eine andere. sevQuelle() entscheidet: 'ix' nur dann, wenn die
Wechselwirkung die Stufe ANHEBT. Ist ein Wirkstoff schon genetisch auf
Alarm, bleibt es ALARM, auch wenn zusaetzlich eine Wechselwirkung besteht -
sonst verschwaende das genetische Ergebnis hinter dem Etikett.

DAZU DIE BILANZ ENTZERRT: die Medikamentenkacheln zaehlten bisher ueber
overallSev, also inklusive Wechselwirkungen - dieselbe Wechselwirkung
tauchte links und rechts auf. Links stehen jetzt die genetischen Stufen
(listSev), rechts die Wechselwirkungen. Keine Doppelzaehlung mehr.
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

# ------------------------------------------------------- Quelle der Stufe
sub("""const SLABEL={ok:"OK",unk:"Offen",warn:"Achtung",crit:"ALARM"};""",
    """const SLABEL={ok:"OK",unk:"Offen",warn:"Achtung",crit:"ALARM"};
/* Woher kommt die Stufe - aus dem Genprofil oder aus einer Wechselwirkung?
   'ix' nur, wenn die Wechselwirkung die Stufe ANHEBT. Ist ein Wirkstoff
   schon genetisch auf Alarm, bleibt ALARM stehen; sonst verschwaende das
   genetische Ergebnis hinter dem Etikett. */
function sevQuelle(id,pool){
  if(!pool)return 'gen';
  const g=statusFor(id).sev, ges=overallSev(id,pool);
  return RANK[ges]>RANK[g]?'ix':'gen';
}
function sevLabel(id,sev,pool){
  return sevQuelle(id,pool)==='ix'?'Interaktion':SLABEL[sev];
}
function sevIcon(id,sev,pool){
  return sevQuelle(id,pool)==='ix'?'c-ix':(sev==='ok'?'st-ok':'st-excl');
}""",
    "sevQuelle, sevLabel, sevIcon", wo="script")

# ------------------------------------------------------------ Wirkstoffkarte
sub("""        ${ico(sev==='ok'?'st-ok':'st-excl','st s-'+sev)}
        <span class="sw t-${sev}">${SLABEL[sev]}</span>""",
    """        ${ico(sevIcon(id,sev,opts.sevPool),'st s-'+sev)}
        <span class="sw t-${sev}">${sevLabel(id,sev,opts.sevPool)}</span>""",
    "Karte: Etikett nach Ursache", wo="script")

# ------------------------------------------------------------- Arztbericht
sub("""        <span class="pillbadge b-${sev}">${ico(sev==='ok'?'st-ok':'st-excl','',15)} ${SLABEL[sev]}</span>""",
    """        <span class="pillbadge b-${sev}">${ico(sevIcon(id,sev,pool),'',15)} ${sevLabel(id,sev,pool)}</span>""",
    "Arztbericht: Etikett nach Ursache", wo="script")

# ------------------------------------------------------- Beurteilungskasten
sub("""      <span class="ab-badge b-${sev}">${SLABEL[sev]}</span></div>""",
    """      <span class="ab-badge b-${sev}">${sevLabel(id,sev,workspace)}</span></div>""",
    "Beurteilung: Etikett nach Ursache", wo="script")

# ------------------------------------------------------------ Bilanz entzerrt
sub("""function medScore(){
  const z={crit:0,warn:0,ok:0,unk:0};
  workspace.forEach(id=>{
    const ersatz=altChoice[id]?findDrug(altChoice[id]):null;
    const s=overallSev(ersatz||id,workspace);
    z[s]=(z[s]||0)+1;
  });
  return z;
}""",
    """/* Nur die GENETISCHE Stufe - die Wechselwirkungen stehen als eigene
   Kacheln daneben. Vorher lief das ueber overallSev, dadurch tauchte
   dieselbe Wechselwirkung in beiden Gruppen auf. */
function medScore(){
  const z={crit:0,warn:0,ok:0,unk:0};
  workspace.forEach(id=>{
    const ersatz=altChoice[id]?findDrug(altChoice[id]):null;
    const s=listSev(ersatz||id);
    z[s]=(z[s]||0)+1;
  });
  return z;
}""",
    "Bilanz: Medikamente nur nach Genetik", wo="script")

sub("""      ${kachel('neutral',workspace.length,'Medikamente')}
      ${kachel('crit',m.crit,'mit Alarm')}
      ${kachel('warn',m.warn,'mit Achtung')}
      ${kachel('ok',m.ok,'unauff&auml;llig')}""",
    """      ${kachel('neutral',workspace.length,'Medikamente')}
      ${kachel('crit',m.crit,'genetisch Alarm')}
      ${kachel('warn',m.warn,'genetisch Achtung')}
      ${kachel('ok',m.ok,'genetisch unauff&auml;llig')}""",
    "Bilanz: Beschriftung der Medikamentenkacheln", wo="script")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
for name in ("function sevQuelle(", "function sevLabel(", "function sevIcon("):
    assert s.count(name) == 1, "%s nicht genau einmal vorhanden" % name
assert s.count("sevLabel(") == 4, "sevLabel nicht an allen drei Etiketten"
assert s.count("sevIcon(") == 3, "sevIcon nicht an beiden Symbolen"
assert "listSev(ersatz||id)" in s, "medScore rechnet noch ueber overallSev"
# sevQuelle braucht RANK und overallSev - beide Funktionsdeklarationen bzw.
# vorher deklariert; RANK ist ein const und muss davorstehen
assert s.index("const RANK=") < s.index("function sevQuelle("), "RANK steht hinter sevQuelle (TDZ)"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
