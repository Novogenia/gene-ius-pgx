# -*- coding: utf-8 -*-
"""
Die drei Risikoklassen aus dem Agentenlauf sichern und gegen unsere Wirkstoffliste
abgleichen. Das ist der wertvolle Teil des Laufs: Klassen, die MED-RT gar nicht kennt,
alle aus kommerziell nutzbaren Quellen.
"""
import json, re, unicodedata
from collections import Counter

def norm(s):
    s = unicodedata.normalize("NFKD", str(s).lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).strip()

TASK = (r"C:\Users\DANIEL~1\AppData\Local\Temp\claude"
        r"\C--Users-DanielWallerstorfer-Novogenia-GmbH-AI-RESOURCES---Dokumente-AI-CHAT-BOTS"
        r"\d13e6d57-00c4-4087-9670-60f2d9f79dcd\tasks\wr9p2ja4w.output")
d = json.load(open(TASK, encoding="utf-8"))
kl = d["result"]["risikoklassen"]

M = json.load(open("rxcui_map.json", encoding="utf-8"))
unsere = {}
for k, v in M.items():
    unsere[norm(v["name"])] = k
# deutsche/englische Varianten grob angleichen
def varianten(n):
    n = norm(n)
    yield n
    yield re.sub(r"\s*\(.*?\)", "", n).strip()
    for a, b in [("ä","ae"),("ö","oe"),("ü","ue"),("ß","ss")]:
        n = n.replace(a, b)
    yield n
    # deutsche Endungen -> englische
    for de, en in [("in$","ine"),("on$","one"),("ol$","ol"),("id$","ide"),
                   ("at$","ate"),("saeure$","ic acid"),("um$","um")]:
        yield re.sub(de, en, n)

KURZ = {0: "qt", 1: "anticholinerg", 2: "hepatotox"}
LABEL = {"qt": "QT-Zeit-Verlaengerung",
         "anticholinerg": "Anticholinerge Last",
         "hepatotox": "Lebertoxizitaet"}

aus = {}
for i, k in enumerate(kl):
    key = KURZ.get(i, "k%d" % i)
    eintraege, treffer = [], 0
    for w in k["wirkstoffe"]:
        gefunden = None
        for v in varianten(w["name"]):
            if v in unsere:
                gefunden = unsere[v]; break
        if gefunden:
            treffer += 1
        eintraege.append({"name": w["name"], "stufe": w.get("stufe", ""),
                          "key": gefunden, "beleg": w.get("beleg", "")})
    aus[key] = {"label": LABEL[key], "quelle": k.get("quelle", ""),
                "lizenz": k.get("lizenz", ""), "wirkstoffe": eintraege}
    print("%-16s %3d Eintraege, davon %3d in unserer Liste zugeordnet (%.0f %%)"
          % (LABEL[key], len(eintraege), treffer, 100 * treffer / max(1, len(eintraege))))

json.dump(aus, open("risikoklassen.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\ngeschrieben: risikoklassen.json")

# Wie viele zusaetzliche Wechselwirkungspaare ergeben sich daraus?
print("\nZusaetzliche Paare aus diesen Klassen (nur unsere Wirkstoffe):")
ges = 0
for key, v in aus.items():
    n = sum(1 for w in v["wirkstoffe"] if w["key"])
    p = n * (n - 1) // 2
    ges += p
    print("  %-24s %3d Wirkstoffe -> %5d Paare" % (v["label"], n, p))
print("  Summe: %d" % ges)

# Lizenzlage festhalten
print("\nLizenzen (aus dem Agentenlauf, jeweils belegt):")
for key, v in aus.items():
    print("  %-24s %s" % (v["label"], v["lizenz"][:110].replace("\n", " ")))
