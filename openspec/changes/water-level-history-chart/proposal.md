## Why

A vékony alap csak a legutóbbi értéket és egy rövid idősort mutat, hover-tooltippel. A
termék fő ígérete viszont a „mélyebb betekintés akár jó pár évre visszamenőleg": egy
víztestre kattintva többéves vízállás-grafikont kell látni. Ehhez historikus mélységű
adat (~10 év) és egy kattintásra nyíló oldalpanel grafikonnal kell.

## What Changes

- Az ingest historikus mélységet tölt be (konfigurálható évszám, alapból ~10 év) a vizugy
  API dátumtartomány-lekérésével; a tárolás már idempotens, így a backfill biztonságos.
- Az artifact-generátor többéves, aggregált idősort ad víztestenként: napi a friss ~2 évre,
  havi átlag a régebbi évekre (kis fájlméret, gyors grafikon).
- A frontend: víztestre kattintva oldalpanel nyílik a többéves vízállás-grafikonnal és egy
  időtartomány-választóval (pl. 1 év / 5 év / teljes).

## Capabilities

### New Capabilities
- `water-level-detail-panel`: víztestre kattintva oldalpanel a többéves vízállás-grafikonnal
  és időtartomány-választóval.

### Modified Capabilities
<!-- Új követelmények ADDED-ként a meglévő capability-khez (még nincs archivált baseline). -->
- `water-level-ingestion`: új követelmény a konfigurálható historikus backfillről.
- `data-artifacts`: új követelmény a többéves, aggregált (napi+havi) idősorról.

## Impact

- `ingest`: a pipeline `days`/`years` paramétere és a backfill belépési pont; az
  artifact-generátor aggregálási logikája bővül.
- `web`: új oldalpanel-komponens + grafikon (könnyű chart-lib, pl. uPlot), kattintás-kezelés
  a térképen, a `water-levels/{id}.json` bővebb idősorának fogyasztása.
- Nagyobb (de továbbra is kis) artifact-fájlok a többéves sorozat miatt.
