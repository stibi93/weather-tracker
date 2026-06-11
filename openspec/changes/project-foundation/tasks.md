## 1. Repo scaffold

- [x] 1.1 `ingest/` Python csomag váz: `domain/`, `adapters/`, `storage/`, `artifacts/`, `config/`, `pipeline/`, `tests/` almappák + `pyproject.toml` függőségekkel (httpx, pytest)
- [x] 1.2 `web/` Vite + React + TypeScript app inicializálása, `web/public/data/` mappa az artifactoknak
- [x] 1.3 `.gitignore` (`.superpowers/`, `node_modules/`, `.env`, Python cache), `.env.example` az alaptérkép-kulcsnak
- [x] 1.4 Rövid `README.md`: hogyan futtatható a pipeline és a frontend lokálisan

## 2. Domain és portok

- [x] 2.1 Domain modellek: `WaterBody`, `Station`, `WaterLevelReading` (tiszta adatosztályok, hálózat nélkül)
- [x] 2.2 `WaterLevelSource` port (interfész): `fetch(date_range) -> list[WaterLevelReading]`
- [x] 2.3 Állomás→víztest leképezés konfig a hat víztestre (`ingest/config`)

## 3. data.vizugy.hu adapter

- [x] 3.1 `VizugyApiAdapter` a `WaterLevelSource` porttal; a végpontok/paraméterek felderítve (token + TS/TsShortList)
- [x] 3.2 Nyers válasz normalizálása `WaterLevelReading`-ekké a konfigurált állomásokra
- [x] 3.3 Forráshiba kezelése: hibás állomás kihagyása + naplózás, a futás összeomlása nélkül
- [x] 3.4 Adapter unit-teszt rögzített (fixture) válaszon, élő hálózat nélkül

## 4. Kanonikus SQLite tár

- [x] 4.1 Séma: `water_body`, `station`, `water_level_reading(station_id, date, value)` egyedi `(station_id, date)` kulccsal
- [x] 4.2 Idempotens upsert tárolási réteg
- [x] 4.3 Teszt: ugyanazon leolvasások kétszeri tárolása nem hoz duplikátumot

## 5. Artifact-generátor

- [x] 5.1 Víztest-pont geometria a vizugy állomás-koordinátákból (`Lat`/`Lon`) a hat reprezentatív állomásra
- [x] 5.2 `web/public/data/water-bodies.geojson` generálása (érvényes GeoJSON Point feature-ök, stabil `id` + név)
- [x] 5.3 `web/public/data/water-levels/{id}.json` generálása a kanonikus tárból (legutóbbi érték + rövid idősor)
- [x] 5.4 Teszt: determinisztikus kimenet kis minta-DB-ből + JSON/GeoJSON séma-ellenőrzés

## 6. Pipeline belépési pont

- [x] 6.1 `run` belépési pont, amely láncolja: lehúzás (vizugy) → tárolás (SQLite) → artifact-generálás
- [x] 6.2 Kézi futtatás végigviszi a láncot és előállítja az artifactokat a hat víztestre

## 7. Frontend térkép

- [x] 7.1 MapLibre GL JS integráció, saját hangolású topográfiai/földes (C) vektoros stílus, Magyarországra illesztett nézet
- [x] 7.2 `water-bodies.geojson` betöltése és víztestek megjelenítése térképi rétegként
- [x] 7.3 Hover-kiemelés a víztesteken (+ tooltip a legutóbbi vízállással)
- [x] 7.4 Forrás-megjelölés a felületen („Országos Vízügyi Főigazgatóság")

## 8. Verifikáció

- [x] 8.1 `ingest` tesztek zölden futnak (`pytest`) — 12 teszt
- [x] 8.2 Kézi end-to-end: pipeline lefut (185 valós leolvasás), artifactok elkészülnek, a frontend a térképen mutatja a hat víztestet hover-kiemeléssel
- [x] 8.3 `openspec validate project-foundation --strict` hibamentes
