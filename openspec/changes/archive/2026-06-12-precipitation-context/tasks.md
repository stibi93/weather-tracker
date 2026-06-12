## 1. Domain és config

- [x] 1.1 Domain: `PrecipReading(water_body_id, date, precip_mm)` + `PrecipitationSource` port
- [x] 1.2 Config: víztestenként vízgyűjtő-közeli pont-felhő (3–4 koordináta) a területi átlaghoz

## 2. Open-Meteo adapter

- [x] 2.1 `OpenMeteoPrecipAdapter` (archív API): víztestenként a pont-felhő napi csapadékának átlaga
- [x] 2.2 Hibatűrés: forráshiba nem dönti össze a futást (üres/null)
- [x] 2.3 Adapter unit-teszt rögzített (fixture) válaszon, élő hálózat nélkül

## 3. Tárolás és pipeline

- [x] 3.1 `precip_reading` tábla + idempotens upsert a kanonikus tárban
- [x] 3.2 A pipeline a csapadékot is lehúzza és tárolja (a vízállás mellett)
- [x] 3.3 Teszt: idempotens csapadék-tárolás

## 4. Artifact: igazított csapadék

- [x] 4.1 Az idősor minden pontjához `precip_mm` (a bucket napi csapadékának átlaga, vagy null)
- [x] 4.2 Teszt: az igazítás helyes (napi és havi bucket), determinisztikus

## 5. Frontend: kéttengelyes grafikon

- [x] 5.1 A `Chart` csapadék-oszlopokat rajzol a vízállás-vonal mögött, külön jobb oldali mm-tengelyen
- [x] 5.2 A hover-tooltip kiírja a csapadékot (mm) is
- [x] 5.3 A (C) földes stílushoz illő színek (vízállás teal vonal, csapadék halvány kék oszlop) + jelmagyarázat

## 6. Verifikáció

- [x] 6.1 `ingest` tesztek zölden (20 teszt, + új csapadék-tesztek)
- [x] 6.2 Éles futtatás: csapadék lehúzva és tárolva (21906), artifactok igazítva (828/828 pont)
- [x] 6.3 E2e (Playwright): csapadék-oszlopok + tooltip ("2025. szept. 10." / 72 cm / 16.9 mm)
- [x] 6.4 `openspec validate precipitation-context --strict` hibamentes
