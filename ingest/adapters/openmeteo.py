"""Open-Meteo adapter a `PrecipitationSource` porthoz.

Az archív (ERA5) API ingyenes, kulcs nélküli, és napi csapadékot ad ~10 évre, tegnapig.
Több koordináta egy hívásban: a válasz lokációnkénti tömb. Víztestenként a hozzá rendelt
pont-felhő napi csapadékát **átlagoljuk** (területi közelítés).

Endpoint: ``GET https://archive-api.open-meteo.com/v1/archive``
  params: ``latitude=a,b``, ``longitude=x,y``, ``start_date``, ``end_date``,
          ``daily=precipitation_sum``, ``timezone=Europe/Budapest``
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import date as Date

import httpx

from ingest.domain.models import PrecipReading
from ingest.domain.ports import DateRange

logger = logging.getLogger(__name__)

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"


class OpenMeteoPrecipAdapter:
    """A `PrecipitationSource` portot implementáló Open-Meteo adapter."""

    def __init__(
        self,
        areas: dict[str, list[tuple[float, float]]],
        client: httpx.Client | None = None,
    ) -> None:
        self._areas = areas
        self._client = client or httpx.Client(timeout=60.0)

    def fetch(self, date_range: DateRange) -> list[PrecipReading]:
        """Víztestenkénti napi területi csapadék. Sosem dob."""
        readings: list[PrecipReading] = []
        for water_body_id, points in self._areas.items():
            try:
                daily = self._fetch_area(points, date_range)
            except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
                logger.error("csapadék lekérés sikertelen (%s): %s", water_body_id, exc)
                continue
            for day, mm in daily.items():
                readings.append(PrecipReading(water_body_id, day, mm))
        return readings

    def _fetch_area(
        self, points: list[tuple[float, float]], date_range: DateRange
    ) -> dict[Date, float]:
        params = {
            "latitude": ",".join(str(lat) for lat, _ in points),
            "longitude": ",".join(str(lon) for _, lon in points),
            "start_date": date_range.start.isoformat(),
            "end_date": date_range.end.isoformat(),
            "daily": "precipitation_sum",
            "timezone": "Europe/Budapest",
        }
        resp = self._client.get(ARCHIVE_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
        locations = data if isinstance(data, list) else [data]
        return _average_daily(locations)


def _average_daily(locations: list[dict]) -> dict[Date, float]:
    """A lokációk napi csapadékának átlaga (mm, egy tizedesre)."""
    buckets: dict[Date, list[float]] = defaultdict(list)
    for loc in locations:
        daily = loc["daily"]
        for time, value in zip(daily["time"], daily["precipitation_sum"]):
            if value is None:
                continue
            buckets[Date.fromisoformat(time)].append(float(value))
    return {day: round(sum(vals) / len(vals), 1) for day, vals in sorted(buckets.items())}
