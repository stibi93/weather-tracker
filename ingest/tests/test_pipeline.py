"""A pipeline lánc tesztje injektált forrással (hálózat nélkül)."""

import json
from datetime import date

from ingest.config import STATIONS
from ingest.domain.models import WaterLevelReading
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


def test_run_chains_fetch_store_artifacts(tmp_path):
    fake = FakeSource(
        [
            WaterLevelReading("142300", date(2026, 6, 10), 84),
            WaterLevelReading("142300", date(2026, 6, 11), 83),
            WaterLevelReading("818", date(2026, 6, 11), 120),
        ]
    )
    count = run(
        db_path=tmp_path / "c.sqlite",
        out_dir=tmp_path / "out",
        days=30,
        source=fake,
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
