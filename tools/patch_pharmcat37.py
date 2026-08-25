# -*- coding: utf-8 -*-
"""
Die App heisst jetzt NOVO Drug Response.

Vorgabe Daniel, 2026-08-25: "NOVO Drug Response sollte diese app heissen."

WARUM NICHT MEDICHECK ODER MEDMATCH: beide waren im Gespraech, beide sind
besetzt. CGM (CompuGroup Medical) fuehrt "MediCheck" als Medikationsanalyse
fuer Apotheken im deutschsprachigen Raum - gleiche Kategorie, gleicher Markt,
gleiche Sprache. "MedMatch" nutzt Hims & Hers seit 2023 fuer KI-gestuetzte
Medikamentenzuordnung, dazu drei weitere Firmen im Gesundheitsbereich.
"NOVO Drug Response" ist beschreibend; die Unterscheidungskraft kommt aus
NOVO und stellt die App zu NOVO ACADEMY, NOVO REPORTER, NOVO DAILY.

WARUM DER NAME GENE-IUS WEG MUSS: "GENE-ius" ist bei Novogenia bereits das
Komponenten-Designsystem der Reports. Doppelbelegung.

NICHT ANGEFASST - das sind keine Namensnennungen:
  ClinPGx        externe Allel-Datenbank, Eigenname
  hasPGx()       interner Funktionsname, "PGx" = Pharmakogenetik allgemein

Das Logo traegt jetzt N statt G. In der Seitenleiste steht der Zusatz unter
dem Namen und wird per CSS in Grossbuchstaben gesetzt - aus "Drug Response"
wird dort DRUG RESPONSE. Der Zusatz ist deutlich laenger als das bisherige
"PGx", deshalb bekommt .brand small eine engere Laufweite und darf umbrechen;
die Leiste ist 16px innen gepolstert und sonst waere es knapp.
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

# ------------------------------------------------------------- Dokumentkopf
sub("<title>GENE-IUS PGx</title>",
    "<title>NOVO Drug Response</title>",
    "Titel der Seite")

sub('<meta name="apple-mobile-web-app-title" content="GENE-IUS PGx">',
    '<meta name="apple-mobile-web-app-title" content="NOVO Drug Response">',
    "Name auf dem Startbildschirm (iOS)")

sub('<meta name="description" content="Pharmakogenetik-Clickdummy - Prototyp zur Abstimmung, kein Medizinprodukt.">',
    '<meta name="description" content="NOVO Drug Response - Pharmakogenetik-Clickdummy. Prototyp zur Abstimmung, kein Medizinprodukt.">',
    "Beschreibung")

# --------------------------------------------------------------- Markenzeile
sub("""<div class="brand"><div class="logo">G</div><div>GENE-IUS<small>PGx</small></div></div>""",
    """<div class="brand"><div class="logo">N</div><div>NOVO<small>Drug Response</small></div></div>""",
    "Marke in der Seitenleiste", wo="script")

# Der Zusatz ist von 3 auf 13 Zeichen gewachsen. Bisher stand er garantiert in
# einer Zeile; jetzt braucht er Umbrucherlaubnis und etwas engere Laufweite.
sub("""  .brand small{display:block;font-weight:600;font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:#d8b6cd;margin-top:2px}""",
    """  .brand small{display:block;font-weight:600;font-size:10.5px;letter-spacing:.055em;text-transform:uppercase;color:#d8b6cd;margin-top:2px;line-height:1.25}""",
    "Zusatz vertraegt den laengeren Text", wo="style")

# ------------------------------------------------------------ Sichtbare Texte
sub("""<p>Trage ein, was du t&auml;glich einnimmst. Erst dann kann GENE-IUS pr&uuml;fen, ob deine Medikamente""",
    """<p>Trage ein, was du t&auml;glich einnimmst. Erst dann kann NOVO Drug Response pr&uuml;fen, ob deine Medikamente""",
    "Leerer Zustand der Medikamentenliste", wo="script")

sub("""<div class="ex">Deshalb pr&uuml;ft GENE-IUS beides: dein Genprofil <b>und</b> die Kombination deiner Medikamente.</div>""",
    """<div class="ex">Deshalb pr&uuml;ft NOVO Drug Response beides: dein Genprofil <b>und</b> die Kombination deiner Medikamente.</div>""",
    "Erklaertext zu Wechselwirkungen", wo="script")

sub("""&middot; GENE-IUS PGx</div>'""",
    """&middot; NOVO Drug Response</div>'""",
    "Fusszeile", wo="script")

# ------------------------------------------------- Kopfzeilen der Datenbloecke
for alt, was in [
    ("GENE-IUS PGx - Genprofil aus dem PharmCAT-3.2.0-Lauf", "Datenblock Genprofil"),
    ("GENE-IUS PGx - Einzelpositionen mit Studienhinweis", "Datenblock rs-Befunde"),
    ("GENE-IUS PGx - DEMO-GENOTYPEN, KEINE MESSWERTE", "Datenblock Genotypen"),
    ("GENE-IUS PGx - Wirkstoffdaten aus den Novogenia-Quelldateien", "Datenblock Wirkstoffe"),
]:
    sub(alt, alt.replace("GENE-IUS PGx", "NOVO Drug Response"), was, wo="script")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
assert "GENE-IUS" not in s and "GENEIUS" not in s, "der alte Name steht noch irgendwo"
# ClinPGx ist eine fremde Datenbank, hasPGx ein Funktionsname - beide bleiben.
uebrig = s.count("PGx") - s.count("ClinPGx") - s.count("hasPGx")
assert uebrig == 0, "unerwartete PGx-Vorkommen uebrig: %d" % uebrig
# Zehnmal am Stueck: Titel, iOS-Name, Beschreibung, leerer Zustand,
# Erklaertext, Fusszeile und vier Datenblock-Kopfzeilen. Die Markenzeile zaehlt
# NICHT mit - dort steht Auszeichnung zwischen "NOVO" und "Drug Response".
assert s.count("NOVO Drug Response") == 10, \
    "neuer Name nicht zehnmal gesetzt, sondern %d" % s.count("NOVO Drug Response")
assert '<div class="logo">N</div>' in s, "Logo traegt nicht N"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
