## Why

A tavak fő összefüggés-szórásdiagramja napi Δszinten készül, de a **napi szintváltozás egész
cm-ben** van, és többnyire 0 (Balaton: a napok 77%-a 0 cm). Így a több ezer pont néhány
vízszintes sorba torlódik — a kapcsolat valós (Spearman r≈0,41), de **vizuálisan
olvashatatlan**. A napi cm-kvantáltságot csak időbeli aggregálás oldja fel.

## What Changes

- A tavak fő kapcsolatának szórásdiagramja **havi aggregálásra** vált: *havi szintváltozás vs
  havi (csapadék − párolgás)*. A felhő tisztán, pozitív meredekséggel látszik, az R² reálisabb.
- A folyók vízállás vs vízhozam (rating curve) változatlan — az már tiszta és erős.
- A hajtónkénti korrelációs tábla **napi, késleltetett Spearman** marad (a napi időzítés/late
  miatt informatív; a rang-alapú korreláció robusztus a kvantáltságra).

## Capabilities

### Modified Capabilities
- `relationship-analysis`: a tavak fő kapcsolata havi aggregálásra vált (a napi cm-kvantáltság
  feloldására); a folyóké és a hajtó-tábla változatlan.

## Impact

- `ingest`: az `analysis` modul havi vízmérleg-aggregálással számítja a tavak fő kapcsolatát.
- `web`: nincs változás (a `RelationshipsPanel` a feliratokat/pontokat az artifactból veszi).
