"""Az OpenMeteoPrecipAdapter tesztjei fixture-ön, élő hálózat nélkül."""

import json
from datetime import date
from pathlib import Path

import httpx

from ingest.adapters.openmeteo import (
    OpenMeteoPrecipAdapter,
    OpenMeteoTempAdapter,
    _average_daily,
)
from ingest.domain.models import PrecipReading, TempReading
from ingest.domain.ports import DateRange

FIXTURES = Path(__file__).parent / "fixtures"
RANGE = DateRange(date(2026, 6, 8), date(2026, 6, 11))
AREAS = {"balaton": [(46.90, 18.04), (46.84, 17.73)]}


def _client(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_fetch_averages_cluster_per_day():
    payload = json.loads((FIXTURES / "openmeteo_precip.json").read_text(encoding="utf-8"))
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        return httpx.Response(200, json=payload)

    adapter = OpenMeteoPrecipAdapter(AREAS, client=_client(handler))
    readings = adapter.fetch(RANGE)

    assert "latitude=46.9%2C46.84" in captured["url"] or "latitude=46.9,46.84" in captured["url"]
    assert all(isinstance(r, PrecipReading) for r in readings)
    assert {r.water_body_id for r in readings} == {"balaton"}
    # 4 nap, víztestenként egy érték/nap
    assert len(readings) == 4
    # az átlag a két lokáció napi értékéből
    by_day = {r.date: r.precip_mm for r in readings}
    assert by_day[date(2026, 6, 8)] == 0.0


def test_fetch_empty_on_source_error():
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(500)

    adapter = OpenMeteoPrecipAdapter(AREAS, client=_client(handler))
    assert adapter.fetch(RANGE) == []


def test_temp_adapter_uses_temperature_variable():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        return httpx.Response(
            200,
            json=[
                {"daily": {"time": ["2026-06-08", "2026-06-09"], "temperature_2m_mean": [18.0, 20.0]}},
                {"daily": {"time": ["2026-06-08", "2026-06-09"], "temperature_2m_mean": [16.0, 22.0]}},
            ],
        )

    adapter = OpenMeteoTempAdapter(AREAS, client=_client(handler))
    readings = adapter.fetch(RANGE)

    assert "daily=temperature_2m_mean" in captured["url"]
    assert all(isinstance(r, TempReading) for r in readings)
    by_day = {r.date: r.temp_c for r in readings}
    assert by_day[date(2026, 6, 8)] == 17.0  # (18+16)/2


def test_average_daily_skips_nulls():
    locations = [
        {"daily": {"time": ["2026-06-01", "2026-06-02"], "precipitation_sum": [10.0, None]}},
        {"daily": {"time": ["2026-06-01", "2026-06-02"], "precipitation_sum": [20.0, 4.0]}},
    ]
    assert _average_daily(locations, "precipitation_sum", 1) == {
        date(2026, 6, 1): 15.0,
        date(2026, 6, 2): 4.0,
    }
