# Datenlizenzen — NOVO Drug Response

Die App zeigt Inhalte fremder Quellen an und verändert sie nur so, wie hier
beschrieben. Diese Datei gilt für alle Datendateien im Repository und für
deren Einbettung in `index.html`. Stand: 29.09.2026.

Grundlage für ClinPGx, CPIC und PharmCAT ist die
[ClinPGx Data Usage Policy](https://www.clinpgx.org/page/dataUsagePolicy):
Creative Commons **Attribution-ShareAlike 4.0 International**
([CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)) —
Namensnennung, Lizenzlink, Kennzeichnung von Änderungen, Weitergabe von
Bearbeitungen unter derselben Lizenz. Die Policy hält außerdem fest, dass die
Richtigkeit der Daten nicht garantiert wird; die App sagt das in der Fußzeile,
im Arztbericht und auf der Seite „Quellen und Lizenzen".

## Dateien

| Datei / Teil | Herkunft | Lizenz | Was verändert wurde |
|---|---|---|---|
| `data/clinpgx_alle.json` | ClinPGx/PharmGKB (www.clinpgx.org): clinical annotations und variant-drug annotations, Export „de-AT", Stand der Datei 25.09.2026 | **CC BY-SA 4.0** — diese abgeleitete Datei steht ebenfalls unter CC BY-SA 4.0 | gefiltert auf Zeilen mit Genotyp; Genotypen normalisiert (Buchstaben sortiert, Diplotyp-Hälften sortiert); Spalten umbenannt und gekürzt (siehe `spalten_klinisch`, `spalten_studien` in der Datei); Texte unverändert |
| `data/pharmaco_zusatz.json` → `_rsgen` | aus denselben ClinPGx-Exporten abgeleitet (rs-Nummer → häufigstes Gen, nur Panel-Stellen) | **CC BY-SA 4.0** | Ableitung, keine Texte |
| `data/pharmaco_zusatz.json` → `_allelfn` | CPIC-Alleltabelle, api.cpicpgx.org (`/v1/allele`), Abruf 29.09.2026 | **CC BY-SA 4.0** (ClinPGx Data Usage Policy) | nur Spalten Name, Funktion, klinische Funktion, Aktivitätswert |
| `data/pharmaco_zusatz.json` → `_allelfreq` | CPIC-Frequenztabelle, api.cpicpgx.org (`/v1/population_frequency_view`), Abruf 01.10.2026 | **CC BY-SA 4.0** (ClinPGx Data Usage Policy) | nur Gen, Allel, biogeografische Gruppe, Fallzahl, gewichteter Mittelwert; Gruppennamen übersetzt, Werte gerundet angezeigt |
| `data/pharmaco_zusatz.json` → `marken`, `atc`, `gruppe` (Quelle „EMA") | European Medicines Agency, Medicines table | © European Medicines Agency; Weiterverwendung mit Quellenangabe erlaubt | nur Monopräparate, exakte Namensgleichheit |
| `data/pharmaco_zusatz.json` → `marken`, `epc` (Quelle „openFDA") | openFDA NDC Directory | CC0 / gemeinfrei | nur Monopräparate, exakte Namensgleichheit |
| `data/pharmaco_zusatz.json` → `ix`, `atc` (Quelle „Wikidata") | Wikidata (P267, P769) | CC0 | unverändert; derzeit leer |
| `data/pharmaco_beispiel_roh.json` → `PharmCat` | PharmCAT-Report (pharmcat.clinpgx.org): Allel-Definitionen, Phänotypen, Leitlinientexte von CPIC, DPWG und FDA, kuratiert über ClinPGx | Software MPL 2.0; Inhalte **CC BY-SA 4.0** (ClinPGx Data Usage Policy); FDA-Labeltexte gemeinfrei; DPWG-Texte © KNMP in der ClinPGx-Annotation | auf die von der App gelesenen Felder gekürzt (`tools/40_build_pharmaco.py`, `kuerze_pharmcat`); Texte unverändert |
| `data/pharmaco_beispiel_roh.json` → `DRUG_*`, `Customer_GenotypeResults`, `OrderData` | Novogenia (Auswertung „Formel", Beispielkunde anonymisiert) | © Novogenia GmbH; die Begründungstexte fassen ClinPGx-Annotationen zusammen und übersetzen sie — Bearbeitung von ClinPGx-Inhalten, bei Weitergabe CC BY-SA 4.0 | anonymisiert (Name, Kontaktdaten) |
| `data/leitlinien_de.json` (Stammtabelle `uebersetzung/leitlinien_de.json`) | deutsche Übersetzung der Leitlinientexte (CPIC, DPWG, FDA über PharmCAT/ClinPGx, Stand 07.10.2026) und der Studientexte des Beispielkunden (ClinPGx, Stand 12.10.2026) durch Novogenia | Bearbeitung von CC-BY-SA-Inhalten → **CC BY-SA 4.0**; DPWG-Texte © KNMP (vor Veröffentlichung außerhalb des Klickdummys deren Bedingungen prüfen); FDA-Texte gemeinfrei | übersetzt, nicht validiert; in der App immer unter dem englischen Original und als „nicht validierte Übersetzung" gekennzeichnet |
| `data/pharmaco_wirkstoffe.json` | Novogenia (Wirkstoffliste) | © Novogenia GmbH | — |
| `data/textbloecke.json`, `app/`, `index.html` (Code) | Novogenia | © Novogenia GmbH, alle Rechte vorbehalten, solange nichts anderes vereinbart ist | — |

## Namensnennung (Wortlaut laut ClinPGx)

- Clinical annotations were obtained from ClinPGx (www.clinpgx.org) [25.09.2026].
- Clinical recommendations were provided by CPIC (www.clinpgx.org/cpic).
- Genotype-to-phenotype translation by PharmCAT (pharmcat.clinpgx.org).

## Zitierweise

- ClinPGx/PharmGKB: M. Whirl-Carrillo, R. Huddart, L. Gong, K. Sangkuhl,
  C.F. Thorn, R. Whaley, T.E. Klein. „An evidence-based framework for
  evaluating pharmacogenomics knowledge for personalized medicine." Clinical
  Pharmacology & Therapeutics (2021) 110(3):563–572. PMID 34216021.
- CPIC: K.E. Caudle, M. Whirl-Carrillo, M.V. Relling et al. „Advancing Clinical
  Pharmacogenomics Worldwide Through the Clinical Pharmacogenetics
  Implementation Consortium (CPIC)." Clinical Pharmacology & Therapeutics
  (2025) 118(6):1512–1522. PMID 40678821.
- PharmCAT: K. Sangkuhl, M. Whirl-Carrillo, R.M. Whaley et al.
  „Pharmacogenomics Clinical Annotation Tool (PharmCAT)." Clinical
  Pharmacology & Therapeutics (2020) 107(1):203–210. PMID 31306493.

## Bei Veröffentlichung

Wer `index.html` oder die Datendateien weitergibt (GitHub Pages, Kundenportal,
Bericht), muss diese Datei und die Hinweise in der App (Fußzeile, „Quellen und
Lizenzen") mitliefern und die abgeleiteten ClinPGx/CPIC-Dateien unter CC BY-SA
4.0 belassen. Die Nutzungsbedingungen von ClinPGx sprechen von
Forschungszwecken und untersagen den Verkauf der Daten als solche; die Nutzung
im Kundenbericht gilt nach Entscheidung von Daniel Wallerstorfer (29.09.2026)
als zulässig.
