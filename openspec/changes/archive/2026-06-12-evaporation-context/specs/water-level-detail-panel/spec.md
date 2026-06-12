## ADDED Requirements

### Requirement: Párolgás a másodlagos kontextus-váltóban
A részletpanel másodlagos kontextus-váltója SHALL kínáljon egy harmadik opciót, a **párolgást**
(ET₀, vonal, mm), a csapadék és a hőmérséklet mellett. A kiválasztott réteg a grafikon jobb
tengelyén jelenik meg; a hover-tooltip az aktív másodlagos értéket mutatja.

#### Scenario: Váltás párolgásra
- **WHEN** a felhasználó a párolgás kontextust választja
- **THEN** a grafikon jobb tengelye az ET₀-t (mm) mutatja vonalként, és a tooltip a párolgást is kiírja
