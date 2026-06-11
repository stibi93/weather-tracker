## Context

A `water-level-detail-panel` foundation-szintű grafikonja statikus (nincs pontos
leolvasás), és a panel kicsi. Kis, csak-frontend finomítás.

## Goals / Non-Goals

**Goals:** nagyobb, olvashatóbb panel; grafikon hover-tooltip dátummal + pontos cm-értékkel.
**Non-Goals:** ingest/adat változás; új capability.

## Decisions

- **uPlot kurzor-tooltip plugin, nem a beépített legend.** Egy kis plugin a `setCursor`
  hookra: a `u.cursor.idx`-ből kiolvassa a dátumot és értéket, és egy abszolút pozícionált
  div-et igazít a kurzorhoz. *Miért X Y helyett:* a beépített legend külön sávban jelenne meg;
  a kurzorhoz tapadó tooltip pontosabb és letisztultabb, illik a (C) földes stílushoz.
- **Méretek a DetailPanelben/CSS-ben.** Szélesebb panel és nagyobb grafikon (a tooltiphez a
  grafikon-konténer `position: relative`). *Miért:* a méret megjelenítési döntés, nem spec-szintű.

## Risks / Trade-offs

- [uPlot plugin lifecycle] → a tooltip-div a wrapper-konténerben él, a uPlot `destroy`-jal együtt
  takarítódik (a komponens újrarajzol tartomány-/víztest-váltáskor).
