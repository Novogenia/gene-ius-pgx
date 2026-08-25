# -*- coding: utf-8 -*-
"""
Die App startet auf "Deine Medikamente" statt auf der Startseite.

Vorgabe Daniel, 2026-08-25: "die Startseite sollte aber deine Medikamente
sein, wenn man die Seite oeffnet."

Eine Zeile - aber render() haengt zwei Nachlaeufe an die Ansicht "meine":
renderList() und renderWorkspace(), und beim naechsten Verkleinern des
Fensters zeichnet ein resize-Horcher die Verbindungslinien neu. Beides steht
bereits am Ende von render() und laeuft damit auch beim ersten Zeichnen -
nachgeprueft, nicht angenommen. Die Reiterleiste liest `view` ebenfalls von
dort, der richtige Reiter ist also von Anfang an hervorgehoben.

Die Startseite bleibt als Reiter erhalten, sie ist nur nicht mehr die erste
Ansicht.
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

sub("""let view="dashboard", detailId=null;""",
    """/* Beim Oeffnen zuerst die eigene Einnahmeliste, nicht die Startseite
   (Vorgabe Daniel, 2026-08-25). render() haengt fuer "meine" renderList()
   und renderWorkspace() an - beides laeuft damit schon beim ersten
   Zeichnen. */
let view="meine", detailId=null;""",
    "Startansicht ist die eigene Medikamentenliste", wo="script")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
assert s.count('let view="meine"') == 1, "Startansicht nicht gesetzt"
assert 'let view="dashboard"' not in s, "alte Startansicht steht noch"
# Die Startseite muss als Reiter erhalten bleiben.
assert '{id:"dashboard"' in s, "Reiter Start ist verschwunden"
assert "view==='dashboard')m.innerHTML=vDashboard()" in s, "Startseite nicht mehr erreichbar"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
