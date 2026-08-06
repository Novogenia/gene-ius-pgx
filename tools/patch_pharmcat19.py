# -*- coding: utf-8 -*-
"""
Drei Aenderungen an den Wirkstoffkarten und der Demo-Kennzeichnung.

1. DEMO-KENNZEICHNUNG AUS DER OBERFLAECHE

   Vorgabe Daniel, 2026-08-06: "Entferne jegliche Referenz, dass es ein
   Demo-Genotyp waere. Es sollte einfach ein realistischer Genotyp sein,
   der hier dargestellt wird."

   Raus: das Banner in Genansicht und Startseite, die Demo-Pillen an den
   Positionen, die Statuszeile "Demo-Genotyp - kein gemessener Wert", der
   Satz "Die N Positionen unten sind erfunden" und die getrennte Zaehlung
   "20 gemessen, 468 mit Demo-Genotyp".

   Bleibt: die Herkunft im Dateikopf von data/dummy_genotypen.js, in
   DOKUMENTATION.md und in der Git-Historie. Das ist der
   Engineering-Nachweis, keine Anzeige - und ohne ihn koennte niemand mehr
   feststellen, welche Werte erfunden sind.

   Bleibt ebenfalls: istDemo() und die Regel aus v69, dass Demo-Positionen
   kein gemessenes Gen faerben. Das ist eine Korrektheitseigenschaft, kein
   Etikett, und sie haengt am Flag - nicht an der Beschriftung.

2. WIRKSTOFFKARTE ZEIGT MARKENNAMEN STATT DES ANWENDUNGSGEBIETS

   Vorgabe Daniel: "Entferne den Text 'Anwendung' und dann wofuer auch
   immer es sein sollte, und liste stattdessen die Markennamen auf, aber
   entferne auch den Text 'Markennamen'."

   Woertlich umgesetzt waere die Zeile bei 2.662 von 2.697 Karten leer -
   im Wirkstoff-Datenblock haben nur 35 Wirkstoffe Markennamen. Deshalb
   wird hier zugleich data/handelsnamen.json verdrahtet: 1.216 Eintraege,
   die seit der Datenpipeline gebaut, aber nie angeschlossen waren (offener
   Punkt 2 in Abschnitt 0). Damit kommen 1.216 statt 35 Karten zu einem
   Markennamen.

   ACHTUNG, steht auch in Abschnitt 8: das sind ueberwiegend US-Marken aus
   openFDA (Ziagen, ReoPro, Zytiga, Precose). Coumadin, Lopressor und
   Ultram fehlen dort. Fuer DACH gibt es keine freie Quelle. Die Namen
   werden ohne Kennzeichnung angezeigt, weil ausdruecklich keine
   Beschriftung gewuenscht ist - das ist eine bewusste Entscheidung, keine
   Nachlaessigkeit.

   Dubletten in der Quelle (abarelix -> Plenaxis, Plenaxis) werden beim
   Zusammenfuehren entfernt.

3. LINKS UND RECHTS DIESELBE KARTE UNTER "DEINE MEDIKAMENTE"

   Die Karten waren schon formgleich - 352x80, dieselbe Komponente. Der
   sichtbare Unterschied war die FARBE: rechts rechnet overallSev() die
   Wechselwirkungen mit der eigenen Liste ein, links stand nur listSev()
   mit der Genetik. Clopidogrel war links gruen und rechts rot - dasselbe
   Medikament, zwei Ampeln.

   Jetzt rendert die linke Spalte in dieser Ansicht mit demselben
   sevPool. Nebeneffekt und erwuenscht: ein Medikament, das mit der
   eigenen Liste kollidiert, zeigt das schon in der Suche.
"""
import io, json, os

APP = "index.html"
s = io.open(APP, encoding="ascii").read()
orig = len(s)
n = 0

# Handelsnamen als ASCII-JS aufbereiten: json.dumps mit ensure_ascii macht
# aus Umlauten \uXXXX, das ist gueltiges JavaScript und bleibt rein ASCII.
HN = json.load(io.open(os.path.join("data", "handelsnamen.json"), encoding="utf-8"))
HN = {k.lower(): sorted(set(v)) for k, v in HN.items() if v}
HN_JS = "const HNAMEN=%s;\n" % json.dumps(HN, separators=(",", ":"), ensure_ascii=True)
print("Handelsnamen: %d Wirkstoffe, %.1f kB" % (len(HN), len(HN_JS) / 1024.0))


def sub(alt, neu, was, anzahl=1, wo=None):
    global s, n
    c = s.count(alt)
    assert c == anzahl, "PATCH '%s': %d erwartet, %d gefunden" % (was, anzahl, c)
    if wo:
        i = s.index(alt)
        si, se = s.index("<style>"), s.index("</style>")
        assert (wo == "style") == (si < i < se), "PATCH '%s': falscher Bereich" % was
    s = s.replace(alt, neu)
    n += 1
    print("  ok  %s" % was)


print("Patche %s (%d Zeichen)" % (APP, orig))

# =================================================== 1. Demo-Kennzeichnung raus
sub("""function demoBannerHtml(kurz){
  if(typeof DUMMY_AKTIV==='undefined'||!DUMMY_AKTIV)return '';
  const z=geneZahlen();
  return `<div class="demoband">${ico('n-warn','',20)}
    <div class="dbt"><b>Ein Teil dieser Auswertung beruht auf Demo-Genotypen.</b>
      Gemessen wurden <b>${z.echt} Gene</b> aus dem PharmCAT-Lauf. Die weiteren
      <b>${z.demo} Gene</b> tragen <b>erfundene</b> Genotypen &mdash; sie zeigen, wie die
      Ansicht mit vollst&auml;ndigen Rohdaten aussehen wird. Keine dieser Angaben ist ein
      Messergebnis.${kurz?'':` Jede erfundene Stelle ist einzeln als
      <span class="demopill">Demo</span> gekennzeichnet; die gemessenen Gene tragen
      keine Demo-Werte in ihrer Bewertung.`}</div></div>`;
}""",
    """/* Die Herkunft der Genotypen steht nicht mehr in der Oberflaeche - Ansage
   Daniel, 2026-08-06. Nachvollziehbar bleibt sie im Kopf von
   data/dummy_genotypen.js, in DOKUMENTATION.md und in der Git-Historie.
   istDemo() bleibt in Kraft: die Regel aus v69, dass erfundene Positionen
   kein gemessenes Gen faerben, haengt am Flag und nicht am Etikett. */
function demoBannerHtml(kurz){return '';}""",
    "Demo-Banner leeren", wo="script")

sub("""        ${istDemo(p)?'<span class="demopill">Demo</span>':''}
""", "", "Demo-Pille an der Position entfernen", wo="script")

# Die zugehoerigen CSS-Regeln werden damit tot - raus, sonst bleibt der
# Begriff im Stylesheet stehen und die Zusicherung unten schlaegt zu Recht an.
sub("""  /* Demo-Genotypen: muss auf den ersten Blick als solche erkennbar sein */
  .demoband{display:flex;align-items:flex-start;gap:11px;background:#FFF8E6;
    border:1.5px solid #E8CE7A;border-radius:14px;padding:13px 16px;margin-bottom:16px}
  .demoband svg{flex:none;width:20px;height:20px;color:#8A6D1F;margin-top:1px}
  .demoband b{color:#6B540F}
  .demoband .dbt{font-size:13px;line-height:1.55;color:#6B540F;max-width:82ch}
  .demopill{display:inline-flex;align-items:center;gap:5px;background:#FFF3D1;color:#6B540F;
    border:1.5px solid #E8CE7A;border-radius:999px;padding:1px 9px;font-size:11px;font-weight:800;
    letter-spacing:.02em;vertical-align:middle}
  .gdemo{display:flex;align-items:center;gap:7px;font-size:11.5px;font-weight:750;color:#6B540F;
    background:#FFF8E6;border:1.5px solid #E8CE7A;border-radius:9px;padding:6px 9px;margin-top:9px}
  .gdemo svg{flex:none;width:14px;height:14px}
""", "", "CSS der Demo-Kennzeichnung entfernen", wo="style")

sub("""      <div class="gdemo">${ico('c-search','',14)} Demo-Genotyp &mdash; kein gemessener Wert</div>`;""",
    """      `;""",
    "Statuszeile 'Demo-Genotyp' entfernen", wo="script")

sub("""        <div class="gsec">Worauf das beruht</div>
        <div class="plain sm">F&uuml;r ${g} liegt in dieser Demo kein gemessener Genotyp vor.
          Die ${nP} Position${nP===1?'':'en'} unten sind <b>erfunden</b> und stehen nur, um zu
          zeigen, wie die Karte mit echten Werten aussehen wird.</div>
        ${gPosHtml(g)}""",
    """        <div class="gsec">Worauf das beruht</div>
        <div class="plain sm">F&uuml;r ${g} liegt kein Metabolisierertyp vor &mdash; das Gen
          wird ueber ${nP} einzelne Position${nP===1?'':'en'} bewertet.</div>
        ${gPosHtml(g)}""",
    "Kartentext ohne Demo-Bezug", wo="script")

sub("""    return `<div class="genecount">${z.echt} gemessene Gene${z.demo?' und '+z.demo+' mit Demo-Genotyp':''}${
      k.length>geneLimit?' &middot; '+geneLimit+' angezeigt':''}</div>""",
    """    return `<div class="genecount">${z.alle} Gene ausgewertet${
      k.length>geneLimit?' &middot; '+geneLimit+' angezeigt':''}</div>""",
    "Zaehlzeile ohne Aufteilung", wo="script")

sub("""        <div class="hsd">${gZ.demo?`${gZ.echt} gemessen, ${gZ.demo} mit Demo-Genotyp`
          :'die pharmakogenetisch entscheidenden Gene'}</div>""",
    """        <div class="hsd">die pharmakogenetisch entscheidenden Gene</div>""",
    "Startseite: Unterzeile ohne Aufteilung", wo="script")

# ============================================ 2. Markennamen auf der Karte
sub("""/* ===== BEGIN DEMO-GENOTYPEN (erzeugt, KEINE MESSWERTE) ===== */""",
    """/* ===== BEGIN HANDELSNAMEN (aus data/handelsnamen.json) =====
   Seit der Datenpipeline gebaut, bis hierher nie angeschlossen. Im
   Wirkstoff-Datenblock haben nur 35 der 2.697 Wirkstoffe einen
   Markennamen, hierueber sind es 1.216. Ueberwiegend US-Marken aus
   openFDA - siehe Abschnitt 8 der Doku. Schluessel ist der Wirkstoffname
   in Kleinschreibung. */
""" + HN_JS + """/* ===== END HANDELSNAMEN ===== */
/* ===== BEGIN DEMO-GENOTYPEN (erzeugt, KEINE MESSWERTE) ===== */""",
    "Handelsnamen einbetten", wo="script")

sub("""function listItemHtml(id,ctx){""",
    """/* Markennamen aus der Zusatzquelle nachziehen, ohne den Datenblock zu
   veraendern. Dubletten der Quelle (abarelix -> Plenaxis, Plenaxis)
   fliegen dabei raus. */
var _brandCache=null;
function brandsOf(id){
  if(!_brandCache){
    _brandCache={};
    if(typeof HNAMEN!=='undefined'){
      Object.keys(DRUGS).forEach(k=>{
        const nm=(DRUGS[k].name||'').toLowerCase();
        const t=HNAMEN[nm];
        if(t&&t.length)_brandCache[k]=[...new Set(t)];
      });
    }
  }
  const d=DRUGS[id];
  if(d.brands&&d.brands.length)return d.brands;
  return _brandCache[id]||[];
}
function listItemHtml(id,ctx){""",
    "brandsOf: Handelsnamen zusammenfuehren", wo="script")

sub("""        <div class="cbrands" title="${d.brands.length?d.brands.join(', '):(d.sub||'')}">${d.brands.length
          ?'<b>Markennamen:</b> '+d.brands.join(', ')
          :(d.sub?'<b>Anwendung:</b> '+d.sub:'<span class="nobr">keine Markennamen hinterlegt</span>')}</div>""",
    """        <div class="cbrands" title="${brandsOf(id).join(', ')}">${brandsOf(id).join(', ')}</div>""",
    "Kartenzeile: nur noch Markennamen, ohne Beschriftung", wo="script")

# ================================ 3. Links wie rechts unter "Deine Medikamente"
sub("""  el.innerHTML=show.map(i=>listItemHtml(i,'list')).join('')""",
    """  /* Unter "Deine Medikamente" muss die linke Karte genauso aussehen wie die
     rechte. Sie tat es nicht: rechts rechnet overallSev die Wechselwirkungen
     mit der eigenen Liste ein, links stand nur die Genetik - Clopidogrel war
     links gruen und rechts rot. Jetzt derselbe sevPool. */
  const opts=(view==='meine')?{sevPool:workspace}:null;
  el.innerHTML=show.map(i=>listItemHtml(i,'list',opts)).join('')""",
    "Liste unter 'Deine Medikamente' mit demselben sevPool", wo="script")

sub("""function listItemHtml(id,ctx){
  return `<div class="lirow">${cardHtml(id,ctx)}${addBtnHtml(id)}</div>`;
}""",
    """function listItemHtml(id,ctx,opts){
  return `<div class="lirow">${cardHtml(id,ctx,opts||{})}${addBtnHtml(id)}</div>`;
}""",
    "listItemHtml nimmt Optionen entgegen", wo="script")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
assert "Demo-Genotyp" not in s.split("/* ===== BEGIN DEMO-GENOTYPEN")[0], \
    "Demo-Bezug noch im Code vor dem Datenblock"
for wort in ("demopill", "gdemo", "Messergebnis", "sind <b>erfunden</b>"):
    # nur ausserhalb des erzeugten Datenblocks pruefen
    kopf = s.split("/* ===== BEGIN DEMO-GENOTYPEN")[0]
    rest = s.split("/* ===== END DEMO-GENOTYPEN ===== */")[-1]
    assert wort not in kopf and wort not in rest, "'%s' steht noch in der Oberflaeche" % wort
assert s.count("function brandsOf(") == 1, "brandsOf nicht genau einmal definiert"
# nur die Wirkstoffkarte pruefen - der Wechselwirkungsdialog fuehrt weiter
# eine Zeile "Anwendung", das ist eine andere Flaeche und war nicht gemeint
assert "'<b>Anwendung:</b> '+d.sub" not in s, "Anwendung steht noch auf der Karte"
assert "<b>Markennamen:</b>" not in s, "Markennamen-Beschriftung steht noch auf der Karte"
assert "keine Markennamen hinterlegt" not in s, "Platzhaltertext steht noch auf der Karte"
assert s.count("function istDemo(") == 1, "istDemo wurde entfernt - v69-Regel haengt daran"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
