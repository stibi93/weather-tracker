"""Open-Meteo adapter a területi időjárás-porthoz (csapadék + hőmérséklet + ET₀).

Az archív (ERA5) API ingyenes, kulcs nélküli, és napi értékeket ad ~10 évre, tegnapig.
Egy hívás víztestenként mindhárom változót lekéri; több koordináta egy hívásban (lokációnkénti
tömb). Víztestenként a pont-felhő napi értékét **átlagoljuk** (területi közelítés).

Endpoint: ``GET https://archive-api.open-meteo.com/v1/archive``
  ``daily=precipitation_sum,temperature_2m_mean,et0_fao_evapotranspiration``
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from datetime import date as Date

import httpx

from ingest.domain.models import WeatherReading
from ingest.domain.ports import DateRange

logger = logging.getLogger(__name__)

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
VARIABLES = ("precipitation_sum", "temperature_2m_mean", "et0_fao_evapotranspiration")
_RATE_LIMIT_RETRIES = 4
_RATE_LIMIT_WAIT_S = 15


def _average_daily_multi(
    locations: list[dict], decimals: int = 1
) -> dict[Date, dict[str, float | None]]:
    """A lokációk napi értékének átlaga változónként (kerekítve)."""
    buckets: dict[str, dict[Date, list[float]]] = {var: defaultdict(list) for var in VARIABLES}
    for loc in locations:
        daily = loc["daily"]
        times = daily["time"]
        for var in VARIABLES:
            for time_str, value in zip(times, daily.get(var, [])):
                if value is None:
                    continue
                buckets[var][Date.fromisoformat(time_str)].append(float(value))

    days: set[Date] = set()
    for var in VARIABLES:
        days |= buckets[var].keys()

    out: dict[Date, dict[str, float | None]] = {}
    for day in sorted(days):
        out[day] = {}
        for var in VARIABLES:
            vals = buckets[var].get(day)
            out[day][var] = round(sum(vals) / len(vals), decimals) if vals else None
    return out


def _fetch_area_weather(
    client: httpx.Client, points: list[tuple[float, float]], date_range: DateRange
) -> dict[Date, dict[str, float | None]]:
    params = {
        "latitude": ",".join(str(lat) for lat, _ in points),
        "longitude": ",".join(str(lon) for _, lon in points),
        "start_date": date_range.start.isoformat(),
        "end_date": date_range.end.isoformat(),
        "daily": ",".join(VARIABLES),
        "timezone": "Europe/Budapest",
    }
    for attempt in range(_RATE_LIMIT_RETRIES):
        resp = client.get(ARCHIVE_URL, params=params)
        if resp.status_code == 429 and attempt < _RATE_LIMIT_RETRIES - 1:
            logger.warning("Open-Meteo rate limit, újrapróba %ds múlva", _RATE_LIMIT_WAIT_S)
            time.sleep(_RATE_LIMIT_WAIT_S)
            continue
        resp.raise_for_status()
        data = resp.json()
        locations = data if isinstance(data, list) else [data]
        return _average_daily_multi(locations)
    return {}


class OpenMeteoWeatherAdapter:
    """Az `AreaWeatherSource` portot implementáló adapter (egy hívás: csapadék+hőmérséklet+ET₀)."""

    def __init__(
        self, areas: dict[str, list[tuple[float, float]]], client: httpx.Client | None = None
    ) -> None:
        self._areas = areas
        self._client = client or httpx.Client(timeout=60.0)

    def fetch(self, date_range: DateRange) -> list[WeatherReading]:
        readings: list[WeatherReading] = []
        for water_body_id, points in self._areas.items():
            try:
                daily = _fetch_area_weather(self._client, points, date_range)
            except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
                logger.error("Open-Meteo lekérés sikertelen (%s): %s", water_body_id, exc)
                continue
            for day, vals in daily.items():
                readings.append(
                    WeatherReading(
                        water_body_id,
                        day,
                        precip_mm=vals["precipitation_sum"],
                        temp_c=vals["temperature_2m_mean"],
                        et0_mm=vals["et0_fao_evapotranspiration"],
                    )
                )
        return readings
