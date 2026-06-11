## Context

A foundation a teljes láncot bizonyította egy adatdoménon, de csak rövid idősorral és
hover-tooltippel. Ez a change a fő interakciót adja hozzá: kattintás → többéves grafikon.
A vizugy API dátumtartomány-lekérése bizonyítottan ad többéves napi adatot (Balaton: 4180
napi pont 2015–2026; a folyók órásban, amit a meglévő adapter napi szintre aggregál).

## Goals / Non-Goals

**Goals:**
- ~10 év historikus vízállás betöltése a kanonikus tárba (idempotens backfill).
- Kompakt, többéves artifact: napi a friss ~2 évre, havi átlag a régebbire.
- Kattintásra nyíló oldalpanel többéves grafikonnal és időtartomány-választóval.

**Non-Goals:**
- Csapadék-domén, valódi tó/folyó geometria, CI/ütemezés (külön change-ek).
- Több állomás víztestenként (továbbra is egy reprezentatív állomás).

## Decisions

- **Backfill a meglévő `run`-ra építve, `years` paraméterrel.** A `run(days=...)` mellé
  `run_backfill(years=10)` (vagy `--years`), amely a `today - years*365 .. today` tartományt
  húzza le egy TS-lekéréssel állomásonként. *Miért:* a tárolás már idempotens; a backfill
  csak egy nagyobb dátumtartomány — nincs új tárolási logika.
- **Aggregálás az artifact-generátorban, nem a tárban.** A kanonikus tár napi felbontást őriz;
  az artifact-réteg számolja a havi átlagot a régebbi évekre. *Miért:* a tár maradjon teljes
  felbontású igazságforrás; az aggregálás megjelenítési döntés.
- **Felbontás-küszöb: utolsó ~2 év napi, azelőtt havi.** *Alternatíva:* mindig napi —
  elvetve a fájlméret és a grafikon-teljesítmény miatt; ~2 év napi elég részletes a közelképhez.
- **Chart-lib: uPlot.** Apró (~40 KB), canvas-alapú, több ezer pontot is gyorsan rajzol.
  *Miért X Y helyett:* a Recharts (SVG) több ezer pontnál lassú; a uPlot pont erre való.
  Imperatív API-ját egy vékony React-wrapper kezeli (ref + effect).
- **Kiválasztás React state-ben.** A térkép-kattintás beállítja a kiválasztott víztest id-t;
  a panel ebből tölti a `water-levels/{id}.json`-t és rajzol. Bezárás = state null.

## Risks / Trade-offs

- [Nagy backfill-válasz: órás folyók 10 év ~100k pont/állomás] → Egy TS-lekérés állomásonként
  ezt elbírja (tesztelve); ha gond lesz, évekre chunkolható. Az adapter napi aggregálása a
  tárolt méretet ~4200/állomásra szorítja.
- [uPlot imperatív API React-ben] → izolált wrapper-komponens (ref, cleanup), így a React-fa
  tiszta marad.
- [Artifact-méret] → a napi+havi aggregálás ~850 pont/víztest (~25 KB), lazy módon töltve.

## Migration Plan

Additív, nincs törő változás. A backfill kézzel futtatható; az artifactok újragenerálódnak.
Rollback = a régebbi (rövid sorozatú) artifactokra visszaállás újragenerálással.

## Open Questions

- A napi/havi küszöb pontos értéke (2 év) finomítható vizuális ellenőrzéssel.
