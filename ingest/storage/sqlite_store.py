"""Kanonikus SQLite tár.

Az igazságforrás: víztestek, állomások és vízállás-leolvasások. Minden írás
idempotens upsert — ugyanaz a futtatás megismételhető duplikáció nélkül. A
leolvasások egyedi kulcsa ``(station_id, date)``.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from datetime import date as Date
from pathlib import Path

from ingest.domain.models import Station, WaterBody, WaterBodyKind, WaterLevelReading

_SCHEMA = """
CREATE TABLE IF NOT EXISTS water_body (
    id   TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    kind TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS station (
    id            TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    water_body_id TEXT NOT NULL REFERENCES water_body(id),
    lat           REAL NOT NULL,
    lon           REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS water_level_reading (
    station_id TEXT NOT NULL REFERENCES station(id),
    date       TEXT NOT NULL,
    value_cm   REAL NOT NULL,
    PRIMARY KEY (station_id, date)
);
"""


class CanonicalStore:
    """SQLite-alapú kanonikus tár. Használható context managerként is."""

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        self._conn = sqlite3.connect(self.path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    # -- írás (idempotens) -------------------------------------------------

    def upsert_water_bodies(self, bodies: Iterable[WaterBody]) -> None:
        self._conn.executemany(
            "INSERT INTO water_body (id, name, kind) VALUES (?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET name=excluded.name, kind=excluded.kind",
            [(b.id, b.name, b.kind.value) for b in bodies],
        )
        self._conn.commit()

    def upsert_stations(self, stations: Iterable[Station]) -> None:
        self._conn.executemany(
            "INSERT INTO station (id, name, water_body_id, lat, lon) VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET name=excluded.name, "
            "water_body_id=excluded.water_body_id, lat=excluded.lat, lon=excluded.lon",
            [(s.id, s.name, s.water_body_id, s.lat, s.lon) for s in stations],
        )
        self._conn.commit()

    def upsert_readings(self, readings: Iterable[WaterLevelReading]) -> None:
        self._conn.executemany(
            "INSERT INTO water_level_reading (station_id, date, value_cm) VALUES (?, ?, ?) "
            "ON CONFLICT(station_id, date) DO UPDATE SET value_cm=excluded.value_cm",
            [(r.station_id, r.date.isoformat(), float(r.value_cm)) for r in readings],
        )
        self._conn.commit()

    # -- olvasás -----------------------------------------------------------

    def water_bodies(self) -> list[WaterBody]:
        rows = self._conn.execute("SELECT id, name, kind FROM water_body ORDER BY id").fetchall()
        return [WaterBody(r["id"], r["name"], WaterBodyKind(r["kind"])) for r in rows]

    def stations(self) -> list[Station]:
        rows = self._conn.execute(
            "SELECT id, name, water_body_id, lat, lon FROM station ORDER BY id"
        ).fetchall()
        return [Station(r["id"], r["name"], r["water_body_id"], r["lat"], r["lon"]) for r in rows]

    def readings_for_station(self, station_id: str) -> list[tuple[Date, float]]:
        rows = self._conn.execute(
            "SELECT date, value_cm FROM water_level_reading WHERE station_id = ? ORDER BY date",
            (station_id,),
        ).fetchall()
        return [(Date.fromisoformat(r["date"]), r["value_cm"]) for r in rows]

    def count_readings(self) -> int:
        return self._conn.execute("SELECT COUNT(*) FROM water_level_reading").fetchone()[0]

    # -- élettartam --------------------------------------------------------

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "CanonicalStore":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
