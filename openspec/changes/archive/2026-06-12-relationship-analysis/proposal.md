## Why

A felhasználó látja a vízállást és a magyarázó változókat (csapadék, párolgás, hőmérséklet,
vízhozam), de nem látja **mihez kötődnek** — az összefüggést számszerűsíteni és őszintén
elmagyarázni kell. A vízszint *felhalmozott állapot*: nyersen korrelálva hamis (autokorreláció
+ szezonalitás). A helyes feldolgozás a **napi szintváltozással (Δszint)** dolgozik, és tisztán
jelzi, hogy **korreláció ≠ okság**.

## What Changes

- Az ingest víztestenként kiszámít egy **összefüggés-összegzést** (Pythonban, a teljes napi
  adatból): Δszint vs magyarázó változók **késleltetett Spearman-korrelációja** (a legjobb késleltetéssel),
  és egy **fő kapcsolat** illesztett vonallal + **R²**-tel:
  - tavak: Δszint vs (csapadék − párolgás) — vízmérleg;
  - folyók: vízállás vs vízhozam — vízhozamgörbe (rating curve).
- Új lazy-load artifact: `relationships/{id}.json` (szórásdiagram-pontok + statisztikák).
- A részletpanelen egy **„Összefüggések"** szekció: szórásdiagram + korrelációs tábla +
  **a metrikák pontos magyarázata** (mit jelent a Δszint, a Spearman-r, a késleltetés, az R²,
  hogyan kell értelmezni) + kötelező figyelmeztetés.

## Capabilities

### New Capabilities
- `relationship-analysis`: a vízszint és a magyarázó változók közti összefüggés számítása (Δszinten,
  késleltetett Spearman + vízmérleg/rating R²), és az „Összefüggések" megjelenítés magyarázatokkal.

## Impact

- `ingest`: új `analysis` modul (tiszta-Python Spearman + OLS, új függőség nélkül); az
  artifact-generátor `relationships/{id}.json`-t is ír.
- `web`: új `RelationshipsPanel` (szórásdiagram uPlot-tal + tábla + magyarázó szövegek), lazy-load.
- A statisztika a teljes napi kanonikus adatból számol, nem a leritkított sorozatból.
