## Why

A vízállás-számok önmagukban nehezen értelmezhetők: a felhasználó nem látja, *mihez
kapcsolódnak*. A legközvetlenebb magyarázó faktor a csapadék — különösen a sekély tavaknál
(„nagy eső → megugrik", „száraz időszak → esik"). A legnagyobb haszon, ha a csapadékot
**ráhúzzuk a vízállás-grafikonra**, így vizuálisan azonnal látszik az összefüggés.

## What Changes

- Új adatdomén: **területi (vízgyűjtő-közeli) napi csapadék** víztestenként, az Open-Meteo
  archív API-ból (ingyenes, kulcs nélkül), ~10 évre visszamenőleg, a vízállással azonos
  felbontásra igazítva.
- A `water-levels/{id}.json` minden idősor-pontja kap egy `precip_mm` mezőt (a pont
  időszakára átlagolt napi csapadék), így a frontend ugyanazon a grafikonon tudja mutatni.
- A részletpanel grafikonja **kétféle adatot** mutat: a vízállás-vonal mögött **csapadék-oszlopok**
  (külön, jobb oldali mm-tengelyen), a hover-tooltip a csapadékot is kiírja.

## Capabilities

### New Capabilities
- `precipitation-context`: víztestenkénti területi napi csapadék lehúzása, tárolása, és a
  vízállás-idősorhoz igazított csapadék-sorozat az artifactban.

### Modified Capabilities
- `water-level-detail-panel`: új követelmény — a grafikon a vízállás mellett a csapadékot is
  megjeleníti (kéttengelyes), a hover-tooltipben a csapadékkal.

## Impact

- `ingest`: új `PrecipitationSource` port + `OpenMeteoPrecipAdapter`; új `precip_reading` tábla;
  a pipeline a csapadékot is lehúzza és tárolja; az artifact-generátor igazítja a vízállás-sorozathoz.
- `web`: a `Chart` kétféle sorozatot rajzol (vonal + oszlop, két y-tengely), a tooltip bővül.
- A területi csapadék víztestenként egy **közelítő pont-felhő** átlaga (nem valódi vízgyűjtő-poligon);
  a folyóknál a helyi csapadék gyengébb magyarázó, mint a tavaknál — ezt jelezzük.
