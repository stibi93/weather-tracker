## Context

A vízállás-grafikon kész és olvasható; most kontextust adunk hozzá, hogy a számok
értelmezhetők legyenek. A legközvetlenebb faktor a csapadék. Az Open-Meteo archív API
(ERA5) bizonyítottan ad napi csapadékot (mm) magyar koordinátákra, ~10 évre, tegnapig,
kulcs nélkül (et0/hőmérséklet is jön — későbbi (b)/(c) bővítéshez).

## Goals / Non-Goals

**Goals:**
- Víztestenkénti területi napi csapadék (~10 év), a vízállás-idősorhoz igazítva.
- A részletpanel grafikonján csapadék-oszlopok a vízállás-vonal mögött, kéttengelyesen, a
  tooltip a csapadékkal.

**Non-Goals:**
- Valódi vízgyűjtő-poligonra súlyozott aggregálás (közelítő pont-felhőt használunk).
- Térkép-szintű csapadék-réteg (területi poligonos eloszlás) — külön, későbbi feature.
- Hőmérséklet/ET₀ (tavak) és vízhozam (folyók) — a következő szeletek, ugyanerre az adapterre építve.

## Decisions

- **Forrás: Open-Meteo archív API, ports & adapters.** Új `PrecipitationSource` port és
  `OpenMeteoPrecipAdapter`. *Miért:* ingyenes, kulcs nélküli, hosszú historikus, és az injektálható
  port megőrzi a teszt­elhetőséget (fixture, élő hálózat nélkül).
- **Területi átlag közelítő pont-felhővel.** Víztestenként 3–4 koordináta a vízgyűjtő-közeli
  területen (config), a napi csapadékuk **átlaga**. *Alternatíva:* valódi watershed-poligon —
  elvetve (külön hidrológiai adat, túl nagy a thin szelethez); a pont-felhő őszintén közelítés.
- **A csapadék a vízállás-sorozat pontjaihoz igazítva.** Mivel a uPlot egy közös x-tengelyt
  használ, a `precip_mm` ugyanazokra a pontokra (napi/havi bucket) kerül, **napi átlag mm**-ben
  (a havi bucketnél is a napi átlag, hogy az oszlop-skála konzisztens legyen a napi oszlopokkal).
  *Miért X Y helyett:* havi **összeg** ~30× a napi értéknek → eltörné a közös mm-skálát.
- **Kéttengelyes grafikon.** Vízállás bal (cm) vonal, csapadék jobb (mm) oszlop. A tooltip
  mindkettőt mutatja.
- **Őszinte jelzés a folyókról.** A nagy folyóknál (Duna, Tisza) a helyi csapadék gyenge
  magyarázó (a felvízi vízgyűjtő + hóolvadás a fő hajtó). A csapadékot megmutatjuk, de nem
  állítunk ok-okozatot; a sekély tavaknál a legbeszédesebb.

## Risks / Trade-offs

- [Pont-felhő közelítés, nem valódi vízgyűjtő] → őszintén jelölve; később finomítható valódi
  poligonra súlyozással.
- [Open-Meteo archív ~ tegnapig] → a vízállás (vizugy) és a csapadék vége 1 napon belül illeszkedik;
  a hiányzó pont `null`, a grafikon nem törik.
- [Nagyobb artifact] → a `precip_mm` pontonként egy szám; elhanyagolható méretnövekedés.

## Open Questions

- A pont-felhők pontos koordinátái finomíthatók (most kézzel választott, vízgyűjtő-közeli pontok).
