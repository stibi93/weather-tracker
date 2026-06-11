## ADDED Requirements

### Requirement: Többéves aggregált idősor
A rendszer víztestenként SHALL többéves vízállás-idősort generáljon a `water-levels/{id}.json`
artifactba: napi felbontással a friss ~2 évre, és havi átlaggal a régebbi évekre. Így a
fájl kicsi marad, a grafikon mégis évekre visszanyúlik.

#### Scenario: Vegyes felbontású sorozat
- **WHEN** az artifact-generátor többéves adaton fut
- **THEN** a sorozat a friss ~2 évre napi pontokat, a korábbi évekre havi (átlagolt)
  pontokat tartalmaz, időrendben

#### Scenario: Kompakt, frontend-fogyasztható forma
- **WHEN** egy víztest többéves sorozata elkészül
- **THEN** minden pont dátumot, értéket (cm) és felbontás-jelölést (`daily`/`monthly`)
  tartalmaz, böngészőben közvetlenül grafikonra köthető alakban
