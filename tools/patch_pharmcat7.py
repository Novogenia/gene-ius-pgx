# -*- coding: utf-8 -*-
"""
Zwei Korrekturen an pharmMetrics:

1. Es wurden die Implikationen ALLER Quellen aneinandergehaengt. Bei
   Fluvastatin stehen darin SLCO1B1 ("Typical myopathy risk") und CYP2C9
   ("Mildly reduced metabolism") nebeneinander - das ergibt ein schiefes
   Bild. Massgeblich ist die Zeile, die auch die Ampel bestimmt.

2. 143 von 324 Boxen standen auf "Nicht angegeben". Vier Kaesten, von denen
   die Haelfte leer ist, sehen nach Fehler aus. Boxen ohne Aussage werden
   weggelassen; die Handlung bleibt immer stehen, und darunter steht, worauf
   sich die Empfehlung stuetzt.
"""
import io

APP = "pgx_app.html"
s = io.open(APP, encoding="ascii").read()
orig = len(s)

ALT = """  const pr=pharmRec(id); if(!pr)return null;
  const t=pr.alle.map(x=>x.imp||'').join(' ').toLowerCase();"""
NEU = """  const pr=pharmRec(id); if(!pr)return null;
  /* Massgeblich ist die Zeile, die auch die Ampel bestimmt. Erst wenn die
     keine Folge nennt, wird die naechste Quelle herangezogen. */
  const q=pr.haupt.imp || (pr.alle.find(x=>x.imp)||{}).imp || '';
  const t=q.toLowerCase();"""
assert s.count(ALT) == 1, "Implikationsquelle nicht eindeutig gefunden"
s = s.replace(ALT, NEU)
print("  ok  nur die massgebliche Zeile auswerten")

ALT2 = """  const akt=(f&1) ? B("Handlung","Anderer Wirkstoff","crit","s-stop")
          : (f&2) ? B("Handlung","Dosis anpassen","warn","s-up")
          : (f&4) ? B("Handlung","&Uuml;berwachen","warn","s-up")
          :         B("Handlung","Keine Anpassung","ok","s-check");
  return [wirk,ums,tox,akt];"""
NEU2 = """  const akt=(f&1) ? B("Handlung","Anderer Wirkstoff","crit","s-stop")
          : (f&2) ? B("Handlung","Dosis anpassen","warn","s-up")
          : (f&4) ? B("Handlung","&Uuml;berwachen","warn","s-up")
          :         B("Handlung","Keine Anpassung","ok","s-check");
  /* Was der Text nicht hergibt, wird weggelassen statt grau angezeigt.
     Stattdessen kommt der Genotyp dazu, auf den sich die Empfehlung stuetzt -
     das ist die eigentliche Grundlage und immer vorhanden. */
  const o=[wirk,ums,tox].filter(x=>x.sev!=='unk');
  o.push(akt);
  if(st.gt)o.push(B("Grundlage",st.gt.replace(/ Metabolizer/g,'').replace(/ Function/g,''),
                    st.sev==='ok'?'ok':(st.sev==='crit'?'crit':'warn'),'n-dna'));
  return o;"""
assert s.count(ALT2) == 1, "Rueckgabe nicht eindeutig gefunden"
s = s.replace(ALT2, NEU2)
print("  ok  leere Boxen weglassen, Grundlage ergaenzen")

assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\nDatei: %d -> %d Zeichen" % (orig, len(s)))
