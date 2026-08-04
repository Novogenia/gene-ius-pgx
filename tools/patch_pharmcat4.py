# -*- coding: utf-8 -*-
"""
Korrektur der Wirkstoff-Zuordnung.

Der erste Versuch hat nur 11 von 94 PharmCAT-Wirkstoffen getroffen, weil er
ueber die Objektschluessel gegangen ist. Die sind aber uneinheitlich:
Demo-Wirkstoffe haben deutsche Schluessel ("codein"), die 2.697 aus der
Datenbank synthetische ("w127") mit englischem Anzeigenamen. Zugeordnet wird
deshalb ueber den Namen, mit ALIAS in beide Richtungen.
"""
import io

APP = "pgx_app.html"
s = io.open(APP, encoding="ascii").read()
orig = len(s)

ALT = """  const loese=(name)=>{
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
  };"""

NEU = """  /* Namensregister: Anzeigename klein -> Schluessel. Noetig, weil die
     Schluessel uneinheitlich sind - Demo-Wirkstoffe deutsch ("codein"),
     Datenbank-Wirkstoffe synthetisch ("w127") mit englischem Namen. */
  const NAMEIDX={};
  Object.keys(DRUGS).forEach(k=>{
    const nm=(DRUGS[k].name||'').toLowerCase().trim();
    if(nm&&NAMEIDX[nm]===undefined)NAMEIDX[nm]=k;
  });
  /* ALIAS zeigt deutsch -> englisch; fuer PharmCAT wird die Gegenrichtung
     gebraucht, und die deutsche Demo-Karte hat Vorrang, damit sich die
     Bewertung nicht auf zwei Karten desselben Wirkstoffs aufteilt. */
  const ALIASREV={};
  if(typeof ALIAS!=='undefined')Object.keys(ALIAS).forEach(de=>{
    if(DRUGS[de])ALIASREV[String(ALIAS[de]).toLowerCase()]=de;
  });
  const SALZ=/\\s+(sulfate|sulphate|hydrochloride|hcl|sodium|potassium|calcium|maleate|tartrate|citrate|besylate|mesylate|succinate|fumarate|acetate|phosphate)$/;
  const einer=(t)=>{
    t=t.trim().toLowerCase(); if(!t)return null;
    if(ALIASREV[t])return ALIASREV[t];
    if(NAMEIDX[t]!==undefined)return NAMEIDX[t];
    if(DRUGS[t])return t;
    const b=t.replace(SALZ,'');
    if(b!==t){ if(ALIASREV[b])return ALIASREV[b];
               if(NAMEIDX[b]!==undefined)return NAMEIDX[b];
               if(DRUGS[b])return b; }
    return null;
  };
  const loese=(name)=>{
    /* Verbundpraeparate stehen als "a / b / c" - jeder Bestandteil einzeln */
    const out=name.split('/').map(einer).filter(Boolean);
    return [...new Set(out)];
  };"""

assert s.count(ALT) == 1, "Zuordnungsfunktion nicht eindeutig gefunden"
s = s.replace(ALT, NEU)
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("Zuordnung ueber Namensregister eingebaut. %d -> %d Zeichen" % (orig, len(s)))
