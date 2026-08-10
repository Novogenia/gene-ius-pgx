# -*- coding: utf-8 -*-
"""
"Medikament hinzufuegen" sichtbar machen: Pluszeichen, prominenter Knopf,
angehefteter Plus-Knopf.

Vorgabe Daniel, 2026-08-08: "die Handyansicht von Deinen Medikamenten sieht
nun viel besser aus. Es sollte nur 'Medikament hinzufuegen' mit einem
Pluszeichen und einem prominenten Button oben sein. Das ist irgendwie noch
nicht sehr sichtbar. Eventuell sogar rechts angeheftet ein Plus-Button mit
'Medikament hinzufuegen', wo ich draufklicke, der dann das Pop-Up oeffnet."

DREI AENDERUNGEN:

  1. Lupe raus, Plus rein. Das Symbol c-search sagte "suchen", der Knopf tut
     aber "hinzufuegen". Das Pluszeichen gibt es bereits als Symbol.
  2. Der Knopf oben wird am Telefon volle Breite und 50px hoch statt eines
     schmalen Knopfes neben der Ueberschrift.
  3. Dazu ein angehefteter Plus-Knopf unten rechts, oberhalb der Tableiste.
     Er bleibt beim Scrollen stehen - bei vier oder mehr Medikamenten ist
     der Knopf oben sonst laengst aus dem Bild, und genau dann will man
     etwas hinzufuegen.

Beide oeffnen dasselbe Popup. Der angeheftete Knopf erscheint nur am
Telefon und nur unter "Deine Medikamente"; am Desktop steht der Knopf oben
neben der Ueberschrift und ist dort immer sichtbar.

ABSTAND NACH UNTEN: die Tableiste ist rund 68px hoch plus sicherer Bereich.
Der Knopf sitzt darueber, und die Seite bekommt unten entsprechend mehr
Polster, damit die letzte Karte nicht darunter verschwindet.
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

# ---------------------------------------- 1+3. Plus im Knopf, angehefteter Knopf
sub("""      <button class="btn btn-plum addbtn" onclick="openAdd()">
        ${ico('c-search','',16)} Medikament hinzuf&uuml;gen</button>
    </div>
    <div id="wsrows"></div>
  </div>`;""",
    """      <button class="btn btn-plum addbtn" onclick="openAdd()">
        ${ico('plus','',17)} Medikament hinzuf&uuml;gen</button>
    </div>
    <div id="wsrows"></div>
  </div>
  <button class="fab" onclick="openAdd()" aria-label="Medikament hinzuf&uuml;gen">
    ${ico('plus','',20)}<span>Medikament hinzuf&uuml;gen</span></button>`;""",
    "Plus im Knopf und angehefteter Knopf", wo="script")

sub("""      <button class="btn btn-plum" style="margin-top:14px"
        onclick="openAdd()">${ico('c-search','',16)} Medikament hinzuf&uuml;gen</button>""",
    """      <button class="btn btn-plum" style="margin-top:14px"
        onclick="openAdd()">${ico('plus','',17)} Medikament hinzuf&uuml;gen</button>""",
    "Plus auch im leeren Zustand", wo="script")

# ------------------------------------------------------------------- CSS
sub("""  .addbtn{flex:none;white-space:nowrap}""",
    """  .addbtn{flex:none;white-space:nowrap}
  /* Angehefteter Knopf - nur am Telefon. Bei vier oder mehr Medikamenten ist
     der Knopf oben aus dem Bild gescrollt, und genau dann will man etwas
     hinzufuegen. */
  .fab{display:none}""",
    "CSS: Grundzustand des angehefteten Knopfs", wo="style")

sub("""    .tabbar{display:flex}""",
    """    .tabbar{display:flex}
    /* Der Knopf oben ueber die volle Breite statt schmal neben der
       Ueberschrift - er war so kaum als Handlungsaufforderung erkennbar. */
    .wshead2{display:block}
    /* .wshead2 .addbtn statt nur .addbtn: die Sammelregel fuer
       Beruehrflaechen setzt min-height:44px und steht weiter unten im
       Stylesheet - bei gleicher Spezifitaet gewinnt die spaetere. Mit zwei
       Klassen ist die Reihenfolge egal. */
    .wshead2 .addbtn{display:flex;width:100%;min-height:52px;justify-content:center;
      margin-top:14px;font-size:15px}
    .fab{display:flex;align-items:center;gap:9px;position:fixed;right:14px;
      bottom:calc(80px + env(safe-area-inset-bottom,0px));z-index:55;
      min-height:52px;padding:0 20px;border:0;border-radius:999px;cursor:pointer;
      background:var(--plum);color:#fff;font:inherit;font-size:14.5px;font-weight:800;
      box-shadow:0 10px 26px -8px rgba(94,0,71,.7);-webkit-tap-highlight-color:transparent}
    .fab svg{flex:none;width:20px;height:20px}
    .fab:active{transform:scale(.97)}""",
    "CSS: prominenter und angehefteter Knopf", wo="style")

# Platz nach unten, damit die letzte Karte nicht unter dem Knopf verschwindet
sub("""    main#main{padding:16px 14px calc(84px + env(safe-area-inset-bottom,0px))}""",
    """    main#main{padding:16px 14px calc(146px + env(safe-area-inset-bottom,0px))}""",
    "Mehr Polster unten (820px)", wo="style")

sub("""    main#main{padding:14px 12px calc(84px + env(safe-area-inset-bottom,0px))}""",
    """    main#main{padding:14px 12px calc(146px + env(safe-area-inset-bottom,0px))}""",
    "Mehr Polster unten (430px)", wo="style")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
assert s.count('class="fab"') == 1, "angehefteter Knopf nicht genau einmal"
assert s.count(".fab{display:none}") == 1, "Grundzustand fehlt"
assert "ico('c-search','',16)} Medikament" not in s, "Lupe steht noch im Hinzufuegeknopf"
# drei neue Stellen plus die eine, die es schon gab (Startseite, "Zu deinen
# Medikamenten")
assert s.count("ico('plus'") == 4, "Pluszeichen nicht an allen Stellen"
assert "calc(84px + env" not in s, "altes Polster steht noch"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
