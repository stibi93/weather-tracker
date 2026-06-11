## ADDED Requirements

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
