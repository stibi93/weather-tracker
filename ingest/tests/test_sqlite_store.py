"""A CanonicalStore tesztjei: séma, upsert, idempotencia."""

from datetime import date

from ingest.domain.models import (
    DischargeReading,
    Et0Reading,
    PrecipReading,
    Station,
    TempReading,
    WaterBody,
    WaterBodyKind,
    WaterLevelReading,
)
from ingest.storage import CanonicalStore

BODY = WaterBody("balaton", "Balaton", WaterBodyKind.LAKE)
STATION = Station("142300", "Balaton átlag", "balaton", 46.8838, 17.8154)


def _store(tmp_path):
    store = CanonicalStore(tmp_path / "c.sqlite")
    store.upsert_water_bodies([BODY])
    store.upsert_stations([STATION])
    return store


def test_roundtrip_water_body_and_station(tmp_path):
    with _store(tmp_path) as store:
        assert store.water_bodies() == [BODY]
        assert store.stations() == [STATION]


def test_readings_idempotent_upsert(tmp_path):
    readings = [
        WaterLevelReading("142300", date(2026, 6, 1), 84),
        WaterLevelReading("142300", date(2026, 6, 2), 83),
    ]
    with _store(tmp_path) as store:
        store.upsert_readings(readings)
        store.upsert_readings(readings)  # ugyanaz mégegyszer
        assert store.count_readings() == 2  # nincs duplikátum

        # ugyanarra a kulcsra új érték -> felülír, nem duplikál
        store.upsert_readings([WaterLevelReading("142300", date(2026, 6, 2), 90)])
        assert store.count_readings() == 2
        series = store.readings_for_station("142300")
        assert series == [(date(2026, 6, 1), 84.0), (date(2026, 6, 2), 90.0)]


def test_precip_idempotent_upsert(tmp_path):
    rows = [PrecipReading("balaton", date(2026, 6, 1), 4.0), PrecipReading("balaton", date(2026, 6, 2), 0.0)]
    with _store(tmp_path) as store:
        store.upsert_precip(rows)
        store.upsert_precip(rows)
        assert store.count_precip() == 2
        store.upsert_precip([PrecipReading("balaton", date(2026, 6, 2), 9.5)])
        assert store.count_precip() == 2
        assert store.precip_for_water_body("balaton") == {date(2026, 6, 1): 4.0, date(2026, 6, 2): 9.5}


def test_discharge_idempotent_upsert(tmp_path):
    rows = [DischargeReading("142300", date(2026, 6, 1), 1343.0)]
    with _store(tmp_path) as store:
        store.upsert_discharge(rows)
        store.upsert_discharge(rows)
        assert store.count_discharge() == 1
        store.upsert_discharge([DischargeReading("142300", date(2026, 6, 1), 1400.5)])
        assert store.discharge_for_station("142300") == {date(2026, 6, 1): 1400.5}


def test_temp_idempotent_upsert(tmp_path):
    rows = [TempReading("balaton", date(2026, 6, 1), 18.3)]
    with _store(tmp_path) as store:
        store.upsert_temp(rows)
        store.upsert_temp(rows)
        assert store.count_temp() == 1
        store.upsert_temp([TempReading("balaton", date(2026, 6, 1), 22.0)])
        assert store.temp_for_water_body("balaton") == {date(2026, 6, 1): 22.0}


def test_et0_idempotent_upsert(tmp_path):
    rows = [Et0Reading("balaton", date(2026, 6, 1), 4.2)]
    with _store(tmp_path) as store:
        store.upsert_et0(rows)
        store.upsert_et0(rows)
        assert store.count_et0() == 1
        store.upsert_et0([Et0Reading("balaton", date(2026, 6, 1), 5.0)])
        assert store.et0_for_water_body("balaton") == {date(2026, 6, 1): 5.0}


def test_persists_across_reopen(tmp_path):
    path = tmp_path / "c.sqlite"
    store = CanonicalStore(path)
    store.upsert_water_bodies([BODY])
    store.upsert_stations([STATION])
    store.upsert_readings([WaterLevelReading("142300", date(2026, 6, 1), 84)])
    store.close()

    reopened = CanonicalStore(path)
    assert reopened.count_readings() == 1
    assert reopened.water_bodies() == [BODY]
    reopened.close()
