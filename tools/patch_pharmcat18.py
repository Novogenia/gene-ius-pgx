# -*- coding: utf-8 -*-
"""
Zwei Korrekturen an den Demo-Genotypen aus v68.

1. DEMO-DATEN FAERBEN KEIN GEMESSENES GEN MEHR.

   Aufgefallen bei der Gegenprobe: CYP3A4 und DPYD stehen auf echten Daten
   auf gruen und wurden durch je eine ERFUNDENE Position gelb -
   CYP3A4 ueber rs2740574, DPYD ueber rs12119882. Damit hat die Fiktion die
   Bewertung eines gemessenen Gens veraendert, und bei DPYD ist das
   besonders unangenehm: daran haengen Fluorouracil und Capecitabin.

   Neue Regel: hat ein Gen einen gemessenen Phaenotyp, zaehlen fuer seine
   Stufe NUR die echten Positionen. Demo-Positionen bleiben auf der Karte
   sichtbar - einzeln als Demo markiert - aber sie faerben nichts.
   Reine Demo-Gene haengen weiter an ihren Demo-Positionen; dort ist es die
   einzige Aussage, und die Karte sagt das auch.

2. DIE DEMO-KENNZEICHNUNG STAND NUR UNTER "DEINE GENE".

   Vorgabe Daniel, 2026-08-06: "die Info, dass es Demo-Genotypen sind, ist
   ueberall weg." Stimmt - Dashboard, Wirkstoffliste, eigene Liste und
   Arztbericht hatten keinen Hinweis.

   Das Banner wird zu einer Funktion und steht jetzt auch auf der
   Startseite, direkt an den Kennzahlen, die die Demo-Gene mitzaehlen.

   Wirkstoffliste und eigene Liste bekommen keins: dort steckt keine
   Demo-Aussage drin - die Ampel der Wirkstoffe kommt aus PharmCAT und der
   Leitlinienmatrix, nicht aus rs-Befunden. Der Arztbericht ebenfalls
   nicht: seine Genkarten sind die 17 gemessenen, und nach Korrektur 1
   traegt keine davon mehr eine Demo-Stufe. Das ist eine Zusicherung, keine
   Nachlaessigkeit - sie wird unten mitgeprueft.

3. STARTSEITE ZAEHLT JETZT ALLE GENE.

   "Gene ausgewertet" stand auf 17, waehrend die Genansicht 488 Karten
   zeigt. Jetzt 488, mit der Aufteilung in der Unterzeile, und
   "Gene arbeiten anders" zaehlt die auffaelligen ueber geneSev().
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

# ------------------------------- 1. Demo faerbt kein gemessenes Gen
sub("""function rsGeneSev(g){
  const l=RS_BY[g]; if(!l)return null;""",
    """function rsGeneSev(g){
  let l=RS_BY[g]; if(!l)return null;
  /* Hat das Gen einen gemessenen Phaenotyp, zaehlen nur die echten
     Positionen. Sonst faerbt eine erfundene Position ein gemessenes
     Ergebnis um - genau so sind CYP3A4 und DPYD in v68 faelschlich auf
     gelb gesprungen. Die Demo-Zeilen bleiben auf der Karte sichtbar,
     sie entscheiden nur nichts. */
  if(PHENO[g]){ l=l.filter(p=>!istDemo(p)); if(!l.length)return null; }""",
    "Demo-Positionen faerben kein gemessenes Gen", wo="script")

# ------------------------------- 2. Banner als Funktion, auch auf der Startseite
sub("""  ${(typeof DUMMY_AKTIV!=='undefined'&&DUMMY_AKTIV)?`<div class="demoband">
    ${ico('n-warn','',20)}
    <div class="dbt"><b>Ein Teil dieser Karten beruht auf Demo-Genotypen.</b>
      Gemessen wurden ${geneZahlen().echt} Gene aus dem PharmCAT-Lauf. Die weiteren
      ${geneZahlen().demo} Gene tragen <b>erfundene</b> Genotypen &mdash; sie zeigen, wie die
      Ansicht mit vollst&auml;ndigen Rohdaten aussehen wird, und sind einzeln als
      <span class="demopill">Demo</span> gekennzeichnet. Keine dieser Angaben ist ein
      Messergebnis.</div></div>`:''}""",
    """  ${demoBannerHtml()}""",
    "Genansicht: Banner ueber die Funktion", wo="script")

sub("""function geneZahlen(){""",
    """/* Ein Hinweis, kein Kleingedrucktes. Steht ueberall dort, wo Demo-Zahlen
   in die Anzeige eingehen - Genansicht und Startseite. */
function demoBannerHtml(kurz){
  if(typeof DUMMY_AKTIV==='undefined'||!DUMMY_AKTIV)return '';
  const z=geneZahlen();
  return `<div class="demoband">${ico('n-warn','',20)}
    <div class="dbt"><b>Ein Teil dieser Auswertung beruht auf Demo-Genotypen.</b>
      Gemessen wurden <b>${z.echt} Gene</b> aus dem PharmCAT-Lauf. Die weiteren
      <b>${z.demo} Gene</b> tragen <b>erfundene</b> Genotypen &mdash; sie zeigen, wie die
      Ansicht mit vollst&auml;ndigen Rohdaten aussehen wird. Keine dieser Angaben ist ein
      Messergebnis.${kurz?'':` Jede erfundene Stelle ist einzeln als
      <span class="demopill">Demo</span> gekennzeichnet; die gemessenen Gene tragen
      keine Demo-Werte in ihrer Bewertung.`}</div></div>`;
}
function geneZahlen(){""",
    "Banner als Funktion", wo="script")

# ------------------------------------------------- 3. Startseite: Zahlen
sub("""  const auff=Object.keys(PHENO).filter(g=>PHENO[g].lvl>=0&&PHENO[g].lvl!==2).length;
  const nGene=Object.keys(PHENO).filter(g=>PHENO[g].lvl>=0).length;""",
    """  /* Zaehlt, was die Genansicht auch zeigt - sonst stehen auf der Startseite
     17 Gene und eine Ansicht weiter 488 Karten. auffaellig kommt aus
     geneSev(), also derselben Stelle wie die Kartenfarbe. */
  const gAlle=geneListe(), gZ=geneZahlen();
  const auff=gAlle.filter(g=>{const v=geneSev(g);return v==='warn'||v==='crit';}).length;
  const nGene=gAlle.length;""",
    "Startseite: Gene ueber geneListe zaehlen", wo="script")

sub("""        <div class="hsn">${nGene}</div>
        <div class="hsl">Gene ausgewertet</div>
        <div class="hsd">die pharmakogenetisch entscheidenden Gene</div>""",
    """        <div class="hsn">${nf(nGene)}</div>
        <div class="hsl">Gene ausgewertet</div>
        <div class="hsd">${gZ.demo?`${gZ.echt} gemessen, ${gZ.demo} mit Demo-Genotyp`
          :'die pharmakogenetisch entscheidenden Gene'}</div>""",
    "Startseite: Aufteilung in der Unterzeile", wo="script")

sub("""    <div class="hstats">
      <div class="hstat">
        <div class="hsic">${ico('n-dna','',22)}</div>""",
    """    ${demoBannerHtml(true)}
    <div class="hstats">
      <div class="hstat">
        <div class="hsic">${ico('n-dna','',22)}</div>""",
    "Startseite: Banner ueber den Kennzahlen", wo="script")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
assert s.count("function demoBannerHtml(") == 1, "Banner nicht genau einmal definiert"
assert s.count("demoBannerHtml(") == 3, "Banner nicht an beiden Stellen eingesetzt"
assert s.count("filter(p=>!istDemo(p))") == 1, "Demo-Filter fehlt in rsGeneSev"
# Der Arztbericht darf keine Demo-Positionen rendern
i = s.index("function geneReportCard(")
j = s.index("function drugReportBlock(")
assert "gPosHtml" not in s[i:j], "Arztbericht rendert Demo-Positionen"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
