## ADDED Requirements

### Requirement: Vízhozam lehúzása és tárolása
A rendszer a folyó-víztestek állomásaira SHALL lehúzzon napi vízhozamot (m³/s) a vizugy
API-ból (adatfajta-kód 87), napi szintre aggregálva, és idempotensen tárolja a kanonikus
tárba az `(állomás, dátum)` kulcson. Ahol nincs vízhozam (tavak szintmérője), ott üres marad.

#### Scenario: Folyó vízhozama tárolva
- **WHEN** a pipeline vízhozamot kér a Duna/Tisza állomásaira
- **THEN** napi vízhozam-érték (m³/s) keletkezik és tárolódik állomásonként és naponként

#### Scenario: Tónál nincs vízhozam
- **WHEN** a pipeline vízhozamot kér egy tó szintmérő-állomására
- **THEN** nem keletkezik vízhozam-rekord, és a futás hiba nélkül folytatódik

### Requirement: Vízálláshoz igazított vízhozam-sorozat
A `water-levels/{id}.json` minden idősor-pontja SHALL tartalmazzon egy `discharge_m3s` mezőt:
az adott bucket napi vízhozamának átlaga, vagy `null`, ha nincs adat. Így a vízhozam ugyanazon
az időtengelyen, ugyanazokon a pontokon köthető grafikonra, mint a vízállás.

#### Scenario: Igazított vízhozam minden ponthoz
- **WHEN** az artifact-generátor egy folyó idősorát készíti
- **THEN** minden ponthoz tartozik `discharge_m3s` érték a bucket napi vízhozamának átlagaként

#### Scenario: Tó esetén null
- **WHEN** az artifact-generátor egy tó idősorát készíti
- **THEN** minden pont `discharge_m3s` értéke `null`
