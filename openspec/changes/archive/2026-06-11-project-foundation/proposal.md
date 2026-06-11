## Why

A projektnek még nincs váza: sem ingest pipeline, sem kanonikus tár, sem frontend. Mielőtt
bármilyen gazdag funkciót (több forrás, csapadék, grafikonok) építenénk, egy vékony, de
végpontól-végpontig működő alapra van szükség, amely bizonyítja az architektúrát: forrás →
normalizálás → SQLite → artifact → statikus térkép. Erre épül majd minden további change.

## What Changes

- Repo scaffold: `ingest/` (Python, ports & adapters) és `web/` (Vite + React + TypeScript)
  alap struktúra.
- Domain modell és portok: `WaterBody`, `Station`, `WaterLevelReading`, valamint a
  `WaterLevelSource` port.
- **Egyetlen** vízállás-adapter: `VizugyApiAdapter` (data.vizugy.hu) — a friss vízállás
  lehúzása a tervezett víztestekre. (A hydroinfo backfill + fallback későbbi change.)
- Kanonikus tár: `data/canonical.sqlite` séma + idempotens upsert (kulcs: állomás + dátum).
- Artifact-generátor: a SQLite-ból `web/public/data/water-bodies.geojson` (geometria) és
  víztestenként egy minimális `water-levels/{id}.json` (legutóbbi érték + rövid idősor).
- Minimális frontend: MapLibre GL JS térkép a **topográfiai/földes (C)** stílusban, amely
  megjeleníti a víztesteket a GeoJSON-ból. Hover = kiemelés. (Kattintásra nyíló grafikon és
  csapadék-réteg későbbi change.)
- Nincs CI/ütemezés ebben a change-ben; a pipeline kézzel futtatható (`run` belépési pont).

## Capabilities

### New Capabilities
- `water-level-ingestion`: vízállás-leolvasások lehúzása egy forrás-adapterből, normalizálása a
  domain modellbe, és idempotens tárolása a kanonikus SQLite-ba.
- `data-artifacts`: a kanonikus tárból a frontend által fogyasztott, karcsú JSON/GeoJSON
  artifactok determinisztikus legenerálása.
- `map-view`: statikus webes térkép, amely a topográfiai stílusban megjeleníti a víztesteket az
  artifactokból, hover-kiemeléssel.

### Modified Capabilities
<!-- Nincs meglévő capability; ez a legelső change. -->

## Impact

- Új kód: `ingest/` Python csomag (domain, adapters, pipeline, artifacts), `web/` frontend app.
- Új adat: `data/canonical.sqlite` (verziózva), `web/public/data/*` generált artifactok.
- Új külső függőség: data.vizugy.hu API (hálózat, runtime), MapLibre GL JS + ingyenes
  alaptérkép-tier (frontend).
- Nincs CI/deploy hatás ebben a szakaszban.
