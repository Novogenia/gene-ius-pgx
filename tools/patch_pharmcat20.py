# -*- coding: utf-8 -*-
"""
Drei Aenderungen an der Darstellung.

1. WIRKSTOFFNAMEN BRECHEN UM STATT ABZUSCHNEIDEN

   Vorgabe Daniel, 2026-08-07: "mach zeilenumbruch in medikamentkarten".
   Auf dem Screenshot standen "(2-BENZHYDRYLOX...", "[32P]NATRIUMPHO...",
   "4-DIMETHYLAMINO..." - abgeschnitten mit Auslassungszeichen.

   .cname hatte white-space:nowrap plus text-overflow:ellipsis. Beides raus,
   dafuer ein Umbruch mit Zeilenbegrenzung: bis zu drei Zeilen, danach
   erst Auslassungszeichen. Lange chemische Namen ohne Leerzeichen brechen
   ueber overflow-wrap:anywhere - sonst schiebt ein einziger 60 Zeichen
   langer Name die Karte auf.

   Die Karte darf dabei nicht mehr fix hoch sein, sonst ueberlappt der
   Name den Statusblock. .chead wechselt von align-items:center auf
   flex-start, damit Pille und Statusblock oben buendig stehen.

2. DAS INTERAKTIONS-SVG LIEGT HINTER DEN KNOEPFEN

   Vorgabe: "setze die grafische Darstellung von Interaktionen hinter die
   Buttons". Bisher #wsvg z-index 6 gegen .wsactions z-index 4 - die rote
   Verbindungslinie lief ueber Tausch- und Loeschknopf.

   Jetzt z-index 2: weiterhin ueber den Karten (.wrow z-index 1), aber
   unter den Knoepfen. Fallstrick 4 bleibt gewahrt - das SVG behaelt
   pointer-events:none, und der Interaktionsknopf sitzt rechts ausserhalb
   des Knopfstreifens, wird also von nichts verdeckt.

3. DER AUSTAUSCH WIRD ALS EIN VORGANG LESBAR

   Vorgabe: "mache das Ersetzen eines Medikaments durch ein anderes,
   grafisch deutlicher und klarer, um zu verbessern, dass man versteht, was
   da passiert ist."

   Bisher: zwei lose Karten mit einer kleinen Zeile "ERSETZT DURCH"
   dazwischen. Man sah zwei Medikamente, nicht einen Vorgang.

   Jetzt eine zusammenhaengende Gruppe:
     - ein Rahmen um beide Karten mit Kopfzeile "Ausgetauscht"
     - die abgesetzte Karte bekommt die Marke "abgesetzt" und bleibt
       ausgegraut
     - dazwischen ein durchgezogener Pfeil statt einer Textzeile
     - die neue Karte bekommt die Marke "neu"
   Damit ist auf einen Blick zu sehen, was ersetzt wurde und wodurch.
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

# ================================================= 1. Namen brechen um
sub("""  .cname{font-size:15.5px;font-weight:800;letter-spacing:-.004em;line-height:1.15;color:#221c26;text-transform:uppercase;
    white-space:nowrap;overflow:hidden;text-overflow:ellipsis}""",
    """  /* Umbruch statt Abschneiden. overflow-wrap:anywhere ist noetig, weil
     chemische Namen wie (2-benzhydryloxyethyl)diethyl-methylammonium keine
     Leerzeichen haben und die Karte sonst aufschieben. Nach vier Zeilen
     doch abschneiden, sonst wird eine Karte beliebig hoch - der
     vollstaendige Name steht ohnehin im title-Attribut. Vier statt drei,
     weil bei drei genau ein Name der Datenbank noch geklemmt hat. */
  .cname{font-size:15.5px;font-weight:800;letter-spacing:-.004em;line-height:1.18;color:#221c26;text-transform:uppercase;
    overflow-wrap:anywhere;display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden}""",
    "Wirkstoffname bricht um", wo="style")

# Bei mehrzeiligem Namen muessen Pille und Statusblock oben stehen
sub("""  .chead{position:relative;display:flex;align-items:center;gap:10px;padding:13px 30px 13px 13px;cursor:pointer;min-width:0}""",
    """  /* flex-start statt center: sonst rutscht der Statusblock bei einem
     dreizeiligen Namen in die Mitte und wirkt wie verrutscht. */
  .chead{position:relative;display:flex;align-items:flex-start;gap:10px;padding:13px 30px 13px 13px;cursor:pointer;min-width:0}
  .chead .pill,.chead .cstate,.chead .cchev{margin-top:1px}""",
    "Kartenkopf oben buendig", wo="style")

# ================================== 2. Interaktions-SVG hinter die Knoepfe
sub("""  #wsvg{position:absolute;inset:0;pointer-events:none;z-index:6}""",
    """  /* z-index 2: ueber den Karten (.wrow liegt auf 1), aber unter dem
     Knopfstreifen (.wsactions liegt auf 4). Vorgabe Daniel, 2026-08-07 -
     die Verbindungslinie lief vorher ueber Tausch- und Loeschknopf.
     pointer-events:none bleibt zwingend (Fallstrick 4); der
     Interaktionsknopf sitzt rechts neben dem Streifen und bleibt frei. */
  #wsvg{position:absolute;inset:0;pointer-events:none;z-index:2}""",
    "Interaktions-SVG hinter die Knoepfe", wo="style")

# ============================================ 3. Austausch als ein Vorgang
sub("""  .replrow{display:flex;align-items:center;justify-content:center;gap:7px;margin:-2px 0 8px;color:var(--plum);
    font-size:11.5px;font-weight:800;letter-spacing:.06em;text-transform:uppercase}""",
    """  /* Der Austausch war zwei lose Karten mit einer Textzeile dazwischen -
     man sah zwei Medikamente, nicht einen Vorgang. Jetzt eine Gruppe mit
     Rahmen, Kopfzeile und durchgezogenem Pfeil. */
  .swapbox{border:1.5px solid var(--plum-ln,#D9C3D4);border-radius:16px;background:var(--plum-050);
    padding:10px 11px 11px;position:relative}
  .swaphead{display:flex;align-items:center;gap:7px;font-size:11px;font-weight:800;letter-spacing:.09em;
    text-transform:uppercase;color:var(--plum);margin:0 0 9px 2px}
  .swaphead svg{width:15px;height:15px}
  .swapitem{position:relative}
  .swaplabel{font-size:11px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;
    color:var(--muted);margin:0 0 4px 3px}
  .swapitem.alt .swaplabel{color:var(--faint);text-decoration:line-through}
  .swapitem.neu .swaplabel{color:var(--plum)}
  /* Durchgezogener Pfeil statt Textzeile */
  .swaparrow{display:flex;flex-direction:column;align-items:center;margin:5px 0 7px}
  .swaparrow .ln{width:2.5px;height:13px;background:var(--plum);opacity:.5}
  .swaparrow .hd{width:26px;height:26px;border-radius:50%;background:var(--plum);color:#fff;
    display:grid;place-items:center}
  .swaparrow .hd svg{width:15px;height:15px;transform:rotate(90deg)}
  .replrow{display:flex;align-items:center;justify-content:center;gap:7px;margin:-2px 0 8px;color:var(--plum);
    font-size:11.5px;font-weight:800;letter-spacing:.06em;text-transform:uppercase}""",
    "CSS fuer die Austauschgruppe", wo="style")

sub("""    return `<div class="wrow" data-row="${id}">
      ${cardHtml(id,'ws',{sevPool:workspace,faded:true})}
      <div class="replrow">${ico('arr','',16)} ersetzt durch</div>
      ${aid?cardHtml(aid,'wsalt',{sevPool:workspace}):''}
      ${wsActions(id,sev,true)}
    </div>`;""",
    """    /* Der Austausch als EIN Vorgang: Rahmen um beide Karten, die abgesetzte
       durchgestrichen beschriftet, dazwischen ein durchgezogener Pfeil. */
    return `<div class="wrow" data-row="${id}">
      <div class="swapbox">
        <div class="swaphead">${ico('swap','',15)} Ausgetauscht</div>
        <div class="swapitem alt">
          <div class="swaplabel">bisher</div>
          ${cardHtml(id,'ws',{sevPool:workspace,faded:true})}
        </div>
        <div class="swaparrow"><div class="ln"></div>
          <div class="hd">${ico('arr','',15)}</div><div class="ln"></div></div>
        <div class="swapitem neu">
          <div class="swaplabel">neu</div>
          ${aid?cardHtml(aid,'wsalt',{sevPool:workspace}):''}
        </div>
      </div>
      ${wsActions(id,sev,true)}
    </div>`;""",
    "Austausch als Gruppe rendern", wo="script")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
assert "white-space:nowrap;overflow:hidden;text-overflow:ellipsis}" not in s.split(".cbrands")[0], \
    "Abschneiden steht noch am Wirkstoffnamen"
assert "#wsvg{position:absolute;inset:0;pointer-events:none;z-index:2}" in s, "SVG-Ebene nicht gesetzt"
assert "pointer-events:none" in s[s.index("#wsvg{"):s.index("#wsvg{") + 90], \
    "pointer-events:none fehlt am SVG (Fallstrick 4)"
assert s.count("class=\"swapbox\"") == 1, "Austauschgruppe nicht genau einmal"
assert s.count("swaparrow") >= 2, "Pfeil der Austauschgruppe fehlt"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
