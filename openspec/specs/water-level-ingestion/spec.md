# water-level-ingestion Specification

## Purpose
TBD - created by archiving change project-foundation. Update Purpose after archive.
## Requirements
### Requirement: Forrásfüggetlen vízállás port
A rendszer egy `WaterLevelSource` portot (interfészt) SHALL definiáljon, amely egy
megadott időtartamra vízállás-leolvasásokat ad vissza, függetlenül attól, hogy az adat
honnan származik. A domain logika kizárólag ezen a porton keresztül ér el forrásadatot.

#### Scenario: Port absztrakció
- **WHEN** a pipeline vízállásadatot kér egy időtartamra
- **THEN** a `WaterLevelSource.fetch(date_range)` hívás `WaterLevelReading` domain
  objektumok listáját adja vissza, forrás-specifikus típusok kiszivárgása nélkül

### Requirement: data.vizugy.hu adapter
A rendszer egy `VizugyApiAdapter`-t SHALL biztosítson, amely a `WaterLevelSource` portot
implementálja, és a data.vizugy.hu forrásból lehúzza a konfigurált víztestek aktuális
vízállását. A forrásválasz nyers formátumát az adapter normalizálja domain modellé.

#### Scenario: Sikeres lehúzás
- **WHEN** az adapter lefut a konfigurált víztestekre (Balaton, Velencei-tó, Fertő-tó,
  Tisza-tó/Kisköre, Duna, Tisza)
- **THEN** minden elérhető állomásra `WaterLevelReading` keletkezik állomással, dátummal és
  vízállás-értékkel

#### Scenario: Forráshiba nem dönti össze a futást
- **WHEN** a data.vizugy.hu hívás hibázik vagy hiányos választ ad
- **THEN** az adapter naplózza a hibát, és a hibás állomást kihagyja a pipeline összeomlása
  nélkül

### Requirement: Idempotens kanonikus tárolás
A rendszer a normalizált leolvasásokat SHALL elmentse egy SQLite kanonikus tárba
(`data/canonical.sqlite`), az `(állomás, dátum)` kulcson upserttel, hogy ugyanaz a futtatás
megismételhető legyen duplikáció nélkül.

#### Scenario: Újrafuttatás nem hoz létre duplikátumot
- **WHEN** a tárolás kétszer fut le ugyanazokra a leolvasásokra
- **THEN** víztestenként és naponként pontosan egy rekord létezik, a második futás az elsőt
  felülírja, nem duplikálja

### Requirement: Konfigurálható historikus backfill
A rendszer SHALL támogasson konfigurálható évszámú (alapból ~10 év) historikus
vízállás-backfillt a vizugy API dátumtartomány-lekérésével. A backfill a meglévő
idempotens tárolásra épül, így biztonságosan újrafuttatható.

#### Scenario: Megadott évszámra tölt
- **WHEN** a backfill `years=10` paraméterrel fut a konfigurált állomásokra
- **THEN** a kanonikus tárba az elmúlt ~10 év napi vízállásai kerülnek minden elérhető
  állomásra

#### Scenario: Ismételt backfill nem duplikál
- **WHEN** a backfill kétszer fut ugyanarra az időszakra
- **THEN** állomásonként és naponként pontosan egy rekord marad, a második futás felülír,
  nem duplikál

