## Why

A hőmérséklet fontos kontextus a vízálláshoz — különösen a sekély tavaknál, ahol a nyári
**párolgás** (amit a hőmérséklet hajt) a vízszintesés fő oka. Az Open-Meteo ugyanabból a
hívásból adja, amit a csapadékhoz már használunk. Tegyük a grafikonra választható
másodlagos rétegként a csapadék mellé.

## What Changes

- Az ingest víztestenként napi **átlaghőmérsékletet** (°C) is lehúz az Open-Meteo-ból (a
  vízgyűjtő-közeli pont-felhő átlaga), ~10 évre, a vízállás-idősorhoz igazítva.
- A `water-levels/{id}.json` minden idősor-pontja kap egy `temp_c` mezőt (vagy `null`).
- A grafikon jobb tengelyén **másodlagos kontextus-váltó**: Csapadék (oszlop, mm) ↔
  Hőmérséklet (vonal, °C). A tooltip az aktív másodlagos értéket is mutatja.

## Capabilities

### New Capabilities
- `temperature-context`: víztestenkénti napi területi átlaghőmérséklet lehúzása, tárolása, és a
  vízállás-idősorhoz igazított hőmérséklet-sorozat az artifactban.

### Modified Capabilities
- `water-level-detail-panel`: új követelmény — másodlagos kontextus-váltó a grafikonon
  (csapadék ↔ hőmérséklet).

## Impact

- `ingest`: új `TempReading` + `TemperatureSource` port; `OpenMeteoTempAdapter` (közös Open-Meteo
  segédfüggvény a csapadék-adapterrel); `temp_reading` tábla; a pipeline lehúzza+tárolja; az
  artifact igazítja.
- `web`: a `Chart` másodlagos rétege csapadék (oszlop) vagy hőmérséklet (vonal); a `DetailPanel`
  kontextus-váltóval.
