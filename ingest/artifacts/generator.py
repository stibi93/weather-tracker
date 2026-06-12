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
from collections import defaultdict
from datetime import date as Date
from datetime import timedelta
from pathlib import Path

from ingest.analysis import compute_relationships
from ingest.storage import CanonicalStore

SOURCE_ATTRIBUTION = "Országos Vízügyi Főigazgatóság"
UNIT = "cm"
DAILY_WINDOW_YEARS = 2


def _opt_round1(value: float | None) -> float | None:
    return round(value, 1) if value is not None else None


def _monthly_means(values: dict[Date, float], cutoff: Date) -> dict[tuple[int, int], float]:
    """Havi átlag a cutoff előtti napokra, egy tizedesre kerekítve."""
    buckets: dict[tuple[int, int], list[float]] = defaultdict(list)
    for day, value in values.items():
        if day < cutoff:
            buckets[(day.year, day.month)].append(value)
    return {key: round(sum(vals) / len(vals), 1) for key, vals in buckets.items()}


def mixed_resolution_series(
    series: list[tuple[Date, float]],
    precip: dict[Date, float] | None = None,
    discharge: dict[Date, float] | None = None,
    temp: dict[Date, float] | None = None,
    et0: dict[Date, float] | None = None,
    daily_window_years: int = DAILY_WINDOW_YEARS,
) -> list[dict]:
    """Vegyes felbontású sorozat: a friss ablakra napi pont, azelőtt havi átlag.

    Minden pont: ``{"date", "value_cm", "precip_mm", "discharge_m3s", "temp_c", "et0_mm",
    "resolution"}``, időrendben. A másodlagos mezők az adott bucket napi átlaga, vagy ``null``
    (pl. vízhozam a tavaknál). Üres bemenetre üres lista.
    """
    if not series:
        return []
    precip = precip or {}
    discharge = discharge or {}
    temp = temp or {}
    et0 = et0 or {}
    cutoff = series[-1][0] - timedelta(days=365 * daily_window_years)
    p_month = _monthly_means(precip, cutoff)
    d_month = _monthly_means(discharge, cutoff)
    t_month = _monthly_means(temp, cutoff)
    e_month = _monthly_means(et0, cutoff)

    monthly_wl: dict[tuple[int, int], list[float]] = defaultdict(list)
    daily: list[dict] = []
    for day, value in series:
        if day >= cutoff:
            daily.append(
                {
                    "date": day.isoformat(),
                    "value_cm": int(value),
                    "precip_mm": _opt_round1(precip.get(day)),
                    "discharge_m3s": _opt_round1(discharge.get(day)),
                    "temp_c": _opt_round1(temp.get(day)),
                    "et0_mm": _opt_round1(et0.get(day)),
                    "resolution": "daily",
                }
            )
        else:
            monthly_wl[(day.year, day.month)].append(value)

    monthly = [
        {
            "date": Date(year, month, 1).isoformat(),
            "value_cm": round(sum(vals) / len(vals)),
            "precip_mm": p_month.get((year, month)),
            "discharge_m3s": d_month.get((year, month)),
            "temp_c": t_month.get((year, month)),
            "et0_mm": e_month.get((year, month)),
            "resolution": "monthly",
        }
        for (year, month), vals in sorted(monthly_wl.items())
    ]
    return monthly + daily


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
        precip = store.precip_for_water_body(body.id)
        discharge = store.discharge_for_station(station.id)
        temp = store.temp_for_water_body(body.id)
        et0 = store.et0_for_water_body(body.id)
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
            out / "relationships" / f"{body.id}.json",
            compute_relationships(
                body.id, body.name, body.kind.value, dict(series), precip, et0, discharge, temp
            ),
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
                "series": mixed_resolution_series(series, precip, discharge, temp, et0),
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
