# -*- coding: utf-8 -*-
"""
Baut den JS-Datenblock fuer GENE-IUS PGx aus Hristos PharmCAT-3.2.0-Lauf
(Ordner "PharmCAT Validation 20260730", 40 Proben, Reporter-Stufe vorhanden).

Quellen je Probe:
  <Probe>.report.json     Gene + Wirkstoff-Empfehlungen (CPIC, DPWG, FDA)
  <Probe>.match.json      gerufene und fehlende Positionen je Gen
Dazu unveraendert:
  Pharmgkb drug recommendations V4.xlsx   Novogenias eigene Leitlinien-Matrix

Ampelregel - kommt aus PharmCATs eigenen Flags, nicht aus einer Textdeutung:
  alternateDrugAvailable -> ALARM    (ein anderer Wirkstoff ist angezeigt)
  dosingInformation      -> ACHTUNG  (Dosis muss angepasst werden)
  otherPrescribingGuidance -> ACHTUNG (Ueberwachung noetig)
  sonst                  -> OK       (kein Handlungsbedarf)

Regel: nichts erfinden. Was PharmCAT nicht ruft, bleibt "nicht bestimmbar".

Ausgabe: pharmcat_profil.js (rein ASCII)
"""
import html, json, os, re, sys
from collections import Counter, defaultdict
from openpyxl import load_workbook

PROBE = sys.argv[1] if len(sys.argv) > 1 else "NA17454"
BASIS = os.path.join("pharmcat40", "outputs", PROBE)
XL = (r"C:\Users\DanielWallerstorfer\Novogenia GmbH\AI RESOURCES - Dokumente"
      r"\PHARMACOGENETICS\Pharmgkb drug recommendations V4.xlsx")
OUT = "pharmcat_profil.js"

# ---------------------------------------------------------------- Hilfsmittel
def esc(s):
    """ASCII-sicher. PharmCAT liefert HTML-Entities und teils <ul>-Listen."""
    if s is None: return ""
    s = html.unescape(str(s))
    s = re.sub(r"<li>", " \u2022 ", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    rep = {"\u00e4":"&auml;","\u00f6":"&ouml;","\u00fc":"&uuml;","\u00c4":"&Auml;",
           "\u00d6":"&Ouml;","\u00dc":"&Uuml;","\u00df":"&szlig;","\u2022":"&middot;",
           "\u2013":"&mdash;","\u2014":"&mdash;","\u2019":"'","\u2018":"'",
           "\u201c":'"',"\u201d":'"',"\u201e":'"',"\u2265":"&ge;","\u2264":"&le;",
           "\u2192":"&rarr;","\u00d7":"x","\u00b7":"&middot;","\u00e9":"&eacute;",
           "\u00e8":"&egrave;","\u00b0":"&deg;","\u00a0":" ","\u2011":"-",
           "\u00b5":"&micro;","\u03b1":"alpha","\u03b2":"beta"}
    for a, b in rep.items(): s = s.replace(a, b)
    s = s.replace("\\", "").replace("`", "'").replace("${", "$ {")
    return "".join(c if ord(c) < 128 else "" for c in s)

def j(o): return json.dumps(o, separators=(",", ":"), ensure_ascii=True)

# Phaenotyp -> Kanon
CANON = {
 "ultrarapid metabolizer":"UM","rapid metabolizer":"RM","normal metabolizer":"NM",
 "likely intermediate metabolizer":"IM","intermediate metabolizer":"IM",
 "likely poor metabolizer":"PM","poor metabolizer":"PM",
 "increased function":"IF","normal function":"NF","possible decreased function":"DF",
 "decreased function":"DF","poor function":"PF","normal":"NM","deficient":"PM",
 "indeterminate":"?","no result":"?","n/a":"?","":"?",
}
SHEET = {"ULTRARAPID":"UM","RAPID":"RM","EXTENSIVE":"NM","NORMAL":"NM",
         "INTERMEDIATE":"IM","POOR":"PM"}
LVLOF = {"PM":0,"PF":0,"IM":1,"DF":1,"NM":2,"NF":2,"RM":3,"UM":3,"IF":3}
DE_ENZ = {"UM":"Ultraschneller Metabolisierer","RM":"Schneller Metabolisierer",
          "NM":"Normaler Metabolisierer","IM":"Intermedi\u00e4rer Metabolisierer",
          "PM":"Langsamer Metabolisierer"}
DE_TRANS = {"IF":"Gesteigerte Transportfunktion","NF":"Normale Transportfunktion",
            "DF":"Verminderte Transportfunktion","PF":"Stark verminderte Transportfunktion"}
DE_SPEZIAL = {"G6PD":{"NM":"Kein G6PD-Mangel","PM":"G6PD-Mangel","IM":"G6PD-Mangel (teilweise)"}}
KIND = {
 "CYP2B6":"enz","CYP2C19":"enz","CYP2C9":"enz","CYP2D6":"enz","CYP3A4":"enz",
 "CYP3A5":"enz","DPYD":"enz","NAT2":"enz","NUDT15":"enz","TPMT":"enz","UGT1A1":"enz",
 "CYP4F2":"enz","G6PD":"enz","SLCO1B1":"trans","ABCG2":"trans",
 "VKORC1":"ziel","CFTR":"ziel","RYR1":"risiko","CACNA1S":"risiko","MT-RNR1":"risiko",
 "HLA-A":"hla","HLA-B":"hla","IFNL3":"marker",
}
ROLLE = {
 "CYP2B6":"Abbau von Efavirenz und weiteren HIV-Wirkstoffen",
 "CYP2C19":"Abbau von Clopidogrel, Protonenpumpenhemmern und Antidepressiva",
 "CYP2C9":"Abbau von Gerinnungshemmern, Phenytoin und Schmerzmitteln",
 "CYP2D6":"Abbau von etwa jedem vierten Wirkstoff \u2013 Opioide, Antidepressiva, Betablocker",
 "CYP3A4":"Abbau sehr vieler Wirkstoffe, gemeinsam mit CYP3A5",
 "CYP3A5":"Abbau von Tacrolimus nach Organtransplantation",
 "CYP4F2":"Vitamin-K-Umsatz, beeinflusst die Warfarin-Dosis",
 "DPYD":"Abbau der Krebsmedikamente Fluorouracil und Capecitabin",
 "G6PD":"Schutz der roten Blutk\u00f6rperchen vor oxidativem Stress",
 "NAT2":"Abbau von Isoniazid, Hydralazin und weiteren Wirkstoffen",
 "NUDT15":"Abbau von Thiopurinen wie Azathioprin",
 "TPMT":"Abbau von Thiopurinen wie Azathioprin und Mercaptopurin",
 "UGT1A1":"Ausscheidung von Irinotecan und Atazanavir",
 "SLCO1B1":"Aufnahme von Statinen in die Leber",
 "ABCG2":"Transport von Rosuvastatin und Allopurinol",
 "VKORC1":"Angriffspunkt der Vitamin-K-Antagonisten Warfarin und Acenocoumarol",
 "CFTR":"Chloridkanal \u2013 Ansprechen auf Ivacaftor bei Mukoviszidose",
 "RYR1":"Risiko einer malignen Hyperthermie unter Narkose",
 "CACNA1S":"Risiko einer malignen Hyperthermie unter Narkose",
 "HLA-A":"Risiko schwerer Hautreaktionen auf Carbamazepin",
 "HLA-B":"Risiko schwerer \u00dcberempfindlichkeit auf Abacavir und Carbamazepin",
 "IFNL3":"Ansprechen auf Interferon-Therapie bei Hepatitis C",
 "MT-RNR1":"Risiko einer Schwerh\u00f6rigkeit unter Aminoglykosid-Antibiotika",
}
FN_DE = {"normal function":"normal","increased function":"gesteigert",
 "decreased function":"reduziert","no function":"keine",
 "possible decreased function":"m\u00f6glicherweise reduziert",
 "uncertain function":"unklar","unknown function":"unbekannt","normal":"normal",
 "deficient":"Mangel","reference":"normal","null":"unbekannt",
 "ivacaftor non-responsive":"spricht nicht an","ivacaftor responsive":"spricht an"}
def fn_de(s):
    if s is None: return "unbekannt"
    return FN_DE.get(str(s).strip().lower(), esc(s))
def canon(p): return CANON.get((p or "").strip().lower(), "?")

# ---------------------------------------------------------------- PharmCAT
rep = json.load(open(os.path.join(BASIS, PROBE + ".report.json"), encoding="utf-8"))
mat = json.load(open(os.path.join(BASIS, PROBE + ".match.json"), encoding="utf-8"))

md = {}
for r in mat.get("results", []):
    m = r.get("matchData") or {}
    md[r["gene"]] = dict(
        pos=len(r.get("variants") or []),
        fehlt=len((m.get("missingPositions") or [])),
        unc=[esc(x) for x in (r.get("uncallableHaplotypes") or [])][:40],
        var=[[esc(v.get("rsid") or v.get("position")), esc(v.get("vcfCall") or "")]
             for v in (r.get("variants") or []) if v.get("vcfCall")],
        alle=sorted({esc(a) for v in (r.get("variants") or [])
                     for a in (v.get("alleles") or []) if a},
                    key=lambda s: (0 if s.startswith("*") else 1,
                                   int(re.sub(r"\D", "", s) or 0) if s.startswith("*") else 0, s))[:80],
    )

genes = []
for g in sorted(rep.get("genes", {})):
    val = rep["genes"][g]
    for r in (val if isinstance(val, list) else [val]):
        sym = r.get("geneSymbol") or g
        dl = r.get("recommendationDiplotypes") or r.get("sourceDiplotypes") or []
        d = dl[0] if dl else {}
        phen = "/".join(d.get("phenotypes") or [])
        kein = (not phen) or phen.strip().lower() in ("no result", "n/a", "")
        code = canon(phen.split("/")[0]) if not kein else "?"
        a1 = (d.get("allele1") or {}).get("name") or ""
        f1 = fn_de((d.get("allele1") or {}).get("function"))
        a2 = (d.get("allele2") or {}).get("name") or ""
        f2 = fn_de((d.get("allele2") or {}).get("function"))
        dip = d.get("label") or ""
        if kein: a1 = a2 = f1 = f2 = ""; dip = ""
        kind = KIND.get(sym, "marker")
        lvl = LVLOF.get(code, -1)
        if kind == "trans": de = DE_TRANS.get(code, "")
        elif sym in DE_SPEZIAL: de = DE_SPEZIAL[sym].get(code, "")
        else: de = DE_ENZ.get(code, "")
        flach = 0
        if not de:
            SPEZ = {"uncertain susceptibility":"Keine Risikovariante gefunden",
                    "malignant hyperthermia susceptibility":"Erh\u00f6htes Risiko (maligne Hyperthermie)",
                    "ivacaftor non-responsive in cf patients":"Spricht nicht auf Ivacaftor an",
                    "ivacaftor responsive in cf patients":"Spricht auf Ivacaftor an",
                    "normal":"Normale Funktion"}
            de = SPEZ.get(phen.strip().lower(), "")
            # VKORC1 meldet den Genotyp direkt, z.B. "-1639 AA"
            if not de and not kein and sym == "VKORC1":
                de = {"AA":"Erh\u00f6hte Empfindlichkeit (A/A)",
                      "AG":"Leicht erh\u00f6hte Empfindlichkeit (A/G)",
                      "GG":"Normale Empfindlichkeit (G/G)"}.get(phen.split()[-1], esc(phen))
            if de and not kein and kind in ("risiko","ziel","hla","marker"):
                lvl = 2; flach = 1
        s = md.get(sym, {})
        genes.append(dict(
            g=sym, kind=kind, rolle=esc(ROLLE.get(sym, "")),
            dip=esc(dip), phen=esc(phen) if not kein else "", de=esc(de),
            code=code, lvl=lvl, flach=flach,
            score=str(d.get("activityScore") or "") if d.get("activityScore") not in (None,"","n/a") else "",
            a1=esc(a1), f1=esc(f1), a2=esc(a2), f2=esc(f2),
            ok=0 if kein else 1, mehr=1 if len(dl) > 1 else 0, kand=max(1, len(dl)),
            aussen=1 if r.get("outsideCall") else 0,
            pos=s.get("pos", 0), fehlt=s.get("fehlt", 0),
            alle=s.get("alle", []), unc=s.get("unc", []), var=s.get("var", []),
            alt=[esc(x.get("label")) for x in dl[1:13] if x.get("label")],
        ))

# ------------------------------------------------- Wirkstoff-Empfehlungen
QUELLE = ["CPIC_GUIDELINE", "DPWG_GUIDELINE", "FDA_LABEL", "FDA_ASSOC"]
QDE = ["CPIC-Leitlinie", "DPWG-Leitlinie", "FDA-Beipackzettel", "FDA-Assoziation"]
KLASSE = ["", "Strong", "Moderate", "Optional", "No recommendation", "Unspecified"]

roh = []
for q, grp in rep.get("drugs", {}).items():
    for n, d in grp.items():
        for gl in d.get("guidelines", []):
            for a in gl.get("annotations", []):
                rec = esc(a.get("drugRecommendation") or "")
                imp = esc(" | ".join(a.get("implications") or []))
                if not rec and not imp: continue
                alt = bool(a.get("alternateDrugAvailable"))
                dos = bool(a.get("dosingInformation"))
                oth = bool(a.get("otherPrescribingGuidance"))
                # Ampel aus PharmCATs eigenen Flags
                sev = "crit" if alt else ("warn" if (dos or oth) else "ok")
                ph = a.get("phenotypes") or {}
                roh.append(dict(
                    n=esc(n), q=d.get("source") or "", rec=rec, imp=imp, sev=sev,
                    kl=a.get("classification") or "",
                    gen=esc(", ".join("%s %s" % (k, v) for k, v in ph.items())),
                    url=esc(gl.get("url") or ""),
                    flags=(1 if alt else 0) | (2 if dos else 0) | (4 if oth else 0)))

texte = sorted({r["rec"] for r in roh if r["rec"]})
impl = sorted({r["imp"] for r in roh if r["imp"]})
ti = {t: i for i, t in enumerate(texte)}
ii = {t: i for i, t in enumerate(impl)}
SEV = ["ok", "warn", "crit"]
drugs = [[r["n"], QUELLE.index(r["q"]) if r["q"] in QUELLE else -1,
          ti.get(r["rec"], -1), ii.get(r["imp"], -1),
          KLASSE.index(r["kl"]) if r["kl"] in KLASSE else 0,
          SEV.index(r["sev"]), r["flags"], r["gen"]] for r in roh]

# ------------------------------------------------- Novogenia-Leitlinienmatrix
wb = load_workbook(XL, read_only=True, data_only=True)
ws = wb.worksheets[0]
it = ws.iter_rows(values_only=True)
h = list(next(it))
ci = {}
for i, n in enumerate(h):
    if isinstance(n, str) and n.strip() and n.strip() not in ci: ci[n.strip()] = i
recs = []
for row in it:
    if not row[0]: continue
    def v(k):
        i = ci.get(k)
        return str(row[i]).strip() if i is not None and i < len(row) and row[i] not in (None, "") else ""
    tail = " ".join(str(x) for x in row[15:] if x)
    farbe = "crit" if "BG_COLOR_DRUG_RED" in tail else ("warn" if "BG_COLOR_DRUG_YELLOW" in tail else "")
    cond = []
    g1, gt1, g2, gt2 = v("GENE(1)"), v("GENOTYPE (1)"), v("GENE (2)"), v("METABOLIZER (2)")
    if g1 and gt1: cond.append([g1, SHEET.get(gt1.upper(), ""), esc(gt1)])
    if g2 and gt2: cond.append([g2, SHEET.get(gt2.upper(), ""), esc(gt2)])
    gl = [l for l, c in (("CPIC","CPIC"),("DPWG","DPWG"),("CPNDS","CPNDS"),("FDA","OTHER")) if v(c)]
    recs.append(dict(drug=esc(str(row[0]).strip()), om=v("OM ID"), cond=cond,
                     txt=esc(v("RECOMMEDNATION")), gl=gl, dose=v("DOSE OVERRIDE"),
                     farbe=farbe, dosis=esc(gt1) if (not g1 and gt1) else ""))
wb.close()
mtxt = sorted({r["txt"] for r in recs if r["txt"]})
mti = {t: i for i, t in enumerate(mtxt)}
GL = ["CPIC", "DPWG", "CPNDS", "FDA"]
rectab = [[r["drug"], r["om"], r["cond"], mti.get(r["txt"], -1),
           sum(1 << GL.index(x) for x in r["gl"] if x in GL),
           r["dose"], r["farbe"], r["dosis"]] for r in recs]

# ---------------------------------------------------------------- schreiben
mm = rep.get("matcherMetadata") or {}
posda = sum(g["pos"] for g in genes)
posfehlt = sum(g["fehlt"] for g in genes)
with open(OUT, "w", encoding="ascii", newline="\n") as f:
    f.write("/* ============================================================\n")
    f.write("   GENE-IUS PGx - Genprofil aus dem PharmCAT-3.2.0-Lauf\n")
    f.write("   Quelle: IT/General/PharmCAT Validation 20260730 (40 Proben)\n")
    f.write("   Erzeugt von build_pharmcat.py. Nicht von Hand aendern.\n")
    f.write("   Probe %s | %s | PharmCAT %s | Daten %s\n"
            % (PROBE, mm.get("genomeBuild"), rep.get("pharmcatVersion"), rep.get("dataVersion")))
    f.write("   Gene %d | Positionen %d gerufen / %d fehlend\n" % (len(genes), posda, posfehlt))
    f.write("   Wirkstoff-Empfehlungen %d fuer %d Wirkstoffe\n"
            % (len(drugs), len({r['n'] for r in roh})))
    f.write("   ============================================================ */\n")
    f.write("const P_META=%s;\n" % j(dict(
        probe=esc(PROBE), sentrix=esc(mm.get("sampleId")), build=esc(mm.get("genomeBuild")),
        ver=esc(rep.get("pharmcatVersion")), daten=esc(rep.get("dataVersion")),
        stand=esc(str(rep.get("timestamp"))[:10]), posda=posda, posfehlt=posfehlt,
        kohorte=40)))
    f.write("const P_GENES=%s;\n" % j(genes))
    f.write("const P_DQ=%s;\n" % j(QDE))
    f.write("const P_DKL=%s;\n" % j(KLASSE))
    f.write("const P_DTXT=%s;\n" % j(texte))
    f.write("const P_DIMP=%s;\n" % j(impl))
    f.write("/* [Wirkstoff, Quelle, Textindex, Implikation, Klasse, Ampel, Flags, Genotyp] */\n")
    f.write("const P_DRUGS=%s;\n" % j(drugs))
    f.write("const P_TXT=%s;\n" % j(mtxt))
    f.write("const P_GL=%s;\n" % j(GL))
    f.write("const P_REC=%s;\n" % j(rectab))

print("geschrieben: %s  %.1f kB" % (OUT, os.path.getsize(OUT) / 1024.0))
print("Probe %s | Gene %d (bestimmt %d, mehrdeutig %d, offen %d)"
      % (PROBE, len(genes), sum(g["ok"] for g in genes), sum(g["mehr"] for g in genes),
         sum(1 for g in genes if not g["ok"])))
print("Positionen %d gerufen / %d fehlend (%.0f %%)" % (posda, posfehlt, 100.0*posda/(posda+posfehlt)))
print("Wirkstoff-Empfehlungen %d fuer %d Wirkstoffe" % (len(drugs), len({r['n'] for r in roh})))
print("  Ampel:", dict(Counter(r["sev"] for r in roh)))
print("  Quelle:", dict(Counter(r["q"] for r in roh)))
print("Novogenia-Matrix: %d Zeilen" % len(rectab))
