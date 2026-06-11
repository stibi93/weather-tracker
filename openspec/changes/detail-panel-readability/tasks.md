## 1. Grafikon hover-tooltip

- [x] 1.1 uPlot kurzor-tooltip plugin a `Chart` komponensben: dátum + pontos cm-érték a kurzornál
- [x] 1.2 A grafikon-konténer `position: relative` (uPlot `u.over`), a tooltip a (C) földes stílushoz igazítva
- [x] 1.3 A tooltip eltűnik a grafikon elhagyásakor

## 2. Nagyobb panel-megjelenés

- [x] 2.1 Szélesebb részletpanel (448px) és nagyobb grafikon (400×260)
- [x] 2.2 Tipográfia/spacing arányos igazítása az olvashatóságért (cím 21px, érték 32px)

## 3. Verifikáció

- [x] 3.1 Build hibamentes
- [x] 3.2 E2e (Playwright): kattintásra nagyobb panel (448px); grafikon hoverre dátum + pontos érték; elhagyáskor eltűnik
- [x] 3.3 `openspec validate detail-panel-readability --strict` hibamentes
