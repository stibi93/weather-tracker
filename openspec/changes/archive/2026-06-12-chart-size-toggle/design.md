## Context

A `water-level-detail-panel` grafikonja fix méretű (400×260). Kis, csak-frontend bővítés:
méret-váltó gomb.

## Goals / Non-Goals

**Goals:** gomb a normál ↔ nagyított grafikon-méret váltásához; nagyítva a panel a képernyő
közepén, nagyobb grafikonnal.
**Non-Goals:** ingest/adat változás; folyamatos (drag) átméretezés.

## Decisions

- **Két állapot (normál/nagyított) React state-ben.** A `DetailPanel` `expanded` flag-je
  vezérli a `Chart` méreteit és a panel CSS-osztályát. *Miért X Y helyett:* két jól definiált
  méret elég és kiszámítható; a szabad átméretezés felesleges komplexitás.
- **Nagyított méret a viewporthoz igazítva.** Nagyítva a grafikon szélessége
  `min(viewportszélesség − margó, ~900px)`, magassága ~460px; a panel középre kerül.
  *Miért:* ne lógjon ki kisebb képernyőn.
- **A `Chart` újrarajzol méretváltáskor.** A uPlot a `width`/`height` prop változására
  újrainicializál (a meglévő effect-függőség miatt) — nincs külön logika.

## Risks / Trade-offs

- [Átméretezés nyitott panel mellett (ablak-resize)] → ritka eset; a nagyított szélesség a
  váltáskor/rendereléskor számolódik. Egy `resize` figyelő frissíti, ha nyitva van.
