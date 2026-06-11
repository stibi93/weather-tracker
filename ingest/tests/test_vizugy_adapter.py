"""A VizugyApiAdapter tesztjei rögzített (fixture) válaszokon, élő hálózat nélkül."""

import json
from datetime import date
from pathlib import Path

import httpx
import pytest

from ingest.adapters.vizugy import VizugyApiAdapter, _aggregate_daily
from ingest.domain.models import WaterLevelReading
from ingest.domain.ports import DateRange

FIXTURES = Path(__file__).parent / "fixtures"
RANGE = DateRange(date(2026, 6, 1), date(2026, 6, 11))


def _load(name: str):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _client(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_fetch_maps_readings_and_aggregates_to_daily():
    ts = _load("vizugy_ts_shortlist.json")  # 142300 (napi) + 818 (órás)
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if "auth/token" in url:
            assert request.headers["Origin"] == "https://data.vizugy.hu"
            return httpx.Response(200, json={"access_token": "FAKE"})
        if "TsShortList" in url:
            captured["body"] = json.loads(request.content)
            assert request.headers["Authorization"] == "Bearer FAKE"
            return httpx.Response(200, json=ts)
        return httpx.Response(404)

    adapter = VizugyApiAdapter(["142300", "818"], client=_client(handler))
    readings = adapter.fetch(RANGE)

    # Helyes kérés-body (felszíni vízállás kód, állomáslista, dátumok)
    assert captured["body"]["adatFajtaKod"] == 68
    assert captured["body"]["torzsszamList"] == [142300, 818]
    assert captured["body"]["startTime"] == "2026-06-01"

    assert all(isinstance(r, WaterLevelReading) for r in readings)
    assert {r.station_id for r in readings} == {"142300", "818"}

    # Az órás 818-as állomás naponként pontosan egy értékre aggregálódott
    days_818 = [r.date for r in readings if r.station_id == "818"]
    assert days_818 == sorted(set(days_818))
    assert all(isinstance(r.value_cm, int) for r in readings)


def test_fetch_returns_empty_on_source_error():
    def handler(request: httpx.Request) -> httpx.Response:
        if "auth/token" in str(request.url):
            return httpx.Response(200, json={"access_token": "FAKE"})
        return httpx.Response(500)  # TS hiba

    adapter = VizugyApiAdapter(["142300"], client=_client(handler))
    assert adapter.fetch(RANGE) == []  # nem dob, üres lista


def test_fetch_skips_malformed_station_item():
    def handler(request: httpx.Request) -> httpx.Response:
        if "auth/token" in str(request.url):
            return httpx.Response(200, json={"access_token": "FAKE"})
        return httpx.Response(
            200,
            json=[
                {"ItemId": 1, "TsItemList": [{"UTCTime": "2026-06-01T05:00:00Z", "Adat": 10.0}]},
                {"unexpected": "shape"},  # hiányzó ItemId -> kihagyva
            ],
        )

    adapter = VizugyApiAdapter(["1"], client=_client(handler))
    readings = adapter.fetch(RANGE)
    assert len(readings) == 1
    assert readings[0].station_id == "1" and readings[0].value_cm == 10


def test_aggregate_daily_means_and_rounds_to_cm():
    points = [
        {"UTCTime": "2026-06-01T00:00:00Z", "Adat": 10.0},
        {"UTCTime": "2026-06-01T12:00:00Z", "Adat": 12.0},
        {"UTCTime": "2026-06-02T06:00:00Z", "Adat": 20.0},
        {"UTCTime": "2026-06-03T06:00:00Z", "Adat": None},  # hiányzó -> kihagyva
    ]
    out = _aggregate_daily(points)
    assert out == {date(2026, 6, 1): 11, date(2026, 6, 2): 20}


def test_daterange_rejects_inverted():
    with pytest.raises(ValueError):
        DateRange(date(2026, 6, 11), date(2026, 6, 1))
