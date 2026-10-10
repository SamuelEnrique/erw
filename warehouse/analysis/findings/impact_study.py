"""Analysis: "Impact of X on Y" (session 181): a series before and after a date, against a control series.

A person picks a series, an event the warehouse already holds (or any date), a window of days and a control series.
The card shows, for the W days before the date and the W days from it:

    the series' mean before and after, and its change
    the control's mean before and after, and its change
    the difference between the two changes (a difference in differences)
    a regression with standard errors, on the days both series hold:

        d_t = a + b * after_t + e_t          d_t = series_t - control_t,  after_t = 1 from the date on, else 0

    b is the difference in differences. Its standard error is Newey-West (heteroskedasticity- and autocorrelation-
    consistent, Bartlett kernel) with L = floor(4 * (n / 100)^(2/9)) lags over the n days in their order, and the
    small-sample factor n / (n - 2), as Stata's `newey d after, lag(L)` computes it (statsmodels is not in the
    warehouse's environment: newey_west below is the whole computation, tested against a case worked by hand);
    p from Student's t on n - 2 degrees of freedom.

What the design carries: the difference between two changes over these days, and its error. It carries no cause. The
reading as an effect of the event needs the two series to have moved in parallel without it; that is not asserted
here, it is shown: a second chart draws the series minus the control over the 3 W days before the date, and the
table gives that gap's slope per day with its own Newey-West error.

Refused, with the reason on the card and nothing drawn: a control that is the series itself (or equal to it on every
day), a control in another unit, a date outside what the series or the control holds, fewer than MIN_OBS days on
either side, a date that does not exist.

Daily values: a daily table's own days (ERCOT's are local operating days); an hourly table's UTC days with at least 20
hours, as their mean. SERIES names each series' table. TABLES names only what the Roundup's runner restores; the
series' tables are read on the data machine, where the worker runs this.
"""

import datetime as dt
import math
import os
import re

import numpy as np
import pandas as pd

from findings_common import METHOD_URL, NoData, callout, do_destring, do_file, do_sentinels, fmt, now_iso, read_table

NAME = "impact_study"
TITLE = "IMPACT OF AN EVENT ON A SERIES"
KIND = "econometric"
CSV_NAME = "erw_2026_impact_event_control.csv"
TABLES = ["event_window_daily"]
MIN_OBS = 5            # days both series hold, on each side of the date
MIN_HOURS = 20         # an hourly series' UTC day counts when it holds this many hours
LEAD = 3               # the pre-period chart reaches LEAD * W days before the date


def _s(words, table, entity, variable, unit, hourly=False):
    return {"words": words, "table": table, "entity": entity, "variable": variable, "unit": unit, "hourly": hourly}


SERIES = {
    "ercot_north_rt": _s("ERCOT North Hub real-time price", "ercot_hub_prices_daily", "ercot:HB_NORTH", "rt_mean", "USD/MWh"),
    "ercot_north_da": _s("ERCOT North Hub day-ahead price", "ercot_hub_prices_daily", "ercot:HB_NORTH", "da_mean", "USD/MWh"),
    "ercot_houston_rt": _s("ERCOT Houston Hub real-time price", "ercot_hub_prices_daily", "ercot:HB_HOUSTON", "rt_mean", "USD/MWh"),
    "ercot_south_rt": _s("ERCOT South Hub real-time price", "ercot_hub_prices_daily", "ercot:HB_SOUTH", "rt_mean", "USD/MWh"),
    "ercot_west_rt": _s("ERCOT West Hub real-time price", "ercot_hub_prices_daily", "ercot:HB_WEST", "rt_mean", "USD/MWh"),
    "ercot_west_da": _s("ERCOT West Hub day-ahead price", "ercot_hub_prices_daily", "ercot:HB_WEST", "da_mean", "USD/MWh"),
    "nyiso_nyc_rt": _s("NYISO New York City real-time price", "iso_zone_prices_history", "nyiso:N.Y.C.", "lmp_rtm", "USD/MWh", True),
    "nyiso_nyc_da": _s("NYISO New York City day-ahead price", "iso_zone_prices_history", "nyiso:N.Y.C.", "lmp_dam", "USD/MWh", True),
    "nyiso_capital_da": _s("NYISO Capital day-ahead price", "iso_zone_prices_history", "nyiso:CAPITL", "lmp_dam", "USD/MWh", True),
    "nyiso_west_da": _s("NYISO West day-ahead price", "iso_zone_prices_history", "nyiso:WEST", "lmp_dam", "USD/MWh", True),
    "nyiso_longil_da": _s("NYISO Long Island day-ahead price", "iso_zone_prices_history", "nyiso:LONGIL", "lmp_dam", "USD/MWh", True),
    "spp_south_da": _s("SPP South Hub day-ahead price", "iso_zone_prices_history", "spp:SPPSOUTH_HUB", "lmp_dam", "USD/MWh", True),
    "caiso_zp26_da": _s("CAISO ZP26 day-ahead price", "iso_zone_prices_history", "caiso:TH_ZP26_GEN-APND", "lmp_dam", "USD/MWh", True),
    "henry_hub": _s("Henry Hub natural gas spot price", "eia_fuel_spot_prices", "eia:henry_hub", "spot_price", "USD/MMBtu"),
    "wti": _s("WTI crude spot price at Cushing", "eia_fuel_spot_prices", "eia:wti_cushing", "spot_price", "USD/bbl"),
    "brent": _s("Brent crude spot price", "eia_fuel_spot_prices", "eia:brent", "spot_price", "USD/bbl"),
    "demand_ercot": _s("ERCOT daily demand", "eia930_daily_demand", "eia930:ERCO", "demand_mwh", "MWh"),
    "demand_caiso": _s("CAISO daily demand", "eia930_daily_demand", "eia930:CISO", "demand_mwh", "MWh"),
    "demand_pjm": _s("PJM daily demand", "eia930_daily_demand", "eia930:PJM", "demand_mwh", "MWh"),
    "demand_miso": _s("MISO daily demand (EIA-930)", "eia930_daily_demand", "eia930:MISO", "demand_mwh", "MWh"),
    "demand_nyiso": _s("NYISO daily demand", "eia930_daily_demand", "eia930:NYIS", "demand_mwh", "MWh"),
    "demand_isone": _s("ISO-NE daily demand", "eia930_daily_demand", "eia930:ISNE", "demand_mwh", "MWh"),
    "demand_spp": _s("SPP daily demand", "eia930_daily_demand", "eia930:SWPP", "demand_mwh", "MWh"),
}
# the events the warehouse holds: the first day of each event's window in event_window_daily's header (docs/methods/events.md)
EVENTS = {
    "uri_2021": ("Winter Storm Uri", "2021-02-07"),
    "covid_2020": ("the first COVID-19 spring", "2020-03-01"),
    "caiso_heat_2020": ("the August 2020 heat wave in CAISO", "2020-08-10"),
    "caiso_heat_2022": ("the September 2022 heat wave in CAISO", "2022-08-31"),
    "elliott_2022": ("Winter Storm Elliott", "2022-12-19"),
    "ercot_heat_2023": ("the summer 2023 heat in ERCOT", "2023-08-01"),
    "cold_2025": ("the January 2025 cold", "2025-01-17"),
    "east_heat_2025": ("the June 2025 heat in the east", "2025-06-20"),
}
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
INPUTS = {
    "series": {"label": "Series", "default": "ercot_north_rt", "choices": list(SERIES), "words": {k: v["words"] for k, v in SERIES.items()}},
    "control": {"label": "Control series", "default": "nyiso_nyc_rt", "choices": list(SERIES), "words": {k: v["words"] for k, v in SERIES.items()}},
    "event": {"label": "Event, or a date", "default": "uri_2021", "choices": list(EVENTS) + ["date"],
              "words": {**{k: f"{v[0]} (from {v[1]})" for k, v in EVENTS.items()}, "date": "A date I pick (year, month, day)"}},
    "year": {"label": "Year (when a date is picked)", "default": 2024, "choices": list(range(2015, 2027))},
    "month": {"label": "Month", "default": 5, "choices": list(range(1, 13)), "words": {str(i + 1): m for i, m in enumerate(MONTHS)}},
    "day": {"label": "Day", "default": 15, "choices": list(range(1, 32))},
    "window": {"label": "Window: days before and after", "default": 14, "choices": [7, 14, 28, 56], "words": {"7": "7 days", "14": "14 days", "28": "28 days", "56": "56 days"}},
}


def series_for(table, entity, variable):
    """The key of the series held under (table, entity, variable), or None."""
    for k, v in SERIES.items():
        if (v["table"], v["entity"], v["variable"]) == (table, entity, variable):
            return k
    return None


def default_control(key):
    """A control for a series when nobody picked one (the scanner's full card): the first other series in the same
    unit on another grid (the entity's own name differs), the same variable where one exists. None when none fits."""
    s = SERIES[key]
    grid = lambda v: v["entity"].split(":")[-1][:4] if v["entity"].startswith("eia930:") else v["entity"].split(":")[0]  # noqa: E731
    others = [k for k, v in SERIES.items() if k != key and v["unit"] == s["unit"] and grid(v) != grid(s)]
    same = [k for k in others if SERIES[k]["variable"].split("_")[-1][:2] == s["variable"].split("_")[-1][:2]]
    return (same or others or [None])[0]


def day_words(iso):
    d = dt.date.fromisoformat(iso)
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


def newey_lags(n):
    return int(math.floor(4 * (n / 100.0) ** (2.0 / 9.0)))


def newey_west(y, X, lags):
    """Ordinary least squares with Newey-West standard errors: Bartlett weights 1 - j / (lags + 1), the observations in
    their order, the factor n / (n - k). Returns (coefficients, standard errors, residuals)."""
    y, X = np.asarray(y, float), np.asarray(X, float)
    n, k = X.shape
    bread = np.linalg.inv(X.T @ X)
    beta = bread @ X.T @ y
    e = y - X @ beta
    Z = X * e[:, None]
    S = Z.T @ Z
    for j in range(1, min(lags, n - 1) + 1):
        w = 1.0 - j / (lags + 1.0)
        G = Z[j:].T @ Z[:-j]
        S = S + w * (G + G.T)
    V = (n / (n - k)) * bread @ S @ bread
    return beta, np.sqrt(np.diag(V)), e


def fit(y, X):
    """The regression as the card states it: coefficients, Newey-West errors, t, p, n, lags, R2."""
    from scipy import stats
    y, X = np.asarray(y, float), np.asarray(X, float)
    n, k = X.shape
    L = newey_lags(n)
    beta, se, e = newey_west(y, X, L)
    t = np.where(se > 0, beta / np.where(se > 0, se, 1), np.nan)
    p = 2 * stats.t.sf(np.abs(t), n - k)
    tot = float(((y - y.mean()) ** 2).sum())
    return {"coef": [float(b) for b in beta], "se": [float(s) for s in se], "p": [float(x) for x in p], "n": int(n), "lags": L,
            "r2": 1 - float((e ** 2).sum()) / tot if tot > 0 else 0.0}


def daily(spec, in_dir=None):
    """A series' daily values as {day: value}: the table's own days, or an hourly table's UTC days with MIN_HOURS hours."""
    d = read_table(spec["table"], in_dir, usecols=["entity", "variable", "ts_utc", "value"],
                   keep=lambda c: (c["entity"] == spec["entity"]) & (c["variable"] == spec["variable"]))
    if d.empty:
        raise NoData(f"{spec['table']} holds no row of {spec['entity']} {spec['variable']}")
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    d = d.dropna(subset=["value"])
    d["day"] = d["ts_utc"].str[:10]
    g = d.groupby("day")["value"].agg(["mean", "count"])
    if spec["hourly"]:
        g = g[g["count"] >= MIN_HOURS]
    return g["mean"].to_dict()


def the_date(params):
    """(the date as YYYY-MM-DD or None, its words, why not)."""
    event = str(params.get("event", INPUTS["event"]["default"]))
    if event in EVENTS:
        return EVENTS[event][1], f"{day_words(EVENTS[event][1])}, the first day of {EVENTS[event][0]}", ""
    try:
        d = dt.date(int(params.get("year", 2024)), int(params.get("month", 5)), int(params.get("day", 15)))
    except (TypeError, ValueError):
        return None, "", f"The date {params.get('year')}-{params.get('month')}-{params.get('day')} does not exist: pick a day the month has."
    return d.isoformat(), day_words(d.isoformat()), ""


def compute(params, in_dir=None):
    sk, ck = str(params.get("series", INPUTS["series"]["default"])), str(params.get("control", INPUTS["control"]["default"]))
    W = int(params.get("window", 14))
    if sk not in SERIES or ck not in SERIES:
        raise ValueError("no such series")
    s, c = SERIES[sk], SERIES[ck]
    date, date_words, why_not = the_date(params)
    meta = {"series": sk, "control": ck, "series_words": s["words"], "control_words": c["words"], "unit": s["unit"], "control_unit": c["unit"],
            "event": str(params.get("event", INPUTS["event"]["default"])), "date": date, "date_words": date_words, "window": W,
            "series_table": s["table"], "control_table": c["table"], "refusal": why_not, "min_obs": MIN_OBS}
    if why_not:
        return [], meta
    if sk == ck:
        meta["refusal"] = f"The control is the series itself ({s['words']}): the difference is zero by construction. Pick another control."
        return [], meta
    if s["unit"] != c["unit"]:
        meta["refusal"] = (f"The series is in {s['unit']} and the control in {c['unit']}: a difference between them is not a quantity. "
                           "Pick a control in the same unit.")
        return [], meta
    ys, cs = daily(s, in_dir), daily(c, in_dir)
    meta.update({"series_first": min(ys), "series_last": max(ys), "control_first": min(cs), "control_last": max(cs), "series_days_held": len(ys), "control_days_held": len(cs)})
    d0 = dt.date.fromisoformat(date)
    first, last = d0 - dt.timedelta(days=LEAD * W), d0 + dt.timedelta(days=W - 1)
    rows = []
    for i in range((last - first).days + 1):
        day = first + dt.timedelta(days=i)
        k = day.isoformat()
        y, x = ys.get(k), cs.get(k)
        if y is None and x is None:
            continue
        t = (day - d0).days
        rows.append({"day": k, "t": t, "period": "after" if t >= 0 else ("before" if t >= -W else "lead"), "after": int(t >= 0), "in_window": int(t >= -W),
                     "series_value": y, "control_value": x, "diff": (y - x) if y is not None and x is not None else None})
    both = [r for r in rows if r["in_window"] and r["diff"] is not None]
    n_pre, n_post = sum(1 for r in both if not r["after"]), sum(1 for r in both if r["after"])
    for name, held, a, b in ((s["words"], ys, meta["series_first"], meta["series_last"]), (c["words"], cs, meta["control_first"], meta["control_last"])):
        if date < a or date > b:
            meta["refusal"] = f"{day_words(date)} is outside what {name} holds: it runs from {day_words(a)} to {day_words(b)}."
            return [], meta
    if n_pre < MIN_OBS or n_post < MIN_OBS:
        meta["refusal"] = (f"Too few days to compare: {n_pre} before {day_words(date)} and {n_post} from it are held by both series, and {MIN_OBS} are needed "
                           f"on each side. {s['words']} runs from {day_words(meta['series_first'])} to {day_words(meta['series_last'])}; "
                           f"{c['words']} from {day_words(meta['control_first'])} to {day_words(meta['control_last'])}.")
        return [], meta
    if all(r["diff"] == 0 for r in both):
        meta["refusal"] = f"The control equals the series on every one of the {len(both)} days: there is nothing to compare. Pick another control."
        return [], meta
    return rows, meta


def numbers_from_rows(rows, params=None):
    """Every number of the card, from the CSV's rows alone."""
    if not rows:
        return {}
    win = [r for r in rows if r["in_window"] == 1 and r["diff"] is not None]
    pre, post = [r for r in win if r["after"] == 0], [r for r in win if r["after"] == 1]
    m = lambda rs, k: float(np.mean([r[k] for r in rs]))  # noqa: E731
    n = {"n_pre": len(pre), "n_post": len(post), "n": len(win),
         "series_pre": m(pre, "series_value"), "series_post": m(post, "series_value"), "control_pre": m(pre, "control_value"), "control_post": m(post, "control_value")}
    n["series_change"] = n["series_post"] - n["series_pre"]
    n["control_change"] = n["control_post"] - n["control_pre"]
    n["did"] = n["series_change"] - n["control_change"]
    y = np.array([r["diff"] for r in win], float)
    X = np.column_stack([np.ones(len(win)), np.array([r["after"] for r in win], float)])
    f = fit(y, X)
    n.update({"reg_const": f["coef"][0], "reg_const_se": f["se"][0], "reg_const_p": f["p"][0], "reg_did": f["coef"][1], "reg_did_se": f["se"][1], "reg_did_p": f["p"][1],
              "reg_n": f["n"], "reg_lags": f["lags"], "reg_r2": f["r2"]})
    n["did_low"], n["did_high"] = n["reg_did"] - 1.96 * n["reg_did_se"], n["reg_did"] + 1.96 * n["reg_did_se"]
    lead = [r for r in rows if r["after"] == 0 and r["diff"] is not None]
    n["n_lead"] = len(lead)
    if len(lead) >= MIN_OBS + 2:
        g = fit(np.array([r["diff"] for r in lead], float), np.column_stack([np.ones(len(lead)), np.array([r["t"] for r in lead], float)]))
        n.update({"pre_slope": g["coef"][1], "pre_slope_se": g["se"][1], "pre_slope_p": g["p"][1], "pre_lags": g["lags"], "pre_r2": g["r2"]})
    else:
        n.update({"pre_slope": None, "pre_slope_se": None, "pre_slope_p": None, "pre_lags": None, "pre_r2": None})
    for k in ("series_pre", "series_post", "control_pre", "control_post", "series_change", "control_change", "did", "reg_did", "reg_const", "pre_slope", "did_low", "did_high"):
        n[k + "_abs"] = abs(n[k]) if n[k] is not None else None      # a callout prints a size and says the direction in words
    return n


def money(v, unit):
    """A value in its unit as the sentence prints it: 'USD 1,234.56 per MWh', '1,234 MWh'."""
    if v is None:
        return "not held"
    nd = 0 if abs(v) >= 10000 else 2
    if unit.startswith("USD"):
        return ("minus " if v < 0 else "") + f"USD {fmt(abs(v), nd)}" + (f" per {unit.split('/', 1)[1]}" if "/" in unit else "")
    return ("minus " if v < 0 else "") + f"{fmt(abs(v), nd)} {unit}"


def moved(v, unit):
    return "no change" if v == 0 else f"{'a rise' if v > 0 else 'a fall'} of {money(abs(v), unit)}"


def in_words(n, meta):
    """The effect in plain words, written by code from the numbers. States the difference and its error; no cause."""
    u, W = meta["unit"], meta["window"]
    beyond = abs(n["reg_did"]) > 1.96 * n["reg_did_se"]
    return (f"In the {W} days from {day_words(meta['date'])}, {meta['series_words']} averaged {money(n['series_post'], u)} against {money(n['series_pre'], u)} in the {W} days before, "
            f"{moved(n['series_change'], u)}. The control, {meta['control_words']}, went from {money(n['control_pre'], u)} to {money(n['control_post'], u)}, {moved(n['control_change'], u)}. "
            f"The difference between the two changes is {money(n['did'], u)}, standard error {money(n['reg_did_se'], u)} (Newey-West, {n['reg_lags']} lags, {n['reg_n']} days). "
            + ("That difference is more than 1.96 standard errors from zero. " if beyond else "That difference is within 1.96 standard errors of zero: no difference beyond the error. ")
            + "This is the difference between two changes over these days and its error; it does not say what produced it.")


def chart(rows, meta):
    win = [r for r in rows if r["in_window"] == 1]
    return {"kind": "flag_line", "x": [r["day"] for r in win], "x_label": f"day; the {meta['window']} days from {day_words(meta['date'])} are marked",
            "series": [{"name": meta["series_words"], "type": "line", "unit": meta["unit"], "values": [r["series_value"] for r in win]},
                       {"name": f"control: {meta['control_words']}", "type": "line", "unit": meta["unit"], "values": [r["control_value"] for r in win]}],
            "mark_area": {"from": meta["date"], "to": win[-1]["day"], "label": "after"}, "y_left_label": meta["unit"], "decimals": 2}


def pre_chart(rows, meta, n):
    lead = [r for r in rows if r["after"] == 0]
    return {"kind": "flag_line", "x": [r["day"] for r in lead], "x_label": f"the {LEAD * meta['window']} days before {day_words(meta['date'])}: the series minus the control",
            "series": [{"name": f"{meta['series_words']} minus {meta['control_words']}", "type": "line", "unit": meta["unit"], "values": [r["diff"] for r in lead]}],
            "ref_lines": [{"name": f"mean of the {meta['window']} days before", "value": round(n["reg_const"], 6)}], "y_left_label": meta["unit"], "decimals": 2}


def card(rows, params, meta):
    u, W = meta["unit"], meta["window"]
    words = {"series": meta["series_words"], "control": meta["control_words"], "date": meta["date_words"] or "no date", "window": f"{W} days before and after"}
    head = [f"Energy Research Warehouse (ERW): analysis {NAME}: {TITLE}", f"Computed {now_iso()} by warehouse/analysis/findings/{NAME}.py; method {METHOD_URL}",
            "Rows: one per day from 3 windows before the date to the window's last day: t (days from the date); period (lead or before or after); after; in_window; "
            "series_value; control_value; diff (series minus control)",
            f"Series: {meta['series_words']} ({meta['series_table']}); control: {meta['control_words']} ({meta['control_table']}); date {meta['date']}; window {W} days"]
    head = [h.replace(",", ";") for h in head]          # no comma in a comment line: the do-file reads the names from line 5
    base = {"id": NAME, "title": TITLE, "kind": KIND, "params": {k: params.get(k, v["default"]) for k, v in INPUTS.items()}, "inputs_words": words,
            "tables": sorted({meta["series_table"], meta["control_table"]}), "computed_at": now_iso(), "method": METHOD_URL, "csv_header": head,
            "source_line": f"Source: ERW tables {meta['series_table']}" + (f" and {meta['control_table']}" if meta["control_table"] != meta["series_table"] else "") + "."}
    if meta.get("refusal"):
        return {**base, "subtitle": "Not computed: the request cannot be answered as asked", "refusal": meta["refusal"], "chart": {"kind": "none", "x": [], "x_label": "", "series": []},
                "callouts": [], "why": "", "footnote": f"Nothing was drawn and no number was computed. The rule: at least {MIN_OBS} days held by both series on each side of the date, "
                "a control that is another series in the same unit, a date inside what both hold. Method: docs/methods/automated_analysis_findings.md, the impact study.", "numbers": {}}
    n = numbers_from_rows(rows, params)
    sub = f"{meta['series_words']}: {moved(n['series_change'], u)} around {day_words(meta['date'])}; the control: {moved(n['control_change'], u)}"
    side = lambda v: "higher" if v >= 0 else "lower"  # noqa: E731
    pre_words = (f"Before the date, over the {n['n_lead']} days before it (the card's second chart on the site), the gap between the two moved by {fmt(n['pre_slope'], 4)} {u} a day "
                 f"(Newey-West standard error {fmt(n['pre_slope_se'], 4)}, {n['pre_lags']} lags): the chart shows whether they moved in parallel, the card does not assert it. "
                 if n["pre_slope"] is not None else "Too few days are held before the date to fit the gap's slope; the second chart shows what is held. ")
    foot = (f"Data: {meta['series_words']} from {meta['series_table']} and {meta['control_words']} from {meta['control_table']}, daily (a daily table's own days; an hourly "
            f"table's UTC days with at least {MIN_HOURS} hours, as their mean). Window: the {W} days before {meta['date']} and the {W} days from it; {n['n_pre']} and {n['n_post']} "
            f"days are held by both series. Before and after are means over those days. The difference against the control is a difference in differences: the series' change "
            f"minus the control's. Regression, on the {n['reg_n']} days: (series minus control) = a + b * after + e, by least squares; b = {fmt(n['reg_did'], 4)}, "
            f"standard error {fmt(n['reg_did_se'], 4)}, Newey-West (heteroskedasticity- and autocorrelation-consistent, Bartlett kernel) with L = floor(4 * (n / 100)^(2/9)) = "
            f"{n['reg_lags']} lags over the days in their order and the factor n / (n - 2), as Stata's newey; p = {fmt(n['reg_did_p'], 4)} from Student's t on {n['reg_n'] - 2} "
            f"degrees of freedom; 95 percent interval {fmt(n['did_low'], 2)} to {fmt(n['did_high'], 2)}. {pre_words}"
            "The design carries a difference and its error over these days, not a cause: anything else that changed for one series and not the other in the window is inside b.")
    table = {"columns": ["Term", f"Coefficient, {u}", "SE (Newey-West)", "p", "Days", "R2"],
             "rows": [{"measure": "After the date: the difference in differences (b)", "coef_per_gw": n["reg_did"], "se": n["reg_did_se"], "p": n["reg_did_p"], "n": n["reg_n"], "r2": n["reg_r2"]},
                      {"measure": "Constant: series minus control before the date (a)", "coef_per_gw": n["reg_const"], "se": n["reg_const_se"], "p": n["reg_const_p"], "n": n["reg_n"], "r2": n["reg_r2"]}],
             "in_words": in_words(n, meta)}
    if n["pre_slope"] is not None:
        table["rows"].append({"measure": f"Before the date only: the gap's slope per day over {n['n_lead']} days", "coef_per_gw": n["pre_slope"], "se": n["pre_slope_se"],
                              "p": n["pre_slope_p"], "n": n["n_lead"], "r2": n["pre_r2"]})
    return {**base, "subtitle": sub,
            "chart": chart(rows, meta),
            "more_charts": [{"title": "Before the date: did the two move in parallel?", "spec": pre_chart(rows, meta, n)}],
            "callouts": [callout(f"{meta['series_words']}, {u}", f"{W} days before", fmt(n["series_pre"], 2), f"{W} days from {meta['date']}", fmt(n["series_post"], 2)),
                         callout(f"Control: {meta['control_words']}, {u}", f"{W} days before", fmt(n["control_pre"], 2), f"{W} days from {meta['date']}", fmt(n["control_post"], 2)),
                         callout(f"Difference against the control, {u}", "difference in differences", f"{fmt(n['did_abs'], 2)} {side(n['did'])}", "standard error (Newey-West)", fmt(n["reg_did_se"], 2))],
            "why": in_words(n, meta), "effect_table": table, "footnote": foot, "numbers": n,
            # the CSV's rows and the do-file ride in the card: a card asked for on the site is read from its queue row,
            # where no file is, and its downloads are made from these
            "rows": rows, "csv_name": csv_name(params), "do_file": stata(params)}


def csv_name(params):
    """The CSV's name for these inputs, as run_finding names it (the default card's is CSV_NAME)."""
    parts = [f"{k}-{re.sub(r'[^A-Za-z0-9.]+', '_', str(params[k]))}" for k, spec in INPUTS.items() if k in (params or {}) and str(params[k]) != str(spec["default"])]
    return CSV_NAME if not parts else f"{CSV_NAME[:-4]}__{'__'.join(parts)}.csv"


def stata(params):
    V = ["t", "after", "in_window", "series_value", "control_value", "diff"]
    return do_file([
        f"* ERW analysis {NAME}: {TITLE}. Reproduces the card's means and its regression from the CSV.",
        "* The CSV begins with four comment lines: the names are read from line 5 and the data from line 6.",
        "clear all",
        f'import delimited "{csv_name(params)}", varnames(5) rowrange(6) stringcols(_all) clear',
        *do_destring(V),
        *do_sentinels(V),
        "keep if in_window == 1 & diff < .",
        "tabstat series_value control_value diff, by(after) statistics(mean n) format(%12.4f)",
        "generate obs = _n",
        "tsset obs",
        "local lags = floor(4 * (_N / 100)^(2 / 9))",
        "newey diff after, lag(`lags')",
    ])


SOURCE_PATH = os.path.abspath(__file__)
