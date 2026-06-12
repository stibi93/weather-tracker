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

# Víztestenkénti vízgyűjtő-közeli pont-felhő a területi napi csapadék átlagolásához
# (Open-Meteo). Közelítés, nem valódi vízgyűjtő-poligon; a tavaknál beszédesebb, mint a folyóknál.
PRECIP_AREAS: dict[str, list[tuple[float, float]]] = {
    # Balaton + Zala-vízgyűjtő (DNy)
    "balaton": [(46.90, 18.04), (46.84, 17.73), (46.77, 17.25), (46.84, 16.84)],
    "velencei-to": [(47.19, 18.58), (47.22, 18.66), (47.24, 18.50)],
    "ferto-to": [(47.66, 16.75), (47.70, 16.83), (47.62, 16.90)],
    # Tisza-tó + helyi Tisza-szakasz
    "tisza-to": [(47.49, 20.52), (47.62, 20.75), (47.55, 20.40)],
    # Duna helyi szakasz (a helyi csapadék gyenge proxy a felvízi vízgyűjtőhöz képest)
    "duna": [(47.49, 19.05), (47.79, 18.96), (47.69, 19.07)],
    # Tisza helyi szakasz
    "tisza": [(47.17, 20.19), (47.34, 20.27), (46.92, 20.13)],
}
