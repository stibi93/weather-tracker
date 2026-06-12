## 1. Domain és adapter

- [x] 1.1 Domain: `TempReading(water_body_id, date, temp_c)` + `TemperatureSource` port
- [x] 1.2 Az openmeteo modul közös `_fetch_area_daily(...)` (a `_average_daily` általánosítva változó-kulcsra) + 429-retry
- [x] 1.3 `OpenMeteoTempAdapter` (`temperature_2m_mean`) a `TemperatureSource` porttal
- [x] 1.4 Adapter unit-teszt fixture-ön (a meglévő csapadék-teszt mellett)

## 2. Tárolás és pipeline

- [x] 2.1 `temp_reading` tábla + idempotens upsert + `temp_for_water_body` lekérdezés
- [x] 2.2 A pipeline a hőmérsékletet is lehúzza+tárolja
- [x] 2.3 Teszt: idempotens hőmérséklet-tárolás

## 3. Artifact: igazított hőmérséklet

- [x] 3.1 Minden idősor-pont kap `temp_c`-t (bucket napi átlaga, vagy null)
- [x] 3.2 Teszt: az igazítás helyes (napi+havi), determinisztikus

## 4. Frontend: másodlagos kontextus-váltó

- [x] 4.1 A `Chart` másodlagos rétege: csapadék (oszlop, mm) vagy hőmérséklet (vonal, °C), jobb tengely + felirat vált
- [x] 4.2 A tooltip az aktív másodlagos értéket mutatja
- [x] 4.3 A `DetailPanel` kontextus-váltója (Csapadék/Hőmérséklet); jelmagyarázat frissül
- [x] 4.4 A (C) földes stílushoz illő színek (hőmérséklet okker/arany vonal)

## 5. Verifikáció

- [x] 5.1 `ingest` tesztek zölden (24 teszt + új hőmérséklet-tesztek)
- [x] 5.2 Éles futtatás: hőmérséklet lehúzva (21906, mind a 6 víztest 828/828), artifactok igazítva
- [x] 5.3 E2e (Playwright): kontextus-váltó hőmérsékletre vált (vonal + °C tengely + tooltip "72 cm / 20.4 °C")
- [x] 5.4 `openspec validate temperature-context --strict` hibamentes
