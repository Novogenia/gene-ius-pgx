# GENE-IUS PGx — interaktiver Prototyp

Klickbarer Prototyp einer Pharmakogenetik-App: zeigt, wie das Genprofil einer Person die
Wirkung ihrer Medikamente verändert, prüft die Kombination auf Wechselwirkungen, schlägt
Wirkstoffe derselben Gruppe vor und erzeugt einen vollständigen Bericht für das
Arztgespräch.

### ▶ [Prototyp öffnen](https://evolutionnext696-prog.github.io/gene-ius-pgx/)

Eine einzige HTML-Datei, keine externen Abhängigkeiten, kein Server nötig.
Funktioniert auch offline: `index.html` herunterladen und im Browser öffnen.

---

## Für Testerinnen und Tester

Die App zeigt eine **erfundene Demo-Patientin, „Lisa M."** mit 13 pharmakogenetisch
relevanten Genen. Alle personenbezogenen Daten sind fiktiv.

Ein Rundgang durch die wichtigsten Funktionen:

1. **Start** — persönliche Kennzahlen und die Verteilung der 2.697 Wirkstoffe auf
   OK / Achtung / Alarm. Die farbigen Kacheln sind anklickbar.
2. **Deine Medikamente** — links suchen, mit dem **Herz** auf die Liste setzen (oder die
   Karte nach rechts ziehen). Clopidogrel und Omeprazol sind schon drauf und über eine
   rote Verbindung verknüpft — das Warnsymbol anklicken.
3. **Deine Gene** — 13 Genkarten, schwerste zuerst. Karte anklicken für Klartext, die zwei
   Genkopien und die im Test untersuchten Allele.
4. **Für deinen Arzt** — der vollständige Bericht, druckbar.
5. **Alle Medikamente** — die Datenbank mit Ampelfiltern.

Überall, wo ein **?** steht, gibt es eine Erklärung in Alltagssprache.

Rückmeldungen bitte als [Issue](../../issues) oder direkt an Daniel.

---

## Datengrundlage

| Quelle | Beitrag |
|---|---|
| `All Drugs V12.xlsx` (Novogenia) | 2.694 Wirkstoffe, ATC-Ebenen 1–4, Enzym-Rollen für 41 Enzyme |
| `Pharmgkb drug recommendations V4.xlsx` (Novogenia) | 100 genotypspezifische Empfehlungen für 42 Wirkstoffe |
| CPIC / DPWG | Leitlinienkennzeichnung |
| DrugBank (über den Novogenia-Export) | Wechselwirkungsangaben |

Aufbereitung: [docs/DOKUMENTATION.md](docs/DOKUMENTATION.md) ·
Quellenrecherche: [docs/DATENQUELLEN_RECHERCHE.md](docs/DATENQUELLEN_RECHERCHE.md)

---

## Wichtige Hinweise

> **Kein Medizinprodukt.** Prototyp zu Demonstrationszwecken. Die Bewertungen beschreiben
> ausschließlich den genetisch bedingten Anteil der Arzneimittelwirkung. Alter, Nieren- und
> Leberfunktion, Begleiterkrankungen und weitere Medikamente sind nicht berücksichtigt.
> Keine Grundlage für Therapieentscheidungen.

**„Andere Wirkstoffe derselben Gruppe" sind keine geprüften Alternativen.** Grundlage ist
die ATC-Klassifikation, also die amtliche Substanzklasse — keine belegte therapeutische
Austauschbarkeit. Sammelgruppen wie „Antidote" sind in der App als solche gekennzeichnet.

**Lizenzhinweis zu den Daten.** Der eingebettete Datenblock enthält aus **DrugBank**
abgeleitete Wechselwirkungsangaben. DrugBank stellt seine frei verfügbaren Datensätze unter
**CC BY-NC 4.0** (nicht-kommerzielle Nutzung). Dieses Repository dient ausschließlich der
internen Erprobung des Prototyps. Vor einer kommerziellen Verwendung ist die Lizenzlage zu
klären — die Alternativen sind in
[docs/DATENQUELLEN_RECHERCHE.md](docs/DATENQUELLEN_RECHERCHE.md), Abschnitt 3, aufgeführt.

---

© Novogenia GmbH, Salzburg — Prototyp, Stand Juli 2026
