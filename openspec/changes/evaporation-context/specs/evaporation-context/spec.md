## ADDED Requirements

### Requirement: Párolgás (ET₀) lehúzása és tárolása
A rendszer víztestenként SHALL lehúzzon napi referencia-párolgást (ET₀, mm) az Open-Meteo-ból
(a csapadékkal/hőmérséklettel azonos, konszolidált hívásból), a vízgyűjtő-közeli pont-felhőre
átlagolva, és idempotensen tárolja az `(víztest, dátum)` kulcson.

#### Scenario: ET₀ lehúzása egy hívásból
- **WHEN** a pipeline lekéri egy víztest területi időjárását
- **THEN** egyetlen Open-Meteo hívásból megkapja a napi csapadékot, hőmérsékletet és ET₀-t, és
  mindhármat tárolja víztestenként és naponként

#### Scenario: Idempotens tárolás
- **WHEN** az ET₀-tárolás kétszer fut ugyanarra az időszakra
- **THEN** víztestenként és naponként pontosan egy ET₀-rekord marad

### Requirement: Vízálláshoz igazított ET₀-sorozat
A `water-levels/{id}.json` minden idősor-pontja SHALL tartalmazzon egy `et0_mm` mezőt: az adott
bucket napi ET₀-jának átlaga, vagy `null`.

#### Scenario: Igazított érték minden ponthoz
- **WHEN** az artifact-generátor egy víztest idősorát készíti
- **THEN** minden ponthoz tartozik `et0_mm` érték a bucket napi ET₀-jának átlagaként (vagy `null`)
