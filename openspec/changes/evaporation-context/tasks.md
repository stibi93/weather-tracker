## 1. Domain és kombinált adapter

- [x] 1.1 Domain: `Et0Reading` + kombinált `WeatherReading(water_body_id, date, precip_mm, temp_c, et0_mm)`; `AreaWeatherSource` port (a Precip/Temperature port leváltása)
- [x] 1.2 `OpenMeteoWeatherAdapter`: egy hívás víztestenként (precip+temp+et0), a régi két adapter leváltása; 429-retry megtartva
- [x] 1.3 Adapter unit-teszt fixture-ön (kombinált válasz, élő hálózat nélkül)

## 2. Tárolás és pipeline

- [x] 2.1 `et0_reading` tábla + idempotens upsert + `et0_for_water_body`
- [x] 2.2 A pipeline a kombinált `WeatherReading`-et szétbontja és tárolja (precip/temp/et0)
- [x] 2.3 Teszt: idempotens ET₀-tárolás

## 3. Artifact: igazított ET₀

- [x] 3.1 Minden idősor-pont kap `et0_mm`-t (bucket napi átlaga, vagy null)
- [x] 3.2 Teszt: az igazítás helyes, determinisztikus

## 4. Frontend: párolgás a másodlagos váltóban

- [x] 4.1 A `Chart` másodlagos rétege párolgással is (vonal, mm, terrakotta); jobb tengely + tooltip
- [x] 4.2 A `DetailPanel` kontextus-váltója harmadik gombbal (Párolgás); jelmagyarázat
- [x] 4.3 A (C) földes stílushoz illő szín (#b5562e)

## 5. Verifikáció

- [x] 5.1 `ingest` tesztek zölden (24 teszt; átírt openmeteo-teszt + új ET₀-tesztek)
- [x] 5.2 Éles futtatás: 6 Open-Meteo hívás (18 helyett), ET₀ lehúzva+tárolva (mind a 6 víztest 828/828)
- [x] 5.3 E2e (Playwright): kontextus-váltó párolgásra vált (tooltip "102 cm / 5.6 mm párolgás")
- [x] 5.4 `openspec validate evaporation-context --strict` hibamentes
