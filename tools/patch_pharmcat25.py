# -*- coding: utf-8 -*-
"""
Die Plattform fuer Mobiltelefone brauchbar machen.

Vorgabe Daniel, 2026-08-08: "Macht die ganze Plattform ausserdem responsive
fuer Mobiltelefone."

BESTANDSAUFNAHME. Breakpoints gibt es bereits reichlich - 1180, 1080, 900,
820, 800, 760, 640, 620, 520, 420. Was fehlt, ist der Umgang mit der festen
Kartenbreite:

  --cardw: 352px

Die drei Kartenraster stehen auf `repeat(auto-fill, var(--cardw))` und
fallen erst bei 420px auf eine Spalte. Das hilft nichts: die KARTE bleibt
352px breit. Auf einem Telefon mit 360-390px Breite plus Seitenrand ragt sie
heraus - und weil alle Raster betroffen sind, betrifft es Startseite,
Genansicht und Wirkstoffliste gleichzeitig.

Die Raster bekommen deshalb durchgaengig

  repeat(auto-fill, minmax(min(100%, var(--cardw)), 1fr))

Das ist an jeder Breite richtig: oberhalb 352px verhaelt es sich wie bisher,
darunter schrumpft die Spalte auf die verfuegbare Breite statt
herauszuragen. Die drei 420px-Sonderregeln werden damit ueberfluessig und
fallen weg.

WAS SONST NOCH BRICHT, in der Reihenfolge des Auftretens:

  .col-scroll     minmax(292px,1fr) - dieselbe Falle eine Stufe kleiner
  .cov-tab        sechsspaltige Tabelle im Arztbericht, nicht umbrechbar -
                  bekommt einen eigenen Scrollbereich statt die Seite zu
                  sprengen (Abschnitt 7 verlangt scrollWidth==clientWidth
                  fuer die SEITE, ein Kasten darf scrollen)
  .grow/.mrow     Genzeilen und Matrixzeilen im Bericht, dito
  Genmodal        260px+1fr nebeneinander -> untereinander
  .rd-metrics     minmax(190px,1fr) -> min(100%,190px)
  .cov-rest       minmax(168px,1fr) -> min(100%,168px)
  .bigfilters     minmax(178px,1fr) -> min(100%,178px)
  .kpis           minmax(216px,1fr) -> min(100%,216px)
  .vgrid          minmax(184px,1fr) -> min(100%,184px)
  Seitenrand      unter 430px enger, sonst bleibt kaum Karte uebrig

Die Navigationsleiste wird ab 1080px bereits statisch und steht dann ueber
dem Inhalt - das funktioniert auf dem Telefon und bleibt.

PRUEFUNG. Der Browser-Pane dieser Umgebung geht nicht unter 980px, Media
Queries feuern dort nicht. Geprueft wurde deshalb ueber eine Verschiebung
der Haltepunkte im laufenden Dokument: alle max-width-Werte temporaer auf
einen Wert oberhalb der Panebreite gesetzt, gemessen, zurueckgesetzt. Das
prueft die Regeln selbst, nicht die Fensterbreite.
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

# ------------------------------------- 0. Die Grid-Falle: 1fr schrumpft nicht
# `1fr` hat als Minimum `auto`, also min-content. Ein Kind, das breiter ist,
# sprengt damit den Container statt zu schrumpfen. Gemessen: .split war 356px
# breit, die Spalte rechnete 378px. minmax(0,1fr) erlaubt das Schrumpfen.
sub("""  @media(max-width:1180px){.split{grid-template-columns:1fr} .dragarrow{display:none}}""",
    """  @media(max-width:1180px){.split{grid-template-columns:minmax(0,1fr)} .dragarrow{display:none}}""",
    "Arbeitsflaeche darf schrumpfen", wo="style")

sub("""  @media(max-width:900px){.rgene{grid-template-columns:1fr}}""",
    """  @media(max-width:900px){.rgene{grid-template-columns:minmax(0,1fr)}}""",
    "Genzeile im Bericht darf schrumpfen", wo="style")

sub("""  @media(max-width:900px){.rdrug{grid-template-columns:1fr}}""",
    """  @media(max-width:900px){.rdrug{grid-template-columns:minmax(0,1fr)}}""",
    "Wirkstoffzeile im Bericht darf schrumpfen", wo="style")

# ---------------------------------------------- 1. Die drei Kartenraster
for name, rest in (("dashgrid", "gap:14px"),
                   ("genegrid", "gap:14px"),
                   ("grid3", "gap:0 14px;align-items:start")):
    sub("""  .%s{display:grid;grid-template-columns:repeat(auto-fill,var(--cardw));justify-content:start;%s}
  @media(max-width:420px){.%s{grid-template-columns:1fr}}""" % (name, rest, name),
        """  /* min(100%%,...) statt fester Breite: oberhalb 352px wie bisher, darunter
     schrumpft die Spalte statt herauszuragen. Ersetzt die frueheren
     420px-Sonderregeln. */
  .%s{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%%,var(--cardw)),1fr));
    justify-content:start;%s}""" % (name, rest),
        "Kartenraster %s mitwachsend" % name, wo="style")

# ------------------------------------------------- 2. Die uebrigen Raster
for alt, neu, was in (
    ("""    display:grid;grid-template-columns:repeat(auto-fill,minmax(292px,1fr));""",
     """    display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,292px),1fr));""",
     "Liste unter 'Deine Medikamente'"),
    (""".rd-metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:8px}""",
     """.rd-metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,190px),1fr));gap:8px}""",
     "Kennzahlen im Arztbericht"),
    ("""  .cov-rest{display:grid;grid-template-columns:repeat(auto-fill,minmax(168px,1fr));gap:5px 12px}""",
     """  .cov-rest{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,168px),1fr));gap:5px 12px}""",
     "Genraster im Arztbericht"),
    ("""  .bigfilters{display:grid;grid-template-columns:repeat(auto-fit,minmax(178px,1fr));gap:11px;margin-bottom:16px}""",
     """  .bigfilters{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,178px),1fr));gap:11px;margin-bottom:16px}""",
     "Grosse Filterknoepfe"),
    ("""  .kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(216px,1fr));gap:16px;margin-bottom:24px}""",
     """  .kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,216px),1fr));gap:16px;margin-bottom:24px}""",
     "Kennzahlenkacheln"),
    ("""  .cov-g{display:grid;grid-template-columns:repeat(auto-fit,minmax(132px,1fr));gap:10px;margin-bottom:12px}""",
     """  .cov-g{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,132px),1fr));gap:10px;margin-bottom:12px}""",
     "Abdeckungs-Kennzahlen"),
):
    sub(alt, neu, was, wo="style")

sub("""  .rd-genecards{display:grid;grid-template-columns:repeat(auto-fill,var(--cardw));justify-content:start;gap:10px}""",
    """  .rd-genecards{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,var(--cardw)),1fr));
    justify-content:start;gap:10px}""",
    "Genkarten im Arztbericht mitwachsend", wo="style")

sub("""  .vgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(184px,1fr));gap:4px 12px;""",
    """  .vgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,184px),1fr));gap:4px 12px;""",
    "Variantenraster", wo="style")

# ------------------------------------------------- 3. Genmodal untereinander
sub("""      <div style="display:grid;grid-template-columns:260px minmax(0,1fr);gap:18px;align-items:start">""",
    """      <div class="gm-split">""",
    "Genmodal: Klasse statt Inline-Stil", wo="script")

# --------------------------------------------- 4. Mobilblock am Stylesheet-Ende
sub("""  /* Kugelsymbol ist quadratisch, nicht hochkant wie die Helix */""",
    """  /* ---------- Telefon ----------------------------------------------
     Die breiten Raster sind oben schon mitwachsend. Hier bleibt, was sich
     nicht rechnen laesst: nebeneinanderliegende Bloecke, nicht umbrechbare
     Tabellen und der Seitenrand. */
  .gm-split{display:grid;grid-template-columns:260px minmax(0,1fr);gap:18px;align-items:start}
  /* Nicht umbrechbare Tabellen scrollen in ihrem eigenen Kasten. Die SEITE
     bleibt damit ueberlauffrei - das verlangt die Pruefroutine, ein Kasten
     darf scrollen. */
  .tabscroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
  @media(max-width:820px){
    .gm-split{grid-template-columns:1fr}
  }
  @media(max-width:640px){
    .cov-tab{min-width:560px}
    .grow,.mrow{min-width:520px}
    /* Die Aktionsknoepfe sitzen sonst absolut 44px RECHTS AUSSERHALB der
       Zeile - auf dem Telefon ragen sie damit aus dem Bild. Hier stehen sie
       als Reihe unter der Karte. */
    .wsactions{position:static;transform:none;right:auto;top:auto;
      display:flex;flex-direction:row;gap:8px;justify-content:flex-end;
      margin:-6px 0 12px}
    .ixs-trenn{display:none}
    .ixs-row{gap:14px}
    .ixs-n{font-size:22px}
  }
  @media(max-width:430px){
    main#main{padding:14px 12px 56px}
    .hero{padding:20px 15px;border-radius:16px}
    .wsurface{padding:15px 13px 17px}
    .rsband,.ixscore{padding:13px 13px}
    .rgene,.rdrug{padding:14px 13px}
    .cov-b{padding:13px}
    .sec-title{font-size:20px}
    .genebox,.card{border-radius:14px}
    .bigfilters{gap:8px}
    .sevfilters{grid-template-columns:repeat(2,minmax(0,1fr))}
  }
  /* Kugelsymbol ist quadratisch, nicht hochkant wie die Helix */""",
    "Mobilblock", wo="style")

# ------------------------------------------ 5. Tabellen in Scrollkaesten
sub("""      <table class="cov-tab">""",
    """      <div class="tabscroll"><table class="cov-tab">""",
    "Abdeckungstabelle scrollbar", wo="script")

sub("""        <tbody>${rows}</tbody></table>""",
    """        <tbody>${rows}</tbody></table></div>""",
    "Abdeckungstabelle schliessen", wo="script")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
assert "@media(max-width:420px)" not in s, "alte 420px-Sonderregeln noch da"
assert s.count("minmax(min(100%,var(--cardw)),1fr)") == 4, "nicht alle Kartenraster umgestellt"
assert "grid-template-columns:repeat(auto-fill,var(--cardw))" not in s, \
    "irgendwo steht noch ein Raster mit fester Kartenbreite"
assert s.count("class=\"tabscroll\"") == 1, "Scrollkasten fehlt"
assert s.count("</table></div>") == 1, "Scrollkasten nicht geschlossen"
assert s.count(".gm-split{") == 2, "Modal-Klasse nicht sauber definiert"
assert "grid-template-columns:260px minmax(0,1fr);gap:18px;align-items:start\">" not in s, \
    "Inline-Stil im Modal noch da"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
