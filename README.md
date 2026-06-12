# Magyar vízállás- és csapadék-térkép

Interaktív térkép a hazai nagy tavak és folyók vízállásáról (később: országos
csapadék-eloszlás), napi frissítéssel és historikus mélységgel. Statikus-first
(Jamstack): Python ingest pipeline → SQLite kanonikus tár → előre generált
JSON/GeoJSON artifactok → statikus React + MapLibre frontend.

Teljes architektúra: `docs/superpowers/specs/2026-06-11-vizallas-csapadek-terkep-design.md`
Spec-driven fejlesztés OpenSpec-kel: `openspec/`.

## Felépítés

```
ingest/   Python pipeline (ports & adapters): domain, adapters, storage, artifacts, config
web/      Vite + React + TypeScript + MapLibre GL JS frontend
data/      kanonikus SQLite (generált, nem verziózott)
openspec/  spec-driven change-ek és globális kontextus
```

## Ingest pipeline (Python)

Környezet (uv ajánlott):

```bash
uv venv --python 3.12
uv pip install -e ".[dev]"
```

Teljes lánc futtatása (lehúzás → tárolás → artifact-generálás):

```bash
./.venv/bin/python -m ingest.pipeline.run --days 30        # napi friss
./.venv/bin/python -m ingest.pipeline.run --years 10       # historikus backfill (~10 év)
# kimenet: web/public/data/{water-bodies.geojson, water-levels/*.json, manifest.json}
```

A `water-levels/{id}.json` többéves, vegyes felbontású idősort tartalmaz: napi a friss
~2 évre, havi átlag a régebbi évekre. A frontend kattintásra grafikonon jeleníti meg.

Tesztek (élő hálózat nélkül, fixture-alapú):

```bash
./.venv/bin/pytest ingest/tests/ -q
```

## Frontend (web/)

```bash
cd web
npm install
npm run dev      # fejlesztői szerver
npm run build    # éles build a dist/-be
```

Az alaptérkép alapból kulcs nélküli, saját hangolású OpenFreeMap vektoros stílus.
Opcionálisan a `web/.env`-ben megadható `VITE_MAPTILER_KEY` a MapTiler „outdoor"
stílushoz (lásd `web/.env.example`).

## Adatforrások

- **Vízállás + vízhozam:** data.vizugy.hu nyílt API — forrás: *Országos Vízügyi Főigazgatóság*.
  A vízhozam (m³/s) csak a folyókra elérhető; a grafikonon metrika-váltóval (vízállás ↔ vízhozam).
- **Időjárás (csapadék + hőmérséklet + párolgás):** Open-Meteo archív (ERA5) API egy hívásban
  víztestenként — vízgyűjtő-közeli pont-felhő napi átlaga (közelítés); a részletpanel grafikonján
  másodlagos rétegként, váltható: csapadék (oszlop, mm) ↔ hőmérséklet (vonal, °C) ↔ párolgás
  (ET₀, vonal, mm).
- **Térkép:** OpenFreeMap vektor csempék, © OpenMapTiles, © OpenStreetMap közreműködők.
