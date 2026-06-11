## Why

A részletpanel jelenleg kicsi, és a grafikon nem ad pontos leolvasást: hoverre nem
látszik az adott nap dátuma és vízállás-értéke. A „mélyebb betekintés" élményhez a panel
legyen nagyobb/olvashatóbb, a grafikon pedig adjon pontos értéket a kurzor alatt.

## What Changes

- A részletpanel nagyobb, olvashatóbb megjelenést kap (szélesebb panel, nagyobb grafikon).
- A grafikonon a kurzort mozgatva tooltip jelzi az adott pont **dátumát és pontos
  vízállás-értékét** (cm), a kurzorhoz igazítva.

## Capabilities

### Modified Capabilities
- `water-level-detail-panel`: új követelmény a grafikon hover-tooltipjéről (dátum + pontos érték).

## Impact

- `web`: `Chart` komponens kurzor-tooltip pluginnal; `DetailPanel`/`styles.css` nagyobb méretek.
- Nincs ingest/adat hatás.
