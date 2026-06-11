"""A CanonicalStore tesztjei: séma, upsert, idempotencia."""

from datetime import date

from ingest.domain.models import Station, WaterBody, WaterBodyKind, WaterLevelReading
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
