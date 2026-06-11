"""data.vizugy.hu adapter a `WaterLevelSource` porthoz.

A hozzáférés visszafejtve a hivatalos portál (Angular SPA) hálózati hívásaiból:

- Token:    ``GET  https://data.vizugy.hu/AuthApi/auth/token``   (``Origin`` fejléccel,
            anonim JWT-t ad ``access_token`` mezőben)
- Idősor:   ``POST https://vmservice.vizugy.hu/vraquery/TS/TsShortList``  (``Bearer`` token)
            body: ``torzsszamList``, ``adatFajtaKod=68`` (felszíni vízállás),
            ``adatTipusKod=100``, ``valueFilter="Relativ"``, ``amKodFilter=[0]``,
            ``startTime``/``endTime`` (ISO dátum).
            válasz: ``[{ItemId, TsItemList:[{UTCTime, Adat}]}]`` — ``Adat`` cm-ben.

Egyes állomások órás adatot adnak, ezért naponként egy értékre aggregálunk (átlag, cm-re
kerekítve). Forráshiba nem dob: a hibát naplózzuk, az érintett rész kimarad.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime

import httpx

from ingest.domain.models import WaterLevelReading
from ingest.domain.ports import DateRange

logger = logging.getLogger(__name__)

TOKEN_URL = "https://data.vizugy.hu/AuthApi/auth/token"
QUERY_ROOT = "https://vmservice.vizugy.hu/vraquery/"
ORIGIN = "https://data.vizugy.hu"
SURFACE_WATER_LEVEL_CODE = 68  # "Felszíni vízállás"


class VizugyApiAdapter:
    """A `WaterLevelSource` portot implementáló data.vizugy.hu adapter."""

    def __init__(self, station_ids: list[str], client: httpx.Client | None = None) -> None:
        self._station_ids = list(station_ids)
        self._client = client or httpx.Client(timeout=40.0)

    def fetch(self, date_range: DateRange) -> list[WaterLevelReading]:
        """Napi vízállás-leolvasások a konfigurált állomásokra. Sosem dob."""
        try:
            token = self._get_token()
            items = self._post_ts(token, date_range)
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            logger.error("vizugy lekérés sikertelen, a futás kimarad: %s", exc)
            return []

        readings: list[WaterLevelReading] = []
        for item in items:
            try:
                station_id = str(item["ItemId"])
                for day, value in _aggregate_daily(item.get("TsItemList", [])).items():
                    readings.append(WaterLevelReading(station_id, day, value))
            except (KeyError, TypeError, ValueError) as exc:
                logger.warning("hibás állomás-adat kihagyva (%r): %s", item, exc)
        return readings

    def _get_token(self) -> str:
        resp = self._client.get(TOKEN_URL, headers={"Origin": ORIGIN, "Referer": ORIGIN + "/"})
        resp.raise_for_status()
        return resp.json()["access_token"]

    def _post_ts(self, token: str, date_range: DateRange) -> list[dict]:
        body = {
            "torzsszamList": [int(s) for s in self._station_ids],
            "adatFajtaKod": SURFACE_WATER_LEVEL_CODE,
            "adatTipusKod": 100,
            "valueFilter": "Relativ",
            "amKodFilter": [0],
            "startTime": date_range.start.isoformat(),
            "endTime": date_range.end.isoformat(),
        }
        resp = self._client.post(
            QUERY_ROOT + "TS/TsShortList",
            json=body,
            headers={"Authorization": f"Bearer {token}", "Origin": ORIGIN},
        )
        resp.raise_for_status()
        return resp.json()


def _aggregate_daily(ts_item_list: list[dict]) -> dict:
    """Órás/napi pontokból naponként egy érték (átlag, cm-re kerekítve)."""
    buckets: dict = defaultdict(list)
    for point in ts_item_list:
        utc = point["UTCTime"]
        value = point["Adat"]
        if value is None or value == "":
            continue
        day = datetime.fromisoformat(utc).date()
        buckets[day].append(float(value))
    return {day: round(sum(vals) / len(vals)) for day, vals in sorted(buckets.items())}
