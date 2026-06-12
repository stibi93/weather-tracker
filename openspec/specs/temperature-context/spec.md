# temperature-context Specification

## Purpose
TBD - created by archiving change temperature-context. Update Purpose after archive.
## Requirements
### Requirement: Hőmérséklet lehúzása és tárolása
A rendszer víztestenként SHALL lehúzzon napi átlaghőmérsékletet (°C) az Open-Meteo-ból, a
víztest vízgyűjtő-közeli pont-felhőjére átlagolva, és idempotensen tárolja a kanonikus tárba
az `(víztest, dátum)` kulcson.

#### Scenario: Hőmérséklet lehúzása és átlagolása
- **WHEN** a pipeline hőmérsékletet kér egy víztestre egy időtartamra
- **THEN** a pont-felhő napi átlaghőmérsékletének átlaga keletkezik víztestenként és naponként (°C)

#### Scenario: Idempotens tárolás
- **WHEN** a hőmérséklet-tárolás kétszer fut ugyanarra az időszakra
- **THEN** víztestenként és naponként pontosan egy hőmérséklet-rekord marad

### Requirement: Vízálláshoz igazított hőmérséklet-sorozat
A `water-levels/{id}.json` minden idősor-pontja SHALL tartalmazzon egy `temp_c` mezőt: az adott
bucket napi átlaghőmérséklete, vagy `null`. Így a hőmérséklet ugyanazon az időtengelyen,
ugyanazokon a pontokon köthető grafikonra, mint a vízállás és a csapadék.

#### Scenario: Igazított érték minden ponthoz
- **WHEN** az artifact-generátor egy víztest idősorát készíti
- **THEN** minden ponthoz tartozik `temp_c` érték a bucket napi hőmérsékletének átlagaként
  (ha nincs adat, `null`)

