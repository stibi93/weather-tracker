## Why

A sekély tavaknál a **párolgás** a nyári vízszintesés fő oka — a hőmérsékletnél is
közvetlenebb mérőszám. Az Open-Meteo a referencia-párolgást (ET₀, FAO) ugyanabból a
hívásból adja, amit a csapadékhoz/hőmérséklethez már használunk. Tegyük a grafikonra
harmadik választható másodlagos rétegként.

Egyúttal: most három Open-Meteo változó (csapadék, hőmérséklet, párolgás) három külön
hívást jelentene víztestenként (18 nagy hívás), ami a rate limitet veri. Konszolidáljuk
egyetlen hívásba (6 összesen), tisztább és gyorsabb.

## What Changes

- Az ingest víztestenként napi **ET₀-t (mm)** is lehúz az Open-Meteo-ból, a vízállás-idősorhoz
  igazítva (`et0_mm` minden ponton, vagy `null`).
- **Open-Meteo konszolidáció:** egyetlen `OpenMeteoWeatherAdapter` (egy hívásban csapadék +
  hőmérséklet + ET₀) váltja a két korábbi külön adaptert (csapadék, hőmérséklet).
- A grafikon másodlagos kontextus-váltója harmadik opciót kap: **Párolgás** (vonal, mm).

## Capabilities

### New Capabilities
- `evaporation-context`: víztestenkénti napi ET₀ lehúzása (a konszolidált Open-Meteo hívásból),
  tárolása, és a vízállás-idősorhoz igazított ET₀-sorozat az artifactban.

### Modified Capabilities
- `water-level-detail-panel`: a másodlagos kontextus-váltó harmadik opcióval bővül (párolgás).

## Impact

- `ingest`: új `Et0Reading` + `WeatherReading` (kombinált) + `AreaWeatherSource` port;
  `OpenMeteoWeatherAdapter` (a csapadék/hőmérséklet külön adaptert + portot leváltja); `et0_reading`
  tábla; a pipeline a kombinált forrásból tölti a három metrikát.
- `web`: a `Chart`/`DetailPanel` másodlagos rétege párolgással is (Csapadék/Hőmérséklet/Párolgás).
