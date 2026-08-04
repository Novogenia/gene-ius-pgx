# -*- coding: utf-8 -*-
"""
Sind die 508 Naeherungstreffer richtig? Gegenprobe: den Namen holen, den RxNorm
zu dieser RXCUI fuehrt, und mit unserem Wirkstoffnamen vergleichen.

Falsche Zuordnungen waeren hier gefaehrlich - sie wuerden einem Wirkstoff die
Indikationen und Wechselwirkungen eines anderen zuschreiben.
"""
import json, re, time, unicodedata, urllib.request, urllib.error
UA = {"User-Agent": "Novogenia-PGx-Pipeline/1.0"}
M = json.load(open("rxcui_map.json", encoding="utf-8"))

def entkleide(s):
    """Vergleichsform: klein, ohne Akzente, ohne Salze und Trennzeichen."""
    s = unicodedata.normalize("NFKD", str(s).lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"\b(hydrochloride|hcl|sodium|potassium|calcium|sulfate|sulphate|"
               r"maleate|tartrate|citrate|mesylate|besylate|fumarate|succinate|"
               r"acetate|phosphate|nitrate|bromide|chloride|dihydrate|monohydrate|"
               r"anhydrous|salt|base)\b", " ", s)
    return re.sub(r"[^a-z0-9]", "", s)

def name_zu(rxcui):
    try:
        req = urllib.request.Request(
            "https://rxnav.nlm.nih.gov/REST/rxcui/%s/property.json?propName=RxNorm%%20Name" % rxcui,
            headers=UA)
        with urllib.request.urlopen(req, timeout=25) as r:
            d = json.load(r)
        p = d.get("propConceptGroup", {}).get("propConcept", [])
        return p[0]["propValue"] if p else None
    except Exception:
        return None

kand = [(k, v) for k, v in M.items() if v["quelle"] == "naeherung"]
print("Naeherungstreffer gesamt: %d" % len(kand))

gut, schlecht, unklar = [], [], []
for i, (k, v) in enumerate(kand):
    rn = name_zu(v["rxcui"])
    v["rxnorm_name"] = rn
    if not rn:
        unklar.append((v["name"], v["rxcui"], None)); continue
    a, b = entkleide(v["name"]), entkleide(rn)
    if a == b or a in b or b in a:
        v["geprueft"] = "ok"; gut.append((v["name"], rn))
    else:
        v["geprueft"] = "abweichend"; schlecht.append((v["name"], rn, v["rxcui"], v["score"]))
    time.sleep(0.05)
    if (i + 1) % 100 == 0:
        print("  %d/%d geprueft" % (i + 1, len(kand)))

print("\nNamensgleich (nach Entfernen von Salzen/Akzenten): %d" % len(gut))
print("Abweichend:                                        %d" % len(schlecht))
print("Nicht pruefbar:                                    %d" % len(unklar))

print("\n=== Abweichende Zuordnungen - die sind zu verwerfen ===")
for n, rn, rx, sc in schlecht[:30]:
    print("   %-32s -> RXCUI %-9s '%s' (Score %.1f)" % (n[:32], rx, (rn or "")[:34], sc))

# Abweichende verwerfen: lieber kein Treffer als ein falscher
verworfen = 0
for k, v in M.items():
    if v.get("geprueft") == "abweichend":
        v["rxcui_verdacht"] = v["rxcui"]
        v["rxcui"] = None
        v["quelle"] = "verworfen"
        verworfen += 1
json.dump(M, open("rxcui_map.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)

mit = sum(1 for v in M.values() if v["rxcui"])
print("\n%d Zuordnungen verworfen." % verworfen)
print("Belastbare RXCUI-Zuordnungen: %d von %d = %.0f %%" % (mit, len(M), 100 * mit / len(M)))
