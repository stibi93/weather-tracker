"""Az összefüggés-elemzés tesztjei ismert mintán."""

from datetime import date, timedelta

from ingest.analysis.relationships import (
    _best_lag_spearman,
    _monthly_balance,
    compute_relationships,
    delta_level,
    ols,
    spearman,
)


def test_spearman_monotonic():
    assert round(spearman([1, 2, 3, 4], [10, 20, 30, 40]), 6) == 1.0
    assert round(spearman([1, 2, 3, 4], [40, 30, 20, 10]), 6) == -1.0


def test_ols_perfect_line():
    slope, intercept, r2 = ols([0, 1, 2, 3], [1, 3, 5, 7])  # y = 2x + 1
    assert round(slope, 6) == 2.0
    assert round(intercept, 6) == 1.0
    assert round(r2, 6) == 1.0


def test_delta_level_only_consecutive_days():
    base = date(2026, 6, 1)
    level = {base: 10.0, base + timedelta(days=1): 13.0, base + timedelta(days=2): 12.0,
             base + timedelta(days=4): 20.0}
    assert delta_level(level) == {
        base + timedelta(days=1): 3.0,
        base + timedelta(days=2): -1.0,
    }


def test_best_lag_finds_known_lag():
    base = date(2024, 1, 1)
    predictor = {base + timedelta(days=i): float((i * 7) % 13) for i in range(40)}
    # a célváltozó a magyarázó változó 2 nappal korábbi értéke
    target = {
        base + timedelta(days=i): predictor[base + timedelta(days=i - 2)] for i in range(2, 40)
    }
    lag, r = _best_lag_spearman(predictor, target, max_lag=5)
    assert lag == 2
    assert r is not None and r > 0.99


def test_monthly_balance_sums_and_diffs():
    base = date(2024, 1, 1)
    level, net = {}, {}
    lvl = 100.0
    for i in range(120):  # ~4 hónap
        d = base + timedelta(days=i)
        n = float((i % 7) - 2)  # nettó vízmérleg napi
        net[d] = n
        lvl += 0.5 * n
        level[d] = lvl
    xs, ys = _monthly_balance(level, net)
    # a havi szintváltozás a havi nettó 0,5-szerese (a szintépítés szerint)
    assert len(xs) >= 2
    for x, y in zip(xs, ys):
        assert abs(y - 0.5 * x) < 1.0  # kerekítési tűréssel


def _synthetic(kind: str):
    base = date(2024, 1, 1)
    level, precip, et0, temp, discharge = {}, {}, {}, {}, {}
    lvl = 100.0
    for i in range(900):
        d = base + timedelta(days=i)
        p = float((i * 3) % 11)  # csapadék
        e = 2.0 + (i % 5) * 0.5  # párolgás
        precip[d], et0[d], temp[d] = p, e, 10.0 + (i % 7)
        discharge[d] = 50.0 + (i % 9) * 4
        # a szint a nettó vízmérleg szerint mozog (tavakra); nagy együttható, hogy a havi
        # szintváltozás az egész-cm kerekítés fölött legyen
        lvl += 1.0 * (p - e)
        level[d] = lvl
    return base, level, precip, et0, temp, discharge


def test_compute_relationships_lake_structure():
    _, level, precip, et0, temp, discharge = _synthetic("lake")
    rel = compute_relationships("balaton", "Balaton", "lake", level, precip, et0, {}, temp)
    assert rel["kind"] == "lake"
    labels = [d["label"] for d in rel["predictors"]]
    assert "Csapadék − párolgás" in labels
    assert "Vízhozam" not in labels  # tónál nincs
    assert "havi" in rel["primary"]["title"].lower()
    assert "csapadék − párolgás" in rel["primary"]["title"].lower()
    assert rel["primary"]["n"] >= 12  # hónapok
    # a havi szintváltozást a havi nettó hajtja -> magas R²
    assert rel["primary"]["r2"] is not None and rel["primary"]["r2"] > 0.9


def test_compute_relationships_river_uses_discharge():
    _, level, precip, et0, temp, discharge = _synthetic("river")
    rel = compute_relationships("duna", "Duna", "river", level, precip, et0, discharge, temp)
    assert rel["kind"] == "river"
    assert "vízhozam" in rel["primary"]["title"].lower()
    assert rel["primary"]["y_label"] == "Vízállás (cm)"
    labels = [d["label"] for d in rel["predictors"]]
    assert "Vízhozam" in labels
