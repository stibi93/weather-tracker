## Context

A vizugy API ugyanazon a TS/TsShortList úton adja a vízhozamot (kód 87, m³/s), mint a
vízállást (kód 68). Felderítve: a Duna (Budapest, 1026) és a Tisza (Szolnok, 2046)
állomásra van vízhozam; a 4 tó szintmérőjére nincs.

## Goals / Non-Goals

**Goals:**
- Napi vízhozam a folyó-állomásokra (~10 év), a vízállás-idősorhoz igazítva (`discharge_m3s`).
- A grafikonon metrika-váltó (vízállás ↔ vízhozam) a folyóknál; a csapadék marad.

**Non-Goals:**
- Tavak ki-/befolyásának vízhozama (pl. Sió zsilip) — külön állomás/feladat.
- Egyszerre két vonal (vízállás+vízhozam) — a váltó tisztábban tartja a grafikont.

## Decisions

- **A vizugy adapter újrahasználata, megosztott segédfüggvénnyel.** A token+POST+napi aggregálás
  egy közös `_fetch_daily_values(client, station_ids, code, range)` függvénybe kerül; a vízállás
  (kód 68) és a vízhozam (kód 87) adaptere ezt hívja. *Miért:* ne duplikáljuk az auth/HTTP logikát.
- **Vízhozam csak a folyó-állomásokra.** A pipeline a `WaterBodyKind.RIVER` víztestek
  állomásaira kéri a vízhozamot. *Miért:* a tavaknál nincs, felesleges hívás.
- **Vízhozam az állomáshoz, a vízálláshoz igazítva az artifactban.** Új `discharge_reading`
  tábla (állomás, dátum, m³/s); a generátor a vízállás-sorozat bucketjeihez átlagol (mint a csapadéknál),
  `discharge_m3s` vagy `null`. *Miért:* közös x-tengely a uPlot-on.
- **Metrika-váltó, nem harmadik tengely.** A fővonal (bal tengely) vízállás vagy vízhozam; a
  csapadék (jobb tengely, oszlop) marad. A váltó csak akkor jelenik meg, ha a sorozatban van
  `discharge_m3s`. *Miért X Y helyett:* három tengely zsúfolt; a váltó tiszta és fókuszált.

## Risks / Trade-offs

- [Vízhozam nagyságrendje tág (Tisza ~70, Duna ~1300+ m³/s)] → víztestenként saját autoskála a
  bal tengelyen; a váltáskor a uPlot újraskáláz.
- [Tavaknál nincs vízhozam] → a váltó elrejtve; a `discharge_m3s` `null`, a grafikon nem törik.

## Open Questions

- Később a tavak kifolyás-vízhozama (Sió, Kisköre-leeresztés) külön állomásból bevehető.
