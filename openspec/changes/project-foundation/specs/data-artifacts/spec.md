## ADDED Requirements

### Requirement: Víztest-geometria artifact
A rendszer a kanonikus tárból egy `web/public/data/water-bodies.geojson` fájlt SHALL
legenerálni, amely a megjelenítendő víztestek geometriáját és azonosítóját tartalmazza
érvényes GeoJSON FeatureCollection formában.

#### Scenario: Érvényes GeoJSON keletkezik
- **WHEN** az artifact-generátor lefut
- **THEN** a `water-bodies.geojson` érvényes GeoJSON, és minden feature-höz tartozik egy
  stabil víztest-azonosító (`id`) és név

### Requirement: Vízállás idősor artifact víztestenként
A rendszer víztestenként egy `web/public/data/water-levels/{id}.json` fájlt SHALL
legenerálni, amely tartalmazza a legutóbbi vízállás-értéket és egy rövid idősort a friss
időszakra. Az artifactok determinisztikusan, kizárólag a kanonikus tárból készülnek.

#### Scenario: Determinisztikus generálás
- **WHEN** az artifact-generátor változatlan kanonikus táron kétszer fut le
- **THEN** a kimeneti JSON-fájlok tartalma azonos

#### Scenario: Frontend által fogyasztható forma
- **WHEN** egy `water-levels/{id}.json` elkészül
- **THEN** tartalmazza a víztest azonosítóját, a legutóbbi értéket dátummal, és egy
  dátum→érték idősort, böngészőben közvetlenül feldolgozható alakban
