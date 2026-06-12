## Context

A csapadék és a hőmérséklet már a grafikonon van, külön Open-Meteo adapterekkel. Az ET₀
(`et0_fao_evapotranspiration`) ugyanabból az archív hívásból elérhető. Három különálló hívás
víztestenként (18) a rate limitet veri (a hőmérsékletnél már láttunk 429-et) — konszolidáljuk.

## Goals / Non-Goals

**Goals:**
- Napi ET₀ víztestenként (~10 év), a vízállás-idősorhoz igazítva (`et0_mm`).
- Egyetlen Open-Meteo hívás víztestenként (csapadék + hőmérséklet + ET₀).
- A grafikon másodlagos váltója harmadik opcióval (párolgás).

**Non-Goals:**
- Vízmérleg (precip − ET₀) explicit modell — a következő (korreláció) feature témája.

## Decisions

- **Kombinált `OpenMeteoWeatherAdapter`, `WeatherReading`-gel.** Egy hívás víztestenként a
  `daily=precipitation_sum,temperature_2m_mean,et0_fao_evapotranspiration` paraméterrel; a válasz
  lokációnkénti tömbjéből mindhárom változó napi átlaga. Visszaad
  `WeatherReading(water_body_id, date, precip_mm, temp_c, et0_mm)`-et. Leváltja a két korábbi
  külön adaptert és a `PrecipitationSource`/`TemperatureSource` portot egy `AreaWeatherSource`-ra.
  *Miért X Y helyett:* 6 hívás 18 helyett → nincs rate-limit gond; DRY; a három metrika
  természetesen egy „területi időjárás" lekérés.
- **Tárolás külön táblákban marad.** A pipeline a `WeatherReading`-et szétbontja és a meglévő
  `precip_reading`/`temp_reading` + új `et0_reading` táblákba írja. *Miért:* a tároló- és
  artifact-réteg változatlan; csak a lekérés konszolidálódik.
- **ET₀ vonalként, mm-ben.** A másodlagos váltó: csapadék (oszlop, mm), hőmérséklet (vonal, °C),
  párolgás (vonal, mm). Az ET₀ a párolgási igény — vonal illik hozzá, megkülönböztető színnel
  (terrakotta/vörös), a csapadék-oszloptól elkülönülve.

## Risks / Trade-offs

- [A konszolidáció leváltja a meglévő precip/temp adaptert] → a tároló/artifact/teszt-séma
  stabil marad; csak a fetch-réteg és a pipeline-bekötés változik, fixture-alapú tesztekkel fedve.
- [Open-Meteo rate limit] → a megtartott 429-retry továbbra is véd; 6 hívással ritkán szükséges.
