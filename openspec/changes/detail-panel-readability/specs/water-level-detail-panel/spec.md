## ADDED Requirements

### Requirement: Grafikon hover-tooltip
A részletpanel grafikonján a kurzort egy pont fölé mozgatva a rendszer SHALL megjelenítsen
egy tooltipet az adott pont **dátumával** és **pontos vízállás-értékével** (cm), a kurzorhoz
igazítva. A kurzor elhagyásakor a tooltip eltűnik.

#### Scenario: Pontos érték a kurzor alatt
- **WHEN** a felhasználó a grafikon egy adatpontja fölé viszi a kurzort
- **THEN** megjelenik az adott nap dátuma és a vízállás pontos értéke cm-ben

#### Scenario: Tooltip eltűnik
- **WHEN** a kurzor elhagyja a grafikon területét
- **THEN** a tooltip eltűnik
