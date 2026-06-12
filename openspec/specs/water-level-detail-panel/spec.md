# water-level-detail-panel Specification

## Purpose
TBD - created by archiving change water-level-history-chart. Update Purpose after archive.
## Requirements
### Requirement: Kattintásra nyíló részletpanel
A felhasználó egy víztestre kattintva SHALL egy oldalpanelt kapjon, amely a víztest
többéves vízállás-grafikonját mutatja a `water-levels/{id}.json` adatból, a víztest
nevével és a legutóbbi értékkel.

#### Scenario: Panel megnyitása
- **WHEN** a felhasználó a térképen egy víztestre kattint
- **THEN** megnyílik az oldalpanel az adott víztest nevével, legutóbbi vízállásával és a
  többéves grafikonnal

### Requirement: Időtartomány-választó
A részletpanel SHALL kínáljon időtartomány-választót (pl. 1 év / 5 év / teljes), amely a
grafikon megjelenített tartományát szűri.

#### Scenario: Tartomány szűrése
- **WHEN** a felhasználó más időtartományt választ
- **THEN** a grafikon a kiválasztott tartományra frissül, a panel többi tartalma változatlan

### Requirement: Panel bezárása
A felhasználó SHALL be tudja zárni a részletpanelt, visszatérve a teljes térkép-nézethez.

#### Scenario: Bezárás
- **WHEN** a felhasználó a panel bezáró vezérlőjére kattint
- **THEN** a panel eltűnik, a térkép újra teljes nézetben látszik

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

### Requirement: Grafikon méret-váltó
A részletpanel SHALL kínáljon egy gombot, amellyel a grafikon (és a panel) normál és
nagyított méret között váltható. A nagyított nézet érezhetően nagyobb grafikont mutat, és a
gomb ismételt megnyomására visszatér a normál méretre.

#### Scenario: Nagyobb nézetre váltás
- **WHEN** a felhasználó a méret-váltó gombra kattint normál nézetben
- **THEN** a grafikon (és a panel) nagyított méretre vált

#### Scenario: Vissza normál méretre
- **WHEN** a felhasználó a méret-váltó gombra kattint nagyított nézetben
- **THEN** a grafikon és a panel visszatér a normál méretre

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

### Requirement: Párolgás a másodlagos kontextus-váltóban
A részletpanel másodlagos kontextus-váltója SHALL kínáljon egy harmadik opciót, a **párolgást**
(ET₀, vonal, mm), a csapadék és a hőmérséklet mellett. A kiválasztott réteg a grafikon jobb
tengelyén jelenik meg; a hover-tooltip az aktív másodlagos értéket mutatja.

#### Scenario: Váltás párolgásra
- **WHEN** a felhasználó a párolgás kontextust választja
- **THEN** a grafikon jobb tengelye az ET₀-t (mm) mutatja vonalként, és a tooltip a párolgást is kiírja

