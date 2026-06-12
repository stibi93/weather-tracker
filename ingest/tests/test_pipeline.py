"""A pipeline lánc tesztje injektált forrással (hálózat nélkül)."""

import json
from datetime import date

from ingest.config import STATIONS
from ingest.domain.models import DischargeReading, WaterLevelReading, WeatherReading
from ingest.domain.ports import DateRange
from ingest.pipeline import run


class FakeSource:
    """A `WaterLevelSource` portot kielégítő, determinisztikus teszt-forrás."""

    def __init__(self, readings):
        self._readings = readings
        self.received_range: DateRange | None = None

    def fetch(self, date_range: DateRange):
        self.received_range = date_range
        return self._readings


class FakeWeatherSource:
    """Az `AreaWeatherSource` portot kielégítő teszt-forrás."""

    def __init__(self, readings):
        self._readings = readings

    def fetch(self, _date_range: DateRange):
        return self._readings


class FakeDischargeSource:
    """A `DischargeSource` portot kielégítő teszt-forrás."""

    def __init__(self, readings):
        self._readings = readings

    def fetch(self, _date_range: DateRange):
        return self._readings


def test_run_chains_fetch_store_artifacts(tmp_path):
    fake = FakeSource(
        [
            WaterLevelReading("142300", date(2026, 6, 10), 84),
            WaterLevelReading("142300", date(2026, 6, 11), 83),
            WaterLevelReading("1026", date(2026, 6, 11), 134),  # Duna (folyó)
        ]
    )
    weather = FakeWeatherSource(
        [
            WeatherReading("balaton", date(2026, 6, 10), 4.0, 20.0, 3.5),
            WeatherReading("balaton", date(2026, 6, 11), 12.5, 21.4, 3.2),
        ]
    )
    discharge = FakeDischargeSource([DischargeReading("1026", date(2026, 6, 11), 1343.0)])
    count = run(
        db_path=tmp_path / "c.sqlite",
        out_dir=tmp_path / "out",
        days=30,
        source=fake,
        weather_source=weather,
        discharge_source=discharge,
        today=date(2026, 6, 11),
    )

    assert count == 3
    assert fake.received_range == DateRange(date(2026, 5, 12), date(2026, 6, 11))

    # Minden konfigurált víztest szerepel a geojson-ban (akár adat nélkül is)
    geo = json.loads((tmp_path / "out" / "water-bodies.geojson").read_text(encoding="utf-8"))
    assert len(geo["features"]) == len({s.water_body_id for s in STATIONS})

    balaton = json.loads(
        (tmp_path / "out" / "water-levels" / "balaton.json").read_text(encoding="utf-8")
    )
    assert balaton["latest"] == {"date": "2026-06-11", "value_cm": 83}
    by_date = {p["date"]: p for p in balaton["series"]}
    assert by_date["2026-06-11"]["precip_mm"] == 12.5  # csapadék igazítva
    assert by_date["2026-06-11"]["temp_c"] == 21.4  # hőmérséklet igazítva
    assert by_date["2026-06-11"]["et0_mm"] == 3.2  # párolgás igazítva
    assert by_date["2026-06-11"]["discharge_m3s"] is None  # tónál nincs vízhozam

    # A folyónál (Duna) a vízhozam igazítva jelenik meg
    duna = json.loads((tmp_path / "out" / "water-levels" / "duna.json").read_text(encoding="utf-8"))
    duna_by_date = {p["date"]: p for p in duna["series"]}
    assert duna_by_date["2026-06-11"]["discharge_m3s"] == 1343.0


def test_years_overrides_range_for_backfill(tmp_path):
    from datetime import timedelta

    fake = FakeSource([])
    run(
        db_path=tmp_path / "c.sqlite",
        out_dir=tmp_path / "out",
        years=10,
        source=fake,
        weather_source=FakeWeatherSource([]),
        discharge_source=FakeDischargeSource([]),
        today=date(2026, 6, 11),
    )
    assert fake.received_range == DateRange(date(2026, 6, 11) - timedelta(days=3650), date(2026, 6, 11))
