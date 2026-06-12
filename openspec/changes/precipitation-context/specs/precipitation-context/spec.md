## ADDED Requirements

### Requirement: Területi csapadék lehúzása és tárolása
A rendszer víztestenként SHALL lehúzzon napi területi csapadékot (mm) egy forrás-adapterből
(Open-Meteo), a víztest vízgyűjtő-közeli pont-felhőjére átlagolva, és idempotensen tárolja a
kanonikus tárba az `(víztest, dátum)` kulcson.

#### Scenario: Csapadék lehúzása és átlagolása
- **WHEN** a pipeline csapadékot kér egy víztestre egy időtartamra
- **THEN** a víztesthez rendelt pontok napi csapadékának **átlaga** keletkezik víztestenként és
  naponként, mm-ben

#### Scenario: Idempotens tárolás
- **WHEN** a csapadék-tárolás kétszer fut ugyanarra az időszakra
- **THEN** víztestenként és naponként pontosan egy csapadék-rekord marad

### Requirement: Vízálláshoz igazított csapadék-sorozat
A `water-levels/{id}.json` minden idősor-pontja SHALL tartalmazzon egy `precip_mm` mezőt: az
adott pont időszakára (napi vagy havi bucket) átlagolt napi csapadékot. Így a vízállás és a
csapadék azonos időtengelyen, azonos pontokon köthető grafikonra.

#### Scenario: Igazított érték minden ponthoz
- **WHEN** az artifact-generátor egy víztest idősorát készíti
- **THEN** minden ponthoz tartozik `precip_mm` érték az adott bucket napi csapadékának átlagaként
  (ha nincs adat, `null`)
