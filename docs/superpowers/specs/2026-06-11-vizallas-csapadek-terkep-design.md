# Magyar vízállás- és csapadék-térkép — Architektúra terv

> Interaktív térkép-alkalmazás a hazai nagy tavak és folyók vízállásának, valamint az
> országos csapadék-eloszlás követésére, napi frissítéssel és ~10 év historikus mélységgel.

- **Dátum:** 2026-06-11
- **Státusz:** Terv (jóváhagyásra vár) → implementáció előtt
- **Projekt jellege:** belső / hobbi eszköz, ingyenes tierekre optimalizálva, igényes megjelenéssel

---

## 1. Cél és scope

Egy stílusos, „trendi" megjelenésű webes térkép, amelyen:

- látszik az összes nagyobb hazai **tó és folyó**;
- hoverre/kattintásra **mélyebb betekintés** nyílik az adott víztest vízállásába, akár több évre visszamenőleg;
- külön rétegként követhető a **csapadék területi eloszlása**, megfelelő területi bontásban (rács/poligon), időszak szerint szűrhetően — hasonlóan ahhoz, ahogy a HungaroMet granuláris poligonokban jeleníti meg;
- az adatok **naponta frissülnek** automatikusan.

### Döntések (jóváhagyva a brainstorming során)

| Téma | Döntés |
|------|--------|
| Projekt érettség | Belső / hobbi eszköz; funkció elsődleges, megjelenés igényes, **költséghatékony (ingyenes tier)** |
| Adatforrások | A fejlesztő utánajárt; lásd 3. szakasz |
| Vízállás stratégia | **API a napi friss adatra + scrape a historikus backfillre/fallbacknek**, port/adapter mögött |
| Futtatási modell | **Statikus + ütemezett pipeline (Jamstack)**, GitHub Actions cron |
| Historikus mélység | **~10 év** (kb. 2015–) |
| Vizuális stílus | **Topográfiai / földes** (természetes tónusok, terep-érzet, arany-okker akcentus) |

### Nem cél (YAGNI)

- Nincs külön futó DB-szerver.
- Nincs felhasználói auth / mentett nézet.
- Nincs valós idejű (perces) frissítés — napi elég.

---

## 2. Magas szintű architektúra

Tisztán **Jamstack**: nincs futó szerver, nincs üzemeltetett adatbázis-szerver.

```
  [ KÜLSŐ FORRÁSOK ]          [ INGEST PIPELINE (Python) ]        [ FRONTEND (statikus) ]
                                  napi GitHub Actions cron
  vizugy.hu API ───┐
  hydroinfo.hu  ───┼──►  ports & adapters → normalizálás → SQLite ──► artifact-generátor
  odp.met.hu     ──┤        (kanonikus historikus tár)               │ (JSON/GeoJSON)
  Open-Meteo    ───┘                                                 ▼
                                                          web/public/data/*.json
                                                                    │
                                                          MapLibre térkép + panelek
                                                          (Vercel / Netlify / GH Pages)
```

**Adatfolyam:** napi cron → adapterek lehúzzák az új adatot → közös domain-modellbe
normalizálódik → bekerül a repóban verziózott **SQLite** kanonikus tárba → az
artifact-generátor ebből legyártja a frontend által fogyasztott, előre aggregált
JSON/GeoJSON fájlokat → commit + deploy. A böngésző kizárólag statikus fájlokat olvas.

**Miért SQLite a repóban:** a teljes adatmennyiség kicsi (~6 víztest napi értékei +
~150 csapadék-rácspont, 10 év). A SQLite a kanonikus „igazságforrás" (idempotens
backfill, könnyű újragenerálni belőle az artifactokat), a frontend viszont sosem ezt
olvassa, hanem a belőle gyártott karcsú JSON-okat.

---

## 3. Adatforrások (kutatás eredménye)

### 3.1 Vízállás — tavak és folyók

| Forrás | URL | Hozzáférés | Szerep | Megjegyzés |
|--------|-----|-----------|--------|-----------|
| **OVF nyílt adat** | https://data.vizugy.hu/ | REST API (JSON) | **Elsődleges, napi** | 2024.07 óta nyílt; 400+ állomás (Balaton, Velencei-tó, Fertő-tó, Tisza-tó/Kisköre, Duna, Tisza). Dokumentáció éretlen → portál hálózati hívásait vissza kell fejteni. |
| **hydroinfo.hu** | https://www.hydroinfo.hu/ | HTML scrape | **Historikus backfill + fallback** | Kiszámítható éves URL-minták állomásonként, akár évtizedes archívum. Tisza-tó a *folyó*-táblában (Kisköre), nem a tó-táblában. |

Forrás-megjelölés kötelező: „Országos Vízügyi Főigazgatóság".

### 3.2 Csapadék — területi eloszlás

| Forrás | URL | Hozzáférés | Szerep | Megjegyzés |
|--------|-----|-----------|--------|-----------|
| **HungaroMet HuClim** | https://odp.met.hu/climate/homogenized_data/gridded_data_series/daily_data_series/from_1971/ | Fájl-letöltés (.txt.zip) | **Historikus rácsos alap** | 1971–2024, 0,1° (~11 km), 1233 rácspont. Egyedi szöveges formátum, évente (márciusban) frissül → egyszeri import, nem napi. |
| **Open-Meteo** | https://open-meteo.com/en/docs/historical-weather-api | REST API (JSON), kulcs nélkül | **Napi friss + idei év** | 1940-től napi csapadék; ~150 rácsponttal lefedhető az ország, belefér az ingyenes 10.000 hívás/nap keretbe. CC BY 4.0. |

Forrás-megjelölés kötelező: „HungaroMet" (HuClim), illetve Open-Meteo / ERA5 attribúció.

### 3.3 Tartalék / opcionális

- **Open-Meteo Flood API** (GloFAS, folyó-vízhozam m³/s, 1984–) — kiegészítő indikátor Dunára/Tiszára.
- **Copernicus CDS / ERA5-Land** — ha később valódi NetCDF raszter kell; account + cdsapi szükséges.

> Megjegyzés: a tavak **vízszintjét** egyik pán-európai API sem adja (csak csapadékot /
> folyó-vízhozamot), ezért a hazai vízügyi forrás nélkülözhetetlen.

---

## 4. Ingest pipeline — ports & adapters (hexagonális)

A forrás-specifikus csúfságok adapterekbe zárva; a mag tiszta és forrásfüggetlen.

- **Domain modell:** `WaterBody`, `Station`, `WaterLevelReading`, `PrecipitationCell`, `PrecipitationField`.
- **Portok (interfészek):** `WaterLevelSource`, `PrecipitationSource` — `fetch(date_range) -> list[Reading]`.
- **Adapterek:**
  - `VizugyApiAdapter` — napi friss vízállás (elsődleges).
  - `HydroinfoScraperAdapter` — egyszeri historikus backfill + fallback.
  - `HuClimAdapter` — historikus rácsos csapadék (egyszeri import).
  - `OpenMeteoAdapter` — napi friss csapadék (~150 rácspont).
- **Orchestrátor:** `run_daily()` és `run_backfill(years=10)`. Minden lépés **idempotens**
  (upsert kulcs: állomás+dátum / cella+dátum) → újrafuttatható duplikáció nélkül.

Új forrás = új adapter; a mag és a frontend változatlan.

---

## 5. Adattárolás & artifact-stratégia

A frontend-artifactok szándékosan kicsik és cél-specifikusak (a nyers napi adat nem ömlik a böngészőbe):

| Artifact | Tartalom |
|----------|----------|
| `water-bodies.geojson` | Tavak/folyók geometriája (egyszer beszerezve OpenStreetMap-ből). Statikus. |
| `water-levels/{id}.json` | Víztestenként idősor: napi a friss évre, **havi aggregátum** a régebbi évekre (10 év ~ pár tíz KB). |
| `precip/{period}.geojson` | Rácscellák csapadékösszeggel, előre aggregálva időszakonként (`2025-06`, `2025`, `last-30d`). Időszűrés = másik fájl. |
| `manifest.json` | Mi érhető el, mikori a frissítés. A frontend ebből tudja, mit kérhet. |

Lazy-load: a részletes idősort/időszakot csak hoverre/kattintásra/szűrésre tölti a frontend.

---

## 6. Frontend (statikus SPA)

- **Stack:** Vite + React + TypeScript + **MapLibre GL JS** (vektoros, trendi, ingyenes).
- **Alaptérkép:** topográfiai stílus a C-irányhoz — ingyenes tier (MapTiler „outdoor"/„topo" free, vagy OpenFreeMap); kulcs env-be.
- **Térkép-rétegek:**
  - víztestek interaktív poligonként — hover = kiemelés + tooltip, kattintás = oldalpanel;
  - külön **csapadék-réteg** (rácscellák színezve), kapcsolható + **időszak-szűrővel**.
- **Oldalpanel:** kiválasztott víztest többéves vízállás-grafikonja (könnyű chart-lib: uPlot a teljesítményért vagy Recharts az egyszerűségért), időtartomány-választóval.
- **Stílus:** végig a topográfiai/földes paletta (természetes tónusok, arany-okker akcentus).

---

## 7. CI / ütemezés / hosting

- **GitHub Actions napi cron:** `run_daily()` → SQLite frissül → artifactok újragenerálódnak → commit → deploy.
- **Külön workflow:** kézi `run_backfill` az első, ~10 éves feltöltéshez.
- **Hosting:** Vercel vagy Netlify (statikus, ingyenes tier), auto-deploy push-ra.

---

## 8. Hibakezelés

- **Forrás-leállás:** ha egy adapter hibázik, a nap kimarad (a pipeline nem dől össze); a `manifest.json` jelzi az utolsó sikeres frissítést, a régi artifact marad élőben. Riasztás: a GH Action bukása e-mail.
- **Részleges adat / kiugró érték:** validációs réteg a normalizálás után (tartomány-ellenőrzés, hiányzó-nap jelölés); gyanús érték naplózva, nem kerül be.
- **Fallback:** vízállásnál API-hiba esetén automatikus hydroinfo-scrape kísérlet.

---

## 9. Tesztelés és siker-kritérium

**Tesztelés:**

- **Adapterek:** rögzített (fixture) HTML/JSON válaszokon unit-teszt, élő hálózat nélkül → a parsolás stabil marad forrásváltozásra is.
- **Domain / normalizálás / aggregálás:** tiszta függvény unit-tesztek.
- **Artifact-generátor:** kis minta-DB-ből generál, ellenőrzi a JSON-sémát.
- **Frontend:** komponens-szintű smoke-teszt + a manifest/data sémák típusozása.

**Siker-kritérium (loop until verified):**

1. `run_backfill` után valós ~10 éves adat látszik mind a víztestekre.
2. A napi cron zölden lefut és frissíti az artifactokat.
3. A térkép hoverre/kattintásra grafikont mutat a kiválasztott víztestre.
4. A csapadék-réteg időszűrővel vált a területi eloszlás között.
5. Minden ingyenes tierben elfér.

---

## 10. Projekt-struktúra

```
weather-tracker/
├─ ingest/            # Python pipeline
│  ├─ domain/         # modellek, portok
│  ├─ adapters/       # vizugy, hydroinfo, huclim, openmeteo
│  ├─ pipeline/       # orchestrátor, validáció, aggregálás
│  ├─ artifacts/      # JSON/GeoJSON generátor
│  └─ tests/
├─ web/               # Vite + React + TS frontend
│  ├─ src/
│  └─ public/data/    # generált artifactok
├─ data/              # canonical.sqlite (verziózva)
└─ .github/workflows/ # daily.yml, backfill.yml
```

---

## 11. Nyitott kockázatok

- **data.vizugy.hu API** dokumentációja éretlen → a tényleges végpontokat/paramétereket a portál hálózati hívásaiból kell visszafejteni; a historikus mélységet ellenőrizni kell az API-n.
- **hydroinfo.hu scrape** törékeny lehet, ha az oldal HTML-szerkezete változik → fixture-alapú tesztek és világos hibajelzés mérséklik.
- **HuClim** egyedi szöveges formátum → parsolás a leíró PDF alapján; csak historikus alap, nem napi.
- **Alaptérkép ingyenes tier** kulcs-limit → figyelni a havi load-keretet.
