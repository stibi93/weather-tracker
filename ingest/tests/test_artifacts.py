"""Az artifact-generátor tesztjei: determinizmus + séma."""

import json
from datetime import date

from ingest.artifacts import generate_artifacts
from ingest.artifacts.generator import mixed_resolution_series
from ingest.domain.models import Station, WaterBody, WaterBodyKind, WaterLevelReading
from ingest.storage import CanonicalStore


def test_mixed_resolution_daily_recent_monthly_old():
    # 'régi' (>2 év a legutóbbihoz képest) havi átlag, 'friss' napi
    series = [
        (date(2020, 1, 10), 100.0),
        (date(2020, 1, 20), 110.0),  # 2020-01 átlag = 105
        (date(2020, 2, 5), 50.0),  # 2020-02 átlag = 50
        (date(2026, 6, 1), 84.0),  # friss -> napi
        (date(2026, 6, 2), 83.0),  # friss -> napi
    ]
    out = mixed_resolution_series(series, daily_window_years=2)
    assert out == [
        {"date": "2020-01-01", "value_cm": 105, "precip_mm": None, "discharge_m3s": None, "temp_c": None, "et0_mm": None, "resolution": "monthly"},
        {"date": "2020-02-01", "value_cm": 50, "precip_mm": None, "discharge_m3s": None, "temp_c": None, "et0_mm": None, "resolution": "monthly"},
        {"date": "2026-06-01", "value_cm": 84, "precip_mm": None, "discharge_m3s": None, "temp_c": None, "et0_mm": None, "resolution": "daily"},
        {"date": "2026-06-02", "value_cm": 83, "precip_mm": None, "discharge_m3s": None, "temp_c": None, "et0_mm": None, "resolution": "daily"},
    ]


def test_mixed_resolution_aligns_secondary_metrics():
    series = [
        (date(2020, 1, 10), 100.0),
        (date(2020, 1, 20), 110.0),  # havi bucket
        (date(2026, 6, 1), 84.0),  # napi
        (date(2026, 6, 2), 83.0),  # napi, másodlagos adat nélkül -> None
    ]
    precip = {date(2020, 1, 10): 5.0, date(2020, 1, 20): 15.0, date(2026, 6, 1): 2.0}
    discharge = {date(2020, 1, 10): 60.0, date(2020, 1, 20): 80.0, date(2026, 6, 1): 72.3}
    temp = {date(2020, 1, 10): 0.0, date(2020, 1, 20): 4.0, date(2026, 6, 1): 21.5}
    et0 = {date(2020, 1, 10): 0.5, date(2020, 1, 20): 1.5, date(2026, 6, 1): 4.8}
    out = mixed_resolution_series(series, precip, discharge, temp, et0, daily_window_years=2)
    assert out == [
        {"date": "2020-01-01", "value_cm": 105, "precip_mm": 10.0, "discharge_m3s": 70.0, "temp_c": 2.0, "et0_mm": 1.0, "resolution": "monthly"},
        {"date": "2026-06-01", "value_cm": 84, "precip_mm": 2.0, "discharge_m3s": 72.3, "temp_c": 21.5, "et0_mm": 4.8, "resolution": "daily"},
        {"date": "2026-06-02", "value_cm": 83, "precip_mm": None, "discharge_m3s": None, "temp_c": None, "et0_mm": None, "resolution": "daily"},
    ]


def test_mixed_resolution_empty():
    assert mixed_resolution_series([]) == []


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
        {"date": "2026-06-01", "value_cm": 84, "precip_mm": None, "discharge_m3s": None, "temp_c": None, "et0_mm": None, "resolution": "daily"},
        {"date": "2026-06-02", "value_cm": 83, "precip_mm": None, "discharge_m3s": None, "temp_c": None, "et0_mm": None, "resolution": "daily"},
    ]


def test_generates_relationships_artifact(tmp_path):
    with _seed(tmp_path / "c.sqlite") as store:
        generate_artifacts(store, tmp_path / "out")
    rel = json.loads(
        (tmp_path / "out" / "relationships" / "balaton.json").read_text(encoding="utf-8")
    )
    assert rel["id"] == "balaton"
    assert rel["kind"] == "lake"
    assert "primary" in rel and "drivers" in rel


def test_output_is_deterministic(tmp_path):
    with _seed(tmp_path / "c.sqlite") as store:
        generate_artifacts(store, tmp_path / "a")
        generate_artifacts(store, tmp_path / "b")

    for rel in ("water-bodies.geojson", "manifest.json", "water-levels/balaton.json"):
        assert (tmp_path / "a" / rel).read_bytes() == (tmp_path / "b" / rel).read_bytes()
