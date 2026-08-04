# GENE-IUS PGx — Projektdokumentation

**Stand:** 2026-07-30 · **Version:** v58 · **Status:** Clickdummy mit echtem PharmCAT-Genprofil, lauffähig

**Repository:** `origin` ist seit 2026-07-30 Azure DevOps —
`https://novogenia@dev.azure.com/novogenia/BusinessVibeCodes/_git/pharmacogenetics`
(Vorgabe von Nick Wassermann, IT). Das alte GitHub-Remote heißt lokal `github` und
bespielt weiterhin die öffentliche Testseite; es wird **nicht** automatisch mitgepusht.

Diese Datei ist die Übergabe- und Arbeitsdoku. Sie wird bei jeder größeren Änderung
fortgeschrieben. Wenn etwas hier steht, ist es geprüft — Vermutungen sind als solche
gekennzeichnet.

---

## 0. Schnellstart auf einem neuen Rechner

**Lies zuerst diesen Abschnitt, dann §6 (Fallstricke) und §11 (PharmCAT).**
Der Rest ist Nachschlagewerk.

### Was das ist, in drei Sätzen

GENE-IUS PGx ist ein Clickdummy für eine Pharmakogenetik-App: eine einzige
HTML-Datei ohne Build-Schritt, die 2.697 Wirkstoffe gegen ein echtes Genprofil
bewertet. Das Genprofil kommt aus einem PharmCAT-3.2.0-Lauf, die
Wirkstoff-Empfehlungen aus PharmCATs Reporter (CPIC/DPWG/FDA) plus Novogenias
eigener Leitlinienmatrix. Es ist ein Prototyp zur Abstimmung mit Daniel, kein
Produkt.

### Repository

```
git clone https://novogenia@dev.azure.com/novogenia/BusinessVibeCodes/_git/pharmacogenetics C:\dev\gene-ius-pgx
```

`origin` = **Azure DevOps** (verbindlich, Vorgabe von Nick Wassermann/IT).
`github` = `github.com/evolutionnext696-prog/gene-ius-pgx` — speist nur die
öffentliche Testseite [evolutionnext696-prog.github.io/gene-ius-pgx](https://evolutionnext696-prog.github.io/gene-ius-pgx/).
Beim Pushen **beide** bedienen, sonst friert der Testlink ein:

```
git push origin main
git push github main
```

Git-Operationen über **cmd-Batchdateien**, nicht PowerShell — PowerShell kehrt
bei git zu früh zurück und schlägt still fehl.

### Was im Repo liegt

| Pfad | Inhalt |
|---|---|
| `index.html` | die komplette App, 685 kB, rein ASCII, kein Build |
| `docs/DOKUMENTATION.md` | diese Datei |
| `docs/DATENQUELLEN_RECHERCHE.md` | 52-Agenten-Recherche zu Alternativ- und Interaktionsquellen |
| `tools/build_pharmcat.py` | erzeugt `pharmcat_profil.js` aus einem PharmCAT-Lauf |
| `tools/build_pgx_data.py` | erzeugt `pgx_data.js` aus den Novogenia-Excels |
| `tools/resplice.py` | tauscht den Datenblock zwischen den Markern in `index.html` |
| `tools/patch_pharmcat*.py` | die angewandten Umbauten, chronologisch — dokumentieren das Wie |
| `tools/01_*.py` … `07_*.py` | Datenpipeline (RxNorm, MED-RT, Lückenanalyse, Risikoklassen) |
| `data/*.json` | die Ergebnisse dieser Pipeline, **noch nicht in der App verdrahtet** |

### App ansehen

`index.html` ist eine einzelne Datei ohne Abhängigkeiten — im Browser öffnen
genügt. Für die Prüfroutine (§7) einen statischen Server auf dem Ordner starten.

### Daten neu erzeugen

Nur nötig, wenn eine andere Probe oder aktualisierte Quelldaten hinein sollen.

```
python tools/20_entpacken.py            # PharmCAT-Archiv entpacken + Kohortenübersicht
python tools/build_pharmcat.py NA17454  # -> pharmcat_profil.js
python tools/resplice.py                # in index.html einsetzen
```

Voraussetzungen auf dem neuen Rechner:

1. **PharmCAT-Validierungsdaten.** SharePoint `sites/IT` in OneDrive
   synchronisieren, dann liegt der Ordner unter
   `Novogenia GmbH\IT - Dokumente\General\PharmCAT Validation 20260730\`.
   **Nur so** — Browser-Downloads, Blob-Downloads und POST an `localhost`
   werden alle unterdrückt, Graph lehnt `application/x-gzip` ab, und
   Konsolenausgaben werden bei ~1 kB abgeschnitten.
2. **Novogenia-Quellexcels** unter
   `AI RESOURCES - Dokumente\PHARMACOGENETICS\` (All Drugs V12,
   Pharmgkb drug recommendations V4, drugs_master.csv, drug_pharmacogenetics.csv,
   drug_interactions.csv).
3. `pip install openpyxl`

### Die drei Regeln, die nicht verhandelbar sind

1. **Nichts erfinden.** Kein geratener Genotyp, keine erfundene Zahl. Was
   PharmCAT nicht ruft, bleibt sichtbar „nicht bestimmbar". Eine sichtbare
   Lücke ist harmlos, eine erfundene Variante nicht — darauf würde eine
   Dosierung aufgebaut.
2. **Die Datei bleibt rein ASCII.** Umlaute als HTML-Entities. Jedes
   Generator- und Patch-Skript prüft das am Ende.
3. **Ersetzungen mit Zusicherung.** Nie `s.replace()` ohne zu prüfen, dass der
   Anker genau einmal vorkommt **und im richtigen Bereich liegt** (`<style>`
   vs. `<script>`). Beide Fehler sind hier schon passiert, siehe §6.

### Demo-Proben: was öffentlich darf

Von den 40 Proben der Kohorte sind `HG*` und `NA*` öffentliche GIAB/Coriell-
Referenzgenome — für Clickdummys und den öffentlichen Testlink unbedenklich.
`N8A*`, `XA25*`, `XH1M*`, `XT2M*` sind **echte Kunden** und gehören nie in eine
Demo oder ein öffentliches Repo. Aktuell eingebaut: **NA17454** (Coriell).

### Stand und was als Nächstes ansteht

Fertig und live: echtes Genprofil, PharmCAT-Empfehlungen als erste
Bewertungsquelle, vierter Status „Offen", Arztbericht mit Abdeckungsnachweis,
alphabetische Liste, Sub-Bewertungen aus dem Implikationstext, alle 611
gelesenen Varianten.

Offen, in dieser Reihenfolge sinnvoll:

1. **Bedingte Alternativen herunterstufen.** PharmCAT setzt
   `alternateDrugAvailable` auch bei „…*falls* mehr nötig, Alternative erwägen"
   (Fluvastatin). Die Karte zeigt dann ALARM bei normaler Wirkung und normalem
   Risiko. Daniel wurde darauf hingewiesen, Entscheidung steht aus.
2. **CYP3A5-Lücke in der Novogenia-Matrix.** Für `POOR` fehlt die Zeile,
   obwohl das der häufigste europäische Genotyp ist (30 von 40 in der Kohorte)
   und CPIC eine Empfehlung hat.
3. **`data/*.json` verdrahten** — Handelsnamen (1.216), Alternativen (1.533),
   Interaktionen (1.852), Risikoklassen (QT 115, anticholinerg 151,
   hepatotox 207). Alles gebaut, nichts davon in der App. Für die Risikoklassen
   gilt: QT paarweise ist zulässig, anticholinerge Last und Hepatotoxizität
   müssen **kumulativ** modelliert werden, nicht als 19.171 Paare.
4. **Warfarin-Dosisformel.** Die Matrix hat dafür Dosisbereiche statt
   Phänotypen (`0.5-2`, `3-4`, `5-7` mg/Tag) — eine Formel aus CYP2C9 und
   VKORC1, noch nicht umgesetzt.
5. **198 Lückenwirkstoffe** aus `data/luecke_prio.json` recherchieren. Beim
   ersten Versuch nur 22 bearbeitet, weil eine gekürzte Liste hartkodiert war;
   außerdem war die Gegenprüfung zu streng und hat 21 von 22 an Kleinigkeiten
   verworfen. Beides beim nächsten Lauf anders machen.

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
| v56 | Umstellung auf Hristos PharmCAT-3.2.0-Lauf (40 Proben), Reporter-Stufe mit 168 CPIC/DPWG/FDA-Empfehlungen, Ampel aus PharmCATs eigenen Flags, Probe NA17454 |
| v57 | Liste alphabetisch, Sub-Bewertungen aus dem Implikationstext statt aus dem Prodrug-Schalter, alle 611 gelesenen Varianten unter „Deine Gene" |


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

---

## 11. PharmCAT als Quelle der Gendaten (ab v56)

### Woher die Daten kommen

Quelle ist Hristos Validierungslauf, lokal über die OneDrive-Synchronisierung von
`sites/IT`:

```
Novogenia GmbH\IT - Dokumente\General\PharmCAT Validation 20260730\
```

| Datei | Inhalt |
|---|---|
| `pharmcat-v3.2.0-40-sample-assay-enriched-reports.tar.gz` | 11,7 MB → 182 MB, 407 Dateien, alle 40 Proben |
| `cohort_summary.json` | pro Probe: Sentrix-ID, S3-Quelle, CYP2D6-Outside-Call, fehlende Positionen |
| `README.md` | Hristos Protokoll: Assay-Overlay, SHA-256-Nachweise, Vorgehen |
| `cyp2d6_outside_call_provenance.tsv` | Herkunft der fünf GeT-RM/Coriell-Diplotypen |

Pro Probe liegen im Archiv `<Probe>.match.json`, `.phenotype.json`,
**`.report.json` (1,86 MB)**, `.report.html`, `.report.tsv` und die vorverarbeitete VCF.

**Die `.report.json` ist der entscheidende Unterschied** — das ist die Reporter-Stufe.
PharmCAT läuft in drei Schritten: Named Allele Matcher → Phenotyper → **Reporter**.
Nur der Reporter erzeugt Wirkstoff-Empfehlungen. In den Dateien, die zuerst vorlagen,
fehlte er (`relatedDrugs` überall leer, kein `drugReports`), deshalb kam die erste
Fassung ohne PharmCAT-Empfehlungen aus. Wer künftig nur die Phenotyper-Ausgabe
bekommt: der Reporter braucht keinen Neulauf, `pharmcat -reporter -ri <phenotype.json>
-reporterJson` genügt.

### Erzeugung

```
python 20_entpacken.py            # Archiv entpacken + Kohortenübersicht
python build_pharmcat.py NA17454  # -> pharmcat_profil.js
python resplice.py                # Block zwischen die Marker in die HTML
```

Der Probenname ist Argument — jede der 40 Proben lässt sich einsetzen.

### Die gewählte Probe

**NA17454**, Sentrix `208475230023_R11C02`, GRCh38.p14, PharmCAT 3.2.0,
Allel-Definitionen ClinPGx `2026-02-09-10-28`.

Ein **öffentliches Coriell-Referenzgenom**, kein Kunde — damit ist die App auch in
einem öffentlichen Repository unbedenklich. Von den 40 Proben sind `HG*` und `NA*`
Referenzgenome (GIAB/Coriell), `N8A*`, `XA25*`, `XH1M*`, `XT2M*` echte Kunden.
Für Demos ausschließlich Referenzgenome verwenden.

Gewählt wurde NA17454, weil sie die meisten auffälligen Gene hat (8) und einen
CYP2D6-Outside-Call:

| Gen | Diplotyp | Phänotyp |
|---|---|---|
| ABCG2 | rs2231142 T/T | Poor Function |
| CYP2B6 | \*1/\*6 | Intermediär |
| CYP2C9 | \*1/\*8 | Intermediär (AS 1,5) |
| **CYP2D6** | **\*1x2/\*2x2** | **Ultraschnell (AS 4,0)** — Outside-Call |
| CYP3A5 | \*1/\*3 | Intermediär |
| NAT2 | | Intermediär |

611 Positionen gelesen, 437 fehlend = **58 % Abdeckung**, 27 VCF-Warnungen.

### Was die Kohorte über die Datenqualität sagt

| Gen | bestimmt | Verteilung |
|---|---|---|
| ABCG2, CACNA1S, CFTR, CYP2B6, CYP2C9, CYP3A5, DPYD, G6PD, NAT2, NUDT15, RYR1, SLCO1B1, TPMT, VKORC1 | 40/40 | |
| CYP2C19 | 38/40 | Normal 14, Intermediär 11, Rapid 11, Poor 2 |
| CYP3A4 | 38/40 | Normal 38 |
| **CYP2D6** | **5/40** | nur über Outside-Calls |
| UGT1A1 | 17/40 | Indeterminate 23 |
| CYP4F2, HLA-A, HLA-B, IFNL3, MT-RNR1 | 0/40 | |

**CYP2D6 ist die einzige echte Lücke, und sie ist bauartbedingt.** PharmCAT 3.2.0 ruft
CYP2D6 grundsätzlich **nicht** aus VCF-SNP-Genotypen; es akzeptiert nur einen
Outside-Call. Hristos README nennt den Grund: eine Neun-Locus-Teilpanel reicht nicht
für Kopienzahl, Strukturvarianten und Tandems. Fünf Proben haben deshalb
authoritative GeT-RM/Coriell-Calls: NA20296 `*1/*2`, HG01190 `*68+*4/*5`,
NA17454 `*1x2/*2x2`, NA06989 `*9/*9`, NA18868 `*2/*5`.

Bemerkenswert: **CYP3A5 Poor Metabolizer bei 30 von 40** — das ist der in Europa
häufigste Genotyp und braucht bei Tacrolimus die Standarddosis.

### Korrektur eines früheren Befunds

Eine erste Analyse der drei Dateien aus dem Download-Ordner (PharmCAT 2.0.0-Matcher,
ältere VCF) ergab, dass mehrere leitlinienrelevante Positionen als `./.` No-Call im
VCF standen — darunter DPYD \*2A, \*13 und c.2846A>T, NUDT15 \*3, CYP2C19 \*17 und
VKORC1 rs9923231. Das wäre gefährlich gewesen, weil PharmCAT trotzdem
„Normaler Metabolisierer" meldet.

**In den am 2026-07-29 neu erzeugten VCFs sind alle diese Positionen gelesen.**
Abdeckung 43 % → 58 %, VCF-Warnungen 204 → 27. Der Befund gilt nur für die alte
Datei; die Pipeline ist bereits repariert. Die Lehre bleibt trotzdem gültig:
Ein `*1/*1` heißt nur „keine der **gelesenen** Varianten gefunden" — welche gelesen
wurden, gehört in den Arztbericht.

### Wirkstoff-Empfehlungen aus dem Reporter

Für NA17454: **168 Annotationen zu 94 Wirkstoffen**, davon 75 CPIC, 57 DPWG,
13 FDA-Beipackzettel, 23 FDA-Assoziationen. **80 der 94 lassen sich der
Wirkstoffdatenbank zuordnen.** Die 14 übrigen (Ivacaftor, Rasburicase, Succinylcholin,
Tafenoquin, Eliglustat, Mavacamten …) stehen nicht in `All Drugs V12`.

**Die Ampelstufe kommt aus PharmCATs eigenen Feldern, nicht aus einer Textdeutung:**

| Feld | Stufe | Anzahl bei NA17454 |
|---|---|---|
| `alternateDrugAvailable` | ALARM | 44 |
| `dosingInformation` oder `otherPrescribingGuidance` | ACHTUNG | 37 |
| keins davon | OK | 87 |

Wichtig: **`classification` taugt nicht als Ampel.** 25 der 38 mit *Strong*
klassifizierten Annotationen sind Strong-Empfehlungen, *nichts* zu tun
(„No reason to avoid based on G6PD status", „Initiate therapy with recommended
starting dose").

Bei mehreren Quellen zu einem Wirkstoff gewinnt die schärfste Stufe, bei Gleichstand
CPIC vor DPWG vor FDA-Label vor FDA-Assoziation. **Alle Zeilen bleiben sichtbar** —
Quellen können sich unterscheiden, und das wird nicht geglättet.

### Namenszuordnung — ein Stolperstein

Die Schlüssel in `DRUGS` sind uneinheitlich: Demo-Wirkstoffe haben deutsche Schlüssel
(`codein`), die 2.697 aus der Datenbank synthetische (`w127`) mit englischem
Anzeigenamen. PharmCAT nennt Wirkstoffe englisch und klein.

Der erste Versuch, über die Schlüssel zuzuordnen, traf **11 von 94**. Richtig ist ein
Namensregister (`Anzeigename klein → Schlüssel`) plus `ALIAS` in der Gegenrichtung,
wobei die deutsche Demo-Karte Vorrang hat, damit sich die Bewertung nicht auf zwei
Karten desselben Wirkstoffs aufteilt. Verbundpräparate stehen als `a / b / c` und
werden je Bestandteil aufgelöst. Damit: **80 von 94**.

### Reihenfolge, in der bewertet wird

1. **PharmCAT-Empfehlung** für diesen Wirkstoff → Stufe und Wortlaut aus der Quelle.
2. Novogenias Leitlinienmatrix `P_REC`, wenn **alle** Genbedingungen zutreffen.
3. Es gibt Zeilen, aber ein nötiges Gen ist nicht bestimmbar → **Offen**, mit Grund.
4. Rückfall `recForFallback` aus dem Wirkstoff-Datenblock (nur bei `lvl >= 0`
   auf beiden Seiten, siehe Fallstrick 11).
5. Sonst die Heuristik über Hauptgen und Prodrug-Logik.

Ergebnis über die 2.697 Wirkstoffe: **2.500 OK, 170 Achtung, 27 Alarm.**
Zum Vergleich das erste, fast normale Profil: 2.578 OK, 0/0, 119 offen.

Stichproben: Codein **ALARM** (alle vier Quellen einig, CPIC *Strong*: „Avoid codeine
use because of potential for serious toxicity"), Clopidogrel **OK**
(„use at standard dose (75 mg/day)", CYP2C19 \*1/\*1), Warfarin **ACHTUNG**
(„use 65 % of the standard initial dose").

### Die vier Sub-Bewertungen

Amitriptylin stand auf ALARM, darunter viermal „Normal". Zwei Ursachen, beide behoben:

1. `statusFor` setzte bei einer PharmCAT-Empfehlung `lvl` fest auf 2, und `metrics()`
   verzweigt über `lvl`. Jetzt kommt `lvl` aus dem Genotyp, auf den sich die Empfehlung
   bezieht (bei mehreren Genen das am stärksten abweichende).
2. Der Prodrug-Schalter aus `All Drugs V12` reicht nicht. Amitriptylin und Codein sind
   beide CYP2D6-ultraschnell, aber bei Codein entsteht **mehr** Wirkstoff (Morphin →
   Toxizität), bei Amitriptylin **weniger** (Wirkungsverlust). Der Unterschied steht nur
   im Implikationstext, nicht im Genprofil.

Die Boxen werden deshalb aus dem **Implikationstext der maßgeblichen Annotation**
abgeleitet — der, die auch die Ampel bestimmt, nicht aus allen Quellen zusammengemischt.
Die Texte von CPIC und DPWG sind formelhaft (`less active`, `lower plasma`,
`increased formation`, `higher risk`, `typical risk`), erkannt wird an Wortgruppen.
Was der Text nicht hergibt, wird **weggelassen** statt grau angezeigt; die Box
**Handlung** (aus den Flags) und **Grundlage** (der Genotyp) stehen immer.

Nebenbefund: bei ultraschnellem Abbau stand vorher generell „Wirkung: Verstärkt".
Das gilt nur für Prodrugs — ein normaler Wirkstoff ist dann zu schnell weg und wirkt
**zu schwach**. War ein alter Fehler in `metrics()`.

Offene Feinheit: `alternateDrugAvailable` setzt PharmCAT auch bei bedingten Formulierungen
(Fluvastatin: „≤40 mg/Tag; *falls* mehr nötig, Alternative erwägen"). Die Karte zeigt
dann ALARM, obwohl Wirkung und Risiko normal sind. Der Wortlaut steht darunter.

### Reihenfolge in der Liste

Alphabetisch, nicht mehr nach Schweregrad. Sonst sieht man auf der ersten Seite nur
ALARM und bekommt kein Gefühl für das Verhältnis. Der Arztbericht behält die Sortierung
nach Dringlichkeit — dort ist genau das der Zweck.

### Die 611 Einzelvarianten

Unter „Deine Gene" stehen alle gelesenen Positionen, je Gen aufklappbar, mit rsID,
Genotyp und Link zu dbSNP. Sie ergeben für sich genommen keinen Metabolisierertyp —
sie sind die Bausteine, aus denen der Diplotyp zusammengesetzt wird. Aufgeführt, weil
sie belegen, was geprüft wurde. Verteilung: G6PD 146, RYR1 90, DPYD 78, CFTR 61,
CYP2C9 52, TPMT 38, CYP2C19 29, SLCO1B1 25, CYP2B6 24, NAT2 24, CYP3A4 23, CYP3A5 5,
CYP4F2 4, UGT1A1 4, NUDT15 3, CACNA1S 2, ABCG2 1, IFNL3 1, VKORC1 1.

### Vierter Zustand „Offen"

Bleibt unverändert in Kraft (`unk`, grau, `RANK` zwischen OK und Achtung) — er greift
jetzt seltener, weil mehr Gene bestimmt sind, ist aber für CYP4F2, HLA-A/B, IFNL3,
MT-RNR1 und UGT1A1 weiterhin nötig.

Grundregel: **kein geratener Genotyp.** Eine sichtbare Lücke ist harmlos, eine
erfundene Variante nicht — darauf würde eine Dosierung aufgebaut.

### Datentransport — was nicht funktioniert hat

Falls das Archiv nochmal aus SharePoint geholt werden muss: über die
Browser-Automatisierung geht es **nicht**. Datei-Download über `download.aspx`,
Blob-Download und POST an `http://localhost` werden alle unterdrückt oder
abgebrochen, und Konsolenergebnisse werden bei etwa 1 kB abgeschnitten. Der Graph-
Zugriff lehnt `application/x-gzip` ab. Funktioniert hat: den SharePoint-Ordner in
OneDrive synchronisieren und lokal lesen.

---
