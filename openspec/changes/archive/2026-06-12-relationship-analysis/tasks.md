## 1. Statisztika modul (tiszta Python)

- [x] 1.1 `ingest/analysis/relationships.py`: Δszint (szomszédos napokra), rang-alapú Spearman, OLS (slope/intercept/R²)
- [x] 1.2 Késleltetett Spearman magyarázó változónként, legjobb késleltetés egy rögzített ablakban (tavak 0–14, folyók 0–30)
- [x] 1.3 `compute_relationships(...)`: kind-függő fő kapcsolat (tavak: Δszint vs csapadék−párolgás; folyók: szint vs vízhozam) + magyarázó változók táblája
- [x] 1.4 Unit-teszt: ismert mintán helyes Spearman, R², legjobb késleltetés; determinisztikus

## 2. Artifact

- [x] 2.1 Az artifact-generátor víztestenként `relationships/{id}.json`-t ír (fő kapcsolat pontjai + statisztikák)
- [x] 2.2 Teszt: az artifact szerkezete

## 3. Frontend: Összefüggések szekció

- [x] 3.1 `RelationshipsPanel`: lazy-load `relationships/{id}.json`
- [x] 3.2 Szórásdiagram (uPlot, pont + illesztett vonal) R²-tel
- [x] 3.3 Korrelációs tábla: magyarázó változó | késleltetés | Spearman-r (kis sáv, előjellel)
- [x] 3.4 A metrikák pontos magyarázata (Δszint, Spearman-r, késleltetés, R²) + „korreláció ≠ okság" figyelmeztetés
- [x] 3.5 A (C) földes stílushoz illő megjelenés; megnyitható szekció a panelben

## 4. Verifikáció

- [x] 4.1 `ingest` tesztek zölden (31 teszt; új statisztika/artifact tesztek)
- [x] 4.2 Éles futtatás: `relationships/{id}.json` mind a 6 víztestre (Balaton R²=0,20; Duna R²=0,98)
- [x] 4.3 E2e (Playwright): a szekció megnyílik, szórásdiagram + tábla + magyarázat (tó és folyó is)
- [x] 4.4 `openspec validate relationship-analysis --strict` hibamentes
