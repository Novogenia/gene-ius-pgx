# -*- coding: utf-8 -*-
"""
"Offen" verschwindet vollstaendig aus der Oberflaeche.

Vorgabe Daniel, 2026-08-05 (Nachtrag zu v61): "noch offen sollte weg".

v61 hatte die offenen Gene und Wirkstoffe aus den Listen genommen, aber an
drei Stellen stand der Zustand weiter im Text:

  1. Startseite, Verteilungsbalken: eigenes Segment und der Knopf
     "noch offen / ein dafuer noetiges Gen ist nicht bestimmbar".
  2. Startseite, Ampel-Legende: der Block "Medikamente, bei denen die
     Antwort offen bleibt".
  3. Arztbericht, Abdeckungsblock: die Kennzahl "Gene ohne eindeutiges
     Ergebnis" und die Tabelle, die alle 23 Panel-Gene fuehrte, also auch
     die sechs nicht bestimmbaren.

Die Kennzahl zeigte nach v61 ohnehin 0, weil sie ueber sortedGenes() lief -
eine Null in einem Kasten, der frueher etwas ausgesagt hat.

Was bleibt: der Abdeckungsblock nennt weiterhin **611 gelesene Stellen** und
**58 % Abdeckung der benoetigten Stellen**. Damit steht die Unvollstaendigkeit
weiterhin schwarz auf weiss im Arztbericht - nur eben als Zahl statt als Liste
der Luecken. Die Kennzahl "Gene im Panel (23)" wird zu "Gene ausgewertet (17)",
sonst widerspraeche sie der Tabelle darunter.
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

# ---------------------------------------------------------------- CSS
sub("""  .hb-keys{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-top:14px}""",
    """  .hb-keys{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:14px}""",
    "Verteilungslegende auf drei Knoepfe", wo="style")

# Die Regeln der entfallenen Knoepfe. --unk und die Kartenklassen bleiben:
# statusFor kann intern weiter 'unk' liefern, es taucht nur nicht mehr auf.
sub("""  .bf-unk{background:#77717F} .bf-unk[aria-pressed="true"]{background:#5B5664}
  .sf-unk{background:#77717F}
  .hbb.unk{background:#8E8896}
  .hbk.k-unk{border-left-color:var(--unk)} .hbk.k-unk .hbkn,.hbk.k-unk .hbkl{color:var(--unk-t)}
  .lg-unk .lgbox{background:#77717F} .lg-unk .lgmore{color:var(--unk-t)}
""", "", "CSS der entfallenen Offen-Knoepfe entfernen", wo="style")

# ------------------------------------------- Startseite: Balken und Legende
sub("""        <div class="hbb unk"  style="width:${pct(D.unk)}%"  title="${nf(D.unk)} offen"></div>
""", "", "Verteilungsbalken: Segment 'offen' entfernen", wo="script")

sub("""        <button class="hbk k-unk" onclick="goFilter('unk')">
          <span class="hbkn">${nf(D.unk)}</span>
          <span class="hbkl">noch offen</span>
          <span class="hbkd">ein daf&uuml;r n&ouml;tiges Gen ist nicht bestimmbar</span></button>
""", "", "Verteilungslegende: Knopf 'noch offen' entfernen", wo="script")

sub("""    <button class="lg lg-unk" onclick="goFilter('unk')">
      <div class="lgbox"><span class="lgn">${DBSTATS().unk.toLocaleString('de-DE')}</span><span class="lgl">Offen</span></div>
      <div class="lgtx"><h4>Medikamente, bei denen die Antwort offen bleibt</h4>
        <p>F&uuml;r diese Wirkstoffe gibt es sehr wohl eine Leitlinie &mdash; sie h&auml;ngt aber an
          einem Gen, das <b>in dieser Analyse nicht eindeutig bestimmt werden konnte</b>.
          Statt zu raten wird das offen gelassen. Eine gezielte Nachbestimmung schlie&szlig;t
          diese L&uuml;cke.${ihelp('offen')}</p>
        <span class="lgmore">In der Datenbank ansehen ${ico('arr','',14)}</span></div>
    </button>
""", "", "Ampel-Legende: Block 'Offen' entfernen", wo="script")

# ------------------------------------------------ Arztbericht: Abdeckungsblock
sub("""function covBlock(offen){
  const M=P_META, ges=M.posda+M.posfehlt;
  const pct=(100*M.posda/ges).toFixed(0);
  const rows=P_GENES.slice().sort((a,b)=>(a.ok===b.ok?0:a.ok?1:-1)||a.g.localeCompare(b.g))""",
    """function covBlock(){
  const M=P_META, ges=M.posda+M.posfehlt;
  const pct=(100*M.posda/ges).toFixed(0);
  /* Nur die ausgewerteten Gene, wie ueberall sonst auch (Vorgabe Daniel,
     2026-08-05). Die Unvollstaendigkeit steht weiter in den Kennzahlen
     darueber: 611 gelesene Stellen und 58 % Abdeckung. */
  const zeigbar=P_GENES.filter(g=>g.lvl>=0);
  const rows=zeigbar.slice().sort((a,b)=>(a.ok===b.ok?0:a.ok?1:-1)||a.g.localeCompare(b.g))""",
    "covBlock: Tabelle auf ausgewertete Gene beschraenken", wo="script")

sub("""        <div class="cov-k"><span class="n">${P_GENES.length}</span><span class="l">Gene im Panel</span></div>
        <div class="cov-k"><span class="n">${M.posda.toLocaleString('de-DE')}</span><span class="l">Stellen gelesen</span></div>
        <div class="cov-k"><span class="n">${pct}&thinsp;%</span><span class="l">Abdeckung der ben&ouml;tigten Stellen</span></div>
        <div class="cov-k"><span class="n">${offen.length}</span><span class="l">Gene ohne eindeutiges Ergebnis</span></div>
      </div>""",
    """        <div class="cov-k"><span class="n">${zeigbar.length}</span><span class="l">Gene ausgewertet</span></div>
        <div class="cov-k"><span class="n">${M.posda.toLocaleString('de-DE')}</span><span class="l">Stellen gelesen</span></div>
        <div class="cov-k"><span class="n">${pct}&thinsp;%</span><span class="l">Abdeckung der ben&ouml;tigten Stellen</span></div>
      </div>""",
    "covBlock: Kennzahl 'Gene ohne eindeutiges Ergebnis' entfernen", wo="script")

sub("""        Stand <b>${M.stand}</b>.
        ${offen.length?`Bei <b>${offen.map(g=>g).join(', ')}</b> reichen die gelesenen Stellen
          nicht f&uuml;r ein eindeutiges Ergebnis. Diese Gene sind unten als offen gekennzeichnet und
          flie&szlig;en in keine Empfehlung ein.`:''}</p>""",
    """        Stand <b>${M.stand}</b>.</p>""",
    "covBlock: Satz ueber die offenen Gene entfernen", wo="script")

sub("""  const nOffen=genes.filter(g=>PHENO[g].lvl<0);
  return `<div class="sec-title">F&uuml;r deinen Arzt &mdash; pharmakogenetischer Bericht</div>
  ${covBlock(nOffen)}""",
    """  return `<div class="sec-title">F&uuml;r deinen Arzt &mdash; pharmakogenetischer Bericht</div>
  ${covBlock()}""",
    "Arztbericht: covBlock ohne Offen-Liste aufrufen", wo="script")

# Der v61-Kommentar sagte, covBlock bleibe vollstaendig. Stimmt nicht mehr.
sub("""/* schlechteste Gene zuerst, danach die offenen Faelle, zuletzt die normalen */
const GORDER=[0,1,-1,3,2];
function sortedGenes(){
  /* Gene ohne eindeutiges Ergebnis werden nicht mehr angezeigt (Vorgabe
     Daniel, 2026-08-05). Der Abdeckungsnachweis im Arztbericht (covBlock)
     rechnet weiter auf P_GENES und bleibt vollstaendig - er ist der Beleg,
     was der Test lesen konnte. */""",
    """/* schlechteste Gene zuerst, zuletzt die normalen */
const GORDER=[0,1,-1,3,2];
function sortedGenes(){
  /* Gene ohne eindeutiges Ergebnis werden nicht angezeigt (Vorgabe Daniel,
     2026-08-05). Gilt seit dem Nachtrag auch fuer den Abdeckungsblock im
     Arztbericht; dort belegen jetzt die gelesenen Stellen und die
     Abdeckung in Prozent, wie weit die Auswertung traegt. */""",
    "sortedGenes: Kommentar an den Nachtrag angepasst", wo="script")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
assert "k-unk" not in s, "Legendenknopf k-unk noch vorhanden"
assert "lg-unk" not in s, "Legendenblock lg-unk noch vorhanden"
assert "nOffen" not in s, "nOffen wird noch benutzt"
assert '<span class="l">Gene ohne eindeutiges Ergebnis</span>' not in s, "Kennzahl noch vorhanden"
assert s.count("function covBlock()") == 1, "covBlock nicht sauber umgebaut"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
