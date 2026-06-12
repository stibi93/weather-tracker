"""Az OpenMeteoWeatherAdapter tesztjei fixture-ön, élő hálózat nélkül."""

from datetime import date

import httpx

from ingest.adapters.openmeteo import OpenMeteoWeatherAdapter, _average_daily_multi
from ingest.domain.models import WeatherReading
from ingest.domain.ports import DateRange

RANGE = DateRange(date(2026, 6, 8), date(2026, 6, 9))
AREAS = {"balaton": [(46.90, 18.04), (46.84, 17.73)]}


def _client(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler))


def _two_locations() -> list[dict]:
    return [
        {
            "daily": {
                "time": ["2026-06-08", "2026-06-09"],
                "precipitation_sum": [0.0, 2.0],
                "temperature_2m_mean": [18.0, 20.0],
                "et0_fao_evapotranspiration": [4.0, 5.0],
            }
        },
        {
            "daily": {
                "time": ["2026-06-08", "2026-06-09"],
                "precipitation_sum": [0.0, 4.0],
                "temperature_2m_mean": [16.0, 22.0],
                "et0_fao_evapotranspiration": [5.0, 6.0],
            }
        },
    ]


def test_fetch_one_call_returns_all_three_variables():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        return httpx.Response(200, json=_two_locations())

    adapter = OpenMeteoWeatherAdapter(AREAS, client=_client(handler))
    readings = adapter.fetch(RANGE)

    # egyetlen hívás mindhárom változóval
    assert "precipitation_sum" in captured["url"]
    assert "temperature_2m_mean" in captured["url"]
    assert "et0_fao_evapotranspiration" in captured["url"]

    assert all(isinstance(r, WeatherReading) for r in readings)
    by_day = {r.date: r for r in readings}
    # 2026-06-09: csapadék (2+4)/2=3.0, hőm (20+22)/2=21.0, ET0 (5+6)/2=5.5
    assert by_day[date(2026, 6, 9)].precip_mm == 3.0
    assert by_day[date(2026, 6, 9)].temp_c == 21.0
    assert by_day[date(2026, 6, 9)].et0_mm == 5.5


def test_fetch_empty_on_source_error():
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(500)

    adapter = OpenMeteoWeatherAdapter(AREAS, client=_client(handler))
    assert adapter.fetch(RANGE) == []


def test_average_daily_multi_skips_nulls():
    locations = [
        {
            "daily": {
                "time": ["2026-06-01"],
                "precipitation_sum": [10.0],
                "temperature_2m_mean": [None],
                "et0_fao_evapotranspiration": [4.0],
            }
        },
        {
            "daily": {
                "time": ["2026-06-01"],
                "precipitation_sum": [20.0],
                "temperature_2m_mean": [18.0],
                "et0_fao_evapotranspiration": [6.0],
            }
        },
    ]
    out = _average_daily_multi(locations)
    assert out[date(2026, 6, 1)] == {
        "precipitation_sum": 15.0,
        "temperature_2m_mean": 18.0,  # az egyetlen nem-null érték
        "et0_fao_evapotranspiration": 5.0,
    }
