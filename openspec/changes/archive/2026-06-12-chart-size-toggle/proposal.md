## Why

A részletpanel grafikonja a nagyítás ellenére is kicsi a részletek (napi ingadozás,
csapadék-csúcsok) alapos megnézéséhez. Kell egy gomb, amivel a felhasználó **nagyobb
nézetre** válthatja a grafikont, és vissza kisebbre.

## What Changes

- A részletpanelen egy **méret-váltó gomb**: a grafikont (és a panelt) normál ↔ nagyított
  méret között kapcsolja.
- Nagyított nézetben a panel a képernyő közepére kerül, a grafikon jelentősen nagyobb.

## Capabilities

### Modified Capabilities
- `water-level-detail-panel`: új követelmény — a grafikon mérete gombbal váltható (normál/nagyított).

## Impact

- `web`: `DetailPanel` méret-állapot + gomb; `Chart` a kapott méretekkel; CSS a nagyított panelhez.
- Nincs ingest/adat hatás.
