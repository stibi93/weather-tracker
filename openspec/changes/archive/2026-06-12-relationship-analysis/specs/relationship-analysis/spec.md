## ADDED Requirements

### Requirement: Összefüggés-számítás a napi szintváltozáson
A rendszer víztestenként SHALL kiszámítson egy összefüggés-összegzést a **napi szintváltozás
(Δszint)** alapján (nem a nyers vízszinten), hogy elkerülje az autokorrelációból és
szezonalitásból eredő hamis korrelációt. Minden magyarázó változóra (csapadék, párolgás, hőmérséklet,
és folyóknál vízhozam) **késleltetett Spearman-korrelációt** számol egy előre rögzített
késleltetés-ablakban, és kiválasztja a legjobb késleltetést.

#### Scenario: Δszint-alapú korreláció
- **WHEN** a rendszer egy víztest összefüggéseit számítja
- **THEN** a korrelációk a napi szintváltozáson alapulnak, és minden magyarázó változóhoz tartozik egy
  legjobb késleltetés (nap) és egy Spearman-r érték

#### Scenario: Fő kapcsolat illesztéssel
- **WHEN** a fő kapcsolatot számítja
- **THEN** tavaknál Δszint vs (csapadék − párolgás), folyóknál vízállás vs vízhozam, mindkettő
  illesztett egyenessel és **R²**-tel (a megmagyarázott hányad)

### Requirement: Összefüggés-artifact lazy-loadhoz
A rendszer víztestenként egy `relationships/{id}.json` artifactot SHALL legenerálni a fő
kapcsolat szórásdiagram-pontjaival és a statisztikákkal (késleltetés, Spearman-r, R², slope),
hogy a frontend igény szerint betölthesse.

#### Scenario: Artifact tartalma
- **WHEN** az artifact-generátor lefut
- **THEN** minden víztesthez készül egy `relationships/{id}.json` a fő kapcsolat pontjaival,
  R²-tel és a magyarázó változónkénti (késleltetés, Spearman-r) értékekkel

### Requirement: Összefüggések megjelenítése magyarázattal
A részletpanel egy „Összefüggések" szekciót SHALL kínáljon, amely megjeleníti a fő kapcsolat
szórásdiagramját (illesztett vonallal és R²-tel), a magyarázó változónkénti korrelációs táblát (késleltetés
+ Spearman-r), valamint **a metrikák pontos magyarázatát** (Δszint, Spearman-r, késleltetés,
R² jelentése és értelmezése) és a kötelező figyelmeztetést, hogy a korreláció nem okság.

#### Scenario: Magyarázott megjelenítés
- **WHEN** a felhasználó megnyitja az „Összefüggések" szekciót
- **THEN** látja a szórásdiagramot, a korrelációs táblát, a metrikák magyarázatát és a
  „korreláció ≠ okság" figyelmeztetést (a szabályozás/talajvíz említésével)
