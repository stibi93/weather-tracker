## 1. Méret-váltó

- [x] 1.1 `DetailPanel`: `expanded` állapot + méret-váltó gomb (a fejlécben, a bezárás mellett)
- [x] 1.2 A `Chart` a normál (400×260) vagy nagyított (~viewport ≤900, 460 magas) méretet kapja
- [x] 1.3 Nagyított nézetben a panel középre kerül (CSS osztály); ablak-resize figyelő frissíti a méretet

## 2. Verifikáció

- [x] 2.1 Build hibamentes
- [x] 2.2 E2e (Playwright): gombra a grafikon 400→900 px és a panel középre; újra gombra vissza 400-ra
- [x] 2.3 `openspec validate chart-size-toggle --strict` hibamentes
