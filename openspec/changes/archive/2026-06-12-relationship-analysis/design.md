## Context

Minden szükséges napi adat a kanonikus tárban van (vízszint, csapadék, párolgás, hőmérséklet,
vízhozam). A kutatás (lásd a beszélgetést) egyértelmű: a nyers vízszint-korreláció félrevezető;
a helyes feldolgozás a **napi szintváltozáson (Δszint)** alapul, késleltetett Spearman-nal és —
tavaknál — vízmérleg-regresszióval. A Granger-oksági teszt kerülendő (félrevezető címke, overkill).

## Goals / Non-Goals

**Goals:**
- Δszint-alapú, késleltetett Spearman-korreláció magyarázó változónként + legjobb késleltetés.
- Fő kapcsolat illesztéssel + R² (tavak: Δszint vs csapadék−párolgás; folyók: szint vs vízhozam).
- A részletpanelen szórásdiagram + tábla + **pontos metrika-magyarázatok** + figyelmeztetés.

**Non-Goals:**
- Granger-oksági teszt; prewhitening AR-modellel (a Δszint már nagyrészt csökkenti az
  autokorrelációt — hobbihoz elég); többváltozós elosztott késleltetésű modell.

## Decisions

- **Δszint, nem nyers szint.** Δszint(t) = szint(t) − szint(t−1) csak szomszédos napokra.
  *Miért:* a nyers szint autokorrelált + szezonális → hamis korreláció; a Δszint a napi
  vízmérleg, fizikailag értelmezhető.
- **Tiszta-Python statisztika, új függőség nélkül.** Spearman = a rangok Pearson-korrelációja;
  OLS slope/intercept/R² zárt képlettel. ~3650 pont × néhány késleltetés gyors. *Miért X Y helyett:*
  a scipy/numpy nehéz egy hobbi pipeline-hoz; a képletek egyszerűek és tesztelhetők.
- **Késleltetés-ablak előre rögzítve.** Tavak 0–14 nap, folyók 0–30 nap; a legjobb késleltetés a
  |Spearman-r| maximuma. *Miért:* ne legyen data-mining; a teljes tartomány indokolt.
- **Kind-függő fő kapcsolat.** Tavak: Δszint vs (csapadék − párolgás) a net legjobb késleltetésénél,
  OLS R². Folyók: vízállás vs vízhozam (rating curve, kortárs, fizikailag erős — itt a nyers szint
  helyes, mert pillanatnyi fizikai kapcsolat). *Miért:* a felhasználónak a folyóknál a vízhozam a
  legérthetőbb „mihez kötődik", a tavaknál a vízmérleg.
- **Külön lazy-load artifact.** `relationships/{id}.json` (szórás-pontok + statisztikák), a fő
  `water-levels` fájl karcsú marad; a szekció megnyitásakor töltődik.
- **Magyarázat és figyelmeztetés a UI-ban.** Minden metrikához rövid, pontos magyarázat
  (Δszint, Spearman-r −1..+1, késleltetés, R² 0..1) + „korreláció ≠ okság; szabályozás (Sió,
  Kisköre), talajvíz, felvízi folyamatok is hatnak".

## Risks / Trade-offs

- [Napi R² szerény (tavak ~0,1–0,35)] → őszintén kiírjuk, mit jelent; nem ígérünk többet.
- [Szabályozott tavak/folyók (Sió, Kisköre)] → a figyelmeztetés kiemeli; a maradék-szórás nem hiba.
- [Hőmérséklet ≈ párolgás kollinearitás] → a regresszióba csak a párolgás megy; a hőmérséklet csak a
  táblában, transzparenciából (gyenge közvetlen kapcsolat).

## Open Questions

- A szórásdiagram pontszáma (teljes ~3650 vagy ritkított) — méret/olvashatóság alapján implementáció közben.
