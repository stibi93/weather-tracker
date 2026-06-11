"""A kanonikus tárból karcsú, determinisztikus frontend-artifactokat ír.

Kimenetek (``out_dir`` alatt):
- ``water-bodies.geojson`` — víztestenként egy Point feature (a reprezentatív állomás
  koordinátáival), a legutóbbi vízállással a property-kben.
- ``water-levels/{id}.json`` — víztestenként a legutóbbi érték + a teljes idősor.
- ``manifest.json`` — mi érhető el, forrás-megjelölés.

A kimenet kizárólag a tárból készül; változatlan táron kétszer futtatva azonos.
"""

from __future__ import annotations

import json
from pathlib import Path

from ingest.storage import CanonicalStore

SOURCE_ATTRIBUTION = "Országos Vízügyi Főigazgatóság"
UNIT = "cm"


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def generate_artifacts(store: CanonicalStore, out_dir: str | Path) -> None:
    out = Path(out_dir)
    bodies = store.water_bodies()
    station_for_body = {s.water_body_id: s for s in store.stations()}

    features = []
    for body in bodies:  # tár szerint id-rendezett -> determinisztikus
        station = station_for_body.get(body.id)
        if station is None:
            continue
        series = store.readings_for_station(station.id)
        latest = series[-1] if series else None

        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [station.lon, station.lat]},
                "properties": {
                    "id": body.id,
                    "name": body.name,
                    "kind": body.kind.value,
                    "station": station.name,
                    "latest_value_cm": int(latest[1]) if latest else None,
                    "latest_date": latest[0].isoformat() if latest else None,
                },
            }
        )

        _write_json(
            out / "water-levels" / f"{body.id}.json",
            {
                "id": body.id,
                "name": body.name,
                "station": station.name,
                "unit": UNIT,
                "source": SOURCE_ATTRIBUTION,
                "latest": (
                    {"date": latest[0].isoformat(), "value_cm": int(latest[1])}
                    if latest
                    else None
                ),
                "series": [{"date": d.isoformat(), "value_cm": int(v)} for d, v in series],
            },
        )

    _write_json(out / "water-bodies.geojson", {"type": "FeatureCollection", "features": features})

    _write_json(
        out / "manifest.json",
        {
            "water_bodies": [b.id for b in bodies],
            "unit": UNIT,
            "sources": {"water_level": SOURCE_ATTRIBUTION},
        },
    )
