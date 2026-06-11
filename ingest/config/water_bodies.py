"""A megjelenített víztestek és reprezentatív vizugy-állomásaik.

Az állomás-azonosítók (`Tsz`), nevek és koordináták a data.vizugy.hu API
``Vra/InternetVmo/11`` (felszíni vízállás) állomáslistájából származnak.
A vékony alapban víztestenként egy reprezentatív állomás van; később bővíthető.
"""

from ingest.domain.models import Station, WaterBody, WaterBodyKind

WATER_BODIES: list[WaterBody] = [
    WaterBody("balaton", "Balaton", WaterBodyKind.LAKE),
    WaterBody("velencei-to", "Velencei-tó", WaterBodyKind.LAKE),
    WaterBody("ferto-to", "Fertő tó", WaterBodyKind.LAKE),
    WaterBody("tisza-to", "Tisza-tó (Kisköre)", WaterBodyKind.LAKE),
    WaterBody("duna", "Duna", WaterBodyKind.RIVER),
    WaterBody("tisza", "Tisza", WaterBodyKind.RIVER),
]

STATIONS: list[Station] = [
    Station("142300", "Balaton átlag", "balaton", 46.8838, 17.8154),
    Station("818", "Agárd", "velencei-to", 47.1900, 18.5829),
    Station("52", "Fertőrákos", "ferto-to", 47.7205, 16.6934),
    Station("2041", "Kisköre felső", "tisza-to", 47.4941, 20.5169),
    Station("1026", "Budapest", "duna", 47.4949, 19.0484),
    Station("2046", "Szolnok", "tisza", 47.1696, 20.1886),
]
