# PGx-Datenquellen - Rechercheergebnis

**Stand:** 2026-07-28 | **Methode:** 52 Agenten, 1.713 Werkzeugaufrufe, 115 Quellen gefunden,
25 nach Gegenpruefung bestaetigt, 15 korrigiert.
Jede genannte URL wurde von mindestens einem Agenten tatsaechlich abgerufen.

**Zwei Fragen von Daniel:**
1. Welche Datenbanken mit Alternativwirkstoff-Empfehlungen koennen wir heranziehen?
2. Kommen wir an PharmGKB-Rohdaten per Export oder Schnittstelle, um die gelieferten
   Pharmakogenetik-CSVs selbst zu bauen - taeglich automatisch?

---

## 1. Alternativwirkstoffe — was es gibt

| Quelle | Was drin ist | Lizenz / Kosten | API | DACH |
|---|---|---|---|---|
| **MED-RT** (VA, via NCI-Mirror) — [Core_MEDRT_XML.zip](https://evs.nci.nih.gov/ftp1/MED-RT/Core_MEDRT_XML.zip) | 96.516 Tripel: may_treat 15.419, has_PE 12.077, CI_with 11.526, has_MoA 7.919, may_prevent 2.760; 4.589 echte RXCUIs mit may_treat, 1.401 MeSH-Indikationen | MED-RT-Kern US-Bundesdaten; **aber** SNOMED-CT-Anteil eingebettet (761/592 Assoziationen) → Doku sagt „Some proprietary data requires licensing". 0 EUR | Bulk-XML, 2,56 MB, ohne Login, monatlich | Lücke: US-FDA-Labels, siehe unten |
| **RxClass / RxNav** (NLM) — [rxnav.nlm.nih.gov](https://lhncbc.nlm.nih.gov/RxNav/APIs/RxClassAPIs.html) | Dieselben MED-RT-Relationen live abfragbar + EPC/MOA/ATC1-4; `similarByRxcuis` als fertiger Ähnlichkeits-Score | Frei, kein Key. **Korrektur:** „no license needed" gilt *mit einer Ausnahme* — RxClass IST die Ausnahme (SNOMED-Affiliate-Lizenz), [ToS](https://lhncbc.nlm.nih.gov/RxNav/TermsofService.html). 20 req/s, Attributionssatz Pflicht | REST, JSON/XML | wie MED-RT |
| **RxNav-in-a-Box** — [Doku](https://lhncbc.nlm.nih.gov/RxNav/applications/RxNav-in-a-Box.html) | Identische Endpunkte lokal, eingefrorener Datenstand | UMLS-Lizenz nötig (kostenlos, jährlich zu erneuern) | Docker, monatlich | neutral |
| **DrugCentral** — [drugcentral.org/download](https://drugcentral.org/download) | 12.047 Indikationen (79 % SNOMED), 27.731 Kontraindikationen (97 % SNOMED), 2.525 Off-Label; struct2atc echte n:m (ASS = 20 ATC-Codes) | CC BY-SA 4.0, kommerziell erlaubt, [privacy](https://drugcentral.org/privacy). ShareAlike beachten | REST + 1,4 GB Postgres-Dump | ATC ist WHO-System, EMA-Kategorie vorhanden; keine DE/AT-Handelsnamen |
| **Open Targets 26.06** — [FTP](https://ftp.ebi.ac.uk/pub/databases/opentargets/platform/26.06/output/) | clinical_indication, drug_mechanism_of_action, pharmacogenomics; EFO/MONDO-Hierarchie + therapeuticAreas | **CC0 1.0**, keine Attributionspflicht, [Lizenz](https://platform-docs.opentargets.org/licence) | GraphQL + Parquet-FTP, quartalsweise | EU-Betreiber (EMBL-EBI) |
| **ChEMBL 37** — [FTP](https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/latest/) | 60.055 Indikationszeilen (MeSH + EFO, 99,7 % dual), MOLECULE_ATC_CLASSIFICATION n:m | CC BY-SA 3.0 Unported, [LICENSE](https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/latest/LICENSE) | REST + PostgreSQL-Dump 1,9 GB, halbjährlich | EU-Betreiber |
| **CPIC** — [api.cpicpgx.org](https://api.cpicpgx.org/v1/recommendation) | 2.115 Empfehlungen, 324 Wirkstoffe, 635 Paare; 476 Zeilen mit „alternat*" im Freitext; drug.atcid ist Array (Aspirin 13 Codes) | **CC0 1.0** — die sauberste Lizenz im Feld. Aber ToU derselben Seite: „use the data for research purposes and not with any intent to offer … for sale as a commercial item" | REST (PostgREST 12.0.2) + SQL-Dump 3,8 MB | Wirkstoffe generisch |
| **ClinPGx guidelineAnnotations** — [ZIP](https://api.clinpgx.org/v1/download/file/data/guidelineAnnotations.json.zip) | 219 Leitlinien (DPWG 111, CPIC 78, RNPGx 16); 114 mit alternateDrugAvailable=true; 54 mit **namentlicher** Alternative | CC BY-SA 4.0 **+ „Under no circumstances can ClinPGx data be sold"** (LICENSE.txt im ZIP) → für kommerzielle App gesperrt | Bulk + REST | DPWG/RNPGx = EU |
| **DPWG/KNMP Original-PDF** — [Link](https://www.knmp.nl/sites/default/files/2026-04/pharmacogenetic_recommendation_text_20250501.pdf) | 276 Einträge, 112 Gen-Wirkstoff-Paare, 26–37 mit benannter Alternative | **Keine Lizenzangabe im PDF** → normales Urheberrecht KNMP + EU-Datenbankrecht. G-Standaard = kostenpflichtig | Nein, nur PDF | EU, nächste an DACH-Verfügbarkeit |
| **WIdO ATC-Index 2026** — [wido.de](https://www.wido.de/publikationen-produkte/analytik/arzneimittel-klassifikation/) | XLSX, 7.598 Level-5-Zeilen, 6.215 Substanznamen, 738 mit Mehrfach-ATC, **deutsche Wirkstoffnamen** | Download gratis, aber „Jede Änderung oder Manipulation des Materials ist untersagt" + Genehmigungspflicht (Urheberrechte.pdf im ZIP) | Nein, ZIP 8 MB, jährlich | **DE, hoch** |
| **BfArM amtliche ATC-Fassung** — [Downloadbedingungen](https://www.bfarm.de/SharedDocs/Downloads/DE/Kodiersysteme/ATC/atc-ddd-amtlich-2026.html) | 273-S.-PDF, Stoffregister mit Mehrfach-ATC (ASS = A01AD05/B01AC06/N02BA01) | **Korrigierter Befund:** BfArM erklärt selbst „anderes amtliches Werk i. S. des § 5 Absatz 2 UrhG … dürfen Sie dieses Werk nutzen" — Auflagen: § 62 Änderungsverbot, § 63 wörtliche Quellenangabe | Nein, nur PDF | **DE, amtlich** |
| **ABDATA / ABDAmed²** — [avoxa.de](https://avoxa.de/datenbanken/abdata-pharma-daten-service/) | „AMTS Indikationen" = alle zugelassenen Anwendungsgebiete strukturiert, ICD-10-GM, SNOMED CT, amtliche dt. ATC-Version, codierte Gegenanzeigen | Kommerziell, **Preis nicht veröffentlicht — anzufragen** | Keine öffentliche API, Rohdaten-Paket, 14-täglich | **DE, beste** |

**Was unser Problem löst.** Mehrfach-ATC ist gelöst und zwar mehrfach: DrugCentral liefert für Acetylsalicylsäure 20 ATC-Codes ([struct2atc/struct_id/74](https://uxn2ycvimg.us-east-2.awsapprunner.com/struct2atc/struct_id/74)), CPIC 13 als Array, RxClass gibt für RXCUI 1191 A01AD + B01AC + N02BA + N02AJ zurück, das WIdO-Excel und die BfArM-Fassung ebenfalls alle drei Substanz-Codes. Der Fehler steckt nicht in ATC, sondern in unserer All-Drugs-V12: dort ist pro Wirkstoff nur eine Zeile geführt. Größenordnung des Delta: 738 Substanznamen mit Mehrfach-Code im deutschen Index, 360 von 2.883 bei ClinPGx.

**Das eigentliche Problem — Sammelkategorien — löst ATC prinzipiell nicht.** Das WHOCC schreibt es selbst: „The ATC system is, however, not strictly a therapeutic classification system" und „drugs with similar therapeutic use may be classified in different groups" ([structure_and_principles](https://atcddd.fhi.no/atc/structure_and_principles/)). Die Lösung ist eine zweite Achse. MED-RT liefert sie: Aspirin trägt dort may_treat auf Arthritis, Fever, Gout, Inflammation, Osteoarthritis, Pain und may_prevent auf Cerebral Infarction, TIA, Myocardial Infarction — echte Indikationen statt Chemie-Schublade. Rückwärts funktioniert es genauso: Diabetes Typ 2 (D003924) → 79 Wirkstoffe, Hypertonie (D006973, ttys=IN) → 136, EPC „P2Y12 Platelet Inhibitor" → exakt cangrelor, clopidogrel, prasugrel, ticagrelor. Letzteres ist genau das Set, das CPIC bei CYP2C19-PM empfiehlt — ohne „Other …"-Müll.

**Zwei harte Einschränkungen.** Erstens die DACH-Lücke: metamizole (RXCUI 3523), piritramide (8354), flupirtine (25193), tilidine (10597), benzbromarone (1385), molsidomine (7023), trimetazidine (10826) haben in MED-RT alle einen ATC-Code, aber **null** may_treat, has_moa, has_epc. Für diese Wirkstoffe zeigt die App ohne Fallback keine Alternativen. Zweitens: `may_treat` allein reicht nicht — Clopidogrel hat may_treat = 0, aber 3× may_prevent. Beide Relationen gemeinsam auswerten, sonst fällt die ganze Thrombozytenhemmer-Klasse durch.

**Was NICHT hilft.** Der komplette Block „Therapeutic Equivalence" ist systematisch untauglich, nicht datenqualitativ. FDA-Orange-Book-Preface wörtlich: therapeutische Äquivalenz „does not encompass a comparison of different therapeutic agents used for the same condition (e.g., meperidine hydrochloride vs. morphine sulfate)" ([Preface](https://www.fda.gov/drugs/development-approval-process-drugs/orange-book-preface)). § 129 Abs. 1 SGB V begrenzt den Apothekenaustausch auf „wirkstoffgleich" — aut idem, G-BA Anlage VII und Rabattverträge sind damit rechtssystematisch raus. Im openFDA-Orange-Book (48.502 Produkte) existiert kein Feld, das ein Produkt mit einem *anderen* Wirkstoff verknüpft; Omeprazol, Pantoprazol und Esomeprazol tragen alle „AB", ohne dass das eine Beziehung herstellt. Ein Join über TE-Code wäre ein Modellierungsfehler. Ebenfalls raus: **DrugBank** (CC BY-NC, akademische Downloads derzeit komplett pausiert), **KEGG** („Non-academic use of KEGG requires a commercial license", [legal.html](https://www.kegg.jp/kegg/legal.html)) und **atcd** auf GitHub (CC BY-NC-SA). Fachlich wäre KEGGs DG-Hierarchie ideal gewesen — lizenzrechtlich tot.

**Ein kuratierter Goldstandard zum Testen:** WHO eEML ([list.essentialmeds.org](https://list.essentialmeds.org/)) führt „Therapeutic equivalent for X for Y", also indikationsgebunden. 156 Relationen, ~5 % Abdeckung — als Primärquelle zu dünn, als Validierungs-Testset gut. Lizenz CC BY 3.0 IGO, kommerzielle Nutzung ausdrücklich erlaubt; verboten ist nur die Platzierung neben Produktwerbung ([licencing](https://list.essentialmeds.org/licencing)).

---

## 2. Empfehlung für die App

**Stufe 1 — sofort, 0 EUR, ca. 1–2 Tage.** MED-RT-Bulk-XML einmalig einlesen ([Core_MEDRT_XML.zip](https://evs.nci.nih.gov/ftp1/MED-RT/Core_MEDRT_XML.zip), 2,56 MB, monatlich, ohne Login) und `may_treat` + `may_prevent` invertieren → indikationsbasierte Alternativgruppen in unserer eigenen DB. Ranking über `has_MoA` (engste Alternative), `has_EPC` als zweite Ebene, `CI_with` (11.526 Tripel) als Ausschlussfilter. Vorher die 2.694 Wirkstoffe auf RXCUI mappen: zweistufig, erst `/REST/rxcui.json?name=X&search=2`, Fehlschläge in `/REST/approximateTerm.json`. Das funktioniert auch für deutsche Umschriften (Acetylsalicylsaeure → RXCUI 1191, Score 3,31), aber „Metamizol-Natrium" liefert leeres `idGroup` — Handarbeit einplanen. Bei 20 req/s sind 2.694 Wirkstoffe in ~2,5 Minuten durch. **Wichtig: EPC/MOA/MED-RT primär, ATC nur als Zusatzsignal** — EPC/MOA stammen aus FDA-SPL/VA-Daten und sind sowohl pharmakologisch schärfer als auch lizenzrechtlich sauberer als ATC.

**Stufe 2 — Indikations-Tiefe, 0 EUR, ca. 3–5 Tage.** DrugCentral-Dump ([1,4 GB](https://unmtid-dbs.net/download/drugcentral.dump.11012023.sql.gz)) für SNOMED-kodierte Indikationen + Kontraindikationen als Negativfilter, Open Targets `clinical_indication` + `drug_mechanism_of_action` für die EFO/MONDO-Hierarchie. Letztere ist der Schlüssel gegen zu kleine Gruppen: Median 2 Wirkstoffe pro DrugCentral-Indikation, nur 1.524 von 2.703 Konzepten haben ≥ 2. Über den Krankheitsbaum nach oben aggregieren, bis die Gruppe trägt. Open Targets ist CC0 — die einzige Quelle ohne ShareAlike-Risiko.

**Stufe 3 — PGx-Alternativen, 0 EUR, ca. 2–3 Tage.** CPIC-SQL-Dump ([cpic_db_dump.sql.gz](https://files.cpicpgx.org/data/database/cpic_db_dump.sql.gz), 3,8 MB, v1.59.1 vom 18.06.2026), daraus die ~50–60 relevanten Fälle **manuell** in eine Tabelle `drug_id | gene | phänotyp | ersatz_drug_id | typ` überführen. `typ` ist zwingend, weil im selben Text Kreuzrisiko-Warnungen stehen: Carbamazepin nennt Phenytoin/Lamotrigin — nicht als Alternative, sondern als ebenfalls gefährlich. Naives Textmining wäre in einer Patienten-App gefährlich; das ist an mehreren Falschtreffern konkret aufgetreten. Nicht auf `alternatedrugavailable` bauen: bei allen 2.115 Zeilen `false`.

**Stufe 4 — Produktion.** RxNav-in-a-Box lokal, damit der Datenstand eingefroren und nachweisbar ist. Für eine Medizin-App ohnehin Pflicht: man muss belegen können, auf welcher Datenbasis eine Empfehlung entstand.

**Kosten und Verträge.** Stufen 1–4 kosten 0 EUR Lizenzgebühr. Nötig ist ein kostenloser UMLS-Account (jährlich zu erneuern) für RxNav-in-a-Box. Die einzige Position mit echtem Preisschild wäre ABDATA — **Preis nicht veröffentlicht, anzufragen**. Vor dem Kauf klären, ob ABDAmed² (für Kliniken/Praxen positioniert) oder ABDATA Laiendaten (B2C) das richtige Produkt ist.

**Zwischenlösung, falls ABDATA Zeit oder Vertrag braucht:** BfArM-Fassung für die deutsche Mehrfach-ATC-Zuordnung — nach den eigenen Downloadbedingungen des BfArM nutzbar, auch kommerziell, mit Änderungsverbot und wörtlicher Quellenangabe. Das ist die einzige DACH-Quelle mit deutschen Wirkstoffnamen, die ohne Genehmigungsverfahren einsetzbar ist. Achtung: das ist eine **Korrektur** einer früheren Einschätzung — die WIdO-Boilerplate auf Seite 3 der Datei sagt das Gegenteil, die Downloadbedingungen sind aber der speziellere, vertraglich geschlossene Text.

**Für die DACH-Lücke (Metamizol & Co.):** Swissmedic-OGD-Daten sind als einzige geprüfte Quelle unter „Freie Nutzung" — 7.199 Humanarzneimittel, 7.054 mit ATC, 7.090 mit Freitext-Indikation, 7.198 mit IT-Nummer als zweiter Klassifikationsachse. Gratis, kommerziell verwertbar, gut als Validierungsdatensatz.

---

## 3. PharmGKB-Rohdaten selbst bauen

**Teilweise — 3 von 4 CSVs ja, eine klar nein.**

Vorweg zwei Dinge, die jede bestehende Pipeline betreffen: **`api.pharmgkb.org` existiert nicht mehr** (DNS NXDOMAIN, abgeschaltet 20.07.2026). Alles läuft über `api.clinpgx.org/v1`, identische Syntax, reines Find/Replace. Und: `clinicalAnnotations.zip` antwortet mit HTTP 200, ist aber seit 2025-07-05 eingefroren — Nachfolger ist `summaryAnnotations.zip`. Von 118 Objekten im Bucket sind nur ~25 aktuell gepflegte Nutzdaten.

### drug_products.csv (42.694) — **JA, aber inhaltlich wertlos für uns**
Quelle: openFDA `/drug/drugsfda`, Keys 1:1 identisch mit unseren Spalten.
- API: `https://api.fda.gov/drug/drugsfda.json` (29.227 Anträge, täglich Mo–Fr)
- Bulk: über [download.json](https://api.fda.gov/download.json), 8,96 MB
- Lizenz: **CC0 1.0**, „even for commercial purposes, all without asking permission" ([open.fda.gov/license](https://open.fda.gov/license/))
- Aber: rein US-Zulassungen. Für ein DACH-Produkt ersetzen durch BASG (AT), Swissmedic-OGD (CH), BfArM (DE). Bei BASG und BfArM war die Lizenz **nicht ausgewiesen — anzufragen**.
- Falle: das `openfda`-Objekt sitzt auf **Antrags**-Ebene, nicht pro Produkt, und ist nur bei 12.528 von 29.227 (43 %) überhaupt vorhanden. Kein verlässliches 1:1-Mapping.

### drug_pharmacogenetics.csv (8.228) — **JA, aber nur über CPIC statt ClinPGx**
Der direkte Nachbau wäre `summaryAnnotations.zip` (Feldnamen decken sich fast vollständig; `efficacy/toxicity/dosage` = One-Hot der PharmGKB-Phenotype-Category).
- ClinPGx-Bulk: `https://api.clinpgx.org/v1/download/file/data/summaryAnnotations.zip` (303 → `https://s3.pgkb.org/data/…`)
- **Lizenzproblem:** CC BY-SA 4.0 **plus** in jeder LICENSE.txt im ZIP wörtlich „Under no circumstances can ClinPGx data be sold for other's private or commercial use", plus Data Usage Policy „for research purposes and not with any intent to offer all or any part of the data for sale as a commercial item". Dazu ShareAlike, das unsere abgeleitete Tabelle infiziert, und eine aktive Nachweispflicht: „Proof of such agreement shall be made available to ClinPGx".
- **Sauberer Weg:** die tragenden Empfehlungen direkt aus **CPIC** ziehen — CC0, kommerziell frei. Die CPIC-API ist zudem *besser* strukturiert als der ClinPGx-Bulk: `drugrecommendation` als Klartext, `implications`, `classification`, `lookupkey`, `phenotypes` als echte Objekte, statt HTML-Tabellen parsen zu müssen.
  - `https://api.cpicpgx.org/v1/recommendation` (2.115 Zeilen)
  - `https://api.cpicpgx.org/v1/recommendation_view?drugname=eq.clopidogrel&lookupkey=cs.{"CYP2C19":"Poor Metabolizer"}`
  - `POST https://api.cpicpgx.org/v1/rpc/recommendation_lookup`
  - Dump: `https://files.cpicpgx.org/data/database/cpic_db_dump.sql.gz`
- Restrisiko auch bei CPIC: die ToU derselben Seite enthalten dieselbe „research purposes"-Klausel wie ClinPGx. CC0 ist ein echter Rechteverzicht am *Inhalt* (den kann eine Website-ToU nicht zurückholen), aber der *API-Zugang* ist vertraglich zusätzlich gebunden. Praktische Konsequenz: SQL-Dump verwenden, nicht API-Polling im Verkaufsprodukt.

### drug_interactions.csv (129.355) — **NEIN**
**Das ist der Problemfall.** Quelle ist DrugBank. DrugBank verlangt für alles Kommerzielle eine Lizenz; die freien Datensätze stehen unter CC BY-NC 4.0, und die Gratis-Akademikerlizenz schließt uns explizit aus: „You're a student, professor, or research associate with an academic institution", „Your research is not primarily for the benefit of a commercial third party" ([releases/latest](https://go.drugbank.com/releases/latest)). Zusätzlich sind derzeit **alle** akademischen Downloads gestoppt („All Academic DrugBank dataset downloads are temporarily paused"). Frei ist nur DrugBank Open Data (CC0) — das sind ausschließlich IDs, Namen, Synonyme und Strukturen, **keine Wechselwirkungen**. Preis: **nicht veröffentlicht**; die kursierenden 25–100k USD/Jahr stammen aus einem Wettbewerber-Blog und sind **nicht verifiziert**. Diese CSV darf ohne Lizenz nicht ausgeliefert werden.

Kein gleichwertiger freier Ersatz gefunden:
- DDInter 2.0: CC BY-NC-SA 4.0 → raus
- TWOSIDES/OFFSIDES: falscher Datentyp (FAERS-Disproportionalitätssignale), zusätzlich keine Lizenz ausgewiesen
- DrugCentral hat eine `ddi`-Tabelle, CC BY-SA 4.0 — **Umfang und Herkunft nicht belegt**, muss am Dump selbst nachgezählt werden
- KEGG und CredibleMeds: kommerziell gesperrt
- Einzig rechtlich sauberer Eigenbau: openFDA `drug/label`, Feld `drug_interactions` — CC0, autoritativ, aber Fließtext ohne Struktur. Extraktion per NLP ist ein eigenes Teilprojekt.
- Für DACH wäre ABDATA naheliegender als DrugBank.

Nebenbefund, lizenzfrei und sofort nutzbar: NCATS Inxight FRDB ([drugs.ncats.io](https://drugs.ncats.io/)) ist Public Domain — „All facts appearing in these datasets are in the public domain and may be reproduced or copied without NCATS permission." `frdb-ddi.tsv` hat 34.851 Zeilen über 2.844 Compounds, **aber nur 2.151 mit klinischer Evidenz-Annotation**; der Rest sind In-vitro-Parameter (IC50 7.443, Ki 1.019). Es ist primär ein Enzym-/Transporter-Datensatz, keine klinische DDI-Warnliste. `frdb-pk.tsv`: 13.455 Zeilen über 3.079 Compounds, 2.998 mit Dosiswert — das sind **Studiendosen**, keine Dosierempfehlungen.

### drugs_master.csv (2.219) — **JA**
Keine eigene Quelle nötig, das ist ein Rollup. `drugs.zip` liefert fast alles direkt: Name, Generic Names, Trade Names, RxNorm Identifiers, ATC Identifiers, Clinical/Variant Annotation Count, Top Clinical Annotation Level.
- `https://api.clinpgx.org/v1/download/file/data/drugs.zip` (677.711 Bytes, 3.760 Zeilen)
- Gleiche Lizenzbeschränkung wie oben. Falls das blockiert: Wirkstoff-Vokabular über DrugBank **Open Data** (CC0, auch aus Drittmirrors zulässig — CC0 erlischt nicht dadurch, dass DrugBank den eigenen Download pausiert) + RxNorm Prescribable Release („no license required").
- Nutzwert unabhängig davon: `ATC Identifiers` ist mehrwertig. aspirin → `A01AD05, B01AC06, N02BA01`. 360 von 2.883 Wirkstoffen mit >1 Code. **Aber:** nur 1.606 Einträge haben RxNorm UND ATC gleichzeitig, und 114 der 360 sind vom Typ „Drug Class", also gar keine Einzelsubstanzen — real gewinnt man ~246 echte Wirkstoffe.

**Weitere relevante Endpunkte:**
- Datei-Index für Change-Detection: `https://api.clinpgx.org/v1/data/file/data/?view=min`
- S3 direkt listbar: `https://s3.pgkb.org/?list-type=2&prefix=data/`
- Einzelabruf: `https://api.clinpgx.org/v1/data/guidelineAnnotation/{PA-ID}?view=max`
- MED-RT: `https://evs.nci.nih.gov/ftp1/MED-RT/Core_MEDRT_XML.zip`
- openFDA Bulk: `https://download.open.fda.gov/drug/orangebook/drug-orangebook-0001-of-0001.json.zip`

---

## 4. Tägliche Aktualisierung — Bauplan

**Kernbefund: täglich bauen geht, bringt bei ClinPGx aber fast nichts.** 105 der 118 Dateien im Index tragen als Tag „05" — Releases laufen am 5. des Monats zwischen 00:25 und 01:35 PDT. Der Job läuft täglich, aber als **Change-Detector**, nicht als Voll-Download.

**Abrufplan nach Kadenz:**

| Quelle | Kadenz real | Erkennung |
|---|---|---|
| ClinPGx (drugs, drugLabels, guidelineAnnotations, summaryAnnotations, relationships) | monatlich, am 5. | `GET /v1/data/file/data/?view=min` → JSON mit fileName/lastModified/size/path, gegen letzten Stand diffen. Kein Login, kein Token, CORS offen |
| CPIC | 1–3× pro Monat | GitHub-Releases-API auf `tag_name` pollen; oder HEAD auf den Dump (Last-Modified) |
| MED-RT | monatlich | HEAD auf Core_MEDRT_XML.zip; XML-Header trägt Versionsdatum (aktuell 2026.07.06) |
| openFDA | täglich Mo–Fr | `download.json`, Feld `export_date` |
| DrugCentral | ~jährlich, aktuell 01.11.2023 | Verzeichnis-Listing `https://unmtid-dbs.net/download/DrugCentral/` |
| Open Targets | quartalsweise | FTP `latest/` |
| ChEMBL | halbjährlich | FTP-Verzeichnisdatum |
| WIdO / BfArM | jährlich | manuell |

**Mechanik:** ~10 HEAD-Requests pro Tag mit `If-Modified-Since` / `If-None-Match`. ClinPGx-S3 liefert dreifach abgesicherte Änderungserkennung: `Last-Modified`-Header, `ETag` + `x-amz-meta-md5hash`, und in **jedem** ZIP eine Marker-Datei `CREATED_YYYY-MM-DD.txt` neben `VERSIONS.txt` und `LICENSE.txt`. Nur bei Änderung herunterladen, entpacken, in Staging-Tabellen importieren, QA-Invarianten prüfen, dann promoten. Alter Stand bleibt versioniert liegen — für ein Medizinprodukt ist Reproduzierbarkeit Pflicht.

**Wo:** auf unserer eigenen Infrastruktur, nicht als Live-Call aus der App. Für RxClass zusätzlich RxNav-in-a-Box lokal, dann entfällt die API-Abhängigkeit komplett.

**Fallstricke, konkret aufgetreten:**
- **`api.pharmgkb.org` stirbt mit DNS-Fehler, nicht mit HTTP-Status** — das fällt in Cronjobs stumm aus. Explizit auf Exception prüfen.
- **Cloudflare blockt den Standard-User-Agent von Python urllib mit HTTP 403.** Echten User-Agent setzen. Gilt auch für `api.clinpgx.org/v1/data/label/…`.
- **fda.gov liefert Nicht-Browser-User-Agents 404 statt der Datei.** Ein 404 von fda.gov ist kein Beweis, dass die Seite fehlt.
- **Wirkstoffnamen bei ClinPGx sind case-sensitiv:** `name=Aspirin` → 404, `name=aspirin` → 200.
- **DrugCentral-API macht Substring-Matching:** `/omop_relationship/relationship_name/indication` liefert 39.778 Zeilen = 12.047 indication **plus** 27.731 contraindication. Ungefiltert liest man Kontraindikationen als Indikationen ein. Deshalb Dump statt API — die API hat zusätzlich Default-Paging von 10 auf Sammel-Endpunkten und sporadische 500er.
- **ChEMBL und Open Targets mischen Studienindikationen unter zugelassene.** Aspirin hat in ChEMBL 167 Indikationszeilen, u. a. Kopf-Hals-Karzinom Phase 1. Zwingend `MAX_PHASE_FOR_IND = 4` bzw. `maxClinicalStage = APPROVAL` filtern; danach bleiben ~8.683 statt 60.055 Zeilen.
- **Rate Limits:** RxNav/openFDA 20 req/s bzw. 240 req/min (ohne Key nur 1.000/Tag → Bulk verwenden), ClinPGx 2 req/s (empirisch bestätigt, 429 bei Überschreitung), KEGG 3/s. NLM empfiehlt 12–24 h Caching.
- **Formatbrüche:** ClinPGx-JSON-Wurzel ist `{citations, guideline}` — die Booleans liegen unter `guideline`, nicht top-level. Open-Targets-Parquet hat zwei verschiedene Layouts (`clinical_indication.parquet` als Einzeldatei vs. Spark-Output mit `_SUCCESS` + `part-*`). Orange-Book-ZIP ist latin-1, nicht UTF-8. CPIC-`alerttext` ist `text[]`, enthält aber immer genau ein Element. Open Targets hat `maximumClinicalTrialPhase`/`maxPhaseForIndication` in `maximumClinicalStage`/`maxClinicalStage` umbenannt. ClinPGx selbst warnt: „the parameters and responses may change at any time while we are developing it" — Schema-Toleranz einbauen.
- **Lizenz-Fallstrick im Job:** ClinPGx-Bulk und CPIC nicht in dieselbe Tabelle mischen. CPIC = CC0, ClinPGx/DPWG-Anteil = CC BY-SA 4.0 + Verkaufsverbot. Bei PharmCAT den Reporter mit `-rs CPIC` beschränken, dann bleibt der ausgegebene Empfehlungstext CC0.
- **Attribution im Produkt hinterlegen:** NLM-Satz („This product uses publicly available data from the U.S. National Library of Medicine … NLM is not responsible for the product and does not endorse or recommend this or any other product."), kein NLM-Logo. ChEMBL verlangt Erhalt der ChEMBL-IDs und sichtbaren Release-Ausweis („ChEMBL 37"). BfArM-Nutzung verlangt den wörtlichen WIdO/WHOCC/BfArM-Quellensatz nach § 63 UrhG.

---

## 5. Offene Punkte

**Preise — bei keinem kommerziellen Anbieter öffentlich.** Kein Preis gefunden und keiner erfunden bei: ABDATA/Avoxa, DrugBank (kommerzielle Volllizenz), KNMP G-Standaard, WHOCC-Redistributionslizenz, WIdO-Genehmigung, MMI PHARMINDEX, ApoVerlag, HCI Solutions, FDB, Medi-Span, Elsevier GSDD. Jede Produktseite endet im Kontaktformular.

**Anzuschreiben:**
- **ABDATA / Avoxa** — info@abdata.de, +49 6196 928-422; Vertrieb s.bieber@avoxa.de. Frage: Preis und Umfang für AMTS-Indikationen; und ob ABDAmed² oder ABDATA Laiendaten das richtige Produkt für unseren Kontext ist.
- **WHOCC Oslo** — whocc@fhi.no, +47 21 07 81 60. Zwei Fragen: (a) Dürfen ATC-Codes in einer kommerziellen App angezeigt werden? „Copying and distribution for commercial purposes is not allowed" ([copyright_disclaimer](https://atcddd.fhi.no/copyright_disclaimer/)). (b) „Changing or manipulating the material is not allowed" ist **unbeschränkt** formuliert — betrifft das auch den internen Join gegen unsere 2.694 Wirkstoffe? Der 200-EUR-Kauf im [Bestellportal](https://orders.atcddd.fhi.no/) ist ausdrücklich **keine** Redistributionslizenz; die Klausel steht wörtlich im JS-Bundle des Bezahlportals selbst.
- **WIdO / AOK-Bundesverband** — ai@wido.bv.aok.de. Genehmigung für die Nutzung des ATC-Index. Es gibt einen etablierten Lizenzierungsweg („stellt das WIdO die Arzneimittel-Stammdatei lizenzierten Nutzern zur Verfügung"), eine Antwort ist also wahrscheinlich.
- **ClinPGx / Stanford** — api@clinpgx.org (dieser Kontakt steht in der OpenAPI-Spec; feedback@clinpgx.org ließ sich **nicht bestätigen**, Kontaktseite 404). Frage: Non-Academic License für eine kommerzielle PGx-App. Belegt existiert diese Kategorie: [annotationLicensees](https://www.clinpgx.org/page/annotationLicensees) listet „Human Longevity Inc / Non-Academic License" sowie Personalis. Kein publiziertes Verfahren, kein Preis.
- **KNMP / Werkgroep Farmacogenetica** — Nutzungsanfrage für die DPWG-Empfehlungen. Das PDF enthält **keinerlei** Lizenzhinweis (Volltextsuche nach copyright/licen/rights reserved/permission: null Treffer), es gilt normales Urheberrecht plus EU-Datenbankherstellerrecht.
- **BASG (AT)** — basg@basg.gv.at, für eine offizielle Datenschnittstelle. Die in der Angular-App gefundene interne MiA-REST-API ist nirgends dokumentiert und nicht zugesagt.
- **DrugBank Sales** — go.drugbank.com/contact/sales bzw. go.drugbank.com/clinical für den kostenlosen API-Trial.

**Nicht belegbar / offen geblieben:**
- MED-RTs UMLS-Restriction-Category — nlm.nih.gov lieferte während der Prüfung durchgehend HTTP 502 plus Hinweis auf eine Haushaltssperre.
- Ob RxNav-in-a-Box die restricted sources (FDB/Micromedex/Gold Standard, SRL 3) überhaupt ausliefert oder ein bereinigtes Image ist. **Das entscheidet, ob die SRL-3-Frage für uns überhaupt relevant ist — als Erstes klären.**
- Umfang und Herkunft der DrugCentral-`ddi`-Tabelle — muss am Postgres-Dump selbst nachgezählt werden.
- Lizenz der FDA-PGx-Assoziationstabelle (Seite lieferte 404); Lizenz der BASG- und Swissmedic-Register (BASG-Seite ohne Lizenzangabe, opendata.swiss lieferte 403).
- Ob CPICs `alternatedrugavailable` bewusst leer ist oder ein Bug — im cpic-data-Wiki nicht dokumentiert.
- Ob in der ClinPGx-Spalte `clearance` tatsächlich die umbenannte PharmGKB-Kategorie „metabolism/PK" steckt — **Vermutung, nicht belegt**; an der gelieferten CSV prüfen.

**Juristisch zu bewerten (nicht durch Anfrage lösbar):**
- **ShareAlike-Verträglichkeit bei Quellenmischung.** DrugCentral ist CC BY-SA 4.0, ChEMBL CC BY-SA **3.0 Unported** — 3.0 ist nicht aufwärtskompatibel zu 4.0. Zwei ShareAlike-Quellen unterschiedlicher Versionen können im selben abgeleiteten Datensatz unvereinbar sein. Bei einem Medizinprodukt kein theoretisches Thema. Die Abgrenzung „ShareAlike trifft die abgeleitete Datenbank, nicht die App-UI" sollte ein Jurist bestätigen.
- **ATC-Ausgabe in der App generell.** Das betrifft uns bereits heute über All Drugs V12, unabhängig von allem Neuen. Entschärfen lässt es sich, indem ATC-Codes aus DrugCentral/ChEMBL/Open Targets bezogen werden statt direkt vom WHOCC — Open Targets ist CC0 und erklärt ausdrücklich, alle gelisteten Quellen hätten der uneingeschränkten Nutzung durch Open-Targets-Nutzer zugestimmt.
- **CPIC-ToU vs. CC0.** Inhalt aus dem SQL-Dump = CC0-Argument tragfähig; reines API-Polling in einem Verkaufsprodukt = Graubereich.
- **openFDA-Medizin-Disclaimer** in jeder API-Antwort: „Do not rely on openFDA to make decisions regarding medical care … you should assume all results are unvalidated." Relevant für die Haftungsbetrachtung, unabhängig von der Lizenz.
- **Markenrecht:** Public Domain betrifft nur das Urheberrecht. Die Spalte `Trade_Name` im Orange Book enthält eingetragene Marken Dritter.