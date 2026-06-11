# Project Context — Magyar vízállás- és csapadék-térkép

> Globális, tartós kontextus az OpenSpec change-ekhez. A teljes, részletes architektúra:
> `docs/superpowers/specs/2026-06-11-vizallas-csapadek-terkep-design.md`.

## Mit építünk

Interaktív, „trendi" megjelenésű webes térkép a hazai nagy tavak/folyók **vízállásának** és az
országos **csapadék-eloszlásnak** a követésére. Napi automatikus frissítés, ~10 év historikus
mélység. Hover/kattintás → mélyebb betekintés idősoros grafikonokkal. Csapadék külön rétegként,
területi (rács/poligon) bontásban, időszak szerint szűrhetően.

- **Jelleg:** belső / hobbi eszköz, ingyenes tierekre optimalizálva, igényes megjelenéssel.
- **Vizuális stílus:** topográfiai / földes (természetes tónusok, terep-érzet, arany-okker akcentus).

## Tech stack

- **Ingest pipeline:** Python — hexagonális (ports & adapters). Forrásonként külön adapter.
- **Kanonikus tár:** SQLite a repóban verziózva (`data/canonical.sqlite`). Az igazságforrás;
  idempotens upsert. A frontend SOSEM ezt olvassa.
- **Frontend:** Vite + React + TypeScript + MapLibre GL JS. Topográfiai alaptérkép (ingyenes tier).
- **Artifactok:** a pipeline a SQLite-ból előre legenerált, karcsú JSON/GeoJSON fájlokat ír a
  `web/public/data/`-ba; a statikus frontend csak ezeket olvassa (lazy-load).
- **CI / ütemezés:** GitHub Actions napi cron (`run_daily`) + kézi `run_backfill`. Hosting:
  Vercel/Netlify (statikus, ingyenes tier).

## Architektúra-elvek

- **Ports & adapters:** forrás-specifikus csúfság adapterbe zárva; a domain forrásfüggetlen.
  Új forrás = új adapter, a mag és a frontend változatlan.
- **Idempotencia:** minden ingest lépés újrafuttatható duplikáció nélkül (kulcs: állomás+dátum /
  cella+dátum).
- **Statikus-first:** nincs futó backend/DB-szerver; minden ingyenes tierben elfér.
- **Kis, cél-specifikus artifactok:** a nyers napi adat nem ömlik a böngészőbe; előre aggregálunk
  (napi a friss évre, havi a régebbire).
- **YAGNI:** nincs auth, nincs mentett nézet, nincs perces frissítés.

## Adatforrások (forrás-megjelölés kötelező)

- **Vízállás:** `data.vizugy.hu` API (napi, elsődleges) + `hydroinfo.hu` scrape (historikus
  backfill + fallback). Megjelölés: „Országos Vízügyi Főigazgatóság".
- **Csapadék:** `odp.met.hu` HuClim rácsos (historikus alap, egyszeri import) + Open-Meteo API
  (napi friss). Megjelölés: „HungaroMet", illetve Open-Meteo / ERA5 (CC BY 4.0).

## Víztestek (MVP)

Balaton, Velencei-tó, Fertő-tó, Tisza-tó (Kisköre), Duna, Tisza.

## Konvenciók

- Domain és üzleti logika tiszta, hálózat-mentes; az I/O az adapterekben.
- Adapter-tesztek rögzített (fixture) válaszokon futnak, élő hálózat nélkül.
- Kód a környező kód stílusához igazodik; minimalista, nem spekulatív.
- Magyar domain-fogalmak megtarthatók a kódban, ahol természetes (víztest, vízállás, csapadék).
