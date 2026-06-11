## ADDED Requirements

### Requirement: Kattintásra nyíló részletpanel
A felhasználó egy víztestre kattintva SHALL egy oldalpanelt kapjon, amely a víztest
többéves vízállás-grafikonját mutatja a `water-levels/{id}.json` adatból, a víztest
nevével és a legutóbbi értékkel.

#### Scenario: Panel megnyitása
- **WHEN** a felhasználó a térképen egy víztestre kattint
- **THEN** megnyílik az oldalpanel az adott víztest nevével, legutóbbi vízállásával és a
  többéves grafikonnal

### Requirement: Időtartomány-választó
A részletpanel SHALL kínáljon időtartomány-választót (pl. 1 év / 5 év / teljes), amely a
grafikon megjelenített tartományát szűri.

#### Scenario: Tartomány szűrése
- **WHEN** a felhasználó más időtartományt választ
- **THEN** a grafikon a kiválasztott tartományra frissül, a panel többi tartalma változatlan

### Requirement: Panel bezárása
A felhasználó SHALL be tudja zárni a részletpanelt, visszatérve a teljes térkép-nézethez.

#### Scenario: Bezárás
- **WHEN** a felhasználó a panel bezáró vezérlőjére kattint
- **THEN** a panel eltűnik, a térkép újra teljes nézetben látszik
