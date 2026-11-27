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


FILING_TOLERANCE_PCT = 5.0
FILING_SHIFTS = (-1, 0, 1)


def filing_check(hr, days=CHOICE_DAYS):
    """The operator's day-ahead forecast as filed on Form EIA-930, tested against the demand it forecasts (chain 730,
    part F; method note section 16). For each month of the place's local days: the hours where both are held and the
    demand is above zero, and the filed forecast's sum as a percent of the demand's sum over those hours; a month whose
    percent is more than FILING_TOLERANCE_PCT from 100 is flagged (a level that far off in a whole month is a footprint
    or filing break, not a forecaster's error). And the filed forecast's MAPE over the last `days` days with its hours
    moved by k (k = -1, 0, 1: k = 1 compares the forecast stamped an hour earlier with each hour's demand).
    Judges the comparator only: no forecast of the ERW reads it, and the choice of method does not."""
    x = hr[(hr["actual"] > 0) & hr["operator"].notna()]
    if not len(x):
        return None
    mo = x["day"].dt.strftime("%Y-%m")
    months = []
    for m, g in x.groupby(mo):
        ratio = float(g["operator"].sum() / g["actual"].sum() * 100)
        months.append([m, int(len(g)), round(ratio, 1), bool(abs(ratio - 100) > FILING_TOLERANCE_PCT)])
    last = hr["day"].max()
    r = hr[hr["day"] > last - pd.Timedelta(days=days)]
    a = pd.Series(r["actual"].to_numpy(float), index=pd.DatetimeIndex(r["ts"]))
    o = pd.Series(hr["operator"].to_numpy(float), index=pd.DatetimeIndex(hr["ts"]))
    shift = {}
    for k in FILING_SHIFTS:
        f = o.shift(k, freq="h").reindex(a.index)
        ok = (a > 0) & f.notna()
        shift[str(k)] = round(float(((f[ok] - a[ok]).abs() / a[ok]).mean() * 100), 3) if ok.any() else None
    held = {k: v for k, v in shift.items() if v is not None}
    best = int(min(held, key=held.get)) if held else None
    return {"tolerance_pct": FILING_TOLERANCE_PCT, "months_columns": ["month", "hours", "operator_pct_of_demand", "flagged"],
            "months": months, "months_flagged": sum(1 for m in months if m[3]), "months_held": len(months),
            "shift_mape_last_2_years": shift, "best_shift_hours": best}


def sound_months(check):
    """The months of a filing check that are not flagged (an empty set when there is no check)."""
    return set() if not check else {m[0] for m in check["months"] if not m[3]}


def rows(place, series, hr, methods, events, mape_floor=None, spike_q=None, sound=None):
    """The score rows of one place and series: hr holds `actual`, each method's column and `erw`. `sound`: the months
    whose operator filing passes the filing check; given, two more cuts are scored on their hours, operator_sound
    (all of them) and operator_sound_last_2_years (those of the last two years)."""
    c = common(hr, methods).reset_index(drop=True)
    out = []
    cs = cuts(c, events, spike_q=spike_q)
    if sound is not None:
        ok = c["day"].dt.strftime("%Y-%m").isin(sorted(sound)).to_numpy()
        recent = (c["day"] > c["day"].max() - pd.Timedelta(days=CHOICE_DAYS)).to_numpy()
        cs += [("operator_sound", "", ok), ("operator_sound_last_2_years", "", ok & recent)]
    for cut, key, mask in cs:
        x = c[mask]
        for m in methods:
            n, mae, mape = metric(x, m, mape_floor)
            out.append([place, series, m, cut, key, n, mae, mape, None])
    return out


def held_rows(place, series, methods, reason):
    """A held series' rows: present, every number null, the reason given."""
    return [[place, series, m, "all", "", None, None, None, reason] for m in methods]


def summary(hr, methods, days=None, mape_floor=None, also=()):
    """{first_day, last_day, hours, mae: {m}, mape: {m}} over the common hours (the last `days` days when given). `also`:
    more methods that must be held for an hour to count (the score file's set), reported or not."""
    x = hr
    if days is not None and len(hr):
        x = hr[hr["day"] > hr["day"].max() - pd.Timedelta(days=days)]
    c = common(x, list(methods) + [m for m in also if m not in methods])
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


def peaks(hr, methods):
    """One row a local day whose every hour is held by the actual and every method: the day's actual peak (MW and
    local hour) and each method's forecast peak (the highest of its hourly forecasts, and the hour of it)."""
    c = common(hr, methods)
    full = c.groupby("day")["hour"].transform("size") == hr.groupby("day")["hour"].transform("size").reindex(c.index)
    c = c[full.to_numpy()]
    rows = []
    for day, g in c.groupby("day"):
        r = {"day": day, "actual": float(g["actual"].max()), "actual_hour": int(g.loc[g["actual"].idxmax(), "hour"])}
        for m in methods:
            r[m] = float(g[m].max())
            r[m + "_hour"] = int(g.loc[g[m].idxmax(), "hour"])
        rows.append(r)
    return pd.DataFrame(rows)


def peak_summary(pk, methods, days=None):
    """{days, first_day, last_day, by method: {mae (MW), mape (percent), hour_exact_pct, hour_within_1_pct}} over the
    peak table (the last `days` days when given)."""
    x = pk
    if days is not None and len(pk):
        x = pk[pk["day"] > pk["day"].max() - pd.Timedelta(days=days)]
    out = {"days": int(len(x)), "first_day": x["day"].min().strftime("%Y-%m-%d") if len(x) else None,
           "last_day": x["day"].max().strftime("%Y-%m-%d") if len(x) else None, "methods": {}}
    for m in methods:
        if not len(x):
            out["methods"][m] = None
            continue
        e = (x[m] - x["actual"]).abs()
        dh = (x[m + "_hour"] - x["actual_hour"]).abs()
        out["methods"][m] = {"mae": round(float(e.mean()), 1), "mape": round(float((e / x["actual"]).mean() * 100), 3),
                             "hour_exact_pct": round(float((dh == 0).mean() * 100), 1), "hour_within_1_pct": round(float((dh <= 1).mean() * 100), 1)}
    return out
