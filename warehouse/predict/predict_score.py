"""ERW forecast (predict): the report card. Every place, every method, every cut; no place or period left out.

Session 10600, chain 730 (part D2). Method note: docs/methods/predict.md, section "The scores".

An hour enters a place's comparison only when the actual value and every scored method's forecast are held for it,
the operator's included, so that every method of a place is scored on the same hours; the count is in each row.
"""
import numpy as np
import pandas as pd

CHOICE_DAYS = 730
COLUMNS = ["place", "series", "method", "cut", "key", "hours", "mae", "mape", "held"]


def common(hr, methods):
    """The hours where the actual and every method in `methods` are held."""
    need = ["actual"] + list(methods)
    return hr.dropna(subset=need)


def metric(x, m, mape_floor=None):
    """(hours, mae, mape) of method m over the frame x. mape over the hours whose actual is above zero, or, for a
    price, at least mape_floor in size (a percent of a price near zero means nothing)."""
    if not len(x):
        return 0, None, None
    err = (x[m] - x["actual"]).abs()
    a = x["actual"].abs() if mape_floor is not None else x["actual"]
    keep = a >= mape_floor if mape_floor is not None else a > 0
    mape = float((err[keep] / a[keep]).mean() * 100) if keep.any() else None
    return int(len(x)), round(float(err.mean()), 2), (round(mape, 3) if mape is not None else None)


def choose(hr, candidates, days=CHOICE_DAYS, extra=()):
    """The candidate with the lowest mean absolute error over the last `days` target days, on the hours every candidate
    and every name in `extra` (the operator) holds. Returns (method, {method: mae})."""
    last = hr["day"].max()
    x = hr[hr["day"] > last - pd.Timedelta(days=days)]
    c = common(x, list(candidates) + list(extra))
    maes = {m: metric(c, m)[1] for m in candidates}
    best = min((v, m) for m, v in maes.items() if v is not None)[1]
    return best, maes


def cuts(hr, events, top_n=10, choice_days=CHOICE_DAYS, spike_q=None):
    """[(cut, key, mask)] over the hourly frame: all, last_2_years, month, hour (over the last two years), top10,
    event, and spike (a price: the hours above the series' own spike_q quantile over the whole backtest)."""
    out = [("all", "", np.ones(len(hr), dtype=bool))]
    last = hr["day"].max()
    recent = (hr["day"] > last - pd.Timedelta(days=choice_days)).to_numpy()
    out.append(("last_2_years", "", recent))
    months = hr["day"].dt.strftime("%Y-%m").to_numpy()
    for mo in sorted(set(months)):
        out.append(("month", mo, months == mo))
    hours = hr["hour"].to_numpy()
    for h in range(24):
        out.append(("hour", str(h), recent & (hours == h)))
    peaks = hr.groupby("day")["actual"].max().dropna()
    top = set(peaks.sort_values(ascending=False).index[:top_n])
    out.append(("top10", "", hr["day"].isin(top).to_numpy()))
    for eid, (a, b) in events.items():
        m = ((hr["day"] >= pd.Timestamp(a)) & (hr["day"] <= pd.Timestamp(b))).to_numpy()
        if m.any():
            out.append(("event", eid, m))
    if spike_q is not None:
        thr = hr["actual"].quantile(spike_q)
        out.append(("spike", "", (hr["actual"] > thr).to_numpy()))
    return out


def rows(place, series, hr, methods, events, mape_floor=None, spike_q=None):
    """The score rows of one place and series: hr holds `actual`, each method's column and `erw`."""
    c = common(hr, methods).reset_index(drop=True)
    out = []
    for cut, key, mask in cuts(c, events, spike_q=spike_q):
        x = c[mask]
        for m in methods:
            n, mae, mape = metric(x, m, mape_floor)
            out.append([place, series, m, cut, key, n, mae, mape, None])
    return out


def held_rows(place, series, methods, reason):
    """A held series' rows: present, every number null, the reason given."""
    return [[place, series, m, "all", "", None, None, None, reason] for m in methods]


def summary(hr, methods, days=None, mape_floor=None):
    """{first_day, last_day, hours, mae: {m}, mape: {m}} over the common hours (the last `days` days when given)."""
    x = hr
    if days is not None and len(hr):
        x = hr[hr["day"] > hr["day"].max() - pd.Timedelta(days=days)]
    c = common(x, methods)
    out = {"first_day": c["day"].min().strftime("%Y-%m-%d") if len(c) else None,
           "last_day": c["day"].max().strftime("%Y-%m-%d") if len(c) else None,
           "hours": int(len(c)), "mae": {}, "mape": {}}
    for m in methods:
        _, mae, mape = metric(c, m, mape_floor)
        out["mae"][m] = mae
        out["mape"][m] = mape
    return out


def coverage(hr, m, days=CHOICE_DAYS):
    """The share of the last `days` days' hours (percent) whose actual fell inside method m's band."""
    last = hr["day"].max()
    x = hr[(hr["day"] > last - pd.Timedelta(days=days))].dropna(subset=["actual", m + "_lo", m + "_hi"])
    if not len(x):
        return None
    inside = (x["actual"] >= x[m + "_lo"]) & (x["actual"] <= x[m + "_hi"])
    return round(float(inside.mean() * 100), 1)
