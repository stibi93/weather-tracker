## MODIFIED Requirements

### Requirement: Összefüggés-számítás a napi szintváltozáson
A rendszer víztestenként SHALL kiszámítson egy összefüggés-összegzést a **napi szintváltozás
(Δszint)** alapján (nem a nyers vízszinten), hogy elkerülje az autokorrelációból és
szezonalitásból eredő hamis korrelációt. Minden magyarázó változóra (csapadék, párolgás, hőmérséklet,
és folyóknál vízhozam) **késleltetett Spearman-korrelációt** számol egy előre rögzített
késleltetés-ablakban, és kiválasztja a legjobb késleltetést.

A **fő kapcsolat** szórásdiagramja a kvantáltság miatt aggregált: tavaknál **havi**
szintváltozás vs **havi** (csapadék − párolgás); folyóknál vízállás vs vízhozam.

#### Scenario: Δszint-alapú korreláció
- **WHEN** a rendszer egy víztest összefüggéseit számítja
- **THEN** a magyarázó változónkénti korrelációk a napi szintváltozáson alapulnak, és minden magyarázó változóhoz tartozik
  egy legjobb késleltetés (nap) és egy Spearman-r érték

#### Scenario: Fő kapcsolat illesztéssel (aggregálva)
- **WHEN** a fő kapcsolatot számítja
- **THEN** tavaknál **havi** szintváltozás vs **havi** (csapadék − párolgás), folyóknál vízállás
  vs vízhozam, mindkettő illesztett egyenessel és **R²**-tel (a megmagyarázott hányad)

#### Scenario: Olvasható szórás a kvantáltság ellenére
- **WHEN** egy tó fő kapcsolatát jeleníti meg
- **THEN** a havi aggregálás miatt a szintváltozásnak valós szórása van (nem egész cm-be
  torlódik), így a kapcsolat vizuálisan értelmezhető
