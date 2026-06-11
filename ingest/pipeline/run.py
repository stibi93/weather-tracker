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

from ingest.adapters.vizugy import VizugyApiAdapter
from ingest.artifacts import generate_artifacts
from ingest.config import STATIONS, WATER_BODIES
from ingest.domain.ports import DateRange, WaterLevelSource
from ingest.storage import CanonicalStore

logger = logging.getLogger("ingest.pipeline")

DEFAULT_DB = "data/canonical.sqlite"
DEFAULT_OUT = "web/public/data"
DEFAULT_DAYS = 30


def run(
    db_path: str | Path = DEFAULT_DB,
    out_dir: str | Path = DEFAULT_OUT,
    days: int = DEFAULT_DAYS,
    source: WaterLevelSource | None = None,
    today: date | None = None,
) -> int:
    """Lefuttatja a teljes láncot. Visszaadja a tárolt leolvasások számát.

    A `source` és `today` injektálható teszthez; alapból éles vizugy adapter és
    a mai nap.
    """
    today = today or date.today()
    source = source or VizugyApiAdapter([s.id for s in STATIONS])

    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    store = CanonicalStore(db_path)
    try:
        store.upsert_water_bodies(WATER_BODIES)
        store.upsert_stations(STATIONS)

        date_range = DateRange(today - timedelta(days=days), today)
        readings = source.fetch(date_range)
        store.upsert_readings(readings)
        logger.info("%d leolvasás tárolva (%s..%s)", len(readings), date_range.start, date_range.end)

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
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    count = run(db_path=args.db, out_dir=args.out, days=args.days)
    print(f"Kész: {count} leolvasás, artifactok itt: {args.out}")


if __name__ == "__main__":
    main()
