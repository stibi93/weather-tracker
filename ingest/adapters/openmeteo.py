"""Open-Meteo adapterek a csapadék- és hőmérséklet-portokhoz.

Az archív (ERA5) API ingyenes, kulcs nélküli, és napi értékeket ad ~10 évre, tegnapig.
Több koordináta egy hívásban: a válasz lokációnkénti tömb. Víztestenként a hozzá rendelt
pont-felhő napi értékét **átlagoljuk** (területi közelítés).

Endpoint: ``GET https://archive-api.open-meteo.com/v1/archive``
  params: ``latitude=a,b``, ``longitude=x,y``, ``start_date``, ``end_date``,
          ``daily=<változó>``, ``timezone=Europe/Budapest``
  változók: ``precipitation_sum`` [mm], ``temperature_2m_mean`` [°C].
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from datetime import date as Date

import httpx

from ingest.domain.models import PrecipReading, TempReading
from ingest.domain.ports import DateRange

logger = logging.getLogger(__name__)

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
_RATE_LIMIT_RETRIES = 4
_RATE_LIMIT_WAIT_S = 15


def _average_daily(locations: list[dict], variable: str, decimals: int) -> dict[Date, float]:
    """A lokációk napi értékének átlaga a megadott változóra (kerekítve)."""
    buckets: dict[Date, list[float]] = defaultdict(list)
    for loc in locations:
        daily = loc["daily"]
        for time, value in zip(daily["time"], daily[variable]):
            if value is None:
                continue
            buckets[Date.fromisoformat(time)].append(float(value))
    return {day: round(sum(vals) / len(vals), decimals) for day, vals in sorted(buckets.items())}


def _fetch_area_daily(
    client: httpx.Client,
    points: list[tuple[float, float]],
    variable: str,
    date_range: DateRange,
    decimals: int,
) -> dict[Date, float]:
    """Egy víztest pont-felhőjének napi átlaga a megadott változóra."""
    params = {
        "latitude": ",".join(str(lat) for lat, _ in points),
        "longitude": ",".join(str(lon) for _, lon in points),
        "start_date": date_range.start.isoformat(),
        "end_date": date_range.end.isoformat(),
        "daily": variable,
        "timezone": "Europe/Budapest",
    }
    for attempt in range(_RATE_LIMIT_RETRIES):
        resp = client.get(ARCHIVE_URL, params=params)
        if resp.status_code == 429 and attempt < _RATE_LIMIT_RETRIES - 1:
            logger.warning("Open-Meteo rate limit (%s), újrapróba %ds múlva", variable, _RATE_LIMIT_WAIT_S)
            time.sleep(_RATE_LIMIT_WAIT_S)
            continue
        resp.raise_for_status()
        data = resp.json()
        locations = data if isinstance(data, list) else [data]
        return _average_daily(locations, variable, decimals)
    return {}


def _fetch_by_water_body(
    client: httpx.Client,
    areas: dict[str, list[tuple[float, float]]],
    variable: str,
    date_range: DateRange,
    decimals: int,
) -> dict[str, dict[Date, float]]:
    """Víztestenként a napi átlag a megadott változóra. Sosem dob."""
    out: dict[str, dict[Date, float]] = {}
    for water_body_id, points in areas.items():
        try:
            out[water_body_id] = _fetch_area_daily(client, points, variable, date_range, decimals)
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
            logger.error("Open-Meteo lekérés sikertelen (%s, %s): %s", water_body_id, variable, exc)
    return out


class OpenMeteoPrecipAdapter:
    """A `PrecipitationSource` portot implementáló adapter (napi csapadék, mm)."""

    def __init__(
        self, areas: dict[str, list[tuple[float, float]]], client: httpx.Client | None = None
    ) -> None:
        self._areas = areas
        self._client = client or httpx.Client(timeout=60.0)

    def fetch(self, date_range: DateRange) -> list[PrecipReading]:
        by_body = _fetch_by_water_body(self._client, self._areas, "precipitation_sum", date_range, 1)
        return [
            PrecipReading(wb_id, day, mm)
            for wb_id, daily in by_body.items()
            for day, mm in daily.items()
        ]


class OpenMeteoTempAdapter:
    """A `TemperatureSource` portot implementáló adapter (napi átlaghőmérséklet, °C)."""

    def __init__(
        self, areas: dict[str, list[tuple[float, float]]], client: httpx.Client | None = None
    ) -> None:
        self._areas = areas
        self._client = client or httpx.Client(timeout=60.0)

    def fetch(self, date_range: DateRange) -> list[TempReading]:
        by_body = _fetch_by_water_body(self._client, self._areas, "temperature_2m_mean", date_range, 1)
        return [
            TempReading(wb_id, day, temp)
            for wb_id, daily in by_body.items()
            for day, temp in daily.items()
        ]
