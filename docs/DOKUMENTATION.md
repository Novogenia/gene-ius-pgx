# GENE-IUS PGx — Projektdokumentation

**Stand:** 2026-07-30 · **Version:** v55 · **Status:** Clickdummy mit echtem PharmCAT-Genprofil, lauffähig

**Repository:** `origin` ist seit 2026-07-30 Azure DevOps —
`https://novogenia@dev.azure.com/novogenia/BusinessVibeCodes/_git/pharmacogenetics`
(Vorgabe von Nick Wassermann, IT). Das alte GitHub-Remote heißt lokal `github` und
bespielt weiterhin die öffentliche Testseite; es wird **nicht** automatisch mitgepusht.

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

8. **Anker, die nur einmal vorkommen, aber an der falschen Stelle** — der Abdeckungs-CSS-Block
   wurde an `/* ================= ERKL` gehängt. Der String kam genau einmal vor — aber im
   **JavaScript**, nicht im Stylesheet. Das ganze Skript hat danach nicht mehr geparst
   („Unexpected token '.'"), und zwar **ohne Konsolenmeldung**, weil ein Parse-Fehler im
   Inline-Skript nicht in der MCP-Konsolenausgabe landet. Diagnose: HTML per `fetch` holen,
   Skript herausschneiden, `new Function(src)` in einer binären Suche über die Zeilenzahl.
   Konsequenz: eine Zusicherung auf die **Anzahl** der Treffer reicht nicht, der **Ort**
   muss mitgeprüft werden (`style`-Bereich vs. `script`-Bereich).
9. **Zwei Bedingungen, nur eine geprüft** — 14 der 103 Leitlinienzeilen verlangen
   CYP2C19 **und** CYP2D6 gleichzeitig. Der erste Abgleich prüfte nur `GENE(1)` und
   meldete drei Amitriptylin-Treffer, die in Wirklichkeit CYP2D6 voraussetzen. Bei
   Mehr-Gen-Zeilen müssen **alle** Bedingungen erfüllt sein.
10. **„Uncertain Susceptibility" ist ein Ergebnis, keine Lücke** — bei RYR1 und CACNA1S
   heißt das: *keine bekannte Risikovariante gefunden*. Wer das als „nicht bestimmbar"
   führt, macht aus einem beruhigenden Befund eine Wissenslücke. Gleiches gilt für
   CFTR („spricht nicht auf Ivacaftor an").
11. **Stufe −1 bedeutet in zwei Datensätzen Verschiedenes** — im Wirkstoff-Datenblock
   `D_REC` heißt −1 „Sondergenotyp" (z. B. `*28/*28`), im Genprofil „nicht bestimmbar".
   Der Rückfall-Matcher muss `lvl >= 0` auf beiden Seiten fordern, sonst greift eine
   Sondergenotyp-Empfehlung bei einem Gen ohne Ergebnis.

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

**Falsche Typbezeichnung bei Nicht-Enzym-Genen — erledigt**
Behoben mit v55: G6PD heißt jetzt „Kein G6PD-Mangel" statt „Normaler Metabolisierer",
SLCO1B1/ABCG2 bekommen Transportfunktions-Begriffe, RYR1/CACNA1S/CFTR zeigen statt der
Metabolisierer-Skala eine Befundzeile. ABCB1 und CYP1A2 fallen weg — sie sind nicht Teil
des PharmCAT-Panels (keine CPIC-Gene).

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
| v52 | Leitlinien-Inhalte in einer Box, Genkarten-Umbrüche, Interaktionsknopf-Hover (`transform-box:fill-box`) |
| v55 | Echtes PharmCAT-Genprofil (23 Gene) statt Demo-Genotypen, vierter Status „Offen", Leitlinien-Matrix mit Mehr-Gen-Logik, Abdeckungsblock im Arztbericht |


---

## 11. PharmCAT als Quelle der Gendaten (ab v55)

### Woher die Daten kommen

Drei Dateien aus dem Download-Ordner:

| Datei | Inhalt |
|---|---|
| `pharmcat.match (1).json` | gerufene und fehlende Positionen je Gen, Diplotyp-Kandidaten |
| `pharmcat.phenotype (1).json` | Diplotyp, Phänotyp, Aktivitätsscore, Allelfunktionen je Gen |
| `pharmcat.report (1).tsv` | dieselbe Information flach, nur zur Gegenkontrolle verwendet |

`build_pharmcat.py` erzeugt daraus `pharmcat_profil.js` (49 kB, rein ASCII),
`resplice.py` tauscht den Block zwischen den Markern
`/* ===== BEGIN PHARMCAT PROFIL … */` … `END` in die HTML.

**Wichtig:** `relatedDrugs` ist in dieser `phenotype.json` überall leer und es gibt keine
`drugReports` — der Reporter-Schritt von PharmCAT wurde nicht gelaufen. Die
Wirkstoff-Bewertungen kommen deshalb aus Novogenias eigener Matrix, nicht von PharmCAT.

### Die Probe

`sampleId 208491470165_R06C01` — Format eines **Illumina-BeadChip-Barcodes** mit Position,
also Array-Genotypisierung, keine Sequenzierung. Referenz GRCh38.p14, PharmCAT 2.0.0,
Allel-Definitionen ClinPGx 2025-11-05, Auswertung vom 2026-02-02.

**522 von 1.201 erwarteten Positionen sind vorhanden = 43,5 % Abdeckung.**
204 VCF-Warnungen, alle vom Typ `Ignoring: no call (./.)`.

### Ergebnis je Gen

| Zustand | Anzahl | Gene |
|---|---|---|
| eindeutig bestimmt | 14 | CACNA1S, CFTR, CYP2B6, CYP2C19, CYP2C9, CYP3A4, CYP3A5, DPYD, G6PD, NUDT15, RYR1, SLCO1B1, TPMT, UGT1A1 |
| mehrdeutig | 2 | CYP2D6 (30 Diplotyp-Kandidaten), NAT2 (88) |
| kein Ergebnis | 7 | ABCG2, CYP4F2, HLA-A, HLA-B, IFNL3, MT-RNR1, VKORC1 |

Auffällig ist genau **ein** Gen: **CYP3A5 \*3/\*3 = Langsamer Metabolisierer**. Das ist der
in Europa häufigste CYP3A5-Genotyp; CPIC sieht dafür bei Tacrolimus die **Standarddosis**
vor. Alle übrigen bestimmten Gene sind normal.

### Abgleich mit `Pharmgkb drug recommendations V4.xlsx`

Die Datei enthält **103 Zeilen für 43 Wirkstoffe**. Aufbau, den man kennen muss:

- 89 Zeilen mit einem Gen, **14 mit zwei Genen** (alle CYP2C19 + CYP2D6, alle Amitriptylin).
  Eine Zwei-Gen-Zeile gilt nur, wenn **beide** Phänotypen passen.
- Die unbenannten Spalten ab Index 15 enthalten den **Twig/Jinja-Template-Code** des
  Report Builders, z. B. `{% if CYP2C19Metabolizer == 'ULTRARAPID' and CYP2D6Metabolizer == 'POOR' %}`.
  Daraus wird die Ampelfarbe gezogen: `BG_COLOR_DRUG_RED` → ALARM,
  `BG_COLOR_DRUG_YELLOW` → ACHTUNG. **Alle 103 Zeilen haben eine Farbe: 83 rot, 20 gelb.**
  Damit kommt der Schweregrad aus der Quelle und nicht aus einer Heuristik.
- Vokabular: `EXTENSIVE` = normal (NM), `ULTRARAPID` = UM, `INTERMEDIATE` = IM, `POOR` = PM.
  Für Transporter schreibt das Spreadsheet ebenfalls POOR/INTERMEDIATE, PharmCAT dagegen
  `Poor Function`/`Decreased Function` — Äquivalenztabelle nötig (`PAEQ` in der App).
- Drei Sonderformen: **UGT1A1 `*28/*28`** und **VKORC1 `TT`** vergleichen den Diplotyp
  direkt, nicht den Phänotyp. **Warfarin** hat kein Gen in `GENE(1)`, sondern die
  Dosisbereiche `0.5-2`, `3-4`, `5-7` mg/Tag — eine Formel aus CYP2C9 + VKORC1, in der
  App noch nicht umgesetzt.
- CYP2C9 und DPYD liefern in PharmCAT als `lookupKey` den **Aktivitätsscore** („2.0"),
  nicht den Phänotyp. Der Phänotyp steht daneben in `phenotypes`. Immer `phenotypes`
  zuerst lesen, sonst schlägt der Abgleich fehl.

### Und das Ergebnis des Abgleichs

**Keine einzige der 103 Zeilen greift bei dieser Probe.** Aufgeschlüsselt:

| | Zeilen | Grund |
|---|---|---|
| nicht entscheidbar | 54 | CYP2D6 mehrdeutig (46 Zeilen + 14 Zwei-Gen-Zeilen), VKORC1 und HLA-B ohne Ergebnis |
| trifft nicht zu | 49 | das Gen ist bestimmt und normal — richtig, hier ist keine Anpassung nötig |
| trifft zu | 0 | — |

Das ist die fachlich richtige Antwort, nicht ein Fehler im Abgleich: das Profil ist
bis auf CYP3A5 unauffällig, und die zwei Gene, die etwas ergeben hätten, sind nicht rufbar.

**Folge für die Oberfläche:** 2.578 Wirkstoffe grün, **0 gelb, 0 rot**, 119 grau („Offen").
Die 119 sind die Wirkstoffe, deren Bewertung an CYP2D6, NAT2 oder VKORC1 hängt.

### Eine Lücke im Spreadsheet

**CYP3A5 hat nur Zeilen für EXTENSIVE und INTERMEDIATE.** Für **POOR** — also genau Lisas
Genotyp \*3/\*3 und den häufigsten in Europa — fehlt die Zeile. CPIC hat dafür eine
Empfehlung (Standarddosis Tacrolimus). Sollte ergänzt werden.

### Was diese Probe brauchbar machen würde

Vier der neun ungerufenen Gene hängen an **einer einzigen Position**:

| Gen | fehlende Position | Bedeutung |
|---|---|---|
| **VKORC1** | `rs9923231` | die Warfarin/Acenocoumarol-Position — Standardmarker auf praktisch jedem Array |
| ABCG2 | `rs2231142` | Rosuvastatin, Allopurinol |
| IFNL3 | `rs12979860` | Interferon-Ansprechen |
| CYP4F2 | `rs2108622` (von 19 fehlenden) | Vitamin-K-Umsatz, Warfarin-Dosis |

Bei **CYP2D6** sind 84 von 156 Positionen offen; alle 30 Kandidaten enthalten die seltenen
Allele **\*146** oder **\*148**, die nur an nicht gelesenen Stellen unterscheidbar sind.
Kopienzahl-Varianten (\*5-Deletion, Duplikationen) sind aus Array-Daten grundsätzlich nicht
rufbar — dafür braucht es einen Outside-Call (Astrolabe/StellarPGx) oder Sequenzierung.
HLA-A und HLA-B haben **0 Positionen** im VCF und brauchen ein eigenes Typisierungsverfahren.

### Wie die App damit umgeht

Vierter Zustand **„Offen"** (`unk`, grau, `RANK` zwischen OK und Achtung):

- Gen-Karte zeigt statt eines Metabolisierertyps „Nicht bestimmbar" **plus den Grund**
  („72 von 156 Stellen gelesen, 30 Kombinationen bleiben offen").
- Wirkstoff-Bewertung wird offen gelassen, wenn eine Leitlinie existiert, aber ein dafür
  nötiges Gen nicht bestimmt ist — mit dem konkreten Grund im Text.
- Eigener Filterknopf, eigene Legendenbox, eigene Kennzahl in der Einleitung.
- Der Arztbericht beginnt mit einem **Abdeckungsblock**: Probe-ID, Referenz, PharmCAT-Version,
  522 gelesene Stellen, 43 % Abdeckung, und einer Tabelle mit allen 23 Genen
  (Diplotyp, Phänotyp, Score, Stellen gelesen/erwartet, Status).

Grundregel: **kein geratener Genotyp.** Eine sichtbare Lücke ist harmlos, eine erfundene
Variante nicht — darauf würde eine Dosierung aufgebaut.

### Reihenfolge, in der bewertet wird

1. Leitlinienzeile aus `P_REC`, deren **sämtliche** Genbedingungen zutreffen →
   Text und Ampelfarbe aus der Quelle.
2. Es gibt Zeilen, aber ein nötiges Gen ist nicht bestimmbar → **Offen**, mit Grund.
3. Kein Eintrag in der Matrix → Rückfall auf `recForFallback` aus dem Wirkstoff-Datenblock
   (nur bei `lvl >= 0` auf beiden Seiten, siehe Fallstrick 11).
4. Sonst die bisherige Heuristik über Hauptgen + Prodrug-Logik.

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
