"""Az artifact-generátor tesztjei: determinizmus + séma."""

import json
from datetime import date

from ingest.artifacts import generate_artifacts
from ingest.domain.models import Station, WaterBody, WaterBodyKind, WaterLevelReading
from ingest.storage import CanonicalStore


def _seed(path):
    store = CanonicalStore(path)
    store.upsert_water_bodies(
        [
            WaterBody("balaton", "Balaton", WaterBodyKind.LAKE),
            WaterBody("duna", "Duna", WaterBodyKind.RIVER),
        ]
    )
    store.upsert_stations(
        [
            Station("142300", "Balaton átlag", "balaton", 46.8838, 17.8154),
            Station("1026", "Budapest", "duna", 47.4949, 19.0484),
        ]
    )
    store.upsert_readings(
        [
            WaterLevelReading("142300", date(2026, 6, 1), 84),
            WaterLevelReading("142300", date(2026, 6, 2), 83),
            WaterLevelReading("1026", date(2026, 6, 2), 250),
        ]
    )
    return store


def test_generates_valid_geojson_with_latest(tmp_path):
    with _seed(tmp_path / "c.sqlite") as store:
        generate_artifacts(store, tmp_path / "out")

    geo = json.loads((tmp_path / "out" / "water-bodies.geojson").read_text(encoding="utf-8"))
    assert geo["type"] == "FeatureCollection"
    ids = [f["properties"]["id"] for f in geo["features"]]
    assert ids == ["balaton", "duna"]  # id-rendezett

    balaton = geo["features"][0]
    assert balaton["geometry"]["type"] == "Point"
    assert balaton["geometry"]["coordinates"] == [17.8154, 46.8838]  # [lon, lat]
    assert balaton["properties"]["latest_value_cm"] == 83
    assert balaton["properties"]["latest_date"] == "2026-06-02"


def test_per_body_series_shape(tmp_path):
    with _seed(tmp_path / "c.sqlite") as store:
        generate_artifacts(store, tmp_path / "out")

    doc = json.loads(
        (tmp_path / "out" / "water-levels" / "balaton.json").read_text(encoding="utf-8")
    )
    assert doc["id"] == "balaton"
    assert doc["unit"] == "cm"
    assert doc["latest"] == {"date": "2026-06-02", "value_cm": 83}
    assert doc["series"] == [
        {"date": "2026-06-01", "value_cm": 84},
        {"date": "2026-06-02", "value_cm": 83},
    ]


def test_output_is_deterministic(tmp_path):
    with _seed(tmp_path / "c.sqlite") as store:
        generate_artifacts(store, tmp_path / "a")
        generate_artifacts(store, tmp_path / "b")

    for rel in ("water-bodies.geojson", "manifest.json", "water-levels/balaton.json"):
        assert (tmp_path / "a" / rel).read_bytes() == (tmp_path / "b" / rel).read_bytes()
