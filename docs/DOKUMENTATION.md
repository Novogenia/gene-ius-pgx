# GENE-IUS PGx — Projektdokumentation

**Stand:** 2026-07-28 · **Version:** v52 · **Status:** Clickdummy mit echten Daten, lauffähig

Diese Datei ist die Übergabe- und Arbeitsdoku. Sie wird bei jeder größeren Änderung
fortgeschrieben. Wenn etwas hier steht, ist es geprüft — Vermutungen sind als solche
gekennzeichnet.

---

## 1. Was das ist

Interaktiver Prototyp einer Pharmakogenetik-App für Endkundinnen. Zeigt, wie das
Genprofil einer Person die Wirkung ihrer Medikamente verändert, prüft die Kombination
auf Wechselwirkungen, schlägt Alternativen vor und erzeugt einen vollständigen Bericht
für das Arztgespräch.

Demo-Patientin: **Lisa M.**, 13 pharmakogenetisch relevante Gene mit hinterlegtem Genotyp.

**Dateien**

| Datei | Zweck |
|---|---|
| `AI CHAT BOTS\PGx_App.html` | Die App. Eine einzige Datei, ~514 kB, keine externen Abhängigkeiten. |
| `PGx_App_DOKUMENTATION.md` | Diese Datei. |
| Scratchpad `build_pgx_data.py` | Erzeugt den Datenblock aus den Novogenia-Quelldateien. |
| Scratchpad `patch_app_data.py` | Baut den Datenblock in die App ein. |
| Scratchpad `pgx_data.js` | Erzeugtes Zwischenprodukt, ~342 kB. |

**Artifact (immer dieselbe URL bei Updates):**
https://claude.ai/code/artifact/abe29bcc-ae58-4179-82a3-5076c999b67c

**Lokal testen:** `.claude/launch.json` Konfiguration `pgx-dummy` (python http.server, Port 8779)
→ `http://localhost:8779/PGx_App.html?v=N`. Der Cache-Buster `?v=N` ist nötig, sonst zeigt
der Browser die alte Version.

---

## 2. Datenpipeline

```
Quelldateien (AI RESOURCES - Dokumente\PHARMACOGENETICS\)
        │
        ├── All Drugs V12.xlsx ............ 2.694 Wirkstoffe, ATC-Ebenen 1-4,
        │                                    Enzym-Rollen (Substrat/Hemmer/Induktor/
        │                                    aktivierendes Substrat) für 41 Enzyme
        ├── Pharmgkb drug recommendations
        │   V4.xlsx ....................... 100 genotypspezifische Empfehlungszeilen
        │                                    für 42 Wirkstoffe + CPIC/DPWG/CPNDS/FDA
        ├── drugs_master.csv .............. Evidenzstufe je Wirkstoff (x1A…x4)
        ├── drug_pharmacogenetics.csv ..... Anzahl PGx-Annotationen je Wirkstoff
        └── drug_interactions.csv ......... 129.355 DrugBank-Paare mit Freitext
        │
        ▼  build_pgx_data.py
   pgx_data.js  (kompakte Arrays, ASCII-only)
        │
        ▼  patch_app_data.py
   PGx_App.html
```

### Neu bauen

```bash
cd <scratchpad>
python build_pgx_data.py      # liest die Excels/CSVs, schreibt pgx_data.js
python patch_app_data.py      # schneidet den alten Block raus, setzt den neuen ein
```

`patch_app_data.py` erkennt einen bereits eingebauten Block an den Markern
`/* ===== BEGIN ECHTE WIRKSTOFFDATEN ===== */` / `END` und ersetzt ihn. Der Einbau ist
also wiederholbar, ohne die App zu zerlegen.

**Achtung:** `patch_app_data.py` enthält den JS-Builder als String. Änderungen am Builder
gehören in diese Datei, nicht in die HTML — sonst sind sie beim nächsten Lauf weg.

### Format von `pgx_data.js`

| Konstante | Inhalt |
|---|---|
| `D_ATC1` / `D_ATC1DE` | 14 ATC-Hauptgruppen, englisch und deutsch |
| `D_ATC2` | ATC-Ebene 2, dient als „Anwendung" auf der Karte |
| `D_GENES` | Gene, für die ein Phänotyp modelliert ist |
| `D_ROWS` | `[Name, atc1, atc2, Gen, Prodrug, Evidenz, Leitlinienmaske, Textindex, Annotationen, alleGene]` |
| `D_REC` | `[Wirkstoff, Gen, Stufe, RohGenotyp, Textindex, Leitlinienmaske]` — genotypspezifisch |
| `D_IX` | `[a, b, Schweregrad, Enzym, Wirkungsart, Risikobegriff, 0=a löst aus]` |
| `D_ALT` | `[Wirkstoff, …Alternativen derselben ATC-Ebene-4-Gruppe]` |
| `D_RISK` | 77 Risikobegriffe aus den DrugBank-Sätzen |

### Kennzahlen des aktuellen Standes

| | |
|---|---:|
| Wirkstoffe gesamt | 2.697 |
| davon handgepflegt (mit deutschen Markennamen) | 35 |
| mit modelliertem Gen | 653 |
| mit genotypspezifischer Leitlinien-Empfehlung | 42 |
| Wechselwirkungen | 5.273 |
| davon aus DrugBank | 3.278 |
| davon aus den Enzymspalten abgeleitet | 1.991 |
| Wirkstoffe mit Alternativen | 2.571 |
| Bewertung: OK / Achtung / Alarm | 2.408 / 223 / 66 |

---

## 3. Herleitungsregeln

Grundsatz: **nichts erfinden.** Fehlt ein Wert, bleibt das Feld leer und die Oberfläche
sagt das auch.

**Gen je Wirkstoff** — Reihenfolge der Quellen:
1. `GENE(1)` aus Pharmgkb V4 (autoritativ, 42 Wirkstoffe)
2. Gene aus `drugs_master.csv`
3. Hauptsubstrat-Spalte aus All Drugs (`<Enzym>_Main_Substrate`)
4. Substrat-Spalte (nachrangig)

`PGP_Kardio` wird auf `ABCB1` abgebildet.

**Prodrug** — aus `<Enzym>_Main_Activating_Substrate`. Bei Prodrugs kehrt sich die Logik
um: ein langsames Enzym bedeutet zu wenig Wirkung statt zu viel.

**Wechselwirkungen** — Hauptquelle DrugBank. Die Sätze sind formelhaft und werden in vier
Klassen einsortiert:

| Satzmuster | Klasse | Schweregrad |
|---|---|---|
| „risk or severity of X can be increased" | Risiko | Alarm |
| „serum concentration increased" / „metabolism decreased" / „excretion rate → higher serum level" | Anreicherung | Alarm |
| „therapeutic efficacy decreased" / „metabolism increased" / „serum concentration decreased" | Wirkverlust | Achtung |
| Rest | gegenseitig | Achtung |

Ergänzend: Hemmer von Enzym X × Hauptsubstrat von X aus All Drugs — nur für die
modellierten Gene, das sind die genetisch relevanten. Begrenzung auf 12 Partner je
Wirkstoff, DrugBank-Paare zuerst.

**„Andere Wirkstoffe derselben Gruppe"** — bewusst *nicht* „Alternativen" genannt.
Grundlage ist die ATC-Ebene 4, also die amtliche Substanzklasse. Das ist **keine geprüfte
therapeutische Austauschbarkeit**. Zwei Einschränkungen, beide geprüft:

1. **Sammelgruppen.** 654 von 2.693 Wirkstoffen liegen in Gruppen wie „Antidotes",
   „Other Agents For Local Oral Treatment" oder „All Other Therapeutic Products". Darin
   stehen Wirkstoffe, die einander nie ersetzen könnten (Naloxon neben Kupfersulfat).
   `altGroupMixed()` erkennt diese an den Schlüsselwörtern *other / various / all other /
   antidotes / antibiotics / combinations* und zeigt einen orangen Warnhinweis
   „Gemischte Gruppe — hier ist Vorsicht geboten". Die übrigen 2.039 sind saubere Klassen.
2. **Ein ATC-Pfad je Wirkstoff.** In `All Drugs V12.xlsx` hat jeder Wirkstoff genau **eine**
   Zeile und damit genau **einen** ATC-Code — geprüft, 0 Mehrfacheinträge.
   Substanzen mit mehreren Anwendungen erscheinen deshalb nur unter einer davon.
   **Acetylsalicylsäure** steht dort als *Stomatological Preparations* (Mundspülung),
   nicht als Schmerzmittel (N02BA) und nicht als Thrombozytenhemmer (B01AC). Ihre
   „Gruppenkollegen" sind entsprechend Adrenalon und Amlexanox — fachlich unbrauchbar.

Die Oberfläche zeigt bei jeder Liste den vollständigen ATC-Pfad (Ebene 2 › 3 › 4), den
Hinweis auf fehlende Austauschbarkeit und ein Erklär-Popup mit genau dem
Acetylsalicylsäure-Beispiel. Sortiert wird nach Lisas genetischer Bewertung, unauffällige
zuerst.

**Wenn es belastbar werden soll:** eine echte Indikationszuordnung (mehrere ATC-Codes je
Wirkstoff aus dem WHO-ATC-Index) oder eine kuratierte Austauschbarkeitsliste. Beides liegt
derzeit nicht vor.

**Bewertung eines Medikaments** — `statusFor()` aus Metabolisierertyp × Prodrug-Flag.
`overallSev()` zieht zusätzlich die Wechselwirkungen der aktuellen Liste heran; deshalb
kann dasselbe Medikament in der Datenbank „Achtung" und in Lisas Liste „Alarm" sein.

---

## 4. Aufbau der App

Eine HTML-Datei, 2.426 Zeilen: `<style>` → SVG-Symbolbibliothek → `nav.rail` + `main#main`
→ vier Modals → `<script>`.

| Abschnitt | Zeile ca. | Inhalt |
|---|---:|---|
| DATEN | 834 | Demo-Wirkstoffe, Genotypen, Phänotypen, Annotationen |
| ECHTE WIRKSTOFFDATEN | 1035–1246 | erzeugter Block + Builder (aus `patch_app_data.py`) |
| STATE | 1270 | `view`, `workspace`, `watchlist`, Filter |
| LOGIK | 1279 | `statusFor`, `overallSev`, `metrics`, `listSev` (gecacht) |
| KARTE | 1345 | `cardHtml`, `metricBoxes` |
| NAV / FILTER / VIEWS | 1396–1653 | Navigation, Suche, Startseite, Listen |
| ARZTBERICHT | 1653 | `vMerk`, `geneReportCard`, `drugReportBlock` |
| ERKLÄR-POPUPS | 2056 | 9 Themen, `openInfo()` |
| DETAILSEITE | 2136 | `vDetail` |
| ARBEITSFLÄCHE | 2207 | Lisas Liste, `drawLinks()` für die Interaktionsverbindungen |
| RENDER | 2408 | `render()` |

**Ansichten:** Start · Deine Medikamente · Deine Gene · Für deinen Arzt · Alle Medikamente
(+ Detailseite). Navigation ist gruppiert in ÜBERSICHT / DEINE DATEN / DATENBANK.

---

## 5. Festgelegte Konventionen

Diese Punkte hat Daniel entschieden. Nicht ohne Rücksprache ändern.

**Sprache**
- Durchgehend Du-Form, Lisa wird direkt angesprochen.
- „Deine Medikamente" (nicht „Meine"), Arbeitsflächen-Überschrift „Lisa, das sind **deine**
  Medikamente".
- Der kritische Zustand heißt **ALARM**, nicht „Warnung". Stufen: ALARM / Achtung / OK.
- Metabolisierertypen deutsch mit englischem Kürzel als Zusatz:
  Langsamer (PM) · Intermediärer (IM) · Normaler (NM) · Ultraschneller (UM).
- Kein Fachbegriff ohne Erklärung — jeder hat ein Fragezeichen-Popup daneben.

**Darstellung**
- **Eine** Kartengröße überall: `--cardw: 352px`, identische Innenmaße in Dashboard,
  Datenbank, Suche, Lisas Liste, Detailseite und Modal.
- Aufklapp-Pfeil unten rechts in der Karte, Herz-Button oben rechts.
- Gen-Karten mit Pastellhintergrund je Zustand, Metabolisierertyp in 14 px fett.
- Gene überall sortiert: langsam → intermediär → normal → ultraschnell.
- Mindestschriftgröße 11 px in der PC-Ansicht.
- Vorlage ist das GENESAFE-RX-Design: weiße Boxen, keine farbige Linie links an den
  Karten, Status rechts mit Wort darunter.
- Farben: Plum `#5E0047`, Ampel `#12A150` / `#E08000` / `#D02A2A`, Interaktionsrot `#D0021B`.

**Datei**
- Die HTML ist **reines ASCII**. Umlaute als HTML-Entities (`&auml;` usw.). Grund: ein
  Zeichensatzproblem hatte früher „TOXIZITÄT" zu „TOXIZITÃ¤T" gemacht. Nach jeder Änderung
  prüfen: `sum(1 for c in s if ord(c)>127)` muss 0 sein.

---

## 6. Fallstricke, die schon Zeit gekostet haben

1. **SVG-Symbole mit Verlauf** — `url(#…)`-Verweise auf Verläufe oder Filter funktionieren
   in einem versteckten `<symbol>` **nicht**. Nur Volltonfarben verwenden. Hat zweimal
   dazu geführt, dass Symbole unsichtbar waren.
2. **Browser-Cache** — ohne `?v=N` zeigt der Viewer die alte Datei, obwohl die neue
   korrekt geschrieben wurde. Zweimal falsch diagnostiziert.
3. **`clientWidth` ist 0**, wenn das Element noch nicht sichtbar ist → SVG-Breite 0 →
   keine Interaktionslinien. Stattdessen `getBoundingClientRect().width` mit Fallback.
4. **z-index über der SVG-Ebene** — der Kartencontainer lag über dem Interaktions-SVG und
   hat die Klicks abgefangen. SVG braucht höheren `z-index` **und** `pointer-events:none`,
   nur der Knopf fängt Klicks.
5. **TDZ bei `const`** — der Datenblock steht vor dem Rest des Skripts. Wer dort auf
   später deklarierte `const` zugreift, bekommt „Cannot access before initialization".
   Deshalb ist `DBSTATS()` eine Funktion mit `var`-Cache, keine sofort ausgewertete Konstante.
6. **Leistung bei 2.697 Karten** — alles auf einmal rendern kostet 2,9 s und 1,2 s pro
   Tastendruck. Lösung: `listSev` cachen + nur 120 Treffer zeigen mit Nachlade-Knopf.
   Jetzt 98 ms / 40 ms.
7. **Screenshots im Browser-Pane** schlagen fehl, wenn das Pane nicht sichtbar ist. Prüfen
   deshalb über `javascript_tool` mit `getBoundingClientRect`, `scrollWidth` vs
   `clientWidth`, `getComputedStyle` — das ist verlässlich und schneller.

---

## 7. Prüfroutine nach jeder Änderung

Über `javascript_tool` im laufenden Viewer, alle fünf Ansichten durchlaufen:

- horizontaler Überlauf: `scrollWidth - clientWidth` muss 0 sein
- keine Schrift unter 11 px
- keine rohen HTML-Entities oder `${…}` im sichtbaren Text
- Kartenkopf: Name, Statusblock, Herz und Pfeil dürfen sich nicht überlappen
- Konsolenfehler leer
- Interaktionsknopf anklickbar (`elementFromPoint` in der Knopfmitte)

---

## 8. Offene Punkte

**Markennamen (geprüft, entscheidungsreif)**
- `drug_products.csv` hat 6.424 Handelsnamen, ist aber **nicht** mit den Wirkstoffen
  verknüpft — die Junction-Tabelle ist im Sandbox leer (steht so im README des Exports).
- PharmGKB/ClinPGx liefert **keine** Markennamen.
- **openFDA NDC** (kostenlos, 137.402 Produkte, 27 MB) wurde getestet: 862 Wirkstoffe (32 %)
  bekommen einen Handelsnamen, davon **661 (25 %) eine echte Marke** — Plavix, Advil,
  Zocor, Celexa. Es fehlen Coumadin, Lopressor, Ultram (nicht mehr gelistet).
  → Das sind **US-Marken**. Für DACH gibt es keine freie Quelle (Austria-Codex,
  Rote Liste, mmi sind lizenzpflichtig).
- **Offen:** einbauen mit Kennzeichnung „US-Handelsname" oder auf DACH-Lizenz warten?
  Derzeit zeigen Karten ohne Marken das Anwendungsgebiet aus ATC-Ebene 2.

**Falsche Typbezeichnung bei drei Genen**
VKORC1, ABCB1 und G6PD tragen im Demo-Datensatz einen Metabolisierertyp, obwohl sie keine
abbauenden Enzyme sind. Der Klartext-Satz erfindet dort nichts mehr (er verweist auf die
Bewertung), aber die Typbezeichnung auf der Karte bleibt fachlich falsch, bis die echte
Phänotyp-Spalte vorliegt.

**Zahlen der Legende**
Daniels Vorgabe war 2.655 / 2.144 / 133 / 249; die Summe ergibt 2.526, es fehlen 129.
Die App zeigt jetzt die tatsächlich berechneten Werte (2.697 / 2.408 / 223 / 66), damit
Legende und Filterergebnis übereinstimmen. Zu klären, woher Daniels Zahlen stammen.

**Noch nicht gebaut**
- Phänokonversion (CYP-Hemmer verschiebt den genetischen Phänotyp eine Stufe) — war
  ursprünglich geplant, wurde von Daniel gestrichen.
- Mehrsprachigkeit.
- Echte Patientendaten statt der Demo-Genotypen.

---

## 9. Änderungsverlauf

| Version | Was |
|---|---|
| v13 | Gen-Karten aufklappbar mit Star-Allelen, eine Spalte mit Interaktionssortierung |
| v24 | Arztseite als PC-Ansicht, persönliche Einleitung, 9 Erklär-Popups, Du-Form |
| v27 | Dreispaltige Liste, ALARM statt Warnung, Herz-Button, Ampelfilter |
| v30 | 2.697 echte Wirkstoffe aus den Novogenia-Quelldateien |
| v41 | 5.273 Wechselwirkungen aus DrugBank, Alternativen über ATC-Ebene 4 |
| v45 | Arztbericht mit Gen-Karten, Pastell-Genkarten, halbe/halbe Aufteilung |
| v47 | Einleitung mit hervorgehobenen Kennzahlen und Verteilungsbalken |
| v49 | „Alternativen" ehrlich umbenannt, ATC-Pfad sichtbar, Sammelgruppen gekennzeichnet |


---

## 10. Datenquellen — Rechercheergebnis 2026-07-28

Vollständiger Bericht: `PGx_Datenquellen_Recherche_2026-07-28.md`
(52 Agenten, 115 Quellen, 25 nach Gegenprüfung bestätigt, 15 korrigiert).

### Was die Alternativen-Frage löst

**MED-RT** (Bulk-XML, 2,56 MB, monatlich, 0 EUR) bzw. dieselben Daten live über
**RxClass/RxNav**. Die Relationen `may_treat` + `may_prevent` gruppieren nach *Indikation*
statt nach Substanzklasse. Selbst geprüft: Aspirin bekommt dort 4 ATC-Codes, und die
Rückfrage „wer verhindert Hirninfarkt" liefert exakt Aspirin, Clopidogrel, Prasugrel.
**Beide Relationen zusammen auswerten** — Clopidogrel hat `may_treat` = 0, aber 3× `may_prevent`.

> Achtung: RxClass ist **nicht** lizenzfrei. Es ist die eine Ausnahme in den
> NLM-Nutzungsbedingungen (SNOMED-Affiliate-Lizenz), Attributionssatz Pflicht, 20 req/s.

Ergänzend: **DrugCentral** (CC BY-SA 4.0, kommerziell erlaubt) für SNOMED-kodierte Indikationen
und Kontraindikationen als Negativfilter; **Open Targets** (CC0, einzige Quelle ohne
ShareAlike-Risiko) für die EFO/MONDO-Krankheitshierarchie.

Nicht brauchbar: FDA Orange Book Therapeutic Equivalence (per Definition nur wirkstoffgleich),
aut idem / § 129 SGB V (dito), DrugBank (CC BY-NC), KEGG (kommerziell gesperrt).

**DACH-Lücke:** Metamizol, Piritramid, Flupirtin, Tilidin, Benzbromaron, Molsidomin und
Trimetazidin haben in MED-RT einen ATC-Code, aber **null** Indikationsrelationen.
Für die braucht es einen Fallback.

### Was die Rohdaten-Frage löst

- `api.pharmgkb.org` ist **abgeschaltet** (DNS NXDOMAIN). Alles läuft über `api.clinpgx.org/v1`.
- `clinicalAnnotations.zip` ist seit 2025-07-05 eingefroren, Nachfolger `summaryAnnotations.zip`.
  Deckt sich mit der eigenen Messung: alle anderen ZIPs tragen 2026-07-05.
- Change-Detection: `GET https://api.clinpgx.org/v1/data/file/data/?view=min` liefert
  fileName / lastModified / size für alle 118 Dateien. Releases erscheinen monatlich am 5.
- **CPIC ist die bessere Quelle als ClinPGx**: CC0 statt CC BY-SA plus Verkaufsverbot, und
  besser strukturiert. SQL-Dump `https://files.cpicpgx.org/data/database/cpic_db_dump.sql.gz`
  (3,8 MB). API nur zum Entwickeln, im Verkaufsprodukt den Dump verwenden.
- **Lizenz-Blocker ClinPGx**: *„Under no circumstances can ClinPGx data be sold for other's
  private or commercial use"* — wörtlich in der LICENSE.txt jedes ZIP.
- **`drug_interactions.csv` ist nicht nachbaubar.** Quelle DrugBank, CC BY-NC, akademische
  Downloads derzeit komplett pausiert. Kein gleichwertiger freier Ersatz gefunden.
  Einzig sauberer Eigenbau: openFDA `drug/label`, Feld `drug_interactions` (CC0) — Fließtext,
  Extraktion wäre ein eigenes Teilprojekt.

### Fallstricke für die Pipeline (alle konkret aufgetreten)

- `byRxcui` filtert mit **`relas`** (Plural), nicht `rela` — sonst still falsche Ergebnisse.
- Cloudflare blockt den Standard-User-Agent von Python `urllib` mit HTTP 403. Echten UA setzen.
- ClinPGx-Wirkstoffnamen sind case-sensitiv: `name=Aspirin` → 404, `name=aspirin` → 200.
- DrugCentral-API macht Substring-Matching: `indication` trifft auch `contraindication`.
  Deshalb Dump statt API.
- ChEMBL und Open Targets mischen Studienindikationen unter die zugelassenen — auf Phase 4 filtern.
- `api.pharmgkb.org` stirbt mit DNS-Fehler, nicht mit HTTP-Status — fällt in Cronjobs stumm aus.

### Anzufragen (bei keinem kommerziellen Anbieter ist ein Preis öffentlich)

ABDATA / Avoxa (info@abdata.de) · WHOCC Oslo (whocc@fhi.no, wegen ATC-Anzeige in einer
kommerziellen App) · WIdO (ai@wido.bv.aok.de) · ClinPGx Non-Academic License (api@clinpgx.org) ·
KNMP · BASG · DrugBank Sales.

### Juristisch zu bewerten

ShareAlike-Verträglichkeit bei Quellenmischung (DrugCentral CC BY-SA 4.0 und ChEMBL
CC BY-SA 3.0 Unported sind **nicht** aufwärtskompatibel) · ATC-Ausgabe in der App generell ·
CPIC-ToU „research purposes" gegen CC0.
