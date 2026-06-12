"""Domain modellek: forrásfüggetlen, immutábilis adatosztályok."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date as Date
from enum import Enum


class WaterBodyKind(str, Enum):
    """Víztest típusa."""

    LAKE = "lake"
    RIVER = "river"


@dataclass(frozen=True, slots=True)
class WaterBody:
    """Megjelenítendő víztest (tó vagy folyó).

    Az `id` stabil, kebab-case azonosító (pl. ``"balaton"``), amelyet az
    artifactok és a frontend is használnak.
    """

    id: str
    name: str
    kind: WaterBodyKind


@dataclass(frozen=True, slots=True)
class Station:
    """Vízrajzi mérőállomás, egy víztesthez rendelve.

    Az `id` a forrás (data.vizugy.hu) állomás-azonosítója (a Tsz/törzsszám
    sztringként). A `lat`/`lon` WGS84 koordináták a megjelenítéshez.
    """

    id: str
    name: str
    water_body_id: str
    lat: float
    lon: float


@dataclass(frozen=True, slots=True)
class WaterLevelReading:
    """Egyetlen vízállás-leolvasás egy állomáson, egy napon.

    A `value_cm` a vízállás centiméterben (a vízrajzi szolgálat egysége).
    """

    station_id: str
    date: Date
    value_cm: float


@dataclass(frozen=True, slots=True)
class DischargeReading:
    """Egy állomás napi vízhozama (m³/s), egy napon."""

    station_id: str
    date: Date
    value_m3s: float


@dataclass(frozen=True, slots=True)
class PrecipReading:
    """Egy víztest területi napi csapadéka (mm), egy napon.

    A `precip_mm` a víztesthez rendelt pont-felhő napi csapadékának átlaga.
    """

    water_body_id: str
    date: Date
    precip_mm: float


@dataclass(frozen=True, slots=True)
class TempReading:
    """Egy víztest területi napi átlaghőmérséklete (°C), egy napon."""

    water_body_id: str
    date: Date
    temp_c: float


@dataclass(frozen=True, slots=True)
class Et0Reading:
    """Egy víztest területi napi referencia-párolgása (ET₀, mm), egy napon."""

    water_body_id: str
    date: Date
    et0_mm: float


@dataclass(frozen=True, slots=True)
class WeatherReading:
    """Egy víztest területi napi időjárása egy hívásból: csapadék, hőmérséklet, ET₀.

    Bármelyik mező lehet ``None``, ha az adott napra hiányzik.
    """

    water_body_id: str
    date: Date
    precip_mm: float | None
    temp_c: float | None
    et0_mm: float | None
