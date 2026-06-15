"""A vízszint és a magyarázó változók közti összefüggés számítása — tiszta Python.

A nyers vízszint *felhalmozott állapot* (autokorrelált + szezonális), ezért nyersen korrelálva
hamis. A helyes feldolgozás a **napi szintváltozáson (Δszint)** alapul: ez a napi vízmérleg
proxyja. Magyarázó változónként késleltetett Spearman-korreláció (a legjobb késleltetéssel), és
egy fő kapcsolat illesztéssel + R²-tel:

- tavak: Δszint vs (csapadék − párolgás) — vízmérleg;
- folyók: vízállás vs vízhozam — vízhozamgörbe (rating curve, pillanatnyi fizikai kapcsolat).

Granger-oksági tesztet szándékosan NEM számolunk (félrevezető „okság" címke, overkill).
"""

from __future__ import annotations

from datetime import date as Date
from datetime import timedelta

_MIN_PAIRS = 30
_MAX_LAG_LAKE = 14
_MAX_LAG_RIVER = 30


def _rank(values: list[float]) -> list[float]:
    """1-alapú rangok, kötéseknél átlagrang."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 2:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx == 0 or syy == 0:
        return None
    return sxy / (sxx**0.5 * syy**0.5)


def spearman(xs: list[float], ys: list[float]) -> float | None:
    """Spearman-rangkorreláció = a rangok Pearson-korrelációja."""
    if len(xs) < 2:
        return None
    return _pearson(_rank(xs), _rank(ys))


def ols(xs: list[float], ys: list[float]) -> tuple[float | None, float | None, float | None]:
    """Egyszerű lineáris regresszió: (slope, intercept, R²)."""
    n = len(xs)
    if n < 2:
        return (None, None, None)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return (None, None, None)
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    intercept = my - slope * mx
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else None
    return (slope, intercept, r2)


def delta_level(level: dict[Date, float]) -> dict[Date, float]:
    """Napi szintváltozás csak szomszédos napokra: Δ(t) = szint(t) − szint(t−1)."""
    out: dict[Date, float] = {}
    for day, value in level.items():
        prev = day - timedelta(days=1)
        if prev in level:
            out[day] = value - level[prev]
    return out


def _aligned(predictor: dict[Date, float], target: dict[Date, float], lag: int) -> tuple[list, list]:
    """A magyarázó változó `lag` nappal korábbi értékét párosítja a célváltozó napi értékéhez."""
    xs: list[float] = []
    ys: list[float] = []
    for day in sorted(target):
        src = day - timedelta(days=lag)
        if src in predictor:
            xs.append(predictor[src])
            ys.append(target[day])
    return xs, ys


def _prev_month(ym: tuple[int, int]) -> tuple[int, int]:
    year, month = ym
    return (year - 1, 12) if month == 1 else (year, month - 1)


def _monthly_balance(
    level: dict[Date, float], net: dict[Date, float]
) -> tuple[list[float], list[int]]:
    """Havi vízmérleg: havi (csapadék − párolgás) összeg vs havi szintváltozás.

    A havi szintváltozás a hó végi szint és az előző hó végi szint különbsége (csak
    közvetlenül megelőző naptári hónapra). Feloldja a napi cm-kvantáltságot.
    """
    net_sum: dict[tuple[int, int], float] = {}
    for day, value in net.items():
        ym = (day.year, day.month)
        net_sum[ym] = net_sum.get(ym, 0.0) + value

    month_end_day: dict[tuple[int, int], Date] = {}
    for day in level:
        ym = (day.year, day.month)
        if ym not in month_end_day or day > month_end_day[ym]:
            month_end_day[ym] = day
    month_end_level = {ym: level[day] for ym, day in month_end_day.items()}

    months = sorted(set(net_sum) & set(month_end_level))
    xs: list[float] = []
    ys: list[int] = []
    for ym in months:
        prev = _prev_month(ym)
        if prev in month_end_level:
            xs.append(round(net_sum[ym], 1))
            ys.append(round(month_end_level[ym] - month_end_level[prev]))
    return xs, ys


def _best_lag_spearman(
    predictor: dict[Date, float], target: dict[Date, float], max_lag: int
) -> tuple[int, float | None]:
    """A |Spearman-r| maximumát adó késleltetés (0..max_lag)."""
    best_lag = 0
    best_r: float | None = None
    for lag in range(max_lag + 1):
        xs, ys = _aligned(predictor, target, lag)
        if len(xs) < _MIN_PAIRS:
            continue
        r = spearman(xs, ys)
        if r is not None and (best_r is None or abs(r) > abs(best_r)):
            best_lag, best_r = lag, r
    return best_lag, best_r


def compute_relationships(
    water_body_id: str,
    name: str,
    kind: str,
    level: dict[Date, float],
    precip: dict[Date, float],
    et0: dict[Date, float],
    discharge: dict[Date, float],
    temp: dict[Date, float],
) -> dict:
    """Összefüggés-összegzés egy víztestre. A kind: ``"lake"`` vagy ``"river"``."""
    delta = delta_level(level)
    net = {d: precip[d] - et0[d] for d in precip if d in et0}

    if kind == "river":
        max_lag = _MAX_LAG_RIVER
        predictor_specs = [("Vízhozam", discharge), ("Csapadék", precip), ("Hőmérséklet", temp)]
    else:
        max_lag = _MAX_LAG_LAKE
        predictor_specs = [
            ("Csapadék", precip),
            ("Párolgás", et0),
            ("Csapadék − párolgás", net),
            ("Hőmérséklet", temp),
        ]

    predictors = []
    for label, series in predictor_specs:
        if not series:
            continue
        lag, r = _best_lag_spearman(series, delta, max_lag)
        predictors.append(
            {"label": label, "lag_days": lag, "spearman_r": round(r, 2) if r is not None else None}
        )

    if kind == "river" and discharge:
        xs, ys = [], []
        for day in sorted(discharge):
            if day in level:
                xs.append(discharge[day])
                ys.append(level[day])
        slope, intercept, r2 = ols(xs, ys)
        points = [[round(x, 1), int(y)] for x, y in zip(xs, ys)]
        primary = {
            "title": "Vízállás vs vízhozam (vízhozamgörbe)",
            "x_label": "Vízhozam (m³/s)",
            "y_label": "Vízállás (cm)",
        }
    else:
        # Havi aggregálás: a napi Δszint egész cm-be torlódna, ezért havi vízmérleg.
        xs, ys = _monthly_balance(level, net)
        slope, intercept, r2 = ols(xs, ys)
        points = [[x, y] for x, y in zip(xs, ys)]
        primary = {
            "title": "Havi szintváltozás vs havi (csapadék − párolgás)",
            "x_label": "Havi csapadék − párolgás (mm/hó)",
            "y_label": "Havi szintváltozás (cm/hó)",
        }

    primary.update(
        {
            "r2": round(r2, 3) if r2 is not None else None,
            "slope": round(slope, 4) if slope is not None else None,
            "intercept": round(intercept, 2) if intercept is not None else None,
            "n": len(points),
            "points": points,
        }
    )
    return {"id": water_body_id, "name": name, "kind": kind, "primary": primary, "predictors": predictors}
