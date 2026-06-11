## 1. Repo scaffold

- [ ] 1.1 `ingest/` Python csomag váz: `domain/`, `adapters/`, `pipeline/`, `artifacts/`, `config/`, `seed/`, `tests/` almappák + `pyproject.toml` (vagy requirements) függőségekkel (httpx, pytest)
- [ ] 1.2 `web/` Vite + React + TypeScript app inicializálása, `web/public/data/` mappa az artifactoknak
- [ ] 1.3 `.gitignore` (`.superpowers/`, `node_modules/`, `.env`, Python cache), `.env.example` az alaptérkép-kulcsnak
- [ ] 1.4 Rövid `README.md`: hogyan futtatható a pipeline és a frontend lokálisan

## 2. Domain és portok

- [ ] 2.1 Domain modellek: `WaterBody`, `Station`, `WaterLevelReading` (tiszta adatosztályok, hálózat nélkül)
- [ ] 2.2 `WaterLevelSource` port (interfész): `fetch(date_range) -> list[WaterLevelReading]`
- [ ] 2.3 Állomás→víztest leképezés konfig a hat víztestre (`ingest/config`)

## 3. data.vizugy.hu adapter

- [ ] 3.1 `VizugyApiAdapter` váz a `WaterLevelSource` porttal; a tényleges végpontok/paraméterek felderítése (portál hálózati hívásainak visszafejtése)
- [ ] 3.2 Nyers válasz normalizálása `WaterLevelReading`-ekké a konfigurált állomásokra
- [ ] 3.3 Forráshiba kezelése: hibás állomás kihagyása + naplózás, a futás összeomlása nélkül
- [ ] 3.4 Adapter unit-teszt rögzített (fixture) válaszon, élő hálózat nélkül

## 4. Kanonikus SQLite tár

- [ ] 4.1 Séma: `water_body`, `station`, `water_level_reading(station_id, date, value)` egyedi `(station_id, date)` kulccsal
- [ ] 4.2 Idempotens upsert tárolási réteg
- [ ] 4.3 Teszt: ugyanazon leolvasások kétszeri tárolása nem hoz duplikátumot

## 5. Artifact-generátor

- [ ] 5.1 Víztest-geometria seed beszerzése OpenStreetMap-ből a hat víztestre, `ingest/seed/`-be verziózva
- [ ] 5.2 `web/public/data/water-bodies.geojson` generálása a seedből (érvényes GeoJSON, stabil `id` + név)
- [ ] 5.3 `web/public/data/water-levels/{id}.json` generálása a kanonikus tárból (legutóbbi érték + rövid idősor)
- [ ] 5.4 Teszt: determinisztikus kimenet kis minta-DB-ből + JSON/GeoJSON séma-ellenőrzés

## 6. Pipeline belépési pont

- [ ] 6.1 `run` belépési pont, amely láncolja: lehúzás (vizugy) → tárolás (SQLite) → artifact-generálás
- [ ] 6.2 Kézi futtatás végigviszi a láncot és előállítja az artifactokat a hat víztestre

## 7. Frontend térkép

- [ ] 7.1 MapLibre GL JS integráció, topográfiai/földes (C) stílus, Magyarországra központozott kezdőnézet
- [ ] 7.2 `water-bodies.geojson` betöltése és víztestek megjelenítése térképi rétegként
- [ ] 7.3 Hover-kiemelés a víztesteken
- [ ] 7.4 Forrás-megjelölés a felületen („Országos Vízügyi Főigazgatóság")

## 8. Verifikáció

- [ ] 8.1 `ingest` tesztek zölden futnak (`pytest`)
- [ ] 8.2 Kézi end-to-end: pipeline lefut, artifactok elkészülnek, a frontend a térképen mutatja a hat víztestet hover-kiemeléssel
- [ ] 8.3 `openspec validate project-foundation --strict` hibamentes
