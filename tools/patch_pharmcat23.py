# -*- coding: utf-8 -*-
"""
Vier Korrekturen aus Daniels Rueckmeldung vom 2026-08-08 (zweite Runde).

1. EINE AUFZAEHLUNG STATT ZWEI

   Vorgabe: "Mache nicht zwei separate Aufzaehlungen, sondern zaehle auch die
   Wechselwirkungen in der ersten Aufzaehlung auf." Aus den zwei Spalten wird
   eine Reihe; die Paarzahl bleibt als Fussnote.

2. UEBERSCHRIFT IM ARZTBERICHT GROESSER

   "Die geht zu sehr unter." Der Abdeckungsblock bekommt eine echte
   Ueberschrift statt der kleinen Kopfzeile.

3. ALLE UEBRIGEN GENOTYPEN KOMPAKT DAZU

   Die Tabelle zeigt die Panel-Gene mit Diplotyp. Die uebrigen 468 Gene
   standen im Bericht gar nicht. Sie kommen jetzt als dichtes Raster
   darunter - Genname, Zustand, Zahl der Positionen -, auffaellige zuerst.

4. ZWEI ANZEIGEFEHLER BEI CLOPIDOGREL, beide von Daniel gefunden

   a) "Warum ist normaler Metabolisierer bei CYP2C19 mit gelber Schrift?"

      Weil die Statuszeile die KARTENFARBE nahm, nicht die des Phaenotyps.
      CYP2C19 ist Phaenotyp ok/gruen, die Karte steht auf warn wegen drei
      rs-Befunden der Evidenzstufe 3 (rs12248560, rs4244285, rs4986893).
      Ein gruener Metabolisierertyp in gelber Schrift liest sich wie ein
      Fehler. Die Zeile nimmt jetzt die Farbe des Phaenotyps; die Karte
      bleibt gelb, und die Befundzeile darunter sagt warum.

   b) "Warum gibt es einen Alarm, wenn die Person bei beiden relevanten
      Genen normaler Metabolisierer ist?"

      Weil der Alarm nicht aus der Genetik kommt, sondern aus der
      Wechselwirkung mit Omeprazol. statusFor liefert korrekt ok. Nur stand
      im Beurteilungskasten weiter "Es ist keine Anpassung noetig", waehrend
      oben ALARM prangte - die Ursache war nirgends benannt.

      Der Kasten sagt jetzt ausdruecklich, dass die Stufe aus der
      Wechselwirkung kommt und welcher Partner sie ausloest.
"""
import io

APP = "index.html"
s = io.open(APP, encoding="ascii").read()
orig = len(s)
n = 0


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

# ============================================== 1. Eine Aufzaehlung
sub("""  .ixs-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px 26px}
  @media(max-width:760px){.ixs-grid{grid-template-columns:1fr}}""",
    """  .ixs-grid{display:block}""",
    "CSS: Bilanz einreihig", wo="style")

sub("""  return `<div class="ixscore">
    <div class="ixs-grid">
      <div class="ixs-col">
        <div class="ist">Deine Medikamente</div>
        <div class="ixs-row">
          ${kachel('neutral',workspace.length,'auf der Liste')}
          ${kachel('crit',m.crit,'mit Alarm')}
          ${kachel('warn',m.warn,'mit Achtung')}
          ${kachel('ok',m.ok,'unauff&auml;llig')}
        </div>
      </div>
      <div class="ixs-col">
        <div class="ist">Wechselwirkungen</div>
        <div class="ixs-row">
          ${kachel('crit',z.crit,'mit Alarm')}
          ${kachel('warn',z.warn,'mit Achtung')}
          ${kachel('done',z.done,'gel&ouml;st')}
          ${kachel('ok',z.ok,'unauff&auml;llig')}
        </div>
        <div class="ixs-sum">${z.paare} Paar${z.paare===1?'':'e'} gepr&uuml;ft &mdash;
          jede Kombination deiner Medikamente einzeln</div>
      </div>
    </div>
  </div>`;""",
    """  /* Eine Reihe, nicht zwei Bloecke (Vorgabe Daniel, 2026-08-08). Die
     Wechselwirkungen stehen als eigene Kacheln in derselben Aufzaehlung,
     durch einen Trenner abgesetzt. */
  return `<div class="ixscore">
    <div class="ist">Deine Liste auf einen Blick</div>
    <div class="ixs-row">
      ${kachel('neutral',workspace.length,'Medikamente')}
      ${kachel('crit',m.crit,'mit Alarm')}
      ${kachel('warn',m.warn,'mit Achtung')}
      ${kachel('ok',m.ok,'unauff&auml;llig')}
      <span class="ixs-trenn"></span>
      ${kachel('crit',z.crit+z.warn,z.crit+z.warn===1?'Wechselwirkung':'Wechselwirkungen')}
      ${kachel('done',z.done,'davon gel&ouml;st')}
    </div>
    <div class="ixs-sum">${z.paare} Paar${z.paare===1?'':'e'} gepr&uuml;ft &mdash;
      jede Kombination deiner Medikamente einzeln</div>
  </div>`;""",
    "Bilanz als eine Aufzaehlung", wo="script")

sub("""  .ixs-row{display:flex;gap:18px;flex-wrap:wrap}""",
    """  .ixs-row{display:flex;gap:18px;flex-wrap:wrap;align-items:center}
  .ixs-trenn{flex:none;width:1px;align-self:stretch;background:var(--line2);margin:2px 4px}""",
    "CSS: Trenner in der Reihe", wo="style")

# ======================================== 2+3. Arztbericht: Kopf und Genotypen
sub("""  .cov-h{display:flex;align-items:center;gap:9px;padding:11px 15px;background:var(--plum-050);""",
    """  .cov-h{display:flex;align-items:center;gap:10px;padding:14px 18px;background:var(--plum-050);
    font-size:17px;font-weight:800;letter-spacing:-.01em;""",
    "CSS: Ueberschrift des Abdeckungsblocks groesser", wo="style")

sub("""  .cov-tab{width:100%;border-collapse:collapse;margin-top:11px;font-size:11.5px}""",
    """  .cov-sub{font-size:14px;font-weight:800;letter-spacing:-.01em;margin:16px 0 8px;color:var(--ink)}
  /* Alle uebrigen Gene, dicht gesetzt */
  .cov-rest{display:grid;grid-template-columns:repeat(auto-fill,minmax(168px,1fr));gap:5px 12px}
  .cov-rg{display:flex;align-items:center;gap:7px;font-size:12px;min-width:0}
  .cov-rd{flex:none;width:8px;height:8px;border-radius:50%}
  .cov-rd.ok{background:var(--ok)} .cov-rd.warn{background:var(--warn)}
  .cov-rd.crit{background:var(--crit)}
  .cov-rn{font-weight:750;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .cov-rp{flex:none;color:var(--faint);font-size:11px}
  .cov-tab{width:100%;border-collapse:collapse;margin-top:11px;font-size:11.5px}""",
    "CSS: kompaktes Raster der uebrigen Gene", wo="style")

sub("""      <table class="cov-tab">
        <thead><tr><th>Gen</th><th>Diplotyp</th><th>Ph&auml;notyp</th><th>Score</th>""",
    """      <div class="cov-sub">Gene mit Diplotyp-Auswertung (${zeigbar.length})</div>
      <table class="cov-tab">
        <thead><tr><th>Gen</th><th>Diplotyp</th><th>Ph&auml;notyp</th><th>Score</th>""",
    "Arztbericht: Ueberschrift ueber der Tabelle", wo="script")

sub("""      <p class="cov-p">Die Tabelle f&uuml;hrt die <b>${zeigbar.length} Gene mit
        Diplotyp-Auswertung</b> aus dem PharmCAT-Panel. Die &uuml;brigen Gene werden
        &uuml;ber einzelne Positionen bewertet und stehen unter &bdquo;Deine Gene&ldquo;.</p>
""", "", "Arztbericht: alten Einordnungssatz entfernen", wo="script")

sub("""        <tbody>${rows}</tbody></table>
    </div></div>`;""",
    """        <tbody>${rows}</tbody></table>
      ${(()=>{
        /* Alle uebrigen Gene - die ohne Diplotyp, nur ueber Einzelpositionen
           bewertet. Standen bisher gar nicht im Bericht. Auffaellige zuerst. */
        const rest=geneListe().filter(g=>!zeigbar.some(z=>z.g===g));
        if(!rest.length)return '';
        const srt=rest.slice().sort((a,b)=>{
          const R={crit:0,warn:1,ok:2,ultra:2,unk:3};
          return (R[geneSev(a)]||3)-(R[geneSev(b)]||3)||a.localeCompare(b);});
        const auff=srt.filter(g=>['warn','crit'].indexOf(geneSev(g))>=0).length;
        return `<div class="cov-sub">Weitere ausgewertete Gene (${rest.length})</div>
          <p class="cov-p" style="margin:0 0 9px">Ohne Diplotyp, bewertet &uuml;ber
            einzelne Positionen &mdash; <b>${auff}</b> davon auff&auml;llig.</p>
          <div class="cov-rest">${srt.map(g=>{
            const sv=geneSev(g), nP=(RS_BY[g]||[]).length;
            return `<div class="cov-rg"><span class="cov-rd ${sv}"></span>
              <span class="cov-rn">${g}</span>
              <span class="cov-rp">${nP}</span></div>`;}).join('')}</div>`;})()}
    </div></div>`;""",
    "Arztbericht: uebrige Gene kompakt", wo="script")

# ================================ 4a. Statuszeile in der Farbe des Phaenotyps
sub("""  const colr=sv==='ultra'?'#0b6b36':sv==='ok'?'var(--ok-t)':sv==='warn'?'var(--warn-t)'
    :sv==='unk'?'var(--unk-t)':'var(--crit-t)';""",
    """  /* Die Statuszeile nennt den Metabolisierertyp - also traegt sie dessen
     Farbe, nicht die der Karte. Sonst stand "Normaler Metabolisierer" in
     Gelb, weil ein rs-Befund der Stufe 3 die Karte gelb faerbt. Von Daniel
     gefunden, 2026-08-08. Die Karte bleibt gelb, die Befundzeile sagt warum. */
  const fsv=nurPos?sv:(has?GSEV[lvl]:sv);
  const colr=fsv==='ultra'?'#0b6b36':fsv==='ok'?'var(--ok-t)':fsv==='warn'?'var(--warn-t)'
    :fsv==='unk'?'var(--unk-t)':'var(--crit-t)';""",
    "Genkarte: Statuszeile in der Farbe des Phaenotyps", wo="script")

# ============================ 4b. Ursache der Stufe im Beurteilungskasten
sub("""    <div class="ab-plain">${st.text}</div>""",
    """    <div class="ab-plain">${st.text}</div>
    ${(()=>{
      /* Kommt die Stufe nicht aus der Genetik, sondern aus einer
         Wechselwirkung, muss das hier stehen. Sonst prangt oben ALARM und
         daneben "Es ist keine Anpassung noetig" - genau das war bei
         Clopidogrel der Fall (Genetik ok, Alarm durch Omeprazol). */
      const off=ddisOffen(id,workspace).filter(x=>RANK[x.sev]>RANK[st.sev]);
      if(!off.length)return '';
      const schaerfste=off.slice().sort((a,b)=>RANK[b.sev]-RANK[a.sev])[0];
      const partner=off.map(x=>DRUGS[x.a===id?x.b:x.a].name);
      return `<div class="ab-ursache s-${schaerfste.sev}">${ico('c-ix','',16)}
        <div><b>${SLABEL[schaerfste.sev]} kommt nicht aus deinen Genen</b>, sondern aus
          der Wechselwirkung mit <b>${partner.join(', ')}</b>. Genetisch ist
          ${d.name} f&uuml;r dich ${SLABEL[st.sev].toLowerCase()==='ok'?'unauff&auml;llig':SLABEL[st.sev]}.</div></div>`;})()}""",
    "Beurteilung: Ursache der Stufe benennen", wo="script")

sub("""  .ab-fremd{opacity:.72;border-left:3px solid var(--line2);padding-left:11px;margin-top:10px}""",
    """  .ab-ursache{display:flex;gap:9px;align-items:flex-start;font-size:12.5px;line-height:1.55;
    border-radius:11px;padding:9px 12px;margin-top:10px;background:var(--warn-bg);color:var(--warn-t)}
  .ab-ursache.s-crit{background:var(--crit-bg);color:var(--crit-t)}
  .ab-ursache svg{flex:none;width:16px;height:16px;margin-top:1px}
  .ab-ursache b{font-weight:800}
  .ab-fremd{opacity:.72;border-left:3px solid var(--line2);padding-left:11px;margin-top:10px}""",
    "CSS: Ursachenhinweis", wo="style")

# ------------------------------------------------------------------ Kontrolle
assert all(ord(c) < 128 for c in s), "nicht mehr rein ASCII"
assert s.count("ixs-trenn") == 2, "Trenner nicht sauber gesetzt"
assert s.count("ab-ursache") >= 4, "Ursachenhinweis fehlt"
assert s.count("cov-rest") == 2, "Genraster im Bericht fehlt"
assert "const fsv=" in s, "Farbe der Statuszeile nicht umgestellt"
# fsv braucht nurPos und lvl - beide muessen vorher deklariert sein
assert s.index("const nurPos=") < s.index("const fsv="), "nurPos steht hinter fsv (TDZ)"
io.open(APP, "w", encoding="ascii", newline="\n").write(s)
print("\n%d Ersetzungen. Datei: %d -> %d Zeichen" % (n, orig, len(s)))
