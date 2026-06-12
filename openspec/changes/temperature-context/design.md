## Context

A csapadék már a grafikonon van (precipitation-context). A hőmérséklet ugyanabból az
Open-Meteo hívásból elérhető (`temperature_2m_mean`), bizonyítottan ~10 évre, tegnapig.
A sekély tavak nyári párolgásához a hőmérséklet a fő kontextus.

## Goals / Non-Goals

**Goals:**
- Víztestenkénti napi átlaghőmérséklet (~10 év), a vízállás-idősorhoz igazítva (`temp_c`).
- A grafikon jobb tengelyén másodlagos kontextus-váltó: csapadék (oszlop) ↔ hőmérséklet (vonal).

**Non-Goals:**
- ET₀ / párolgás explicit számítása (a hőmérséklet most a proxy; később bővíthető).
- Három egyidejű tengely — a váltó tisztán tartja a grafikont (max két tengely).

## Decisions

- **Tükör-minta a csapadékhoz, közös Open-Meteo segédfüggvénnyel.** Új `TempReading` +
  `TemperatureSource` port + `OpenMeteoTempAdapter`. Az openmeteo modul közös
  `_fetch_area_daily(client, points, variable, decimals, range)` függvénye (a `_average_daily`
  általánosítva a változó-kulcsra) szolgálja ki a csapadékot és a hőmérsékletet is.
  *Miért X Y helyett:* konzisztens a vízhozam/vízállás tükör-mintával; izolált, kis kockázat.
  A külön Open-Meteo hívás ára elhanyagolható (ingyenes tier, néhány hívás).
- **Hőmérséklet az artifactban a sorozat pontjaihoz igazítva.** `temp_c` minden ponton, a
  bucket napi átlaga (mint a csapadéknál), vagy `null`.
- **Másodlagos kontextus-váltó, nem harmadik tengely.** A jobb tengely tartalma vált:
  csapadék (oszlop, mm, kék) vagy hőmérséklet (vonal, °C, okker/arany — illik a (C) palettához).
  *Miért:* három tengely zsúfolt; a váltó fókuszált marad.

## Risks / Trade-offs

- [Külön Open-Meteo hívás a hőmérsékletre] → elhanyagolható (ingyenes tier); a kód DRY a közös
  segédfüggvénnyel.
- [Hőmérséklet auto-skála negatív értékekkel (tél)] → a jobb tengely a hőmérséklet nézetben
  automatikusan skáláz (a csapadék 0-tól indul, a hőmérséklet nem).

## Open Questions

- Később az ET₀ (referencia-párolgás) is bevehető ugyanebből a hívásból, ha a párolgást
  explicitebben akarjuk mutatni.
