## Why

A folyóknál a **vízhozam (m³/s)** fizikailag beszédesebb, mint a helyi vízállás (a szint a
szelvény-geometriától is függ). A vizugy API ugyanonnan adja (adatfajta-kód 87, „Felszíni
vízhozam"). Ezzel a folyók vízállása mellé odatehető a tényleges áramlás, így jobban
megítélhető a vízjárás.

## What Changes

- Az ingest a folyó-víztestekre lehúzza a **napi vízhozamot** a vizugy API-ból (kód 87),
  ugyanazon a token + TS/TsShortList úton, napi szintre aggregálva.
- A `water-levels/{id}.json` minden idősor-pontja kap egy `discharge_m3s` mezőt (vagy `null`),
  a vízálláshoz/csapadékhoz igazítva.
- A részletpanel grafikonján egy **metrika-váltó** (Vízállás ↔ Vízhozam): a fővonal és a bal
  tengely átvált; a csapadék-oszlopok maradnak. A váltó csak ott jelenik meg, ahol van vízhozam
  (folyók). A tooltip az aktív metrikát mutatja.

## Capabilities

### New Capabilities
- `river-discharge`: folyó-víztestekre napi vízhozam lehúzása, tárolása, és a vízállás-idősorhoz
  igazított vízhozam-sorozat az artifactban.

### Modified Capabilities
- `water-level-detail-panel`: új követelmény — metrika-váltó a grafikonon (vízállás/vízhozam),
  ahol van vízhozam.

## Impact

- `ingest`: új `DischargeReading` + `DischargeSource` port; a vizugy adapter vízhozamot is ad
  (kód 87); új `discharge_reading` tábla; a pipeline a folyókra lehúzza+tárolja; az artifact igazítja.
- `web`: a `Chart`/`DetailPanel` metrika-váltóval; a fővonal adat/tengely vált.
- A vízhozam **csak a folyókra** elérhető; a tavak szintmérője nem mér áramlást (őszintén jelölve).
