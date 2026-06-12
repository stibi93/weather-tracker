"""Portok (interfészek): a domain ezeken keresztül ér el külső adatot.

A konkrét forrás-implementációk (adapterek) az ``ingest.adapters`` csomagban élnek.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date as Date
from typing import Protocol, runtime_checkable

from ingest.domain.models import (
    DischargeReading,
    PrecipReading,
    TempReading,
    WaterLevelReading,
)


@dataclass(frozen=True, slots=True)
class DateRange:
    """Zárt intervallum (mindkét vég beleértve)."""

    start: Date
    end: Date

    def __post_init__(self) -> None:
        if self.end < self.start:
            raise ValueError(f"end ({self.end}) nem lehet korábbi mint start ({self.start})")


@runtime_checkable
class WaterLevelSource(Protocol):
    """Forrásfüggetlen vízállás-port.

    Egy adott időtartamra vízállás-leolvasásokat ad vissza. A domain logika
    kizárólag ezen a porton keresztül ér el forrásadatot — a forrás-specifikus
    részletek az adapterben maradnak.
    """

    def fetch(self, date_range: DateRange) -> list[WaterLevelReading]:
        """Leolvasások a megadott időtartamra. Forráshiba nem dobhat — a hibás
        állomásokat az adapter kihagyja és naplózza."""
        ...


@runtime_checkable
class PrecipitationSource(Protocol):
    """Forrásfüggetlen csapadék-port: víztestenkénti napi területi csapadék."""

    def fetch(self, date_range: DateRange) -> list[PrecipReading]:
        """Csapadék-leolvasások a megadott időtartamra. Forráshiba nem dobhat."""
        ...


@runtime_checkable
class DischargeSource(Protocol):
    """Forrásfüggetlen vízhozam-port: állomásonkénti napi vízhozam (m³/s)."""

    def fetch(self, date_range: DateRange) -> list[DischargeReading]:
        """Vízhozam-leolvasások a megadott időtartamra. Forráshiba nem dobhat."""
        ...


@runtime_checkable
class TemperatureSource(Protocol):
    """Forrásfüggetlen hőmérséklet-port: víztestenkénti napi területi átlaghőmérséklet."""

    def fetch(self, date_range: DateRange) -> list[TempReading]:
        """Hőmérséklet-leolvasások a megadott időtartamra. Forráshiba nem dobhat."""
        ...
