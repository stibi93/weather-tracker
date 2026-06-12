## ADDED Requirements

### Requirement: Grafikon méret-váltó
A részletpanel SHALL kínáljon egy gombot, amellyel a grafikon (és a panel) normál és
nagyított méret között váltható. A nagyított nézet érezhetően nagyobb grafikont mutat, és a
gomb ismételt megnyomására visszatér a normál méretre.

#### Scenario: Nagyobb nézetre váltás
- **WHEN** a felhasználó a méret-váltó gombra kattint normál nézetben
- **THEN** a grafikon (és a panel) nagyított méretre vált

#### Scenario: Vissza normál méretre
- **WHEN** a felhasználó a méret-váltó gombra kattint nagyított nézetben
- **THEN** a grafikon és a panel visszatér a normál méretre
