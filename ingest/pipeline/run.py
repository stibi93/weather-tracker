"""A pipeline belépési pontja: víztest/állomás seed → vizugy lehúzás →
idempotens tárolás → artifact-generálás.

Kézi futtatás::

    python -m ingest.pipeline.run --db data/canonical.sqlite --out web/public/data --days 30
"""

from __future__ import annotations

import argparse
import logging
from datetime import date, timedelta
from pathlib import Path

from ingest.adapters.openmeteo import OpenMeteoPrecipAdapter
from ingest.adapters.vizugy import VizugyApiAdapter, VizugyDischargeAdapter
from ingest.artifacts import generate_artifacts
from ingest.config import PRECIP_AREAS, STATIONS, WATER_BODIES
from ingest.domain.models import WaterBodyKind
from ingest.domain.ports import (
    DateRange,
    DischargeSource,
    PrecipitationSource,
    WaterLevelSource,
)
from ingest.storage import CanonicalStore

_RIVER_BODY_IDS = {b.id for b in WATER_BODIES if b.kind == WaterBodyKind.RIVER}
_RIVER_STATION_IDS = [s.id for s in STATIONS if s.water_body_id in _RIVER_BODY_IDS]

logger = logging.getLogger("ingest.pipeline")

DEFAULT_DB = "data/canonical.sqlite"
DEFAULT_OUT = "web/public/data"
DEFAULT_DAYS = 30


def run(
    db_path: str | Path = DEFAULT_DB,
    out_dir: str | Path = DEFAULT_OUT,
    days: int = DEFAULT_DAYS,
    years: int | None = None,
    source: WaterLevelSource | None = None,
    precip_source: PrecipitationSource | None = None,
    discharge_source: DischargeSource | None = None,
    today: date | None = None,
) -> int:
    """Lefuttatja a teljes láncot. Visszaadja a tárolt vízállás-leolvasások számát.

    Ha `years` meg van adva, az határozza meg a visszamenő tartományt (historikus
    backfill); különben `days`. A `source`/`precip_source`/`today` injektálható teszthez.
    """
    today = today or date.today()
    source = source or VizugyApiAdapter([s.id for s in STATIONS])
    precip_source = precip_source or OpenMeteoPrecipAdapter(PRECIP_AREAS)
    discharge_source = discharge_source or VizugyDischargeAdapter(_RIVER_STATION_IDS)
    span = timedelta(days=years * 365) if years else timedelta(days=days)

    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    store = CanonicalStore(db_path)
    try:
        store.upsert_water_bodies(WATER_BODIES)
        store.upsert_stations(STATIONS)

        date_range = DateRange(today - span, today)
        readings = source.fetch(date_range)
        store.upsert_readings(readings)
        logger.info("%d vízállás-leolvasás tárolva (%s..%s)", len(readings), date_range.start, date_range.end)

        precip = precip_source.fetch(date_range)
        store.upsert_precip(precip)
        logger.info("%d csapadék-leolvasás tárolva", len(precip))

        discharge = discharge_source.fetch(date_range)
        store.upsert_discharge(discharge)
        logger.info("%d vízhozam-leolvasás tárolva", len(discharge))

        generate_artifacts(store, out_dir)
        logger.info("artifactok legenerálva: %s", out_dir)
        return len(readings)
    finally:
        store.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Vízállás ingest pipeline (vizugy)")
    parser.add_argument("--db", default=DEFAULT_DB, help="kanonikus SQLite útvonal")
    parser.add_argument("--out", default=DEFAULT_OUT, help="artifact kimeneti mappa")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS, help="hány napra visszamenőleg")
    parser.add_argument("--years", type=int, default=None, help="historikus backfill évszáma (felülírja a --days-t)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    count = run(db_path=args.db, out_dir=args.out, days=args.days, years=args.years)
    print(f"Kész: {count} leolvasás, artifactok itt: {args.out}")


if __name__ == "__main__":
    main()
