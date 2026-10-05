#!/usr/bin/env python3
"""The Flex Alert scorecard (session 60, California grid-stress tool v1, /grid/caiso/alerts).

Energy Research Warehouse (ERW) derived tables, public, tier derived. The question: how much did CAISO's demand fall in
the hours of a Flex Alert or grid emergency, against what the weather and the calendar predicted, and what was that
worth at the day-ahead price? docs/methods/flex_alert_scorecard.md is the method, written as a paper's methods section;
notebooks/flex_alert_scorecard.ipynb reproduces every number.

    warehouse/output/flex_alert_effects.csv   per alert day (P1D, ts_utc the Pacific day at 00:00:00Z), the alert hours'
                                              actual and predicted MWh, the reduction (predicted less actual) in MW and MWh
                                              with a 90 percent interval, its share of predicted demand, the hub price and
                                              the wholesale value; per alert hour of the evening (PT1H, ts_utc the hour's
                                              start) actual_mw, predicted_mw and its 90 percent band; per year (P1Y)
    warehouse/output/flex_alert_model.csv     the model: the pooled result, fit and out-of-sample statistics, station
                                              weights, every coefficient, and the held-out hot days' errors and prices

    python warehouse/derived/flex_alert_scorecard.py            # the tables (needs the data lock)
    python warehouse/derived/flex_alert_scorecard.py --days     # the days the price pull needs, one per line

The model, in short (the method has it whole). For each local hour h, an ordinary least squares fit on the non-alert days
of May to October, 2018-07 to 2025:
    demand = a + b1 CDH + b2 CDH^2 + b3 CDH24 + b4 CDH24^2 + b5 dew + b6 CDH x dew + Saturday + Sunday + holiday
             + month + year + e
CDH is the cooling degree hour, max(T - 65 F, 0), of the population-weighted temperature of three NOAA stations
(Sacramento 0.30, Fresno 0.20, Los Angeles 0.50); CDH24 the mean CDH over the 24 hours before (heat that builds over
days); dew the weighted dew point. The prompt's minimal model is CDH, its square and the calendar; CDH24 and the dew
point were added because heat builds over days and humid heat drives load, and CDH24^2 and CDH x dew because they cut the
cross-validated error on hot days. Five variants named in advance (VARIANTS) are all fitted and reported, each with its
hot-day error and pooled result, so the choice can be judged. An alert day's reduction is predicted minus actual
demand in its alert hours. Its interval combines the model's parameter uncertainty (a block bootstrap over calendar
weeks of the training days, refitting all 24 hours) with its prediction error (a whole-day out-of-fold residual vector
from a hot day, centred), 1,000 replicates, 5th and 95th percentiles. Out of sample: the hottest tenth of non-alert days
(by the day's highest weighted temperature) is split into five folds; each fold is predicted by the model fitted on every
other non-alert day, and the error in the hours 16:00 to 21:00 reported.
"""

import datetime as dt
import os
import re
import sys
import traceback

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402
import eia930_emissions as em  # noqa: E402
import impossible_hours  # noqa: E402  (session 118: the one rule for impossible values)

EFFECTS, MODEL = "flex_alert_effects", "flex_alert_model"
SOURCE = "erw:flex_alert_scorecard"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/flex_alert_scorecard.md"
TZ = "America/Los_Angeles"
START = "2018-07-01"           # the start of EIA's per-BA workbook as the extract holds it
END = "2025-10-31"             # the last alert season with weather
MONTHS = (5, 6, 7, 8, 9, 10)   # the alert season
WEIGHTS = {"SAC": 0.30, "FAT": 0.20, "LAX": 0.50}  # stated in the method: CAISO's population by region, rounded
BASE_F = 65.0
DEFAULT_HOURS = (16, 17, 18, 19, 20)  # 4 to 9 p.m. Pacific, where a notice gives no hours
EVENING = tuple(range(12, 24))        # the hours the per-day chart shows
ALERT_TYPES = ("flex_alert", "eea_watch", "eea1", "eea2", "eea3", "alert", "warning", "stage1", "stage2", "stage3",
               "load_interruption")
CONSERVE = ("flex_alert",)
EMERGENCY = ("eea_watch", "eea1", "eea2", "eea3", "alert", "stage1", "stage2", "stage3", "load_interruption")
ISO_REGIONS = ("ISO", "CAISO Grid", "")
HOLDOUT_SHARE = 0.10
B = 1000
VARIANT_B = 200  # the robustness rows' replicates
SEED = 20261002
FOLDS = 5
TERMS = ["intercept", "cdh", "cdh2", "cdh_prev24", "cdh_prev24_2", "dew_point", "cdh_x_dew", "saturday", "sunday", "holiday"] + \
        [f"month{m}" for m in MONTHS[1:]] + [f"year{y}" for y in range(2019, 2026)]


# ---------------------------------------------------------------------------------------------------------------------
# alert days and their hours
# ---------------------------------------------------------------------------------------------------------------------

MONTH_NAMES = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                            "september", "october", "november", "december"], 1)}


def _clock(s):
    """'15:00', '15:00:00', '4:00 PM' to minutes after midnight."""
    m = re.match(r"\s*(\d{1,2}):(\d{2})(?::\d{2})?\s*(AM|PM)?", s, re.I)
    if not m:
        return None
    h, mi, ap = int(m.group(1)), int(m.group(2)), (m.group(3) or "").upper()
    if ap == "PM" and h < 12:
        h += 12
    if ap == "AM" and h == 12:
        h = 0
    return h * 60 + mi


def window(row):
    """(first local date, last local date, start minute, end minute) of a notice, or None. From x_start and x_end where
    the table parsed them; else from x_time_frame's text (four other forms the report uses)."""
    if isinstance(row.get("x_start"), str) and row["x_start"] and isinstance(row.get("x_end"), str) and row["x_end"]:
        a, b = pd.Timestamp(row["x_start"]), pd.Timestamp(row["x_end"])
        return a.date(), b.date(), a.hour * 60 + a.minute, b.hour * 60 + b.minute
    tf = str(row.get("x_time_frame") or "")
    y = int(str(row["event_date"])[:4])
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})\s+(?:at\s+)?([\d:]+)\s+through\s+(?:(\d{1,2})/(\d{1,2})/(\d{4})\s+(?:at\s+)?)?([\d:]+)", tf)
    if m:
        d0 = dt.date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
        d1 = dt.date(int(m.group(7)), int(m.group(5)), int(m.group(6))) if m.group(5) else d0
        return d0, d1, _clock(m.group(4)), _clock(m.group(8))
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})\s+([\d:]+)\s+through\s+(\d{4})-(\d{2})-(\d{2})\s+([\d:]+)", tf)
    if m:
        return (dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3))), dt.date(int(m.group(5)), int(m.group(6)), int(m.group(7))),
                _clock(m.group(4)), _clock(m.group(8)))
    m = re.match(r"([A-Za-z]+)\s+(\d{1,2})\s+at\s+([\d:]+\s*[AP]M)\s+to\s+([A-Za-z]+)\s+(\d{1,2})\s+at\s+([\d:]+\s*[AP]M)", tf)
    if m and m.group(1).lower() in MONTH_NAMES:
        return (dt.date(y, MONTH_NAMES[m.group(1).lower()], int(m.group(2))), dt.date(y, MONTH_NAMES[m.group(4).lower()], int(m.group(5))),
                _clock(m.group(3)), _clock(m.group(6)))
    return None


def hours_of(start_min, end_min):
    """The local hours (starts) a daily clock window covers for at least 30 minutes; 23:59 counts as 24:00."""
    if end_min >= 23 * 60 + 59:
        end_min = 24 * 60
    return [h for h in range(24) if min(end_min, (h + 1) * 60) - max(start_min, h * 60) >= 30]


def alert_days(em_rows, first=START, last=END):
    """One row per alert day: day (local), types (the day's notice types, sorted), hours (local hour starts), basis
    (which notice the hours come from: flex_alert, emergency, warning or assumed), assumed (bool), source_notices (the
    event ids used). A notice whose window spans several days covers each day with its daily clock window."""
    x = em_rows[em_rows["event_type"].isin(ALERT_TYPES) & em_rows["x_region"].fillna("").isin(ISO_REGIONS)]
    per_day = {}
    for _, r in x.iterrows():
        w = window(r)
        if w is None:
            days = [pd.Timestamp(r["event_date"]).date()]
            span = None
        else:
            d0, d1, s, e = w
            days = list(pd.date_range(d0, d1, freq="D").date) or [d0]
            span = (s, e) if (s is not None and e is not None and s < e) else None
        for d in days:
            per_day.setdefault(d, []).append((r["event_type"], span, r["event_id"]))
    out = []
    for d in sorted(per_day):
        ds = d.strftime("%Y-%m-%d")
        if ds < first or ds > last:
            continue
        ns = per_day[d]
        types = sorted({t for t, _, _ in ns})
        hours, basis = [], "assumed"
        for group, name in ((CONSERVE, "flex_alert"), (EMERGENCY, "emergency"), (("warning",), "warning")):
            spans = [sp for t, sp, _ in ns if t in group and sp]
            if spans:
                hours = sorted({h for s, e in spans for h in hours_of(s, e)})
                basis = name
                break
        if not hours:
            hours = list(DEFAULT_HOURS)
        out.append(dict(day=ds, types=types, hours=hours, basis=basis, assumed=basis == "assumed",
                        source_notices=sorted({i for _, _, i in ns})))
    return pd.DataFrame(out)


def notice_days(em_rows, first=START, last=END):
    """Every local day with any CAISO notice (all types and regions), for the price pull."""
    days = set()
    for _, r in em_rows.iterrows():
        w = window(r)
        if w is None:
            days.add(str(r["event_date"])[:10])
        else:
            for d in pd.date_range(w[0], w[1], freq="D"):
                days.add(d.strftime("%Y-%m-%d"))
    return sorted(d for d in days if first <= d <= last)


def read_table(name):
    path = os.path.join(ip.OUT_DIR, name + ".csv")
    with open(path, encoding="utf-8") as f:
        n = sum(1 for ln in f if ln.startswith("#"))
    return pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False)


# ---------------------------------------------------------------------------------------------------------------------
# the panel: demand, weather, calendar
# ---------------------------------------------------------------------------------------------------------------------

def suspect(mw):
    """The starter export's screen (warehouse/exports/redivis_starter.py): below 30 percent of the median hour, or one hour
    more than 20 percent above or below both neighbours. mw: a series on a complete hourly UTC index."""
    prev, nxt = mw.shift(1), mw.shift(-1)
    return (mw < 0.3 * mw.median()) | ((mw > 1.2 * prev) & (mw > 1.2 * nxt)) | ((mw < prev / 1.2) & (mw < nxt / 1.2))


def demand(log=print):
    """CISO hourly demand (EIA-930 Demand, the extract session 58's reliability table reads), UTC hour starts, with the
    hours the screen marks suspect set to missing. (series, provenance line)."""
    ex = em.latest_extract("ciso")
    if not ex:
        raise RuntimeError("no CISO extract under warehouse/raw/eia930_emissions/")
    url, lm, got = em.extract_meta(ex)
    x = em.read_extract(ex)[["ts_utc", "demand_mwh"]]
    s = pd.Series(pd.to_numeric(x["demand_mwh"], errors="coerce").to_numpy(), index=pd.to_datetime(x["ts_utc"], utc=True)).sort_index()
    s = s[~s.index.duplicated()]
    s = s.reindex(pd.date_range(s.index.min(), s.index.max(), freq="h"))
    # session 118: the ERW has one rule for impossible hours (docs/methods/impossible_hours.md). This table had another
    # (suspect, above: the starter export's), which marked 27 hours where the one rule marks 37. Built both ways from
    # the same inputs on 2026-10-05, the two tables are the same in every value (2,973 and 881 rows): the hours that
    # differ lie before the weather the model needs. So the one rule is applied here, and no number moved
    bad = impossible_hours.screen(s).isna() & s.notna()
    log(f"CISO demand: {s.notna().sum():,} hours ({url}, last modified {lm}, retrieved {got}); {int(bad.sum())} marked suspect and left out")
    s[bad] = np.nan
    return s, f"{url} (last modified {lm}; extract {os.path.relpath(ex, ROOT)})"


def weather(log=print):
    """Hourly population-weighted temperature and dew point (F) from noaa_isd_hourly's SAC, FAT and LAX observations:
    each observation to its nearest UTC hour, the hour's mean per station, gaps of at most two hours interpolated per
    station, and an hour kept only where all three stations have a value. (DataFrame indexed by UTC hour, provenance)."""
    w = read_table("noaa_isd_hourly")
    w = w[w["entity"].isin([f"noaa:{c}" for c in WEIGHTS])]
    w = w.assign(t=pd.to_datetime(w["ts_utc"], utc=True).dt.round("h"), v=pd.to_numeric(w["value"], errors="coerce"))
    out = {}
    for var in ("temperature_f", "dew_point_f"):
        p = w[w["variable"] == var].groupby(["t", "entity"])["v"].mean().unstack("entity")
        p = p.reindex(pd.date_range(p.index.min(), p.index.max(), freq="h"))
        p = p.interpolate(limit=2, limit_area="inside")
        out[var] = sum(p[f"noaa:{c}"] * wt for c, wt in WEIGHTS.items())  # NaN unless all three stations are there
    f = pd.DataFrame(out)
    f["cdh"] = (f["temperature_f"] - BASE_F).clip(lower=0)
    f["cdh_prev24"] = f["cdh"].shift(1).rolling(24, min_periods=20).mean()
    log(f"weather: {f['temperature_f'].notna().sum():,} weighted hours from noaa_isd_hourly ({', '.join(f'{c} {wt}' for c, wt in WEIGHTS.items())})")
    return f, "noaa_isd_hourly (NOAA NCEI Integrated Surface Database, global-hourly): SAC 72483023232, FAT 72389093193, LAX 72295023174"


def holidays(years):
    from pandas.tseries.holiday import USFederalHolidayCalendar
    return set(USFederalHolidayCalendar().holidays(f"{min(years)}-01-01", f"{max(years)}-12-31").strftime("%Y-%m-%d"))


def panel(load, wx, first=START, last=END):
    """One row per UTC hour of the alert seasons with the hour's demand and features: ts (UTC), day and hour (local),
    y (MW), cdh, cdh2, cdh_prev24, dew_point, saturday, sunday, holiday, month, year, temp_f."""
    idx = load.index.intersection(wx.index)
    p = pd.DataFrame({"y": load.reindex(idx), "temp_f": wx["temperature_f"].reindex(idx), "dew_point": wx["dew_point_f"].reindex(idx),
                      "cdh": wx["cdh"].reindex(idx), "cdh_prev24": wx["cdh_prev24"].reindex(idx)})
    loc = idx.tz_convert(TZ)
    p["ts"] = idx
    p["day"], p["hour"] = loc.strftime("%Y-%m-%d"), loc.hour
    p["month"], p["year"], dow = loc.month, loc.year, loc.dayofweek
    p["dow"] = dow
    p = p[(p["day"] >= first) & (p["day"] <= last) & p["month"].isin(MONTHS)].copy()
    hol = holidays(range(2018, 2026))
    p["holiday"] = p["day"].isin(hol).astype(float)
    p["saturday"] = (p["dow"] == 5).astype(float)
    p["sunday"] = (p["dow"] == 6).astype(float)
    p["cdh2"] = p["cdh"] ** 2
    p["cdh_prev24_2"] = p["cdh_prev24"] ** 2
    p["cdh_x_dew"] = p["cdh"] * p["dew_point"]
    return p.reset_index(drop=True)


def complete_days(p):
    """Days with all of their local hours present (24; 23 or 25 at a clock change) and every feature and demand held."""
    ok = p.dropna(subset=["y", "cdh", "cdh_prev24", "dew_point"])
    n = ok.groupby("day").size()
    need = p.groupby("day")["ts"].size()
    return set(n.index[(n == need.reindex(n.index)) & (n >= 23)])


# ---------------------------------------------------------------------------------------------------------------------
# the estimator: one OLS per local hour
# ---------------------------------------------------------------------------------------------------------------------

# the specifications compared by cross-validation, each named by the weather terms it leaves out; "chosen" leaves out none
VARIANTS = {
    "minimal": ("cdh_prev24", "cdh_prev24_2", "dew_point", "cdh_x_dew"),  # the prompt's: CDH, CDH squared, the calendar
    "base": ("cdh_prev24_2", "cdh_x_dew"),                                # plus the 24 hours before and the dew point
    "base_prev24sq": ("cdh_x_dew",),
    "base_cdh_dew": ("cdh_prev24_2",),
    "chosen": (),
}


def design(p, drop=()):
    """The regressors of TERMS for the rows of p (month and year as indicators; May and 2018 the bases), without the
    weather terms in drop (a variant)."""
    terms = [t for t in TERMS[1:10] if t not in drop]
    cols = [np.ones(len(p))] + [p[t].to_numpy(float) for t in terms]
    cols += [(p["month"].to_numpy() == m).astype(float) for m in MONTHS[1:]]
    cols += [(p["year"].to_numpy() == y).astype(float) for y in range(2019, 2026)]
    return np.column_stack(cols)


def fit(p, days, weights=None, drop=()):
    """{hour: coefficients} fitted on the rows of p whose day is in days. weights: rows' bootstrap multiplicities by day."""
    sub = p[p["day"].isin(days)]
    betas = {}
    for h, g in sub.groupby("hour"):
        X, y = design(g, drop), g["y"].to_numpy(float)
        if weights is not None:
            m = g["day"].map(weights).fillna(0).to_numpy(float)
            keep = m > 0
            X, y, m = X[keep], y[keep], m[keep]
            sw = np.sqrt(m)
            X, y = X * sw[:, None], y * sw
        betas[h] = np.linalg.lstsq(X, y, rcond=None)[0]
    return betas


def predict(p, betas, drop=()):
    out = np.full(len(p), np.nan)
    X = design(p, drop)
    for h, b in betas.items():
        i = (p["hour"] == h).to_numpy()
        out[i] = X[i] @ b
    return out


def hot_days(p, days, share=HOLDOUT_SHARE):
    """The hottest share of days (by the day's highest weighted temperature), and that temperature threshold."""
    tmax = p[p["day"].isin(days)].groupby("day")["temp_f"].max()
    k = max(1, int(round(len(tmax) * share)))
    top = tmax.sort_values(ascending=False).iloc[:k]
    return sorted(top.index), float(top.min())


def folds(hold, k=FOLDS, seed=SEED):
    """The held-out hot days split into k folds, at random (fixed seed)."""
    h = np.array(sorted(hold))
    np.random.default_rng(seed).shuffle(h)
    return [sorted(f) for f in np.array_split(h, k)]


def out_of_sample(p, train_all, hold, hours=DEFAULT_HOURS, drop=()):
    """Each fold of the hot days predicted by the model fitted on every other non-alert day. (metrics, per-day mean error
    in the hours, out-of-fold residual vectors by day: actual less predicted)."""
    parts = []
    for f in folds(hold):
        betas = fit(p, sorted(set(train_all) - set(f)), drop=drop)
        q = p[p["day"].isin(f)].copy()
        q["pred"] = predict(q, betas, drop)
        parts.append(q)
    q = pd.concat(parts)
    q["err"] = q["y"] - q["pred"]
    w = q[q["hour"].isin(hours)]
    metrics = dict(bias_mw=float(w["err"].mean()), rmse_mw=float(np.sqrt((w["err"] ** 2).mean())),
                   mae_mw=float(w["err"].abs().mean()), mape_pct=float((w["err"].abs() / w["y"]).mean() * 100),
                   days=int(w["day"].nunique()), hours=int(len(w)))
    per_day = w.groupby("day")["err"].mean()
    vec = q.pivot_table(index="day", columns="hour", values="err", aggfunc="mean")
    return metrics, per_day, vec


def week_blocks(days):
    """Calendar week (ISO year and week) of each day: the bootstrap's blocks."""
    t = pd.to_datetime(pd.Series(days))
    iso = t.dt.isocalendar()
    return pd.Series((iso["year"].astype(str) + "-" + iso["week"].astype(str).str.zfill(2)).to_numpy(), index=days)


def estimate(p, alerts, train, resid, prices=None, b=B, seed=SEED, evening=EVENING, drop=()):
    """The effects. p: the panel; alerts: alert_days() rows; train: the training days; resid: whole-day residual vectors
    (DataFrame day x hour, actual less predicted) from the held-out hot days, centred here by hour; prices: {(day, hour):
    USD/MWh} or None. Returns (per-day DataFrame, per-hour DataFrame, per-year DataFrame, pooled dict, betas)."""
    rng = np.random.default_rng(seed)
    betas = fit(p, train, drop=drop)
    A = p[p["day"].isin(alerts["day"])].copy()
    A["pred"] = predict(A, betas, drop)
    hours = {r.day: set(r.hours) for r in alerts.itertuples()}
    A["alert"] = [h in hours.get(d, ()) for d, h in zip(A["day"], A["hour"])]
    A["price"] = [prices.get((d, h), np.nan) if prices else np.nan for d, h in zip(A["day"], A["hour"])]
    # the bootstrap: weeks of training days resampled with replacement, all 24 hours refitted; and a centred residual day
    blocks = week_blocks(sorted(train))
    weeks = blocks.unique()
    by_week = {w: list(blocks.index[blocks == w]) for w in weeks}
    R = resid.reindex(columns=range(24))
    R = R - R.mean()
    rdays = list(R.index)
    preds = np.empty((b, len(A)))
    for k in range(b):
        pick = rng.choice(weeks, size=len(weeks), replace=True)
        mult = {}
        for w in pick:
            for d in by_week[w]:
                mult[d] = mult.get(d, 0) + 1
        bb = fit(p, sorted(mult), weights=mult, drop=drop)
        noise = np.zeros(len(A))
        for d in A["day"].unique():
            r = R.loc[rdays[rng.integers(len(rdays))]]
            i = (A["day"] == d).to_numpy()
            noise[i] = r.reindex(A.loc[i, "hour"]).fillna(0).to_numpy()
        preds[k] = predict(A, bb, drop) + noise
    tmax_train = p[p["day"].isin(train)].groupby("day")["temp_f"].max()
    red = A["pred"].to_numpy() - A["y"].to_numpy()              # reduction, MW, each hour
    red_b = preds - A["y"].to_numpy()[None, :]                   # replicates
    lo, hi = 5, 95
    days, hrs = [], []
    for d in alerts["day"]:
        i = ((A["day"] == d) & A["alert"]).to_numpy()
        if not i.any():
            continue
        n = int(i.sum())
        pr = A.loc[i, "price"].to_numpy(float)
        has_price = bool(np.isfinite(pr).all())
        rb = red_b[:, i]
        v = dict(day=d, hours=n, actual_mwh=float(A.loc[i, "y"].sum()), predicted_mwh=float(A.loc[i, "pred"].sum()),
                 reduction_mwh=float(red[i].sum()), reduction_mw=float(red[i].mean()),
                 reduction_mwh_lo=float(np.percentile(rb.sum(1), lo)), reduction_mwh_hi=float(np.percentile(rb.sum(1), hi)),
                 reduction_mw_lo=float(np.percentile(rb.mean(1), lo)), reduction_mw_hi=float(np.percentile(rb.mean(1), hi)),
                 reduction_pct=float(red[i].sum() / A.loc[i, "pred"].sum() * 100),
                 temp_max_f=float(A.loc[A["day"] == d, "temp_f"].max()))
        v["train_days_as_hot"] = int((tmax_train >= v["temp_max_f"]).sum())
        if has_price:
            vb = (rb * pr[None, :]).sum(1)
            v.update(price_usd_mwh=float(pr.mean()), value_usd=float((red[i] * pr).sum()),
                     value_usd_lo=float(np.percentile(vb, lo)), value_usd_hi=float(np.percentile(vb, hi)))
        days.append(v)
        j = ((A["day"] == d) & A["hour"].isin(evening)).to_numpy()
        pb = preds[:, j]
        for t, h, a, pp, plo, phi, al in zip(A.loc[j, "ts"], A.loc[j, "hour"], A.loc[j, "y"], A.loc[j, "pred"],
                                             np.percentile(pb, lo, axis=0), np.percentile(pb, hi, axis=0), A.loc[j, "alert"]):
            hrs.append(dict(day=d, ts=t, hour=int(h), actual_mw=float(a), predicted_mw=float(pp), predicted_mw_lo=float(plo),
                            predicted_mw_hi=float(phi), alert=bool(al)))
    D = pd.DataFrame(days)
    H = pd.DataFrame(hrs)

    def summary(sel_days):
        i = (A["day"].isin(sel_days) & A["alert"]).to_numpy()
        rb = red_b[:, i]
        out = dict(days=len(sel_days), hours=int(i.sum()), reduction_mw=float(red[i].mean()),
                   reduction_mw_lo=float(np.percentile(rb.mean(1), lo)), reduction_mw_hi=float(np.percentile(rb.mean(1), hi)),
                   reduction_mwh=float(red[i].sum()), reduction_mwh_lo=float(np.percentile(rb.sum(1), lo)),
                   reduction_mwh_hi=float(np.percentile(rb.sum(1), hi)),
                   reduction_pct=float(red[i].sum() / A.loc[i, "pred"].sum() * 100))
        pr = A.loc[i, "price"].to_numpy(float)
        ok = np.isfinite(pr)
        out["value_hours"] = int(ok.sum())
        if ok.any():
            vb = (rb[:, ok] * pr[ok][None, :]).sum(1)
            out.update(value_usd=float((red[i][ok] * pr[ok]).sum()), value_usd_lo=float(np.percentile(vb, lo)),
                       value_usd_hi=float(np.percentile(vb, hi)))
        return out
    pooled = summary(list(D["day"]))
    Y = pd.DataFrame([dict(year=int(y), **summary(list(g["day"]))) for y, g in D.groupby(D["day"].str[:4])])
    return D, H, Y, pooled, betas


# ---------------------------------------------------------------------------------------------------------------------
# the run
# ---------------------------------------------------------------------------------------------------------------------

def inputs(log=print):
    emr = read_table("caiso_grid_emergencies")
    alerts = alert_days(emr)
    load, dsrc = demand(log)
    wx, wsrc = weather(log)
    p = panel(load, wx)
    full = complete_days(p)
    alerts = alerts[alerts["day"].isin(full)].reset_index(drop=True) if len(alerts) else alerts
    eligible = sorted(full - set(alert_days(emr)["day"]))
    hold, threshold = hot_days(p, eligible)
    return dict(emr=emr, alerts=alerts, p=p, full=full, eligible=eligible, hold=hold, threshold=threshold, dsrc=dsrc, wsrc=wsrc)


def price_days(log=print):
    """The days the price pull needs: every notice day since 2018-07 (any type or region) and the held-out hot days."""
    x = inputs(log)
    return sorted(set(notice_days(x["emr"])) | set(x["hold"]))


def read_prices():
    """{(local day, local hour): mean of SP15 and NP15 day-ahead LMP} from caiso_dam_alert_day_hub_prices; an hour is kept
    only with both hubs."""
    path = os.path.join(ip.OUT_DIR, "caiso_dam_alert_day_hub_prices.csv")
    if not os.path.exists(path):
        return {}, None
    s = read_table("caiso_dam_alert_day_hub_prices")
    s = s[s["variable"] == "lmp_dam"]
    t = pd.to_datetime(s["ts_utc"], utc=True).dt.tz_convert(TZ)
    s = s.assign(day=t.dt.strftime("%Y-%m-%d"), hour=t.dt.hour, v=pd.to_numeric(s["value"]))
    g = s.groupby(["day", "hour"]).agg(v=("v", "mean"), n=("entity", "nunique"))
    g = g[g["n"] == 2]
    return {k: float(v) for k, v in g["v"].items()}, path


def main():
    if "--days" in sys.argv:
        for d in price_days(lambda *_: None):
            print(d)
        return 0
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"flex_alert_scorecard_{run_id}.log"))
    results = []
    try:
        x = inputs(log)
        p, alerts, eligible, hold = x["p"], x["alerts"], x["eligible"], x["hold"]
        log(f"alert days with complete data: {len(alerts)}; eligible non-alert days: {len(eligible)}; held-out hot days: {len(hold)} "
            f"(highest weighted temperature at least {x['threshold']:.1f} F)")
        prices, ppath = read_prices()
        log(f"prices: {len(prices):,} local hours with both hubs" + ("" if ppath else " (no price table yet: values left out)"))
        metrics, per_day_err, vec = out_of_sample(p, eligible, hold)
        log(f"out of sample, held-out hot days, hours 16 to 20: bias {metrics['bias_mw']:.1f} MW, RMSE {metrics['rmse_mw']:.1f} MW, "
            f"MAPE {metrics['mape_pct']:.2f} percent, {metrics['days']} days")
        ins_betas = fit(p, eligible)
        q = p[p["day"].isin(eligible) & p["hour"].isin(DEFAULT_HOURS)].copy()
        q["err"] = q["y"] - predict(q, ins_betas)
        ins = dict(rmse_mw=float(np.sqrt((q["err"] ** 2).mean())), mape_pct=float((q["err"].abs() / q["y"]).mean() * 100))
        D, H, Y, pooled, betas = estimate(p, alerts, eligible, vec, prices)
        variants = {}
        for name, drop in VARIANTS.items():
            if name == "chosen":
                variants[name] = (metrics, pooled)
                continue
            mv, _, vv = out_of_sample(p, eligible, hold, drop=drop)
            _, _, _, pv, _ = estimate(p, alerts, eligible, vv, prices, b=VARIANT_B, drop=drop)
            variants[name] = (mv, pv)
            log(f"variant {name} (without {', '.join(drop)}): hot-day bias {mv['bias_mw']:.1f} MW, RMSE {mv['rmse_mw']:.1f} MW; pooled "
                f"{pv['reduction_mw']:.1f} MW ({pv['reduction_mw_lo']:.1f} to {pv['reduction_mw_hi']:.1f})")
        log(f"pooled: {pooled['reduction_mw']:.1f} MW (90 percent {pooled['reduction_mw_lo']:.1f} to {pooled['reduction_mw_hi']:.1f}) "
            f"over {pooled['hours']} alert hours on {pooled['days']} days")
        rows = []

        def add(table, ent, var, ts, v, unit, freq):
            if v is None or (isinstance(v, float) and not np.isfinite(v)):
                return
            rows.append((table, ent, var, ts, round(float(v), 4), unit, freq))
        E, M = "eia930:CISO", "erw:flex_alert_model"
        A = alerts.set_index("day")
        for r in D.itertuples():
            ts = f"{r.day}T00:00:00Z"
            a = A.loc[r.day]
            for var, unit in (("hours", "count"), ("actual_mwh", "MWh"), ("predicted_mwh", "MWh"), ("reduction_mwh", "MWh"),
                              ("reduction_mwh_lo", "MWh"), ("reduction_mwh_hi", "MWh"), ("reduction_mw", "MW"), ("reduction_mw_lo", "MW"),
                              ("reduction_mw_hi", "MW"), ("reduction_pct", "pct"), ("temp_max_f", "degF"), ("train_days_as_hot", "count"), ("price_usd_mwh", "USD/MWh"),
                              ("value_usd", "USD"), ("value_usd_lo", "USD"), ("value_usd_hi", "USD")):
                add(EFFECTS, E, "alert_" + var if var == "hours" else var, ts, getattr(r, var, None), unit, "P1D")
            add(EFFECTS, E, "alert_first_hour", ts, min(a["hours"]), "hour", "P1D")
            add(EFFECTS, E, "alert_last_hour", ts, max(a["hours"]) + 1, "hour", "P1D")
            add(EFFECTS, E, "hours_assumed", ts, 1.0 if a["assumed"] else 0.0, "count", "P1D")
            add(EFFECTS, E, "basis_flex_alert", ts, 1.0 if a["basis"] == "flex_alert" else 0.0, "count", "P1D")
        for r in H.itertuples():
            ts = r.ts.strftime("%Y-%m-%dT%H:%M:%SZ")
            for var in ("actual_mw", "predicted_mw", "predicted_mw_lo", "predicted_mw_hi"):
                add(EFFECTS, E, var, ts, getattr(r, var), "MW", "PT1H")
            add(EFFECTS, E, "alert_hour", ts, 1.0 if r.alert else 0.0, "count", "PT1H")
        for r in Y.itertuples():
            ts = f"{r.year}-01-01T00:00:00Z"
            for var, unit in (("days", "count"), ("hours", "count"), ("reduction_mw", "MW"), ("reduction_mw_lo", "MW"), ("reduction_mw_hi", "MW"),
                              ("reduction_mwh", "MWh"), ("reduction_mwh_lo", "MWh"), ("reduction_mwh_hi", "MWh"), ("reduction_pct", "pct"),
                              ("value_usd", "USD"), ("value_usd_lo", "USD"), ("value_usd_hi", "USD")):
                add(EFFECTS, E, "year_" + var, ts, getattr(r, var, None), unit, "P1Y")
        T0 = f"{START}T00:00:00Z"
        for var, v in pooled.items():
            unit = {"days": "count", "hours": "count", "value_hours": "count", "reduction_pct": "pct"}.get(var, "MWh" if "mwh" in var else "USD" if "usd" in var else "MW")
            add(MODEL, M, "pooled_" + var, T0, v, unit, "")
        for var, v in metrics.items():
            add(MODEL, M, "oos_" + var, T0, v, {"days": "count", "hours": "count", "mape_pct": "pct"}.get(var, "MW"), "")
        # the pooled reduction less the model's own hot-day over-prediction (bias = actual less predicted, negative when the
        # model predicts too much): what is left if alert days carry the same error as the hottest non-alert days
        add(MODEL, M, "pooled_reduction_mw_net_of_bias", T0, pooled["reduction_mw"] + metrics["bias_mw"], "MW", "")
        add(MODEL, M, "oos_folds", T0, FOLDS, "count", "")
        for name, (mv, pv) in variants.items():
            for var in ("reduction_mw", "reduction_mw_lo", "reduction_mw_hi"):
                add(MODEL, M, f"variant_{name}_pooled_{var}", T0, pv[var], "MW", "")
            add(MODEL, M, f"variant_{name}_oos_bias_mw", T0, mv["bias_mw"], "MW", "")
            add(MODEL, M, f"variant_{name}_oos_rmse_mw", T0, mv["rmse_mw"], "MW", "")
        add(MODEL, M, "insample_rmse_mw", T0, ins["rmse_mw"], "MW", "")
        add(MODEL, M, "insample_mape_pct", T0, ins["mape_pct"], "pct", "")
        add(MODEL, M, "train_days", T0, len(eligible), "count", "")
        add(MODEL, M, "heldout_threshold_temp_f", T0, x["threshold"], "degF", "")
        add(MODEL, M, "bootstrap_replicates", T0, B, "count", "")
        alert_tmax = p[p["day"].isin(alerts["day"])].groupby("day")["temp_f"].max()
        add(MODEL, M, "alert_days_hotter_than_threshold", T0, int((alert_tmax >= x["threshold"]).sum()), "count", "")
        for c, wt in WEIGHTS.items():
            add(MODEL, M, f"station_weight_{c}", T0, wt, "ratio", "")
        for h, bvec in betas.items():
            for term, v in zip(TERMS, bvec):
                add(MODEL, M, f"coef_h{h:02d}_{term}", T0, v, "MW", "")
        hp = []
        for d, e in per_day_err.items():
            ts = f"{d}T00:00:00Z"
            add(MODEL, M, "heldout_error_mw", ts, e, "MW", "P1D")
            add(MODEL, M, "heldout_temp_max_f", ts, p[p["day"] == d]["temp_f"].max(), "degF", "P1D")
            pr = [prices.get((d, h)) for h in DEFAULT_HOURS]
            if all(v is not None for v in pr):
                add(MODEL, M, "heldout_price_usd_mwh", ts, float(np.mean(pr)), "USD/MWh", "P1D")
                hp.append(float(np.mean(pr)))
        if hp:
            add(MODEL, M, "heldout_price_mean_usd_mwh", T0, float(np.mean(hp)), "USD/MWh", "")
        s = pd.DataFrame(rows, columns=["table", "entity", "variable", "ts_utc", "value", "unit", "freq"])
        s = s.assign(geo="US-CA", market="", node="", source=SOURCE, source_url=METHOD_URL, retrieved_at=retrieved, vintage="")
        n_assumed = int(alerts["assumed"].sum())
        common = [
            f"Retrieved: {run_id} (UTC) by warehouse/derived/flex_alert_scorecard.py",
            f"Run log: warehouse/output/logs/flex_alert_scorecard_{run_id}.log",
            f"Source: {SOURCE} ERW derived table, Flex Alert scorecard method (docs/methods/flex_alert_scorecard.md), {METHOD_URL}",
            "Derived from: caiso_grid_emergencies; eia930_all_demand; noaa_isd_hourly; caiso_dam_alert_day_hub_prices",
            f"  demand: {x['dsrc']}",
            f"  weather: {x['wsrc']}; weights " + ", ".join(f"{c} {wt}" for c, wt in WEIGHTS.items()),
            f"  prices: {os.path.relpath(ppath, ROOT) if ppath else 'not held: values left out'} (mean of TH_SP15_GEN-APND and TH_NP15_GEN-APND, CAISO OASIS PRC_LMP DAM)",
            "License: public. A derived table inherits the most restrictive license of its inputs (Decision 23): EIA, NOAA (public domain), CAISO (credit the California ISO).",
            "Tier: derived. The estimate is the combined demand-side effect on alert days (the Flex Alert, paid programs such as DSGS and ELRP, "
            "utility calls, and on 2020-08-14 and 2020-08-15 rotating outages), not the Flex Alert message alone; the value is a wholesale lower bound.",
        ]
        heads = {
            EFFECTS: ["Energy Research Warehouse (ERW): the Flex Alert scorecard, per alert day, CAISO (derived, session 60)",
                      "Shape: series (docs/datastandard.md v0). P1D rows (ts_utc the Pacific day at 00:00:00Z): alert_hours (count), alert_first_hour and "
                      "alert_last_hour (local, the window's end), hours_assumed (1 where no notice gave hours: 16:00 to 21:00, else 0), basis_flex_alert (1 "
                      "where the hours are the Flex Alert's, else 0; unit count), actual_mwh and predicted_mwh over the alert hours, reduction_mwh and reduction_mw "
                      "(predicted less actual; positive is demand below the model) with _lo and _hi (90 percent interval), reduction_pct (of "
                      "predicted), temp_max_f (population-weighted), train_days_as_hot (training days whose highest weighted temperature was at least the day's: the model's support), price_usd_mwh (mean day-ahead hub price over the alert hours), value_usd "
                      "(reduction times price, summed) with _lo and _hi. PT1H rows (ts_utc the hour's start, local 12:00 to 23:00): actual_mw, "
                      "predicted_mw, predicted_mw_lo and _hi, alert_hour. P1Y rows (ts_utc the year's 1 January): year_<measure>.",
                      f"Alert days: {len(D)} with complete data, {D['day'].min()} to {D['day'].max()}; {n_assumed} with assumed hours. "
                      "CAISO's Grid Emergencies History Report ends 2025-04-30, so the 2025 season has none."],
            MODEL: ["Energy Research Warehouse (ERW): the Flex Alert scorecard's model, CAISO (derived, session 60)",
                    "Shape: series (docs/datastandard.md v0), entity erw:flex_alert_model. Rows at ts_utc 2018-07-01T00:00:00Z (freq blank): "
                    "pooled_<measure> (every alert hour of every alert day), oos_<metric> (the held-out hottest tenth of non-alert days, hours "
                    "16:00 to 21:00, five folds, each predicted by the model fitted on every other non-alert day: bias = mean of actual "
                    "less predicted), pooled_reduction_mw_net_of_bias (the pooled reduction plus that bias), variant_<name>_<measure> "
                    "(the five specifications compared: minimal, the prompt's CDH, CDH squared and the calendar; base, plus the 24 hours "
                    "before and the dew point; base_prev24sq; base_cdh_dew; chosen, every term; robustness rows with 200 replicates), "
                    "insample_<metric>, train_days, "
                    "heldout_threshold_temp_f, alert_days_hotter_than_threshold, bootstrap_replicates, station_weight_<station>, "
                    "coef_h<hour>_<term> (MW per unit of the term; the hour model's coefficients fitted on every non-alert day). "
                    "P1D rows: heldout_error_mw (a held-out day's mean error in hours 16 to 20, actual less predicted), heldout_temp_max_f, "
                    "heldout_price_usd_mwh."],
        }
        for table in (EFFECTS, MODEL):
            t = s[s["table"] == table][ip.SERIES_COLS]
            path = os.path.join(ip.OUT_DIR, table + ".csv")
            if os.path.exists(path):
                os.remove(path)  # rebuilt whole from its inputs each run
            ip.write_csv(t, table, heads[table] + common, log)
        ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                report="Flex Alert scorecard (warehouse/derived/flex_alert_scorecard.py)", report_url=METHOD_URL,
                                document_list="", license="public", tables=[EFFECTS, MODEL])])
        msg = (f"{len(D)} alert days; pooled {pooled['reduction_mw']:.0f} MW ({pooled['reduction_mw_lo']:.0f} to {pooled['reduction_mw_hi']:.0f}); "
               f"out-of-sample RMSE {metrics['rmse_mw']:.0f} MW, bias {metrics['bias_mw']:.0f} MW")
        log(msg)
        print(f"flex_alert_scorecard: {msg}")
        results.append(dict(table=EFFECTS, market="all", status="ok", detail=msg))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"flex_alert_scorecard FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=EFFECTS, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status("flex_alert_scorecard", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
