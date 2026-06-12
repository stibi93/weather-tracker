## ADDED Requirements

### Requirement: Csapadék a vízállás-grafikonon
A részletpanel grafikonja a vízállás-vonal mellett SHALL megjelenítse a területi napi
csapadékot oszlopként, külön (jobb oldali) mm-tengelyen, hogy az összefüggés (eső → vízállás)
vizuálisan látszódjon. A hover-tooltip a dátum és vízállás mellett a csapadékot is SHALL kiírja.

#### Scenario: Csapadék-oszlopok a vonal mögött
- **WHEN** a felhasználó megnyit egy víztest részletpaneljét
- **THEN** a grafikonon a vízállás-vonal mögött csapadék-oszlopok láthatók saját mm-tengelyen

#### Scenario: Tooltip a csapadékkal
- **WHEN** a felhasználó a grafikon egy pontja fölé viszi a kurzort
- **THEN** a tooltip a dátumot, a vízállást (cm) és a csapadékot (mm) is mutatja
