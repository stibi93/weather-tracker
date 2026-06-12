"""data.vizugy.hu adapterek a vízállás- és vízhozam-portokhoz.

A hozzáférés visszafejtve a hivatalos portál (Angular SPA) hálózati hívásaiból:

- Token:    ``GET  https://data.vizugy.hu/AuthApi/auth/token``   (``Origin`` fejléccel,
            anonim JWT-t ad ``access_token`` mezőben)
- Idősor:   ``POST https://vmservice.vizugy.hu/vraquery/TS/TsShortList``  (``Bearer`` token)
            body: ``torzsszamList``, ``adatFajtaKod`` (68 = felszíni vízállás [cm],
            87 = felszíni vízhozam [m³/s]), ``adatTipusKod=100``, ``valueFilter="Relativ"``,
            ``amKodFilter=[0]``, ``startTime``/``endTime`` (ISO dátum).
            válasz: ``[{ItemId, TsItemList:[{UTCTime, Adat}]}]``.

Egyes állomások órás adatot adnak, ezért naponként egy értékre aggregálunk (átlag).
Forráshiba nem dob: a hibát naplózzuk, az érintett rész kimarad.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime

import httpx

from ingest.domain.models import DischargeReading, WaterLevelReading
from ingest.domain.ports import DateRange

logger = logging.getLogger(__name__)

TOKEN_URL = "https://data.vizugy.hu/AuthApi/auth/token"
QUERY_ROOT = "https://vmservice.vizugy.hu/vraquery/"
ORIGIN = "https://data.vizugy.hu"
SURFACE_WATER_LEVEL_CODE = 68  # "Felszíni vízállás" [cm]
SURFACE_DISCHARGE_CODE = 87  # "Felszíni vízhozam" [m³/s]


def _get_token(client: httpx.Client) -> str:
    resp = client.get(TOKEN_URL, headers={"Origin": ORIGIN, "Referer": ORIGIN + "/"})
    resp.raise_for_status()
    return resp.json()["access_token"]


def _post_ts(
    client: httpx.Client, token: str, station_ids: list[str], code: int, date_range: DateRange
) -> list[dict]:
    body = {
        "torzsszamList": [int(s) for s in station_ids],
        "adatFajtaKod": code,
        "adatTipusKod": 100,
        "valueFilter": "Relativ",
        "amKodFilter": [0],
        "startTime": date_range.start.isoformat(),
        "endTime": date_range.end.isoformat(),
    }
    resp = client.post(
        QUERY_ROOT + "TS/TsShortList",
        json=body,
        headers={"Authorization": f"Bearer {token}", "Origin": ORIGIN},
    )
    resp.raise_for_status()
    return resp.json()


def _fetch_daily_values(
    client: httpx.Client, station_ids: list[str], code: int, date_range: DateRange, decimals: int
) -> dict[str, dict]:
    """Állomásonkénti napi aggregált értékek a megadott adatfajtára. Sosem dob."""
    try:
        token = _get_token(client)
        items = _post_ts(client, token, station_ids, code, date_range)
    except (httpx.HTTPError, KeyError, ValueError) as exc:
        logger.error("vizugy lekérés sikertelen (kód %s), kimarad: %s", code, exc)
        return {}
    out: dict[str, dict] = {}
    for item in items:
        try:
            out[str(item["ItemId"])] = _aggregate_daily(item.get("TsItemList", []), decimals)
        except (KeyError, TypeError) as exc:
            logger.warning("hibás állomás-elem kihagyva: %s", exc)
    return out


def _aggregate_daily(ts_item_list: list[dict], decimals: int = 0) -> dict:
    """Órás/napi pontokból naponként egy érték (átlag). Pontonként hibatűrő.

    ``decimals=0`` egész értéket ad (pl. cm), egyébként float (pl. m³/s).
    """
    buckets: dict = defaultdict(list)
    for point in ts_item_list:
        try:
            value = point["Adat"]
            if value is None or value == "":
                continue
            day = datetime.fromisoformat(point["UTCTime"]).date()
            buckets[day].append(float(value))
        except (KeyError, TypeError, ValueError):
            continue
    out = {}
    for day, vals in sorted(buckets.items()):
        mean = sum(vals) / len(vals)
        out[day] = int(round(mean)) if decimals == 0 else round(mean, decimals)
    return out


class VizugyApiAdapter:
    """A `WaterLevelSource` portot implementáló adapter (felszíni vízállás, cm)."""

    def __init__(self, station_ids: list[str], client: httpx.Client | None = None) -> None:
        self._station_ids = list(station_ids)
        self._client = client or httpx.Client(timeout=40.0)

    def fetch(self, date_range: DateRange) -> list[WaterLevelReading]:
        by_station = _fetch_daily_values(
            self._client, self._station_ids, SURFACE_WATER_LEVEL_CODE, date_range, decimals=0
        )
        return [
            WaterLevelReading(sid, day, value)
            for sid, daily in by_station.items()
            for day, value in daily.items()
        ]


class VizugyDischargeAdapter:
    """A `DischargeSource` portot implementáló adapter (felszíni vízhozam, m³/s)."""

    def __init__(self, station_ids: list[str], client: httpx.Client | None = None) -> None:
        self._station_ids = list(station_ids)
        self._client = client or httpx.Client(timeout=40.0)

    def fetch(self, date_range: DateRange) -> list[DischargeReading]:
        by_station = _fetch_daily_values(
            self._client, self._station_ids, SURFACE_DISCHARGE_CODE, date_range, decimals=1
        )
        return [
            DischargeReading(sid, day, value)
            for sid, daily in by_station.items()
            for day, value in daily.items()
        ]
