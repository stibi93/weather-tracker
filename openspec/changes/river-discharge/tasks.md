## 1. Domain és adapter

- [x] 1.1 Domain: `DischargeReading(station_id, date, value_m3s)` + `DischargeSource` port
- [x] 1.2 A vizugy modul közös `_fetch_daily_values(...)` segédfüggvénye (token+POST+napi átlag), kód-paraméterrel
- [x] 1.3 `VizugyDischargeAdapter` (kód 87) a `DischargeSource` porttal, a megadott állomásokra
- [x] 1.4 Adapter unit-teszt fixture-ön (a meglévő vízállás-teszt mellett)

## 2. Tárolás és pipeline

- [x] 2.1 `discharge_reading` tábla + idempotens upsert + `discharge_for_station` lekérdezés
- [x] 2.2 A pipeline a folyó-víztestek állomásaira lehúzza+tárolja a vízhozamot
- [x] 2.3 Teszt: idempotens vízhozam-tárolás

## 3. Artifact: igazított vízhozam

- [x] 3.1 Minden idősor-pont kap `discharge_m3s`-t (bucket napi átlaga, vagy null)
- [x] 3.2 Teszt: az igazítás helyes (napi+havi), tónál null, determinisztikus

## 4. Frontend: metrika-váltó

- [x] 4.1 A `Chart` a fővonalat a kapott metrikával (cm vagy m³/s) és tengely-felirattal rajzolja; a tooltip az aktív metrikát mutatja
- [x] 4.2 A `DetailPanel` metrika-váltója (Vízállás/Vízhozam), csak ha van vízhozam a sorozatban
- [x] 4.3 A (C) földes stílushoz illő megjelenés (szegmens-váltó)

## 5. Verifikáció

- [x] 5.1 `ingest` tesztek zölden (22 teszt + új vízhozam-tesztek)
- [x] 5.2 Éles futtatás: vízhozam lehúzva a folyókra (7302), artifactok igazítva (Duna/Tisza 828/828, tavak null)
- [x] 5.3 E2e (Playwright): folyónál (Duna) metrika-váltó működik (1300 m³/s, tooltip), tónál (Balaton) nincs váltó
- [x] 5.4 `openspec validate river-discharge --strict` hibamentes
