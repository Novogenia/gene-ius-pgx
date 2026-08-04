# -*- coding: utf-8 -*-
"""
Die Ampel kommt aus dem Genotyp, nicht mehr aus den Flags.

Vorgabe Daniel, 2026-08-04: "Ob die Genetik, die wir bekommen, ein Anzeichen
dafuer gibt, dass wir eine nicht optimale Verstoffwechslung des Medikamentes
haben. Das sollte die Bewertung sein. Eine Alternative des Medikaments zu
haben, spielt darin nicht ein."

v59 hatte das Alt-Flag nur gedeckelt. Hier faellt es als Ampelquelle ganz weg.
Es fuellt weiter die Box "Handlung" - das ist eine Aussage der Leitlinie und
wird nicht verschwiegen -, aber es faerbt die Karte nicht mehr.

    lvl 2 normal        -> OK
    lvl 1 intermediaer  -> ACHTUNG
    lvl 0 poor          -> ALARM, ausser die Leitlinie nennt die Folge
                           ausdruecklich typisch/normal -> ACHTUNG
    lvl 3 ultraschnell  -> ALARM, wenn mehr Wirkstoff oder hoeheres Risiko
                           entsteht, sonst ACHTUNG
    kein Gen bestimmt   -> Offen

Warum die Leitlinie bei lvl 0 noch begrenzt: der reine Genotyp allein stellt
Daniels Ausgangsbeschwerde wieder her. Rosuvastatin haengt an ABCG2 Poor
Function; ohne diese Schranke stuende es wieder auf ALARM, obwohl CPIC
"Typical myopathy risk" schreibt. Die Genetik sagt, DASS abgewichen wird, die
Leitlinie sagt, WIE SCHLIMM das fuer diesen Wirkstoff ist. Beides wird
gebraucht - erfunden wird nichts, beide Angaben stehen in den Daten.

Ziel- und Risikogene bleiben vorerst auf der v59-Regel (Flag mit Deckel):
bei CFTR, RYR1, CACNA1S und VKORC1 wird nichts verstoffwechselt, die
Metabolisierer-Skala trifft dort nicht zu. Betrifft 10 Wirkstoffe, siehe
DOKUMENTATION.md 11 - das ist eine offene Entscheidung, keine Umsetzung.

Wirkung an den 94 Wirkstoffen mit PharmCAT-Empfehlung:
  vorher   OK 45 / ACHTUNG 20 / ALARM 29
  nachher  OK 34 / ACHTUNG 52 / ALARM  8
  28 runter, 16 hoch, 10 unberuehrt.

Runter, weil die Genetik keinen entsprechenden Befund hergibt: die
Trizyklika, Ondansetron, Paroxetin, Metoprolol, Flecainid, Haloperidol,
Risperidon (CYP2D6 ultraschnell = Wirkverlust, nicht Vergiftung),
Fluvastatin, Phenytoin, Siponimod (CYP2C9 intermediaer), Rosuvastatin
(ABCG2 poor, Folge typisch) sowie vier Protonenpumpenhemmer (CYP2C19
normal -> OK).

Hoch, weil die Genetik abweicht, obwohl die Leitlinie nichts verlangt:
Ibuprofen, Celecoxib, Meloxicam, Flurbiprofen, Lornoxicam, Tenoxicam,
Avatrombopag (CYP2C9 intermediaer), Venlafaxin, Aripiprazol, Brexpiprazol,
Amoxapin, Donepezil, Fluvoxamin, Hydrocodon, Pimozid (CYP2D6 ultraschnell).

Codein und Tramadol bleiben ALARM: CYP2D6 ultraschnell UND "increased
formation of morphine leading to higher risk of toxicity".
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

# ------------------------------------------------------ 1. Die neue Ampel
sub("""function pEffSev(r){return pDeckel(r.sev,r.flags,r.imp);}""",
    """function pEffSev(r){return pDeckel(r.sev,r.flags,r.imp);}
/* Wo die Leitlinie die Folge ausdruecklich als typisch bezeichnet, ist eine
   Abweichung im Genotyp noch kein Alarm. Ohne diese Schranke stuende
   Rosuvastatin ueber ABCG2 Poor Function wieder auf ALARM, obwohl CPIC
   "Typical myopathy risk" schreibt. */
const PMILD=/low risk|normal risk|typical .*risk|does not appear to translate|typical /;
/* Die Ampel aus dem Genotyp: gibt die Genetik ein Anzeichen dafuer, dass
   dieser Wirkstoff nicht optimal verstoffwechselt wird? Dass eine Alternative
   verfuegbar waere, geht nicht ein - das ist eine Eigenschaft des Marktes,
   keine des Patienten. Vorgabe Daniel, 2026-08-04.
   stoff=false bei Ziel- und Risikogenen (CFTR, RYR1, CACNA1S, VKORC1): dort
   wird nichts verstoffwechselt, die Skala trifft nicht zu, dort bleibt es
   vorerst bei der Flag-Regel mit Deckel. */
function pGenSev(lvl,stoff,bestimmt,h,imp){
  if(!stoff)return pDeckel(h.sev,h.flags,imp);
  if(!bestimmt)return 'unk';
  const t=(imp||'').toLowerCase();
  if(lvl===2)return 'ok';
  if(lvl===1)return 'warn';
  if(lvl===0)return PMILD.test(t)?'warn':'crit';
  /* ultraschnell: die Richtung steht nur im Text. Codein bildet MEHR Morphin
     (Vergiftung), Amitriptylin WENIGER Wirkstoff (Wirkverlust). */
  return (PW_STARK.test(t)||PT_HOCH.test(t))?'crit':'warn';
}""",
    "pGenSev: Ampel aus dem Genotyp", wo="script")

# --------------------------------------------- 2. statusFor umverdrahten
sub("""    let plvl=2;
    Object.keys(PHENO).forEach(g=>{
      if((h.gt||'').indexOf(g)<0)return;
      const l=PHENO[g].lvl; if(l<0)return;
      if(Math.abs(l-2)>Math.abs(plvl-2))plvl=l;
    });
    /* Deckel, siehe pDeckel: eine belegt normale Wirkung bei normalem
       Risiko kann nie ALARM sein. Entscheidung Daniel, 2026-08-04. */
    const sev=pDeckel(h.sev,h.flags,pImpOf(pr)), gekappt=sev!==h.sev;
    const wirkung=sev==='crit'
      ? "Fuer dich ist ein anderer Wirkstoff angezeigt."
      : sev==='warn'
        ? "Die Dosis muss angepasst oder die Wirkung ueberwacht werden."
        : "Es ist keine Anpassung noetig.";
    return{sev:sev, lvl:plvl, pharm:true, gekappt:gekappt, flags:h.flags, gt:h.gt,""",
    """    let plvl=2, stoff=true, gefunden=0, bestimmt=0;
    Object.keys(PHENO).forEach(g=>{
      if((h.gt||'').indexOf(g)<0)return;
      gefunden++;
      const a=PHENO[g].art;
      if(a!=='enz'&&a!=='trans')stoff=false;
      const l=PHENO[g].lvl; if(l<0)return;
      bestimmt++;
      if(Math.abs(l-2)>Math.abs(plvl-2))plvl=l;
    });
    /* Die Ampel kommt aus dem Genotyp, siehe pGenSev. Das Alt-Flag faerbt die
       Karte nicht mehr; es fuellt nur noch die Box "Handlung". */
    const sev=pGenSev(plvl,gefunden&&stoff,bestimmt,h,pImpOf(pr));
    const gekappt=PSEV.indexOf(sev)<PSEV.indexOf(h.sev);
    const wirkung=sev==='crit'
      ? "Fuer dich ist ein anderer Wirkstoff angezeigt."
      : sev==='warn'
        ? "Die Dosis muss angepasst oder die Wirkung ueberwacht werden."
        : sev==='unk'
          ? "Das dafuer noetige Gen konnte nicht bestimmt werden."
          : "Es ist keine Anpassung noetig.";
    return{sev:sev, lvl:plvl, pharm:true, gekappt:gekappt, flags:h.flags, gt:h.gt,""",
    "statusFor: Ampel aus dem Genotyp statt aus den Flags", wo="script")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
for name in ("function pGenSev(", "function pDeckel(", "const PMILD="):
    assert s.count(name) == 1, "%s nicht genau einmal vorhanden" % name
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
