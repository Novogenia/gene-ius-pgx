# -*- coding: utf-8 -*-
"""
Kugelsymbol fuer den Metabolisierertyp statt der DNA-Helix auf der Genkarte.

Vorgabe Daniel, 2026-08-06:
  Poor      -> rote Kugel mit weissem X
  Vermindert-> orange Kugel mit Pfeil nach unten
  Normal    -> gruene Kugel mit weissem Haekchen
  Schnell   -> dunkelgruene Kugel mit zwei Pluszeichen
  "Dieses Icon sollten wir in den GEN-Karten darstellen, anstatt des Icons
   der DNA."

Die Farben sind die bereits vergebenen aus GCOL, damit Symbol und Skala
derselben Karte nicht auseinanderlaufen:
  0 #E12D2D, 1 #F08A00, 2 #12A150, 3 #0b6b36

Gezeichnet wird inline, nicht als <symbol> - genau wie helix() das schon
macht. Grund: die Kugel braucht zwei Farben (Fuellung plus weisses Glyph),
und die Fuellung haengt an der Stufe. Ein <symbol> koennte das nur ueber
currentColor, und das reicht fuer zwei Farben nicht. Verlaeufe waeren
ohnehin verboten (Fallstrick 1).

GENE OHNE METABOLISIERERTYP - CFTR, RYR1, CACNA1S und die Transporter mit
Sonderbefund - haben keine Stufe auf dieser Skala. Sie bekommen dieselbe
Kugelform, aber nach der Kartenstufe: unauffaellig ein gruenes Haekchen,
auffaellig eine orange Kugel mit Ausrufezeichen. Das behauptet keinen
Metabolisierertyp und bleibt in derselben Bildsprache.

helix() bleibt im Code - es wird noch fuer die Karte "nicht getestet"
gebraucht und ist die Vorlage fuer die Zeichenweise.
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

# ------------------------------------------------------------------- CSS
sub("""  .gb-ic svg{width:34px;height:44px}""",
    """  .gb-ic svg{width:34px;height:44px}
  /* Kugelsymbol ist quadratisch, nicht hochkant wie die Helix */
  .gb-ic svg.mtico{width:40px;height:40px}""",
    "CSS: Groesse des Kugelsymbols", wo="style")

# --------------------------------------------------------------- Zeichnung
sub("""function helix(lvl){""",
    """/* Kugelsymbol fuer den Metabolisierertyp (Vorgabe Daniel, 2026-08-06).
   Inline gezeichnet, weil die Kugel zwei Farben braucht - Fuellung nach
   Stufe, Glyph in Weiss. Ein <symbol> kann ueber currentColor nur eine
   Farbe transportieren. */
const MTCOL={0:'#E12D2D',1:'#F08A00',2:'#12A150',3:'#0b6b36'};
const MTGLYPH={
  /* Poor: X */
  0:'<path d="M15.5 15.5 28.5 28.5M28.5 15.5 15.5 28.5" stroke="#fff" stroke-width="3.6" stroke-linecap="round"/>',
  /* Vermindert: Pfeil nach unten */
  1:'<path d="M22 13.5V29M15.8 22.8 22 29.4 28.2 22.8" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>',
  /* Normal: Haekchen */
  2:'<path d="M14.2 22.4 19.6 27.8 30 16.6" fill="none" stroke="#fff" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/>',
  /* Schnell: zwei Pluszeichen */
  3:'<path d="M16.4 18.6V25.4M13 22h6.8M27.6 18.6V25.4M24.2 22H31" stroke="#fff" stroke-width="3" stroke-linecap="round"/>'
};
/* Ausrufezeichen fuer Gene ohne Metabolisierertyp, die auffaellig sind */
const MTAUSRUF='<path d="M22 13.6v9.6" stroke="#fff" stroke-width="3.6" stroke-linecap="round"/><circle cx="22" cy="29.4" r="2.1" fill="#fff"/>';
/* Welche Stufe das Symbol zeigen darf. Risiko- und Zielgene (RYR1, CACNA1S,
   CFTR) tragen zwar lvl 2, haben aber gar keinen Metabolisierertyp - dort
   waere ein gruenes "Normaler Metabolisierer" eine falsche Behauptung.
   Sie bekommen null und damit die Kugel nach Kartenstufe. */
function mtStufe(g,lvl){
  return (PGENE[g]&&PGENE[g].flach)?null:lvl;
}
function mtIcon(lvl, sev){
  let c, glyph;
  if(MTGLYPH[lvl]!==undefined){ c=MTCOL[lvl]; glyph=MTGLYPH[lvl]; }
  else {
    /* Kein Metabolisierertyp: die Kugel folgt der Kartenstufe, ohne einen
       Typ zu behaupten. */
    const auf=(sev==='warn'||sev==='crit');
    c=auf?(sev==='crit'?MTCOL[0]:MTCOL[1]):MTCOL[2];
    glyph=auf?MTAUSRUF:MTGLYPH[2];
  }
  return `<svg class="mtico" viewBox="0 0 44 44" aria-hidden="true">
    <circle cx="22" cy="22" r="19" fill="${c}"/>${glyph}</svg>`;
}
function helix(lvl){""",
    "Kugelsymbol zeichnen", wo="script")

# ------------------------------------------------- auf der Genkarte einsetzen
sub("""    <div class="gb-top"><div class="gb-ic gi-${sv}">${helix(lvl)}</div>""",
    """    <div class="gb-top"><div class="gb-ic gi-${sv}">${mtIcon(mtStufe(g,lvl),sv)}</div>""",
    "Genkarte flach: Kugelsymbol", wo="script")

sub("""      <div class="gb-ic gi-${sv}">${helix(lvl)}</div>""",
    """      <div class="gb-ic gi-${sv}">${mtIcon(mtStufe(g,lvl),sv)}</div>""",
    "Genkarte: Kugelsymbol", wo="script")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
assert s.count("function mtIcon(") == 1, "mtIcon nicht genau einmal definiert"
assert s.count("function mtStufe(") == 1, "mtStufe nicht genau einmal definiert"
assert s.count("${mtIcon(mtStufe(g,lvl),sv)}") == 2, "Kugelsymbol nicht an beiden Kartenstellen"
assert s.count("${helix(lvl)}") == 0, "auf der Genkarte steht noch die Helix"
assert s.count("${helix(2)}") == 1, "Karte 'nicht getestet' soll die Helix behalten"
# keine Verlaeufe im neuen Symbol (Fallstrick 1)
assert "url(#" not in s[s.index("const MTGLYPH="):s.index("function helix(")], \
    "Verweis auf Verlauf oder Filter im Kugelsymbol"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
