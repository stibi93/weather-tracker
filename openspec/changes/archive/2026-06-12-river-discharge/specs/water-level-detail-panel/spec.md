## ADDED Requirements

### Requirement: Metrika-váltó (vízállás / vízhozam)
Ahol a víztesthez van vízhozam-adat (folyók), a részletpanel SHALL kínáljon egy metrika-váltót,
amellyel a grafikon fővonala és bal tengelye **vízállás (cm)** és **vízhozam (m³/s)** között vált.
A csapadék-oszlopok mindkét nézetben láthatók. Ahol nincs vízhozam (tavak), a váltó nem jelenik meg.

#### Scenario: Váltás vízhozamra
- **WHEN** a felhasználó egy folyó paneljén a vízhozam metrikát választja
- **THEN** a grafikon fővonala a vízhozamot (m³/s) mutatja a bal tengelyen, a csapadék-oszlopok maradnak

#### Scenario: Tónál nincs váltó
- **WHEN** a felhasználó egy tó paneljét nyitja meg
- **THEN** a metrika-váltó nem jelenik meg, csak a vízállás látszik

#### Scenario: Tooltip az aktív metrikával
- **WHEN** a felhasználó a grafikon egy pontja fölé viszi a kurzort vízhozam nézetben
- **THEN** a tooltip a dátumot, a vízhozamot (m³/s) és a csapadékot (mm) mutatja
