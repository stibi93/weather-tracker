## ADDED Requirements

### Requirement: Topográfiai alaptérkép
A webes frontend egy MapLibre GL JS térképet SHALL megjeleníteni topográfiai/földes
stílusban (természetes tónusok, terep-érzet, arany-okker akcentus), Magyarországra
fókuszált kezdőnézettel.

#### Scenario: Térkép betöltése
- **WHEN** a felhasználó megnyitja az alkalmazást
- **THEN** a topográfiai alaptérkép betöltődik, Magyarországra középre állítva

### Requirement: Víztestek megjelenítése
A frontend a `water-bodies.geojson` artifactból SHALL megjeleníteni a víztesteket
térképi rétegként. A frontend kizárólag az előre generált statikus artifactokat olvassa.

#### Scenario: Víztestek renderelése
- **WHEN** a térkép betöltődik és a `water-bodies.geojson` elérhető
- **THEN** minden víztest megjelenik a térképen a stílushoz illő kitöltéssel

### Requirement: Hover-kiemelés
A felhasználó egy víztest fölé húzva a kurzort vizuális kiemelést SHALL kapjon, jelezve az
interaktivitást. (A kattintásra nyíló részletes grafikon külön, későbbi change.)

#### Scenario: Kiemelés hoverre
- **WHEN** a felhasználó egy víztest fölé viszi a kurzort
- **THEN** az adott víztest kiemelt állapotba kerül, a többi változatlan marad
