## Context

A napi Δszint egész cm-ben van és többnyire 0 → a napi szórásdiagram néhány vízszintes sorba
torlódik, olvashatatlan. A kutatás szerint a heti/havi aggregálás (gördülő összeg) feloldja ezt
és reálisabb R²-t ad (havi: 0,55–0,80 a szakirodalomban).

## Goals / Non-Goals

**Goals:** a tavak fő szórásdiagramja havi aggregálásra vált; olvasható, pozitív felhő.
**Non-Goals:** a folyók rating-curve nézete és a napi magyarázó változók táblája változatlan.

## Decisions

- **Havi vízmérleg a tavak fő kapcsolatához.** Havonként: `havi_net = Σ(csapadék − párolgás)`,
  `havi_Δszint = hó végi szint − előző hó végi szint`. A szórás ezek párjaiból, OLS + R².
  *Miért havi és nem heti:* a havi a legtisztább felhő és a legintuitívabb vízmérleg-olvasat
  („csapadékosabb hónap → emelkedik"); a heti még zajos. A napi időzítés a magyarázó változók táblájában marad.
- **A magyarázó változók táblája napi, késleltetett Spearman marad.** A rang-alapú korreláció robusztus a
  kvantáltságra, és a napi késleltetés (pl. eső 1 nap múlva) érdekes információ.
- **Frontend változatlan.** A `RelationshipsPanel` a feliratokat és pontokat az artifactból
  veszi; csak a tartalom (havi) változik.

## Risks / Trade-offs

- [Kevesebb pont (~120 hónap)] → bőven elég egy szóráshoz; cserébe tiszta a jel.
- [Szabályozott tavak (Fertő, Tisza-tó) havi szinten is gyenge] → őszinte; a figyelmeztetés fedi.
