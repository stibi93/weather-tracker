## ADDED Requirements

### Requirement: Másodlagos kontextus-váltó (csapadék / hőmérséklet)
A részletpanel SHALL kínáljon egy másodlagos kontextus-váltót, amellyel a grafikon jobb
tengelyén megjelenített réteg **csapadék** (oszlop, mm) és **hőmérséklet** (vonal, °C) között
vált. A fővonal (vízállás/vízhozam) változatlan marad; a hover-tooltip az aktív másodlagos
értéket mutatja.

#### Scenario: Váltás hőmérsékletre
- **WHEN** a felhasználó a hőmérséklet kontextust választja
- **THEN** a grafikon jobb tengelye a hőmérsékletet (°C) mutatja vonalként, a csapadék-oszlopok helyett

#### Scenario: Tooltip az aktív másodlagos értékkel
- **WHEN** a felhasználó a grafikon egy pontja fölé viszi a kurzort hőmérséklet nézetben
- **THEN** a tooltip a dátumot, a fő metrikát és a hőmérsékletet (°C) mutatja
