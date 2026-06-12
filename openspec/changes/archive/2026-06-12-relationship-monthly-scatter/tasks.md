## 1. Havi aggregálás (analysis)

- [x] 1.1 `_monthly_balance(level, net)`: havi net-összeg + havi szintváltozás (hó végi szint különbsége)
- [x] 1.2 A tavak fő kapcsolata havi aggregálásra vált (cím + feliratok: „Havi szintváltozás vs havi (csapadék − párolgás)")
- [x] 1.3 A folyók és a napi hajtó-tábla változatlan

## 2. Teszt és verifikáció

- [x] 2.1 Unit-teszt: havi vízmérleg-aggregálás helyes; tó fő kapcsolata havi, magas R² szintetikus adaton
- [x] 2.2 `ingest` tesztek zölden (32 teszt)
- [x] 2.3 Éles futtatás: a tavak fő kapcsolata havi, olvasható; valós R² (Balaton 0,66; Velencei 0,78; Fertő 0,61; Tisza-tó 0,02 — szabályozott)
- [x] 2.4 E2e (Playwright): a tó szórásdiagramja havi feliratokkal, értelmezhető felhővel
- [x] 2.5 `openspec validate relationship-monthly-scatter --strict` hibamentes
