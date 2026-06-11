## Context

A projekt zöldmezős; ez a legelső change. A cél egy vékony, de végpontól-végpontig működő
váz, amely bizonyítja a `docs/superpowers/specs/2026-06-11-vizallas-csapadek-terkep-design.md`
architektúrát egyetlen adatdoménon (vízállás). A globális kontextust az `openspec/project.md`
rögzíti: statikus-first Jamstack, ports & adapters Python ingest, SQLite kanonikus tár,
Vite + React + MapLibre frontend, topográfiai (C) stílus.

## Goals / Non-Goals

**Goals:**
- Lefuttatható ingest → normalizálás → SQLite → artifact lánc egyetlen forrással (vizugy).
- Determinisztikus, frontend-fogyasztható artifactok (`water-bodies.geojson`, `water-levels/{id}.json`).
- Statikus MapLibre térkép a víztestekkel, topográfiai stílusban, hover-kiemeléssel.
- Tiszta modulhatárok, hogy a következő change-ek (hydroinfo, csapadék, grafikon, CI) ráépüljenek.

**Non-Goals:**
- Hydroinfo backfill/fallback, csapadék-domén, kattintásra nyíló grafikon, idő-szűrő.
- GitHub Actions ütemezés és deploy (külön, későbbi change).
- Történeti mélység-feltöltés (~10 év) — most csak az aktuális lehúzás elég a lánc bizonyításához.

## Decisions

- **Ports & adapters már a vékony alapnál.** A `WaterLevelSource` port és a `VizugyApiAdapter`
  külön él, hiába egyetlen forrás van. *Miért X Y helyett:* a port nélkül a domain a vizugy
  formátumhoz tapadna, és a hydroinfo adapter (köv. change) törné a magot. Az absztrakció ára
  most minimális, a haszna nagy.
- **SQLite mint kanonikus igazságforrás, nem a frontend tára.** A séma: `water_body`, `station`,
  `water_level_reading(station_id, date, value)` egyedi `(station_id, date)` kulccsal, upsert.
  *Alternatíva:* közvetlenül JSON-fájlokba írni — elvetve, mert az idempotencia és a későbbi
  aggregálás (havi átlag) SQL-ben tiszta, fájlokban törékeny.
- **Geometria a vizugy állomás-koordinátákból (pont), nem OSM-ből — a vékony alapnál.** A
  felderítés kiderítette, hogy a vizugy API minden állomáshoz `Lat`/`Lon`-t (WGS84) ad. Ezért a
  foundationben a víztesteket a reprezentatív állomásuk **pont-geometriájával** jelenítjük meg —
  nincs külön geometria-beszerzés. *Miért X Y helyett:* az OSM poligon/vonal seed önálló feladat
  (forrásozás, egyszerűsítés, tárolás), ami a thin szeletet feleslegesen megnöveli; a valódi
  tó-poligon és folyó-vonal geometria dedikált, későbbi change lesz.
- **Állomás→víztest hozzárendelés explicit konfig, koordinátákkal.** Egy `ingest/config`-ban
  rögzített leképezés köti a vizugy-állomásokat a hat víztesthez, a felderített `Tsz` + név +
  `Lat`/`Lon` alapján. *Miért:* a forrás állomásnevei nem feltétlen egyeznek a megjelenített
  víztest-nevekkel; az explicit map kiszámíthatóvá és tesztelhetővé teszi.
- **Token-alapú API-hozzáférés, anonim.** A `data.vizugy.hu/AuthApi/auth/token` `Origin` fejléccel
  anonim JWT-t ad; ezt `Bearer`-ként küldjük a `vmservice.vizugy.hu/vraquery/` hívásokon. Nincs
  szükség regisztrációra/API-kulcsra. *Miért:* automatizálható a napi futás emberi beavatkozás nélkül.
- **Napi aggregálás kliensoldalon.** Egyes állomások órás adatot adnak; az adapter naponként egy
  értékre aggregál (napi átlag, cm-re kerekítve). *Miért:* egységes napi idősor minden víztestre,
  forrástól független felbontással.
- **Frontend csak statikus artifactot olvas.** A React app `web/public/data/`-ból tölt, lazy
  módon. *Miért:* nulla backend, ingyenes tier, és a frontend nem ismeri a forrásokat.
- **Alaptérkép ingyenes tier, kulcs env-ben.** MapTiler „outdoor"/„topo" free vagy OpenFreeMap;
  a kulcs `.env`-ben, nem a repóban.

## Risks / Trade-offs

- [data.vizugy.hu API dokumentálatlan] → Az adapter a portál hálózati hívásait fejti vissza;
  a parsolást fixture-alapú teszt rögzíti, így forrásváltozás látható és kezelhető.
- [Hiányzó/hibás állomás-adat] → Forráshiba esetén az érintett állomás kimarad, a futás nem dől
  össze; naplózás jelzi.
- [Geometria-seed beszerzése kézi lépés] → Egyszeri; a seed verziózva van, így reprodukálható.
- [Alaptérkép tier-limit] → Hobbi forgalomnál bőven elég az ingyenes keret; a kulcs cserélhető.

## Migration Plan

Zöldmezős — nincs migráció. Telepítés: a pipeline kézzel futtatható belépési ponton
(`run`), amely lehúz, tárol és artifactot generál; a frontend lokálisan `dev` szerverrel
indul. Rollback = a generált artifactok és a SQLite eldobása (mindkettő reprodukálható).

## Open Questions

- A reprezentatív állomás víztestenként (most: Balaton→142300 „Balaton átlag", Velencei-tó→818
  Agárd, Fertő-tó→52 Fertőrákos, Tisza-tó→2041 Kisköre felső, Duna→1026 Budapest, Tisza→2046
  Szolnok) — később bővíthető több állomásra víztestenként.
- A valódi tó-poligon és folyó-vonal geometria (OSM) külön change-ben — felbontás/egyszerűsítés
  ott dől el.
