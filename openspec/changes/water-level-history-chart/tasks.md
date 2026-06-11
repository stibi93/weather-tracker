## 1. Historikus backfill (ingest)

- [x] 1.1 `run` kiegészítése: `--years` (vagy külön `run_backfill`) a többéves dátumtartományhoz
- [x] 1.2 Teszt: a backfill a megadott évszámnak megfelelő tartományt kéri a forrástól (injektált forrás)
- [x] 1.3 Éles backfill futtatás ~10 évre, a kanonikus tár feltöltése a hat víztestre (21903 leolvasás)

## 2. Többéves aggregált artifact

- [x] 2.1 Aggregáló: friss ~2 év napi pont, régebbi évek havi átlag; minden pont `resolution` jelöléssel
- [x] 2.2 `water-levels/{id}.json` bővítése a többéves, vegyes felbontású sorozattal (828 pont/víztest)
- [x] 2.3 Teszt: küszöb körüli aggregálás helyes (napi vs havi), determinisztikus kimenet

## 3. Frontend: kattintás-kezelés

- [x] 3.1 Térkép-kattintás egy víztesten → kiválasztott víztest id React state-ben
- [x] 3.2 Kiválasztott marker vizuális kiemelése (a hovertől megkülönböztetve, arany gyűrű)

## 4. Frontend: részletpanel + grafikon

- [x] 4.1 uPlot függőség hozzáadása, vékony React-wrapper komponens (ref + cleanup)
- [x] 4.2 Oldalpanel: víztest neve, legutóbbi érték, többéves vízállás-grafikon a `water-levels/{id}.json`-ból
- [x] 4.3 Időtartomány-választó (1 év / 5 év / teljes), a grafikon szűrése
- [x] 4.4 Panel bezárása, vissza a teljes térkép-nézetre; a (C) földes stílushoz illő megjelenés

## 5. Verifikáció

- [x] 5.1 `ingest` tesztek zölden (15 teszt, + új aggregálás/backfill tesztek)
- [x] 5.2 Kézi end-to-end: kattintásra megnyílik a panel, többéves grafikon, tartomány-váltás és bezárás működik
- [x] 5.3 `openspec validate water-level-history-chart --strict` hibamentes
