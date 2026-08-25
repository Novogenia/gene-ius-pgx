# -*- coding: utf-8 -*-
"""
Nachtrag zu v88: auch "Grundlage" ist ein Fachfeld.

Beim Nachmessen an einer offenen Karte kamen andere Felder heraus als beim
Lesen der ersten Zweige von metrics(): Clopidogrel zeigte

    Wirkung = Normal | Handlung = Keine Anpassung
    Grundlage = CYP2C19 Normal | Interaktion = Kritisch

metrics() hat zwei Pfade. Der PharmCAT-Pfad baut [Wirkung, Abbau/Aktivierung,
Toxizitaet] zusammen, wirft alles Unbestimmte weg und haengt dann "Handlung"
und "Grundlage" an. Der Ersatzpfad liefert Wirkung/Abbau/Toxizitaet/Dosierung.
Insgesamt gibt es also acht Feldnamen, nicht vier.

"Grundlage" nennt den Genotyp, auf den sich die Empfehlung stuetzt - bei
Clopidogrel "CYP2C19 Normal". Das ist die Herleitung, nicht die Folge, und
gehoert damit zur selben Gruppe wie Abbau und Aktivierung.

Bleiben in der einfachen Ansicht: Wirkung, Handlung, Dosierung, Interaktion,
Risiko. Alle fuenf sagen, was ist oder was zu tun ist.
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

sub("""    /* "Abbau" und "Aktivierung" erklaeren die Mechanik - warum etwas
       passiert, nicht was zu tun ist. Das ist der einzige Wert, der in der
       einfachen Ansicht faellt. */
    const mechanik=(m.l==='Abbau'||m.l==='Aktivierung');""",
    """    /* Herleitung statt Folge: "Abbau" und "Aktivierung" erklaeren, WARUM
       etwas passiert, "Grundlage" nennt den Genotyp, auf den sich die
       Empfehlung stuetzt ("CYP2C19 Normal"). Das sind die Felder, die in der
       einfachen Ansicht fallen. Was bleibt - Wirkung, Handlung, Dosierung,
       Interaktion, Risiko - sagt, was ist oder was zu tun ist. */
    const mechanik=(m.l==='Abbau'||m.l==='Aktivierung'||m.l==='Grundlage');""",
    "Grundlage ist ein Fachfeld", wo="script")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
assert s.count("m.l==='Grundlage'") == 1, "Grundlage nicht einsortiert"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
