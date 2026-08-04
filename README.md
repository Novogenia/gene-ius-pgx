# GENE-IUS PGx

Clickdummy für eine Pharmakogenetik-App. Eine einzige HTML-Datei, kein Build-Schritt.
2.697 Wirkstoffe, gegen ein echtes Genprofil aus einem PharmCAT-3.2.0-Lauf bewertet.

**Prototyp zur Abstimmung — kein Medizinprodukt, keine Therapieentscheidung.**

## Anfangen

1. **`docs/DOKUMENTATION.md`, Abschnitt 0** lesen. Das ist der Schnellstart und
   erklärt in fünf Minuten Aufbau, Datenquellen, Regeln und offene Punkte.
2. Danach Abschnitt 6 (Fallstricke) und 11 (PharmCAT).
3. `index.html` im Browser öffnen.

## Repository

`origin` ist **Azure DevOps**:

```
https://novogenia@dev.azure.com/novogenia/BusinessVibeCodes/_git/pharmacogenetics
```

`github` speist nur die öffentliche Testseite. Beim Pushen beide bedienen:

```
git push origin main
git push github main
```

Git über cmd-Batchdateien, nicht PowerShell — PowerShell kehrt bei git zu früh
zurück und schlägt still fehl.

## Inhalt

| Pfad | Was |
|---|---|
| `index.html` | die App, 685 kB, rein ASCII |
| `docs/DOKUMENTATION.md` | Aufbau, Herleitungsregeln, Fallstricke, Änderungsverlauf |
| `docs/DATENQUELLEN_RECHERCHE.md` | Recherche zu Alternativ- und Interaktionsquellen |
| `tools/` | Generatoren und die angewandten Umbauten, chronologisch |
| `data/` | Ergebnisse der Datenpipeline — gebaut, aber noch nicht in der App |

## Die drei Regeln

1. **Nichts erfinden.** Was PharmCAT nicht ruft, bleibt sichtbar „nicht bestimmbar".
2. **Rein ASCII.** Umlaute als HTML-Entities; jedes Skript prüft das.
3. **Ersetzungen mit Zusicherung** — Anker genau einmal *und* im richtigen Bereich
   (`<style>` vs. `<script>`).

## Datengrundlage

Genprofil: Probe **NA17454** aus dem PharmCAT-Validierungslauf vom 2026-07-30
(40 Proben). Ein öffentliches Coriell-Referenzgenom — kein Kundendatensatz.

Empfehlungen: PharmCAT-Reporter (CPIC, DPWG, FDA) plus Novogenias eigene
Leitlinienmatrix. Wirkstoffe, ATC-Klassifikation und Wechselwirkungen aus den
Novogenia-Quelldateien.

Lizenzhinweis: DrugBank-Ableitungen sind CC BY-NC — nicht kommerziell nutzbar,
solange keine Lizenz vorliegt. Details in `docs/DATENQUELLEN_RECHERCHE.md`.
