# GENE-IUS PGx — Projektdokumentation

**Stand:** 2026-08-07 · **Version:** v71 · **Status:** Clickdummy mit echtem PharmCAT-Genprofil **plus Demo-Genotypen**, lauffähig

> ⚠️ **Die Demo-Genotypen sind in der Oberfläche seit v70 nicht mehr als solche
> gekennzeichnet** (Ansage Daniel, 2026-08-06 — sie sollen wie reale Genotypen
> wirken). Welche Werte erfunden sind, steht nur noch hier, im Kopf von
> `data/dummy_genotypen.js` und in der Git-Historie. **Vor jeder Verwendung, bei
> der jemand die Zahlen für Messwerte halten könnte, müssen sie raus** — siehe
> §11, „Demo-Genotypen".

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
| `tools/30_rs_befunde.py` | erzeugt `rs_befunde.js` — rs-Nummern mit Studienhinweis, gegen die gelesenen Positionen geschnitten |
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

1. **Nichts erfinden.** Kein geratener Genotyp, keine erfundene Zahl. Eine
   erfundene Variante ist gefährlich — darauf würde eine Dosierung
   aufgebaut.
   > ⚠️ **Ausgesetzt seit v68 (2026-08-06), auf Ansage von Daniel.** Der
   > Clickdummy enthält **842 erfundene Genotypen in 482 Genen**, damit sich
   > die Ansicht mit vollständigen Rohdaten zeigen lässt. Sie sind an vier
   > Stellen als Demo gekennzeichnet — siehe §11, „Demo-Genotypen". Die 611
   > echten PharmCAT-Positionen sind unberührt. **Vor jeder Verwendung außerhalb
   > der internen Abstimmung müssen die Demo-Daten raus**: `data/dummy_genotypen.js`
   > löschen und `patch_pharmcat17.py` nicht anwenden, oder `DUMMY_AKTIV`
   > auf `false` setzen.
   *Präzisiert am 2026-08-05 (v61/v62):* Was PharmCAT nicht ruft, wird
   **nicht mehr angezeigt** (Vorgabe Daniel) — statt sichtbar „nicht
   bestimmbar" zu bleiben. Das gilt seit v62 auch für den Arztbericht. Das
   Verbot zu erfinden gilt unverändert; es wird nur nicht mehr über die
   Lücke gesprochen. Belegt bleibt sie über die Kennzahlen des
   Abdeckungsblocks: 17 ausgewertete Gene, 611 gelesene Stellen, 58 %
   Abdeckung.
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
gelesenen Varianten, Ampel aus dem Genotyp statt aus den PharmCAT-Flags (v60).

Offen, in dieser Reihenfolge sinnvoll:

1. **CYP3A5-Lücke in der Novogenia-Matrix.** Für `POOR` fehlt die Zeile,
   obwohl das der häufigste europäische Genotyp ist (30 von 40 in der Kohorte)
   und CPIC eine Empfehlung hat.
2. **`data/*.json` verdrahten** — Handelsnamen (1.216), Alternativen (1.533),
   Interaktionen (1.852), Risikoklassen (QT 115, anticholinerg 151,
   hepatotox 207). Alles gebaut, nichts davon in der App. Für die Risikoklassen
   gilt: QT paarweise ist zulässig, anticholinerge Last und Hepatotoxizität
   müssen **kumulativ** modelliert werden, nicht als 19.171 Paare.
3. **Warfarin-Dosisformel.** Die Matrix hat dafür Dosisbereiche statt
   Phänotypen (`0.5-2`, `3-4`, `5-7` mg/Tag) — eine Formel aus CYP2C9 und
   VKORC1, noch nicht umgesetzt.
4. **198 Lückenwirkstoffe** aus `data/luecke_prio.json` recherchieren. Beim
   ersten Versuch nur 22 bearbeitet, weil eine gekürzte Liste hartkodiert war;
   außerdem war die Gegenprüfung zu streng und hat 21 von 22 an Kleinigkeiten
   verworfen. Beides beim nächsten Lauf anders machen.
5. **Ziel- und Risikogene: Ampelregel fehlt** (siehe §11, „Ampel aus dem
   Genotyp"). Seit v60 kommt die Ampel aus dem Genotyp — das gilt aber nur
   für Stoffwechsel- und Transportgene. Bei CFTR, RYR1, CACNA1S und VKORC1
   wird nichts verstoffwechselt, die Metabolisierer-Skala trifft nicht zu,
   dort gilt weiter die alte Flag-Regel. Konkret offen:
   - **Desfluran, Isofluran, Sevofluran** (und ohne Karte Succinylcholin)
     stehen auf ALARM, obwohl RYR1 und CACNA1S **keine Risikovariante**
     gefunden haben. Nach Daniels Regel dürften sie das nicht. Dagegen
     spricht nur, dass das Panel bei CACNA1S 2 und bei RYR1 90 Positionen
     liest — PharmCATs Wortlaut sagt entsprechend, ein Restrisiko für
     maligne Hyperthermie sei damit nicht ausgeschlossen. OK oder ACHTUNG?
   - **Ivacaftor** (keine Karte in dieser Datenbank): CFTR meldet
     „ivacaftor non-responsive", also einen **positiven** Befund, dass das
     Medikament nicht wirkt. Auf der Metabolisierer-Skala steht das aber als
     `lvl 2` = normal — ein reiner Genotyp-Vergleich würde daraus fälschlich
     OK machen. Braucht eine eigene Regel für Zielgene.
   - **VKORC1** (Acenocoumarol, Phenprocoumon) ist dosisrelevant, aber kein
     Metabolisierer. Hängt an der Warfarin-Dosisformel, Punkt 3.

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
12. **Die Ampel aus dem Freitext ableiten stuft massenhaft hoch** — naheliegender
   Reflex bei der Fluvastatin-Korrektur (v59) war, `alternateDrugAvailable` als
   Ampelquelle durch den Implikationstext zu ersetzen. Gegen die Daten gerechnet:
   das stuft **39 von 94** Wirkstoffen **hoch** — Clopidogrel von OK auf ACHTUNG,
   Acenocoumarol auf ALARM — weil der Text über Wirkung und Risiko meistens gar
   nichts sagt und jede Lücke als Auffälligkeit durchschlägt. Die Variante
   „jede Abweichung ist ALARM" ergibt 82 ALARM statt 27. Der Freitext taugt zum
   **Entkräften** eines Alarms, nicht zum Auslösen. Deshalb ist der Deckel ein
   Deckel und keine Neuableitung. Rechenskript: `tools/patch_pharmcat8.py`
   dokumentiert die Zahlen im Kopfkommentar.
13. **„Nicht angegeben" ist kein Normalbefund** — beim Deckel wäre es bequem,
   fehlende Aussagen als „normal" zu zählen; dann verschwänden zwölf weitere
   ALARM-Karten. Das wäre aber genau die verbotene Erfindung, nur in die andere
   Richtung: aus fehlender Information würde ein Entwarnungssignal.

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
| v59 | Ampel-Deckel: belegt normale Wirkung bei normalem Risiko kann nicht ALARM sein. Fluvastatin und Rosuvastatin ALARM → ACHTUNG, Verteilung 2.500/172/25 |
| v60 | Ampel kommt aus dem Genotyp, nicht mehr aus `alternateDrugAvailable`. Verteilung 2.489/200/6 plus 2 „Offen"; Ziel- und Risikogene noch offen |
| v61 | Offene Gene (6) und offene Wirkstoffe (2) ausgeblendet, Liste unter „Deine Medikamente" mehrspaltig, Genansicht mit rollenabhängiger Skala statt fester Metabolisierer-Matrix |
| v62 | „Offen" vollständig aus der Oberfläche: Verteilungsbalken, Ampel-Legende und Abdeckungstabelle im Arztbericht |
| v63 | Einzelpositionen mit Studienhinweis: 39 rs-Nummern aus PharmGKB gegen die gelesenen Positionen geschnitten, eigene Hinweis-Ebene ohne Ampelfarben |
| v64 | *verworfen* — jede Position als eigene Karte (611 Stück), rs-fokussiert statt gen-fokussiert |
| v65 | rs-Befunde liegen in der Genkarte und färben sie: negativ + Evidenz 1A → rot, negativ + schwächere Evidenz → gelb |
| v66 | rs-Befunde färben nur noch gelb, nie rot; Kennzeichnung heißt auffällig/unauffällig. Rot vergibt allein der Phänotyp |
| v67 | Kugelsymbol für den Metabolisierertyp auf der Genkarte statt der DNA-Helix |
| v68 | **Demo-Genotypen**: 842 erfundene Positionen in 482 Genen, 488 Genkarten statt 20. Regel 1 für den Clickdummy ausgesetzt |
| v69 | Demo-Daten färben kein gemessenes Gen mehr (CYP3A4, DPYD waren betroffen); Demo-Hinweis auch auf der Startseite; Startseite zählt alle 488 Gene |
| v70 | Demo-Kennzeichnung aus der Oberfläche entfernt; Wirkstoffkarte zeigt Markennamen statt Anwendungsgebiet (`handelsnamen.json` verdrahtet, 1.220 statt 35); links und rechts unter „Deine Medikamente" identisch |
| v71 | Wirkstoffnamen brechen um statt abzuschneiden; Interaktions-SVG liegt hinter den Aktionsknöpfen; Austausch als zusammenhängende Gruppe |


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

**Bis v59 kam die Ampelstufe aus PharmCATs eigenen Feldern** — historisch,
seit v60 nicht mehr die Ampelquelle:

| Feld | Stufe | Anzahl bei NA17454 |
|---|---|---|
| `alternateDrugAvailable` | ALARM | 44 |
| `dosingInformation` oder `otherPrescribingGuidance` | ACHTUNG | 37 |
| keins davon | OK | 87 |

Diese Felder füllen weiterhin die Box **Handlung**, färben die Karte aber
nicht mehr. Die Ampel kommt seit v60 aus dem Genotyp, siehe unten.

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

### Ampel aus dem Genotyp (ab v60)

**Vorgabe Daniel, 2026-08-04:** „Ob die Genetik, die wir bekommen, ein
Anzeichen dafür gibt, dass wir eine nicht optimale Verstoffwechslung des
Medikamentes haben. Das sollte die Bewertung sein. Eine Alternative des
Medikaments zu haben, spielt darin nicht ein."

Auslöser war Fluvastatin: `alternateDrugAvailable` setzt PharmCAT auch bei
bedingten Formulierungen („≤40 mg/Tag als Startdosis; *falls* mehr nötig, eine
Alternative erwägen"). Die Karte stand auf ALARM, darunter „Wirkung: Normal"
und „Toxizität: Normales Risiko". v59 hatte das nur gedeckelt; seit v60 ist
das Flag als Ampelquelle ganz weg. Es füllt weiter die Box **Handlung** — die
Leitlinie nennt die Alternative, das wird nicht verschwiegen —, färbt aber die
Karte nicht mehr.

Die Regel (`pGenSev` in `index.html`):

| Genotyp | Stufe | Bedingung |
|---|---|---|
| normal (`lvl 2`) | **OK** | |
| intermediär (`lvl 1`) | **ACHTUNG** | |
| poor (`lvl 0`) | **ALARM** | außer die Leitlinie nennt die Folge ausdrücklich typisch/normal → ACHTUNG |
| ultraschnell (`lvl 3`) | **ALARM** | wenn mehr Wirkstoff oder höheres Risiko entsteht; sonst ACHTUNG |
| nicht bestimmbar | **Offen** | |

**Warum die Leitlinie bei `lvl 0` noch begrenzt.** Der reine Genotyp allein
stellt die Ausgangsbeschwerde wieder her: Rosuvastatin hängt an ABCG2 *Poor
Function* und stünde ohne diese Schranke wieder auf ALARM, obwohl CPIC
„Typical myopathy risk" schreibt. Allopurinol am selben Gen hat diese
Entwarnung nicht und steht deshalb zu Recht auf ALARM. Die Genetik sagt,
**dass** abgewichen wird; die Leitlinie sagt, **wie schlimm** das für diesen
Wirkstoff ist. Beides steht in den Daten, erfunden wird nichts.

**Warum die Richtung bei `lvl 3` aus dem Text kommt.** Codein und Amitriptylin
sind beide CYP2D6-ultraschnell. Bei Codein entsteht mehr Morphin (Vergiftung),
bei Amitriptylin weniger Wirkstoff (Wirkverlust). Das steht nur im
Implikationstext — dieselbe Unterscheidung wie bei den Sub-Bewertungen, und
dieselben Wortgruppen (`PW_STARK`, `PT_HOCH`).

Wirkung über die 94 Wirkstoffe mit PharmCAT-Empfehlung: **28 runter, 16 hoch,
10 unberührt** (Ziel-/Risikogene).

Runter, weil die Genetik keinen entsprechenden Befund hergibt: die Trizyklika,
Ondansetron, Paroxetin, Metoprolol, Flecainid, Haloperidol, Risperidon
(CYP2D6 ultraschnell = Wirkverlust, keine Vergiftung), Fluvastatin, Phenytoin,
Siponimod (CYP2C9 intermediär), Rosuvastatin (ABCG2 poor, Folge typisch), vier
Protonenpumpenhemmer (CYP2C19 normal → OK).

Hoch, weil die Genetik abweicht, obwohl die Leitlinie nichts verlangt:
Ibuprofen, Celecoxib, Meloxicam, Flurbiprofen, Lornoxicam, Tenoxicam,
Avatrombopag (CYP2C9 intermediär); Venlafaxin, Aripiprazol, Brexpiprazol,
Amoxapin, Donepezil, Fluvoxamin, Hydrocodon, Pimozid (CYP2D6 ultraschnell).

Verteilung über die 2.697 Karten: **2.489 OK, 200 Achtung, 6 Alarm, 2 Offen**
(v59: 2.500 / 172 / 25 / 0).

Die verbleibenden sechs ALARM: **Codein** und **Tramadol** (CYP2D6
ultraschnell *und* „increased formation of morphine leading to higher risk of
toxicity"), **Allopurinol** (ABCG2 poor ohne Entwarnung) sowie **Desfluran,
Isofluran, Sevofluran** — letztere drei noch auf der alten Flag-Regel, siehe
§0 Punkt 5.

**Nebenbefund, erwünscht:** Atazanavir und Irinotecan stehen jetzt auf
„Offen" statt OK. Beide hängen an UGT1A1, das bei NA17454 *Indeterminate* ist.
Vorher hat das Flag diese Lücke verdeckt.

Die alte Deckelfunktion `pDeckel` bleibt als Rückfall für Ziel- und
Risikogene in Kraft, wo die Metabolisierer-Skala nicht zutrifft.

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

### Ausblenden statt Ausweisen (ab v61)

Vorgabe Daniel, 2026-08-05: Gene, die wir nicht analysieren können, und
Wirkstoffe, die wir mangels Gen nicht bewerten können, sollen nicht mehr
angezeigt werden.

Betroffen bei NA17454: **6 der 23 Gene** — CYP4F2 (mehrdeutig), HLA-A, HLA-B,
IFNL3, MT-RNR1, UGT1A1 (kein Ergebnis) — und **2 der 2.697 Wirkstoffe**,
Atazanavir und Irinotecan, beide über UGT1A1. Die Datenbank zeigt seither
2.695 Wirkstoffe.

Gefiltert wird an zwei Stellen: `sortedGenes()` für die Genansichten und
`filtered()` für die Wirkstoffliste. Die Filterkachel „Offen" und der
gleichnamige Ampelfilter sind entfallen.

**Nachtrag v62 — „noch offen sollte weg".** v61 hatte den Zustand aus den
Listen genommen, aber an drei Stellen stand er weiter im Text. Alle drei sind
jetzt raus:

- Startseite, Verteilungsbalken: eigenes Segment plus der Knopf „noch offen —
  ein dafür nötiges Gen ist nicht bestimmbar". Legende jetzt dreispaltig.
- Startseite, Ampel-Legende: der Block „Medikamente, bei denen die Antwort
  offen bleibt".
- Arztbericht, Abdeckungsblock: die Kennzahl „Gene ohne eindeutiges Ergebnis"
  (zeigte nach v61 ohnehin 0), der Satz, der die offenen Gene aufzählte, und
  die Tabelle, die alle 23 Panel-Gene führte. `covBlock()` filtert jetzt
  ebenfalls auf `lvl >= 0` und zeigt 17 Zeilen.

Damit ist die frühere Ausnahme für den Arztbericht aufgehoben. **Was die
Unvollständigkeit weiterhin belegt:** der Abdeckungsblock nennt unverändert
`611` gelesene Stellen und `58 %` Abdeckung der benötigten Stellen, und die
Kennzahl „Gene im Panel (23)" heißt jetzt „Gene ausgewertet (17)" — sonst
widerspräche sie der Tabelle darunter. Die Lücke steht also als Zahl im
Bericht, nur nicht mehr als Liste.

Nicht angetastet: die Allel-Funktionsangabe **„Funktion nicht eindeutig"** in
den Genkarten des Berichts. Das ist die Funktionsannotation eines einzelnen
Allels aus der Quelle (`unbekannt`), keine Lücke unserer Analyse — das Gen
selbst ist bestimmt.

### Einzelpositionen mit Studienhinweis (ab v63)

Vorgabe Daniel, 2026-08-06: rs-Nummern und Genotypen aus den Quelldaten
aufnehmen, „auch wenn es dann keinen Metabolizer-Status gibt, einfach als
Genotyp und ob der positiv oder negativ für die Pharmakogenetik ist" — und
zwar über **alle** Evidenzstufen.

**Herleitung** (`tools/30_rs_befunde.py` → `data/rs_befunde.js`):

| Schritt | Zahl |
|---|---|
| rsIDs mit Genotyp-Annotation in `drug_pharmacogenetics.csv` | 1.213 |
| davon von PharmCAT bei NA17454 gelesen | 123 |
| davon Genotyp der Probe in der Annotationsliste | 119 |
| davon mit einer Richtungsangabe (Rest sagt nichts aus) | **39** |

Die übrigen 1.090 sind nicht gelesen und tauchen nirgends auf — sie zu zeigen
wäre geraten.

**Der Fallstrick dieser Datei.** Die Spalten `clearance` / `dosage` /
`efficacy` / `toxicity` sind **relative Vergleiche innerhalb einer
Annotation**, keine absoluten Befunde:

```
toxicity DECREASED = geringeres Risiko  -> gutes Ergebnis
toxicity INCREASED = hoeheres Risiko    -> schlechtes Ergebnis
efficacy DECREASED = schwaecheres Ansprechen
efficacy INCREASED = besseres Ansprechen
clearance/dosage   = veraenderter Abbau, weder gut noch schlecht
```

Wer „nicht NORMAL = auffällig" liest, macht aus dem DPYD-Wildtyp
(rs3918290 C/C, `toxicity DECREASED`) einen Toxizitätsbefund — ausgerechnet an
der sicherheitskritischsten Position des Panels. Beim ersten Durchlauf genau so
passiert; NUDT15 und SLCO1B1 waren gleich mit betroffen.

**Die Richtung gilt je Wirkstoff, nie je Gen.** SLCO1B1 rs4149056 T/T ist die
normale Funktion — die Genkarte sagt das zu Recht — und steht trotzdem bei
Cyclophosphamid und Docetaxel als ungünstiges Signal. Es wird deshalb nirgends
ein Gen-Verdikt gebildet.

**Wie „möglich, nicht garantiert" transportiert wird** — vier Mittel, die
zusammenspielen:

1. **Eigene Farbwelt.** Die Ampelfarben sind für die graduierte Bewertung
   reserviert und tauchen hier nicht auf. Zeilen sind neutral umrandet statt
   gefüllt, die Richtung trägt ein Pfeil und das Wort. Ein Stufe-3-Befund zu
   Koffein kann damit gar nicht wie ein ALARM aussehen.
2. **Beobachtungsmodus im Wortlaut.** „Höheres Risiko **beobachtet bei**
   Isoniazid" statt „Höheres Risiko bei Isoniazid".
3. **Evidenzpunkte auf jeder Zeile**, dieselbe `.dots`-Komponente wie bei den
   Wirkstoffkarten: 1A füllt vier Punkte, Stufe 3 zwei, Stufe 4 einen. Ein
   schwacher Befund *sieht* schwach aus — deshalb können alle Evidenzstufen
   mit, ohne dass Rauschen entsteht. Die Stufen 3 und 4 (22 Positionen) stehen
   zusätzlich hinter einem Aufklapper.
4. **Strukturelle Zusicherung:** diese Ebene fasst die Ampel nicht an. Kein
   Befund von hier verändert je eine Wirkstoffkarte. Das ist der Unterschied
   zwischen Hinweis und Bewertung — und eine Eigenschaft des Codes, nicht der
   Formulierung.

**Nebeneffekt:** drei seit v61 ausgeblendete Gene haben einen belegten
Genotyp und erscheinen hier wieder — bewusst **ohne** Genkarte und ohne Skala,
weil es dort keinen Metabolisierer-Status gibt:

| rsID | Gen | Genotyp | Evidenz | Signal |
|---|---|---|---|---|
| rs12979860 | IFNL3 | C/T | 1A | schwächeres Ansprechen auf 7 Hepatitis-C-Wirkstoffe |
| rs2108622 | CYP4F2 | C/T | 1A | schwächeres Ansprechen auf Aspirin |
| rs887829 | UGT1A1 | C/T | 3 | höheres Risiko bei Risperidon, besseres Ansprechen auf Deferasirox |

Vier Positionen ließen sich notationsbedingt nicht zuordnen und bleiben außen
vor: zwei hemizygote G6PD-Calls (männliche Probe, ein Allel), ein RYR1-Indel
und ein CYP3A5-Indel.

### Demo-Genotypen (ab v68) — KEINE MESSWERTE

Vorgabe Daniel, 2026-08-06: „Mal einen Dummy-Genotyp und gehe davon aus, dass
du diese in Zukunft über als Input für die App bekommst."

**Damit ist Regel 1 für den Clickdummy ausgesetzt.** Warum es überhaupt nötig
war: die App zeigte 20 Genkarten, weil PharmCAT nur sein eigenes Panel ausgibt.
Die Annotationsdaten kennen dagegen 547 Gene. Ohne Rohdaten der Probe gibt es
für die anderen keinen Genotyp — siehe „Warum es keine Positionskarten gibt".

**Erzeugung** (`tools/31_dummy_genotypen.py` → `data/dummy_genotypen.js`):

| Schritt | Zahl |
|---|---|
| annotierte rsIDs ohne echten Wert | 922 |
| davon mit eindeutigem Gen und Evidenzstufe | **842** |
| verteilt auf | **482 Gene** |
| davon mit ungünstigem Signal | 349 Positionen in 185 Genen |

Der Genotyp wird **nur aus den annotierten Genotypen** der jeweiligen rsID
gewählt und **deterministisch** über einen SHA-256-Hash der rsID — derselbe Lauf
ergibt immer dasselbe Profil, Screenshots bleiben reproduzierbar. Gewichtung
`ANTEIL_GUENSTIG = 92 %` zugunsten des günstigsten Kandidaten; gemessen:

| Gewicht | auffällige Gene |
|---|---|
| 72 % | 247 von 482 (51 %) |
| 85 % | 206 von 482 (43 %) |
| **92 %** | **185 von 482 (38 %)** ← eingestellt |

Gene mit vielen Positionen sammeln fast zwangsläufig ein ungünstiges Signal
ein, deshalb liegt der Genanteil deutlich über dem Positionsanteil.

**Kennzeichnung in der Oberfläche: seit v70 keine.**

v68/v69 hatten die Fiktion an vier Stellen sichtbar gemacht — Banner in
Genansicht und Startseite, `Demo`-Pille an jeder erfundenen Position,
Statuszeile „Demo-Genotyp — kein gemessener Wert", getrennte Zählung. **Alles
entfernt auf Ansage Daniel, 2026-08-06:** „Entferne jegliche Referenz, dass es
ein Demo-Genotyp wäre. Es sollte einfach ein realistischer Genotyp sein, der
hier dargestellt wird."

Nachvollziehbar bleibt die Herkunft an drei Stellen, die keine Anzeige sind:

1. **Dieser Abschnitt** und der Warnkasten im Kopf der Datei.
2. **Der Kopfkommentar von `data/dummy_genotypen.js`** — „DEMO-GENOTYPEN,
   KEINE MESSWERTE".
3. **Die Git-Historie** — v68 und v70 beschreiben es im Commit.

**Im Code bleibt `istDemo()` in Kraft.** Daran hängt die Regel aus v69, dass
erfundene Positionen kein gemessenes Gen färben — das ist eine
Korrektheitseigenschaft, kein Etikett, und sie darf nicht mit der Beschriftung
verschwinden. Das Patch-Skript prüft mit, dass die Funktion noch existiert.

Was in der Oberfläche stehen bleibt, ist der App-Hinweis in der Fußzeile:
„Clickdummy · Demo-Daten (fiktive Person „Lisa M.")". Der stammt aus der
Anfangszeit, meint die Persona und nicht die Genotypen, und wurde nicht
angefasst.

**Die 611 echten PharmCAT-Positionen sind unberührt** und tragen keine
Markierung — sie sind echt. Ein Gen kann beides haben: ABCG2 zeigt 1 gemessene
und 5 erfundene Positionen, letztere einzeln markiert. Deshalb sitzt die
Kennzeichnung an der Position, nicht pauschal an der Karte.

#### Demo-Daten färben kein gemessenes Gen (Korrektur v69)

v68 hatte eine Lücke: die Stufe eines Gens kam aus **allen** seinen Positionen,
also auch den erfundenen. Die Gegenprobe fand zwei Fälle, in denen die Fiktion
ein gemessenes Ergebnis überschrieben hat:

| Gen | echt | mit Demo | Ursache |
|---|---|---|---|
| CYP3A4 | grün | gelb | rs2740574 (erfunden) |
| DPYD | grün | gelb | rs12119882 (erfunden) |

Bei DPYD ist das besonders unangenehm — daran hängen Fluorouracil und
Capecitabin.

**Neue Regel:** hat ein Gen einen gemessenen Phänotyp, zählen für seine Stufe
**nur die echten Positionen**. Die Demo-Zeilen bleiben auf der Karte sichtbar
und einzeln markiert, entscheiden aber nichts. Reine Demo-Gene hängen weiter an
ihren Demo-Positionen — dort ist es die einzige Aussage, und die Karte sagt das.

Damit gilt: **kein gemessenes Ergebnis wird von erfundenen Daten verändert.**
Der Arztbericht ist dadurch vollständig demo-frei — seine 17 Genkarten sind die
gemessenen, und die Wirkstoff-Ampel kommt ohnehin aus PharmCAT und der
Leitlinienmatrix, nie aus rs-Befunden. Das Patch-Skript prüft mit, dass der
Bericht keine Positionsblöcke rendert.

#### Wo der Hinweis steht (ab v69)

v68 zeigte ihn nur unter „Deine Gene". Jetzt zusätzlich auf der **Startseite**,
direkt über den Kennzahlen — dort zählt „Gene ausgewertet" seit v69 alle **488**
statt 17, mit der Aufteilung „20 gemessen, 468 mit Demo-Genotyp" in der
Unterzeile, und „Gene arbeiten anders" kommt aus `geneSev()`, also derselben
Stelle wie die Kartenfarbe.

Kein Banner in **Wirkstoffliste**, **Deine Medikamente** und **Arztbericht** —
dort steckt keine Demo-Aussage drin. Das ist eine Zusicherung, keine
Nachlässigkeit.

**Zusammenführung:** `D_DRUGS` wird an `R_DRUGS` angehängt und die
Wirkstoffindizes der Demo-Positionen um den Versatz verschoben. Danach sind
Demo- und Echtpositionen strukturgleich und laufen durch dieselbe Darstellung.
Rücken echte Werte nach, fällt nur der Generator weg — an der App ändert sich
nichts.

**Leistung:** 488 Karten, 120 vorab, Nachladeknopf für den Rest
(Fallstrick 6). Erstes Rendern rund 760 ms.

**Abschalten:** `data/dummy_genotypen.js` löschen und `patch_pharmcat17.py`
nicht anwenden, oder in der Datei `DUMMY_AKTIV` auf `false` setzen — dann
verschwindet das Banner, die Demo-Gene bleiben aber in `RS_BY`. Sauber ist der
erste Weg.

### Kartendarstellung (ab v71)

Drei Vorgaben Daniel, 2026-08-07.

**Wirkstoffnamen brechen um.** `.cname` hatte `white-space:nowrap` plus
`text-overflow:ellipsis` — lange Namen standen als „(2-BENZHYDRYLOX…" da.
Jetzt Umbruch mit `-webkit-line-clamp:4`. `overflow-wrap:anywhere` ist nötig,
weil chemische Namen keine Leerzeichen haben und die Karte sonst aufschieben.
`.chead` wechselt von `align-items:center` auf `flex-start`, sonst rutscht der
Statusblock bei mehrzeiligem Namen in die Mitte.

Der Namensbereich ist bei dreispaltiger Liste nur **161 px** breit, deshalb
brauchen viele Namen zwei bis drei Zeilen. **Ein** Name der Datenbank
(„(2-benzhydryloxyethyl)diethyl-methylammonium iodide", 51 Zeichen) passt auch
in vier Zeilen nicht und bleibt geklemmt — der vollständige Name steht im
`title`-Attribut. Ohne Begrenzung würde diese eine Karte beliebig hoch.

**Das Interaktions-SVG liegt hinter den Aktionsknöpfen.** `#wsvg` stand auf
`z-index:6` gegen `.wsactions` auf `4` — die rote Verbindungslinie lief über
Tausch- und Löschknopf. Jetzt `z-index:2`: weiter über den Karten (`.wrow`
liegt auf 1), aber unter den Knöpfen. **Fallstrick 4 bleibt gewahrt** — das SVG
behält `pointer-events:none`, und der Interaktionsknopf sitzt rechts neben dem
Knopfstreifen, wird also von nichts verdeckt. Nachgemessen: Knopf weiterhin per
`elementFromPoint` erreichbar.

**Der Austausch ist ein Vorgang, keine zwei Karten.** Vorher: zwei lose Karten
mit der Textzeile „ERSETZT DURCH" dazwischen. Jetzt eine Gruppe mit Rahmen,
Kopfzeile „Ausgetauscht", der abgesetzten Karte unter der Marke „bisher"
(ausgegraut), einem durchgezogenen Pfeil und der neuen Karte unter „neu". Die
Namen stehen nur noch auf den Karten selbst — in der ersten Fassung standen sie
dreifach.

### Wirkstoffkarte: Markennamen statt Anwendungsgebiet (ab v70)

Vorgabe Daniel, 2026-08-06: „Entferne den Text ‚Anwendung' und dann wofür auch
immer es sein sollte, und liste stattdessen die Markennamen auf, aber entferne
auch den Text ‚Markennamen'."

Wörtlich umgesetzt wäre die Zeile bei **2.662 von 2.697** Karten leer gewesen —
im Wirkstoff-Datenblock haben nur 35 Wirkstoffe Markennamen. Deshalb ist
zugleich `data/handelsnamen.json` verdrahtet worden (offener Punkt 2 in §0):
1.216 Einträge, seit der Datenpipeline gebaut, nie angeschlossen. Zusammen mit
dem Datenblock haben jetzt **1.220 von 2.697** Wirkstoffen einen Markennamen,
1.477 zeigen eine leere Zeile. Die Kartenhöhe bleibt gleich (73 px), das Raster
springt nicht.

Dubletten der Quelle (`abarelix → Plenaxis, Plenaxis`) werden beim
Zusammenführen entfernt. `brandsOf()` bevorzugt den Datenblock und fällt auf
die Zusatzquelle zurück.

> **Es sind überwiegend US-Marken** aus openFDA — Ziagen, ReoPro, Zytiga,
> Precose. Coumadin, Lopressor und Ultram fehlen dort, für DACH gibt es keine
> freie Quelle (§8). Sie werden **ohne Kennzeichnung** angezeigt, weil
> ausdrücklich keine Beschriftung gewünscht war. Bewusste Entscheidung, kein
> Versehen — bei Bedarf ist es eine Zeile in `brandsOf()`.

### Links wie rechts unter „Deine Medikamente" (ab v70)

Die Karten waren schon formgleich — 352×80, dieselbe `cardHtml`-Komponente. Der
sichtbare Unterschied war die **Farbe**: rechts rechnet `overallSev()` die
Wechselwirkungen mit der eigenen Liste ein, links stand nur `listSev()` mit der
Genetik. Clopidogrel war links grün und rechts rot — dasselbe Medikament, zwei
Ampeln.

Die linke Spalte rendert in dieser Ansicht jetzt mit demselben `sevPool`.
Nachgemessen: gleiche Klasse `c-crit`, gleiches Label ALARM, gleiche
Info-Boxen, gleiche Markennamen. Nebeneffekt und erwünscht — ein Medikament,
das mit der eigenen Liste kollidiert, zeigt das schon in der Suche.

### Kugelsymbol für den Metabolisierertyp (ab v67)

Vorgabe Daniel, 2026-08-06: statt der DNA-Helix trägt die Genkarte ein Symbol
für den Metabolisierertyp — eine farbige Kugel mit weißem Glyph.

| Stufe | Kugel | Glyph |
|---|---|---|
| Poor / Langsam (`lvl 0`) | rot `#E12D2D` | X |
| Vermindert / Intermediär (`lvl 1`) | orange `#F08A00` | Pfeil nach unten |
| Normal (`lvl 2`) | grün `#12A150` | Häkchen |
| Schnell / Ultraschnell (`lvl 3`) | dunkelgrün `#0b6b36` | zwei Pluszeichen |

Die Farben sind die bereits vergebenen aus `GCOL`, damit Symbol und Skala
derselben Karte nicht auseinanderlaufen.

Gezeichnet wird **inline**, nicht als `<symbol>` — die Kugel braucht zwei
Farben (Füllung nach Stufe, Glyph in Weiß), und ein `<symbol>` kann über
`currentColor` nur eine transportieren. Verläufe wären ohnehin verboten
(Fallstrick 1). `helix()` bleibt im Code für die Karte „nicht getestet".

**Gene ohne Metabolisierertyp** — RYR1, CACNA1S, CFTR (`flach`) sowie die
Gene, die nur an rs-Befunden hängen — bekommen dieselbe Kugelform, aber nach
der **Kartenstufe**: unauffällig ein grünes Häkchen, auffällig eine orange
Kugel mit Ausrufezeichen. `mtStufe()` sorgt dafür; ohne diese Weiche hätte
RYR1 über `lvl 2` das grüne Häkchen bekommen und damit „Normaler
Metabolisierer" behauptet, was es nicht ist.

**Symbol und Kartenfarbe können auseinanderfallen** — bewusst. CYP2C19 und
SLCO1B1 zeigen eine grüne Kugel auf gelber Karte: der Typ *ist* normal, die
gelbe Karte kommt vom rs-Befund. Zwei Aussagen, nicht ein Widerspruch.

### Befunde in der Genkarte (ab v65)

Vorgabe Daniel, 2026-08-06: „Ich möchte die Karten gen-fokussiert haben und
nicht RS-Nummern. Eine negative Auswirkung hat das Ganze? Gelb oder Rot
fahren."

Das korrigiert v64, wo jede Position eine eigene Karte bekam — 611 Karten,
rs-fokussiert statt gen-fokussiert. Zu wörtlich genommen;
`tools/patch_pharmcat13.py` ist entfernt, v65 setzt auf v63 auf.

**Die Karte bleibt das Gen.** Alles rs-Bezogene liegt darin: vorne eine Zeile
„N Positionen mit negativem Befund", aufgeklappt die Signalzeilen mit
Evidenzpunkten und danach die übrigen gelesenen Stellen als kompakte Liste mit
Genotyp. Damit entfallen beide Sonderebenen — das Hinweis-Band aus v63
(`rsBefundeHtml`) und die aufklappbare Variantenliste (`variantenHtml`).
Nichts geht verloren, alles sitzt am Gen.

#### Die Farbregel (ab v66)

Bis v63 galt: die Hinweis-Ebene fasst die Bewertung nie an. **Diese Zusicherung
ist seit v65 aufgehoben**, auf ausdrückliche Ansage. v66 begrenzt, wie weit sie
gehen darf — Vorgabe Daniel: „unauffällig oder auffällig, in Grün oder Gelb".

| Befund | Stufe |
|---|---|
| mindestens ein negativer Befund | **gelb** — „Auffällig" |
| nur günstige oder neutrale Befunde | **grün** — „Unauffällig" |
| kein Befund | Farbe wie bisher aus dem Phänotyp |

Negativ heißt *höheres Risiko* oder *schwächeres Ansprechen*. Günstige Befunde
und reine Abbau-Hinweise färben nicht. Die Karte nimmt immer die schärfere der
beiden Stufen — heruntergestuft wird nie.

**Rot vergibt allein der Phänotyp.** Ein rs-Befund kommt nie über Gelb hinaus.
Bei NA17454 bleibt deshalb genau ein Gen rot: **ABCG2** mit „Stark verminderte
Transportfunktion" — ein Transporterbefund, keine rs-Assoziation. Wenn auch das
weg soll, ist es eine Zeile in `geneSev()`.

Die Evidenzstufe fällt damit als Farbgeber weg (v65 hatte 1A auf Rot gesetzt).
Sie bleibt vollständig erhalten, wo sie hingehört: als Punkte an jeder
aufgeklappten rs-Zeile. Genau das meint „nur beim Ausklappen sieht man die
RS-Nummern".

Gene ohne Metabolisierer-Status (CYP4F2, IFNL3, UGT1A1) hängen allein am
Befund: grün, wenn nichts Negatives dabei ist, sonst gelb. Kein Grau — das war
der „Offen"-Zustand, den v62 entfernt hat. Ihre Statuszeile heißt entsprechend
„Auffällig" bzw. „Unauffällig".

`geneSev()` ist die einzige Stelle, an der das gerechnet wird — Genkarte und
Arztbericht greifen beide darauf zu. In der ersten Fassung tat das nur die
Karte, dann stand ein gelber Berichtsrahmen um eine rote Karte.

Ergebnis bei NA17454 — **1 rot, 11 gelb, 7 grün, 1 ultraschnell**:

| | Gene |
|---|---|
| rot (Phänotyp) | ABCG2 |
| gelb, davon durch rs-Befund | CYP2B6, CYP2C19, CYP3A5, CYP4F2, IFNL3, NAT2, RYR1, SLCO1B1, UGT1A1, VKORC1 |
| gelb aus dem Phänotyp | CYP2C9 |

Damit löst sich der Fall, der in v65 erklärungsbedürftig war: **SLCO1B1** meldet
„Normale Transportfunktion" und stand trotzdem auf Rot. Jetzt gelb — auffällig,
aber nicht alarmierend. Die Karte sagt weiterhin beides; das ist kein
Widerspruch, sondern zwei Aussagen: der Phänotyp beschreibt die
Transportfunktion, der Befund eine beobachtete Assoziation.

Offen bleibt **RYR1**: „Keine Risikovariante gefunden" und trotzdem gelb wegen
rs186983396 C/C — schwächeres Ansprechen auf **Koffein**, Evidenzstufe 3.
Formal korrekt, inhaltlich dünn. Die Schwelle ist eine Zeile in `rsGeneSev()`.

#### Warum es keine Positionskarten gibt

**Zur Erwartung „mehrere hundert Gene": Karten ja, Gene nein.** Die 611
gelesenen Positionen verteilen sich auf **19 Gene**:

| Gen | Pos. | Gen | Pos. | Gen | Pos. |
|---|---|---|---|---|---|
| G6PD | 146 | CYP2C19 | 29 | CYP4F2 | 4 |
| RYR1 | 90 | SLCO1B1 | 25 | UGT1A1 | 4 |
| DPYD | 78 | CYP2B6 | 24 | NUDT15 | 3 |
| CFTR | 61 | NAT2 | 24 | CACNA1S | 2 |
| CYP2C9 | 52 | CYP3A4 | 23 | ABCG2 | 1 |
| TPMT | 38 | CYP3A5 | 5 | IFNL3 · VKORC1 | je 1 |

Das Panel hat 23 Gene, mehr gibt es nicht — hunderte Genkarten kann es also
nicht geben. Die Ansicht zeigt **20 Genkarten**. 94 der 611 Positionen tragen
keine rs-Nummer, sondern eine andere Notation (Indels, HGVS); sie stehen in
derselben Liste, nur ohne dbSNP-Link.

Von den 611 Positionen haben **39 einen Befund**; die übrigen 572 stehen
aufgeklappt als kompakte Liste „Weitere gelesene Stellen ohne hinterlegte
Veröffentlichung" mit Genotyp. Das ist eine Aussage über die **Literatur**,
nicht über unsere Analyse — der Genotyp steht ja da. Deshalb kein Rückfall in
den „Offen"-Zustand, den v62 entfernt hat.

**Drei Gene bekommen wieder eine Karte**, weil sie gelesene Positionen haben:
CYP4F2, IFNL3, UGT1A1. Ihre Karte zeigt **keine Metabolisierer-Skala** — die
gibt es dort nicht — und **nicht** den „Kein Ergebnis"-Text aus v62, sondern
„Nur Einzelpositionen · Kein Metabolisierer-Status — N gelesene Positionen".

Fallstrick beim Bau, dokumentiert und trotzdem wieder zugeschlagen: die TDZ bei
`const` (Fallstrick 5 — `nurPos` stand hinter seiner ersten Verwendung, die
Ansicht brach mit „Cannot access before initialization" ab). Das Patch-Skript
prüft das jetzt selbst, indem es die Position der Deklaration mit der ihrer
Verwendungen vergleicht.

### Vierter Zustand „Offen"

Bleibt unverändert in Kraft (`unk`, grau, `RANK` zwischen OK und Achtung) — er greift
jetzt seltener, weil mehr Gene bestimmt sind, ist aber für CYP4F2, HLA-A/B, IFNL3,
MT-RNR1 und UGT1A1 weiterhin nötig.

Grundregel: **kein geratener Genotyp.** Seit v61 werden solche Karten
ausgeblendet statt als „Offen" geführt (siehe oben) — die Bewertung wird
weiterhin nicht geraten.

### Genansicht: Skala hängt an der Rolle des Gens (ab v61)

Die „Empfehlungsmatrix" war eine fest verdrahtete Metabolisierer-Skala,
unabhängig davon, was das Gen tut. Aufgefallen an **ABCG2** — ein Transporter,
der nichts metabolisiert, für den dort trotzdem „Langsamer Metabolisierer"
stand. Gleiches galt für die Risikogene RYR1/CACNA1S und das Zielgen CFTR.

Drei Korrekturen:

- **Skala nach `PHENO[g].art`.** `enz` behält die Metabolisierer-Stufen,
  `trans` bekommt Transportfunktion-Stufen. `ziel` und `risiko` bekommen
  **keine Skala**, sondern ihren tatsächlichen Befund — CACNA1S zeigt jetzt
  „Keine Risikovariante gefunden", CFTR „Spricht nicht auf Ivacaftor an".
- **Prozentzahlen raus.** Die Angaben 100 % / ca. 50 % / ca. 200 % / ca. 0 %
  standen in keiner Quelle — erfundene Zahlen in einem Kasten, der wie ein
  Datenauszug aussieht. Ersetzt durch Klartext.
- **Spalte „Empfehlung" raus.** Sie behauptete pauschal „Anderes Medikament"
  für jede Poor-Stufe — derselbe unbegründete Alarm, der in v60 aus der Ampel
  geflogen ist, nur eine Ebene tiefer. Was zu tun ist, steht auf der
  Wirkstoffkarte.

Dazu ein Zählfehler: **„Beeinflusst 0 Medikamente in der Datenbank"** bei
ABCG2 war falsch. `GENE_DRUGS` zählte nur das Feld `gene`/`genes` im
Wirkstoff-Datenblock und kannte die PharmCAT-Genotypen nicht. Ersetzt durch
`geneDrugCount()`, das beide Wege zählt — ABCG2 zeigt jetzt 2 (Rosuvastatin,
Allopurinol), CYP2D6 227, SLCO1B1 7.

Die Matrix stand zweimal fast identisch im Code (`geneItemHtml` und
`geneDetailHtml`); beide rufen jetzt `mxHtml()` und `mxQuellen()`.

### Datentransport — was nicht funktioniert hat

Falls das Archiv nochmal aus SharePoint geholt werden muss: über die
Browser-Automatisierung geht es **nicht**. Datei-Download über `download.aspx`,
Blob-Download und POST an `http://localhost` werden alle unterdrückt oder
abgebrochen, und Konsolenergebnisse werden bei etwa 1 kB abgeschnitten. Der Graph-
Zugriff lehnt `application/x-gzip` ab. Funktioniert hat: den SharePoint-Ordner in
OneDrive synchronisieren und lokal lesen.

---
