#!/usr/bin/env python3
"""The scanner (session 181): a daily look over every public table with a time axis, for five kinds of news.

Energy Research Warehouse (ERW). Method: docs/methods/automated_analysis_scanner.md. Thresholds: ONE file,
warehouse/config/scanner.yaml (every key commented there).

    python warehouse/analysis/findings/findings_scanner.py --in-dir C:/Users/lossa/Documents/erw/warehouse/output --out-dir runs/x
    python warehouse/analysis/findings/findings_scanner.py --daily            # the data machine's daily soft step: scan, keep, load
    python warehouse/analysis/findings/findings_scanner.py --request          # the runner's daily soft step: queue today's scan
    python warehouse/analysis/findings/findings_scanner.py --load runs/x/drafts.json [--dry-run]

What it flags, each against a threshold of scanner.yaml:
    record      the newest value above (below) the series' whole held history, a record that had stood
    negative    a price below zero at a hub or zone that had none in the prior year
    spike       the newest value beyond a multiple of the 99th percentile of the series' prior years
    weekly      the change of the newest 7 days on the 7 before, outside its five-year range
    pair        the residual of a regression between two series that normally move together, beyond its own history

The tables are not listed by hand: every table of warehouse/metadata/coverage.csv whose license is public and whose
columns are the series shape (entity, variable, ts_utc, value) is read; a series is one value of the key columns.
Sub-daily series are scanned by UTC day (mean, minimum, maximum). Guards (never flagged): a paused publisher's series
(paused_sources.csv), a table in known_gaps.csv, dates inside a known fault (known_data_faults.csv), a revised or
partial newest day (settle days, the day's count of intervals), a unit change, a change of source inside the history.

A flag is reproducible: it stores the table, the series key, the dates, the values, the threshold it crossed (name,
value and the configuration keys behind it) and the scanner's version. Each flag becomes a DRAFT finding card computed
by code: a chart of the series with the flagged point and its band or record marked, callouts (the number, its
comparison, the date) and a method footnote. No paragraph, no model. Drafts wait in public.scanner_drafts (migration
029) for a person at /internal/findings; nothing reaches /analysis before it is approved there.

Exit 0 written, 1 failed, 2 bad input, ERW_SKIP_EXIT (75) when the daily step cannot run here, with its reason.
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import findings_common as common  # noqa: E402

CONFIG = os.path.join(ROOT, "warehouse", "config", "scanner.yaml")
META_DIR = os.path.join(ROOT, "warehouse", "metadata")
METHOD = "docs/methods/automated_analysis_scanner.md"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/" + METHOD
STD = ["entity", "variable", "ts_utc", "value"]
RULES = {"record": "RECORD", "negative": "NEGATIVE PRICE WHERE THERE WAS NONE", "spike": "SPIKE BEYOND ITS OWN HISTORY",
         "weekly": "WEEKLY CHANGE OUTSIDE ITS FIVE-YEAR RANGE", "pair": "TWO SERIES PARTED"}
DRAFT_TABLE = "scanner_drafts"
REQUEST_FINDING = "scanner_daily"
D = "datetime64[D]"


def load_config(path=None):
    import yaml
    with open(path or CONFIG, encoding="utf-8") as f:
        return yaml.safe_load(f)


def grain_of(freq):
    """(grain, sub_daily) of a freq value: PT5M, PT15M and PT1H are scanned by day."""
    f = (freq or "").upper()
    if f.startswith("PT"):
        return "daily", True
    return {"P1D": "daily", "P1W": "weekly", "P7D": "weekly", "P1M": "monthly", "P1Y": "yearly"}.get(f), False


def grain_from_spacing(g):
    """The grain of a series whose freq column is empty, from its own days: several values a day is sub-daily; else
    the median spacing of its days (1 day, 7, a month, a year). None when it has fewer than 4 days or fits none."""
    if len(g) < 4:
        return None, False
    if float(np.median(g["count"])) > 1:
        return "daily", True
    gap = float(np.median(np.diff(np.sort(g["day"].to_numpy().astype(D))).astype(int)))
    for name, lo, hi in (("daily", 1, 1), ("weekly", 7, 7), ("monthly", 28, 31), ("yearly", 365, 366)):
        if lo <= gap <= hi:
            return name, False
    return None, False


def first_match(patterns, name):
    for pat, val in (patterns or {}).items():
        if re.search(pat, name):
            return val
    return None


def robust_sigma(x):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    if not len(x):
        return 0.0
    s = 1.4826 * float(np.median(np.abs(x - np.median(x))))
    return s if s > 0 else float(np.std(x))


# ---------------------------------------------------------------------------------------------------------------------
# what is scanned, and the guards' inputs
# ---------------------------------------------------------------------------------------------------------------------
def table_columns(path):
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if not ln.startswith("#"):
                return ln.rstrip("\r\n").split(",")
    return []


def read_meta_csv(path):
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path, dtype=str, keep_default_na=False, comment="#")


def paused_patterns(meta_dir):
    d = read_meta_csv(os.path.join(meta_dir, "paused_sources.csv"))
    return [(r["scope"], re.compile(r["match"])) for _, r in d.iterrows() if r.get("match")] if len(d) else []


def known_gaps(meta_dir):
    d = read_meta_csv(os.path.join(meta_dir, "known_gaps.csv"))
    return set(d["table"]) if len(d) else set()


def known_faults(in_dir):
    """[(fault id, {tables}, first day or None, last day or None)] from known_data_faults.csv. A fault without a first
    day covers its tables whole; one with a first day and no last is open-ended."""
    p = os.path.join(in_dir, "known_data_faults.csv")
    if not os.path.exists(p):
        return []
    d = pd.read_csv(p, dtype=str, keep_default_na=False, comment="#")
    out = []
    for _, r in d.iterrows():
        tables = {t.strip() for t in r.get("entity_ids", "").split(";") if t.strip()}
        if tables:
            out.append((r["event_id"], tables, r.get("x_first") or None, r.get("x_last") or None))
    return out


def fault_for(faults, table, first, last):
    """The known fault that covers [first, last] of a table, or None."""
    for fid, tables, a, b in faults:
        if table not in tables:
            continue
        if a is None:
            return fid
        if last >= a and (b is None or first <= b):
            return fid
    return None


def public_time_tables(cfg, in_dir, meta_dir):
    """(tables to scan as [(name, columns)], [(name, reason)] not scanned, the count of public tables that are not
    series). From coverage.csv and each file's own columns; no list by hand."""
    cov = read_meta_csv(os.path.join(meta_dir, "coverage.csv"))
    gaps = known_gaps(meta_dir) if cfg.get("skip_known_gaps", True) else set()
    scan, skipped, not_series = [], [], []
    for _, r in cov.iterrows():
        if r.get("license") != "public":
            continue
        name = r["table"]
        p = os.path.join(in_dir, name + ".csv")
        if not os.path.exists(p):
            skipped.append((name, "the table is not on this machine"))
            continue
        cols = table_columns(p)
        if not all(c in cols for c in STD):
            not_series.append(name)
            continue
        why = first_match(cfg.get("exclude_tables"), name)
        if why:
            skipped.append((name, why))
        elif r.get("interval") in ("snapshot", "event"):
            skipped.append((name, f"interval {r.get('interval')}: no running time axis"))
        elif name in gaps:
            skipped.append((name, "a known gap (known_gaps.csv): the scheduled run cannot refresh it"))
        else:
            scan.append((name, cols))
    return scan, skipped, not_series


# ---------------------------------------------------------------------------------------------------------------------
# reading a table into daily series
# ---------------------------------------------------------------------------------------------------------------------
class Series:
    __slots__ = ("table", "key", "key_str", "days", "v", "lo", "hi", "unit", "grain", "sub", "source", "note")

    def label(self):
        k = self.key
        m = f" ({k['market']})" if k.get("market") else ""
        extra = "".join(f", {c} {k[c]}" for c in k if c not in ("entity", "variable", "market", "node", "freq") and k[c])
        return f"{k.get('entity', '')} {k.get('variable', '')}{m}{extra}"


def read_series(table, cols, in_dir, cfg, stats):
    """Every series of a table as daily arrays. stats counts what is left out and why."""
    key = [c for c in cfg["key_columns"] + cfg["key_extra_columns"] if c in cols]
    use = key + ["ts_utc", "value"] + [c for c in ("unit", "source") if c in cols]
    parts, units, srcs = [], [], []
    for ch in pd.read_csv(os.path.join(in_dir, table + ".csv"), comment="#", dtype=str, usecols=use, chunksize=common.CHUNK, keep_default_na=False):
        ch["value"] = pd.to_numeric(ch["value"], errors="coerce")
        ch = ch[ch["value"].notna() & (ch["ts_utc"].str.len() >= 10)]
        if ch.empty:
            continue
        ch = ch.assign(day=ch["ts_utc"].str.slice(0, 10))
        parts.append(ch.groupby(key + ["day"], sort=False)["value"].agg(["sum", "count", "min", "max"]).reset_index())
        if "unit" in use:
            units.append(ch[key + ["unit"]].drop_duplicates())
        if "source" in use:
            srcs.append(ch.groupby(key + ["source"], sort=False)["day"].min().reset_index())
    if not parts:
        return []
    d = pd.concat(parts, ignore_index=True).groupby(key + ["day"], sort=False).agg(sum=("sum", "sum"), count=("count", "sum"), min=("min", "min"), max=("max", "max")).reset_index()
    unit_n, unit_of, src_start = {}, {}, {}
    if units:
        u = pd.concat(units, ignore_index=True).drop_duplicates()
        for k, g in u.groupby(key, sort=False):
            unit_n[k], unit_of[k] = len(g), g["unit"].iloc[0]
    if srcs:
        s = pd.concat(srcs, ignore_index=True).groupby(key + ["source"], sort=False)["day"].min().reset_index()
        for k, g in s.groupby(key, sort=False):
            g = g.sort_values("day")
            src_start[k] = (g["source"].iloc[-1], g["day"].iloc[-1] if len(g) > 1 else None)
    out = []
    for k, g in d.groupby(key, sort=False):
        k = k if isinstance(k, tuple) else (k,)
        kd = dict(zip(key, k))
        stats["series_seen"] += 1
        grain, sub = grain_of(kd.get("freq"))
        if grain is None:
            grain, sub = grain_from_spacing(g)
        if grain is None:
            stats["no_grain"] += 1
            stats.setdefault("no_grain_tables", {})
            stats["no_grain_tables"][table] = stats["no_grain_tables"].get(table, 0) + 1
            continue
        if cfg.get("skip_on_unit_change", True) and unit_n.get(k, 1) > 1:
            stats["unit_change"] += 1
            continue
        g = g.sort_values("day")
        cnt = g["count"].to_numpy()
        if sub:
            g = g[cnt >= cfg["partial_day_min_share"] * np.median(cnt)]
        elif cnt.max() > 1:
            stats["key_incomplete"] += 1      # two values on one day of a daily series: the key does not name one series
            continue
        src, changed = src_start.get(k, ("", None))
        note = ""
        if changed and cfg.get("history_from_last_source_change", True):
            g = g[g["day"] >= changed]
            note = f"history from {changed}, when the source became {src}"
            stats["source_change"] += 1
        if len(g) < 3:
            stats["too_short"] += 1
            continue
        s = Series()
        s.table, s.key, s.key_str = table, kd, "|".join(f"{c}={kd[c]}" for c in key)
        s.days = g["day"].to_numpy().astype(D)
        s.v = (g["sum"] / g["count"]).to_numpy(float)
        s.lo, s.hi = g["min"].to_numpy(float), g["max"].to_numpy(float)
        s.unit, s.grain, s.sub, s.source, s.note = unit_of.get(k, ""), grain, sub, src, note
        out.append(s)
    return out


# ---------------------------------------------------------------------------------------------------------------------
# the rules
# ---------------------------------------------------------------------------------------------------------------------
def settle_days(cfg, table):
    v = first_match(cfg.get("settle_days"), table)
    return int(v if v is not None else cfg["settle_days_default"])


def period_end(days, grain):
    """The last day of each point's period: a month's or a year's last day; a daily or a weekly point is its own day
    (the weekly tables hold survey days: EIA's Monday prices, the CFTC's Tuesday positions, final when published)."""
    if grain == "monthly":
        return (days.astype("datetime64[M]") + np.timedelta64(1, "M")).astype(D) - np.timedelta64(1, "D")
    if grain == "yearly":
        return (days.astype("datetime64[Y]") + np.timedelta64(1, "Y")).astype(D) - np.timedelta64(1, "D")
    return days


def settled(s, cfg, scan_date):
    """The series cut at its last settled day, and the index of its first fresh point (None when nothing is fresh)."""
    last_ok = np.datetime64(scan_date, "D") - np.timedelta64(settle_days(cfg, s.table), "D")
    n = int(np.searchsorted(period_end(s.days, s.grain), last_ok, side="right"))    # a period still open is a partial one
    if n < 3:
        return n, None
    first_fresh = np.datetime64(scan_date, "D") - np.timedelta64(int(cfg["fresh_days"][s.grain]), "D")
    i = int(np.searchsorted(period_end(s.days[:n], s.grain), first_fresh, side="left"))     # fresh by its period's end
    return n, (i if i < n else None)


def stat_words(s):
    return "daily mean" if s.sub else {"daily": "daily value", "weekly": "weekly value", "monthly": "monthly value", "yearly": "yearly value"}[s.grain]


def base_flag(s, rule, i, value, cfg, scan_date, strength, threshold, compared, direction, history):
    day = str(s.days[i])
    key = f"{rule}|{s.table}|{s.key_str}"
    fid = "scan-" + rule + "-" + hashlib.sha1(f"{key}|{day}".encode("utf-8")).hexdigest()[:12]
    return {"id": fid, "flag_key": key, "rule": rule, "table": s.table, "series": s.key, "series_key": s.key_str, "label": s.label(),
            "date": day, "value": float(value), "unit": s.unit, "statistic": stat_words(s), "direction": direction,
            "threshold": threshold, "compared": compared, "history": history, "strength": round(float(strength), 4),
            "source": s.source, "note": s.note, "scanner_version": str(cfg["version"]), "scan_date": scan_date, "window": [day, day]}


def history_of(days, n=None):
    days = days if n is None else days[:n]
    return {"first": str(days[0]), "last": str(days[-1]), "points": int(len(days)),
            "years": round(float((days[-1] - days[0]).astype(int)) / 365.25, 2)}


def rule_record(s, cfg, scan_date, n, f):
    if f < cfg["record_min_points"][s.grain]:
        return []
    prior, new = s.v[:f], s.v[f:n]
    sigma = robust_sigma(prior)
    if sigma <= 0:
        return []
    out = []
    for direction, old, j in (("high", prior.max(), int(np.argmax(new))), ("low", prior.min(), int(np.argmin(new)))):
        val = new[j]
        beats = val > old if direction == "high" else val < old
        if not beats:
            continue
        since = int(np.argmax(prior == old))            # the first point that set the old record
        stood = f + j - since                           # points from the old record to the new one
        margin = abs(val - old) / sigma
        if stood < cfg["record_stood_points"][s.grain] or margin < cfg["record_min_margin_sigmas"]:
            continue
        thr = {"name": f"record {direction}", "value": float(old), "statistic": f"the {'highest' if direction == 'high' else 'lowest'} {stat_words(s)} of the held history",
               "config": {"record_min_points": cfg["record_min_points"][s.grain], "record_stood_points": cfg["record_stood_points"][s.grain],
                          "record_min_margin_sigmas": cfg["record_min_margin_sigmas"]}}
        cmp_ = {"old_record": float(old), "old_record_date": str(s.days[since]), "stood_points": int(stood), "margin": float(val - old),
                "margin_sigmas": round(float(margin), 4), "sigma": float(sigma)}
        out.append(base_flag(s, "record", f + j, val, cfg, scan_date, margin, thr, cmp_, direction, history_of(s.days, f)))
    return out


def is_price(s, cfg):
    v = s.key.get("variable", "")
    return bool(re.search(cfg["price_unit"], s.unit or "") and re.search(cfg["price_variable"], v) and not re.search(cfg["price_variable_not"], v))


def rule_negative(s, cfg, scan_date, n, f):
    if s.grain != "daily" or not is_price(s, cfg):
        return []
    lo = s.lo[:n]
    neg = np.nonzero(lo[f:] < 0)[0]
    if not len(neg):
        return []
    i = f + int(neg[0])
    a = s.days[i] - np.timedelta64(int(cfg["negative_prior_days"]), "D")
    j = int(np.searchsorted(s.days, a, side="left"))
    held = i - j
    if held < cfg["negative_min_days_held"] or (lo[j:i] < 0).any():
        return []
    sigma = robust_sigma(lo[j:i]) or 1.0
    before = np.nonzero(lo[:j] < 0)[0]
    thr = {"name": "a price below zero", "value": 0.0, "statistic": "the day's lowest interval price" if s.sub else "the day's price",
           "config": {"negative_prior_days": cfg["negative_prior_days"], "negative_min_days_held": cfg["negative_min_days_held"]}}
    cmp_ = {"prior_days_held": int(held), "prior_lowest": float(lo[j:i].min()), "prior_lowest_date": str(s.days[j + int(np.argmin(lo[j:i]))]),
            "last_negative_before": str(s.days[before[-1]]) if len(before) else None, "day_mean": float(s.v[i])}
    return [base_flag(s, "negative", i, lo[i], cfg, scan_date, abs(lo[i]) / sigma, thr, cmp_, "low", history_of(s.days, i))]


def rule_spike(s, cfg, scan_date, n, f):
    if s.grain not in cfg["spike_min_points"]:
        return []
    a = s.days[f] - np.timedelta64(int(round(365.25 * cfg["spike_history_years"])), "D")
    j = int(np.searchsorted(s.days, a, side="left"))
    prior = s.v[j:f]
    if len(prior) < cfg["spike_min_points"][s.grain]:
        return []
    p, med = float(np.percentile(prior, cfg["spike_percentile"])), float(np.median(prior))
    if p <= 0 or med <= 0 or float(np.mean(prior < 0)) > cfg["spike_max_negative_share"]:
        return []                                       # a signed quantity: a multiple of it says nothing
    i = f + int(np.argmax(s.v[f:n]))
    val, line = s.v[i], cfg["spike_multiple"] * p
    if val <= line:
        return []
    sigma = robust_sigma(prior) or 1.0
    thr = {"name": f"{cfg['spike_multiple']:g} times the {cfg['spike_percentile']}th percentile of the prior {cfg['spike_history_years']} years", "value": float(line),
           "statistic": f"the {stat_words(s)} against the {cfg['spike_percentile']}th percentile of the series' {stat_words(s)}s in the prior {cfg['spike_history_years']} years",
           "config": {"spike_multiple": cfg["spike_multiple"], "spike_percentile": cfg["spike_percentile"], "spike_history_years": cfg["spike_history_years"],
                      "spike_min_points": cfg["spike_min_points"][s.grain], "spike_max_negative_share": cfg["spike_max_negative_share"]}}
    cmp_ = {"percentile_value": p, "median": med, "multiple_of_percentile": round(float(val / p), 4), "prior_points": int(len(prior)), "prior_max": float(prior.max())}
    return [base_flag(s, "spike", i, val, cfg, scan_date, (val - line) / sigma, thr, cmp_, "high", history_of(s.days[j:f]))]


def weekly_changes(days, v, min_days):
    """A daily series' 7-day mean minus the 7-day mean before it, on a full calendar (gaps are gaps)."""
    idx = pd.date_range(str(days[0]), str(days[-1]), freq="D")
    x = pd.Series(v, index=pd.to_datetime(days.astype(str))).reindex(idx)
    m = x.rolling(7, min_periods=min_days).mean()
    return idx.to_numpy().astype(D), (m - m.shift(7)).to_numpy(float)


def rule_weekly(s, cfg, scan_date, n, f):
    if s.grain == "daily":
        cal, c = weekly_changes(s.days[:n], s.v[:n], int(cfg["weekly_min_days"]))
        gap = 14
    elif s.grain == "weekly":
        cal, c = s.days[1:n], np.where(np.diff(s.days[:n]).astype(int) <= 8, np.diff(s.v[:n]), np.nan)
        gap = 7
    else:
        return []
    if not len(c) or np.isnan(c[-1]) or cal[-1] != s.days[n - 1]:
        return []
    t, now = cal[-1], float(c[-1])
    a = t - np.timedelta64(int(round(365.25 * cfg["weekly_range_years"])), "D")
    b = t - np.timedelta64(gap, "D")
    m = (cal >= a) & (cal <= b) & ~np.isnan(c)
    hist, hdays = c[m], cal[m]
    if not len(hist) or (t - hdays[0]).astype(int) < 365.25 * cfg["weekly_min_years"] or len(hist) < (300 if s.grain == "daily" else 100):
        return []
    lo, hi = float(hist.min()), float(hist.max())
    width = hi - lo
    if width <= 0:
        return []
    excess = now - hi if now > hi else (lo - now if now < lo else 0.0)
    if excess < cfg["weekly_min_excess_share"] * width:
        return []
    direction = "high" if now > hi else "low"
    sigma = robust_sigma(hist) or 1.0
    i = n - 1
    week_now = float(np.mean(s.v[max(0, i - 6):i + 1])) if s.grain == "daily" else float(s.v[i])
    thr = {"name": f"the {cfg['weekly_range_years']}-year range of the weekly change", "value": hi if direction == "high" else lo,
           "statistic": "the mean of the newest 7 days minus the mean of the 7 days before" if s.grain == "daily" else "the newest week minus the week before",
           "config": {"weekly_range_years": cfg["weekly_range_years"], "weekly_min_years": cfg["weekly_min_years"], "weekly_min_days": cfg["weekly_min_days"],
                      "weekly_min_excess_share": cfg["weekly_min_excess_share"]}}
    cmp_ = {"change": now, "range_low": lo, "range_high": hi, "range_low_date": str(hdays[int(np.argmin(hist))]), "range_high_date": str(hdays[int(np.argmax(hist))]),
            "range_points": int(len(hist)), "range_first": str(hdays[0]), "week_mean": week_now, "week_before_mean": week_now - now}
    fl = base_flag(s, "weekly", i, now, cfg, scan_date, excess / sigma, thr, cmp_, direction, history_of(hdays))
    fl["window"] = [str(t - np.timedelta64(13, "D")), str(t)]
    fl["statistic"] = thr["statistic"]
    return [fl]


def pair_candidates(series_by_table, cfg):
    """The pairs (y, x, rule name) the rules of scanner.yaml name, from the series that were read."""
    p = cfg.get("pairs") or {}
    out = []
    for rule in p.get("same_table") or []:
        for table, ss in series_by_table.items():
            if not re.search(rule["table"], table):
                continue
            groups = {}
            for s in ss:
                if s.grain == "daily" and re.search(rule["variable"], s.key.get("variable", "")):
                    groups.setdefault((s.key.get("variable"), s.key.get("market"), s.key.get("freq"), s.key.get("entity", "").split(":")[0]), []).append(s)
            for g in groups.values():
                if 2 <= len(g) <= cfg["pair_max_group"]:
                    g = sorted(g, key=lambda s: s.key_str)
                    out += [(g[i], g[j], "hub against hub") for i in range(len(g)) for j in range(i + 1, len(g))]
    ag = p.get("against_gas") or {}
    gas = ag.get("gas")
    if gas:
        gs = [s for s in series_by_table.get(gas["table"], []) if s.key.get("entity") == gas["entity"] and s.key.get("variable") == gas["variable"]]
        for rule in ag.get("price") or []:
            for table, ss in series_by_table.items():
                if re.search(rule["table"], table):
                    out += [(s, gs[0], "price against gas") for s in ss if gs and s.grain == "daily" and re.search(rule["variable"], s.key.get("variable", ""))]
    return out


def rule_pair(y, x, name, cfg, scan_date):
    ny, fy = settled(y, cfg, scan_date)
    nx, fx = settled(x, cfg, scan_date)
    if fy is None or fx is None:
        return []
    t = min(y.days[ny - 1], x.days[nx - 1])
    a = pd.Series(y.v[:ny], index=pd.to_datetime(y.days[:ny].astype(str)))
    b = pd.Series(x.v[:nx], index=pd.to_datetime(x.days[:nx].astype(str)))
    j = pd.concat([a.rename("y"), b.rename("x")], axis=1).dropna()
    tt = pd.Timestamp(str(t))
    new = j[(j.index > tt - pd.Timedelta(days=7)) & (j.index <= tt)]
    fit = j[(j.index > tt - pd.Timedelta(days=7 + int(cfg["pair_fit_days"]))) & (j.index <= tt - pd.Timedelta(days=7))]
    if len(new) < 5 or len(fit) < cfg["pair_min_days"] or fit["x"].std() == 0 or fit["y"].std() == 0:
        return []
    slope, icpt = np.polyfit(fit["x"].to_numpy(), fit["y"].to_numpy(), 1)
    res = fit["y"] - (icpt + slope * fit["x"])
    r2 = 1 - float((res ** 2).sum()) / float(((fit["y"] - fit["y"].mean()) ** 2).sum())
    if r2 < cfg["pair_min_r2"]:
        return []
    r7 = res.reindex(pd.date_range(res.index[0], res.index[-1], freq="D")).rolling(7, min_periods=5).mean().dropna()
    s7 = float(r7.std())
    now = float((new["y"] - (icpt + slope * new["x"])).mean())
    if s7 <= 0 or abs(now) <= cfg["pair_break_sigmas"] * s7 or (r7.min() <= now <= r7.max()):
        return []
    i = int(np.searchsorted(y.days, t, side="left"))
    thr = {"name": f"{cfg['pair_break_sigmas']:g} standard deviations of the 7-day mean residual", "value": float(cfg["pair_break_sigmas"] * s7),
           "statistic": f"the mean residual of the newest 7 days of a least-squares fit of y on x over the {cfg['pair_fit_days']} days before",
           "config": {"pair_fit_days": cfg["pair_fit_days"], "pair_min_days": cfg["pair_min_days"], "pair_min_r2": cfg["pair_min_r2"], "pair_break_sigmas": cfg["pair_break_sigmas"]}}
    cmp_ = {"pair_rule": name, "x_table": x.table, "x_series_key": x.key_str, "x_label": x.label(), "x_unit": x.unit, "slope": float(slope), "intercept": float(icpt),
            "r2": round(r2, 4), "fit_days": int(len(fit)), "new_days": int(len(new)), "residual_sd_7d": s7, "sigmas": round(abs(now) / s7, 4),
            "fit_residual_low": float(r7.min()), "fit_residual_high": float(r7.max()), "y_mean_new": float(new["y"].mean()), "x_mean_new": float(new["x"].mean()),
            "y_expected_new": float((icpt + slope * new["x"]).mean())}
    fl = base_flag(y, "pair", i, now, cfg, scan_date, abs(now) / s7 - cfg["pair_break_sigmas"], thr, cmp_, "high" if now > 0 else "low",
                   {"first": str(fit.index[0].date()), "last": str(fit.index[-1].date()), "points": int(len(fit)), "years": round(len(fit) / 365.25, 2)})
    fl["flag_key"] = f"pair|{y.table}|{y.key_str}|{x.table}|{x.key_str}"
    fl["id"] = "scan-pair-" + hashlib.sha1(f"{fl['flag_key']}|{fl['date']}".encode("utf-8")).hexdigest()[:12]
    fl["window"] = [str(new.index[0].date()), str(new.index[-1].date())]
    fl["statistic"] = "7-day mean residual"
    fl["_pair_chart"] = (j, slope, icpt)
    return [fl]


SINGLE_RULES = (rule_record, rule_negative, rule_spike, rule_weekly)


def scan_series(s, cfg, scan_date, stats):
    n, f = settled(s, cfg, scan_date)
    if f is None:
        stats["stale"] += 1
        return []
    if f < 2 or len(np.unique(s.v[:n])) < cfg["min_distinct_values"]:
        stats["too_short"] += 1
        return []
    stats["series_scanned"] += 1
    out = []
    for rule in SINGLE_RULES:
        out += rule(s, cfg, scan_date, n, f)
    return out


# ---------------------------------------------------------------------------------------------------------------------
# a flag's draft card: chart, callouts, footnote. No paragraph.
# ---------------------------------------------------------------------------------------------------------------------
def nd_for(v):
    a = abs(v)
    return 0 if a >= 10000 else (1 if a >= 100 else (2 if a >= 1 else 4))


def num(v, unit=""):
    if v is None:
        return "not held"
    t = common.fmt(float(v), nd_for(float(v)))
    if unit.startswith("USD"):
        return f"USD {t}" + (f" per {unit.split('/', 1)[1]}" if "/" in unit else "")
    return f"{t} {unit}".strip()


def numbers_from_flag(fl):
    """Every number a draft card shows, from the flag alone (the test compares the card with this)."""
    c, h = fl["compared"], fl["history"]
    n = {"value": fl["value"], "threshold": fl["threshold"]["value"], "history_points": h["points"], "history_years": h["years"], "strength": fl["strength"]}
    for k, v in c.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            n[k] = v
    return n


def chart_for(fl, s, cfg):
    cap = int(cfg["chart_points"][s.grain])
    if fl["rule"] == "pair":
        j, slope, icpt = fl["_pair_chart"]
        j = j[j.index <= pd.Timestamp(fl["window"][1])].tail(180)
        x = [d.strftime("%Y-%m-%d") for d in j.index]
        return {"kind": "flag_line", "x": x, "x_label": f"day (UTC); the newest 7 days are marked; fit on the {fl['history']['points']} days before them",
                "series": [{"name": fl["label"], "type": "line", "unit": fl["unit"], "values": [common.round6(v) for v in j["y"]]},
                           {"name": f"expected from {fl['compared']['x_label']}", "type": "line", "unit": fl["unit"], "values": [common.round6(icpt + slope * v) for v in j["x"]]}],
                "mark_area": {"from": fl["window"][0], "to": fl["window"][1], "label": "newest 7 days"}, "y_left_label": fl["unit"], "decimals": nd_for(fl["compared"]["y_mean_new"])}
    i = int(np.searchsorted(s.days, np.datetime64(fl["date"]), side="left"))
    a = max(0, i + 1 - cap)
    x = [str(d) for d in s.days[a:i + 1]]
    vals = s.lo[a:i + 1] if fl["rule"] == "negative" else s.v[a:i + 1]
    name = fl["label"] + (", the day's lowest interval" if fl["rule"] == "negative" and s.sub else (", daily mean" if s.sub else ""))
    spec = {"kind": "flag_line", "x": x, "x_label": f"{'day (UTC)' if s.grain == 'daily' else s.grain[:-2] if s.grain != 'daily' else ''}; the flagged point is marked",
            "series": [{"name": name, "type": "line", "unit": fl["unit"], "values": [common.round6(v) for v in vals]}],
            "mark": {"x": fl["date"], "value": common.round6(vals[-1]), "label": fl["threshold"]["name"]}, "y_left_label": fl["unit"], "decimals": nd_for(fl["value"])}
    c = fl["compared"]
    if fl["rule"] == "record":
        spec["ref_lines"] = [{"name": f"the record until now ({c['old_record_date']})", "value": common.round6(c["old_record"])}]
    elif fl["rule"] == "negative":
        spec["ref_lines"] = [{"name": "zero", "value": 0}]
    elif fl["rule"] == "spike":
        spec["ref_lines"] = [{"name": "99th percentile of the prior years", "value": common.round6(c["percentile_value"])}, {"name": "the threshold", "value": common.round6(fl["threshold"]["value"])}]
    elif fl["rule"] == "weekly":
        spec["mark_area"] = {"from": fl["window"][0], "to": fl["window"][1], "label": "the two weeks compared"}
        spec["band_words"] = f"weekly change {num(c['change'])}; its range since {c['range_first']}: {num(c['range_low'])} to {num(c['range_high'])}"
    return spec


def full_card_for(fl):
    """The analysis of the engine nearest to a flag, for "Ask for a full card": the impact study on the flagged series
    around the flagged date, when the series is one the study knows and it has a control in the same unit. None: no
    analysis of the engine fits, and the draft is marked for a session to write the card. Nothing is written here."""
    import impact_study
    k = impact_study.series_for(fl["table"], fl["series"].get("entity"), fl["series"].get("variable"))
    c = impact_study.default_control(k) if k else None
    if not k or not c:
        return None
    y, m, d = (int(x) for x in fl["date"].split("-"))
    return {"finding": impact_study.NAME, "params": {"series": k, "control": c, "event": "date", "year": y, "month": m, "day": d, "window": 14}}


def flag_card(fl, s, cfg):
    u, c, h, thr = fl["unit"], fl["compared"], fl["history"], fl["threshold"]
    rule, day = fl["rule"], fl["date"]
    if rule == "record":
        title = f"RECORD {fl['direction'].upper()}"
        sub = f"{fl['label']}: {num(fl['value'], u)} on {day}, the {'highest' if fl['direction'] == 'high' else 'lowest'} {fl['statistic']} of {common.fmt(h['points'], 0)} held"
        calls = [common.callout("The record", f"until now ({c['old_record_date']})", num(c["old_record"], u), day, num(fl["value"], u)),
                 common.callout("How far past it", "margin", num(c["margin"], u), "in robust standard deviations", common.fmt(c["margin_sigmas"], 2)),
                 common.callout("History held", "first point", h["first"], "points before this one", common.fmt(h["points"], 0))]
    elif rule == "negative":
        title = RULES[rule]
        sub = f"{fl['label']}: {num(fl['value'], u)} on {day}, the first price below zero in {common.fmt(c['prior_days_held'], 0)} held days"
        calls = [common.callout("The day's lowest price", f"lowest of the prior year ({c['prior_lowest_date']})", num(c["prior_lowest"], u), day, num(fl["value"], u)),
                 common.callout("Days held before it", "prior days looked at", common.fmt(thr["config"]["negative_prior_days"], 0), "of them held", common.fmt(c["prior_days_held"], 0)),
                 common.callout("Last price below zero before", "date", c["last_negative_before"] or "none held", "the day's mean", num(c["day_mean"], u))]
    elif rule == "spike":
        title = RULES[rule]
        sub = f"{fl['label']}: {num(fl['value'], u)} on {day}, {common.fmt(c['multiple_of_percentile'], 1)} times the 99th percentile of its prior {thr['config']['spike_history_years']} years"
        calls = [common.callout("The value", "99th percentile, prior years", num(c["percentile_value"], u), day, num(fl["value"], u)),
                 common.callout("Against the threshold", "threshold", num(thr["value"], u), "multiple of the percentile", common.fmt(c["multiple_of_percentile"], 2)),
                 common.callout("History compared", "median of the prior years", num(c["median"], u), "points", common.fmt(c["prior_points"], 0))]
    elif rule == "weekly":
        title = RULES[rule]
        sub = f"{fl['label']}: a weekly change of {num(c['change'], u)} to {day}, outside its range since {c['range_first']}"
        calls = [common.callout("The two weeks", "the 7 days before", num(c["week_before_mean"], u), f"the 7 days to {day}", num(c["week_mean"], u)),
                 common.callout("The change against its range", f"largest {'rise' if fl['direction'] == 'high' else 'fall'} before ({c['range_high_date'] if fl['direction'] == 'high' else c['range_low_date']})",
                                num(c["range_high"] if fl["direction"] == "high" else c["range_low"], u), "this change", num(c["change"], u)),
                 common.callout("History compared", "since", c["range_first"], "weekly changes", common.fmt(c["range_points"], 0))]
    else:
        title = RULES[rule]
        sub = f"{fl['label']} against {c['x_label']}: {num(c['y_mean_new'], u)} in the 7 days to {day}, where the year's fit gives {num(c['y_expected_new'], u)}"
        calls = [common.callout("The newest 7 days", "expected from the fit", num(c["y_expected_new"], u), "observed", num(c["y_mean_new"], u)),
                 common.callout("The gap against its history", "standard deviation of 7-day gaps", num(c["residual_sd_7d"], u), "this gap, in those", common.fmt(c["sigmas"], 1)),
                 common.callout("The fit before", "R2", common.fmt(c["r2"], 2), "days", common.fmt(c["fit_days"], 0))]
    cfg_words = "; ".join(f"{k} = {v}" for k, v in thr["config"].items())
    foot = (f"A draft raised by the scanner, version {fl['scanner_version']}, on its run of {fl['scan_date']}; not reviewed. Data: {fl['table']}, series {fl['series_key']}"
            + (f" (source {fl['source']})" if fl["source"] else "") + f". Statistic: {thr['statistic']}. History compared: {h['first']} to {h['last']}, "
            f"{common.fmt(h['points'], 0)} observations, {common.fmt(h['years'], 1)} years" + (f"; {fl['note']}" if fl["note"] else "") + ". "
            f"Rule: {rule} ({thr['name']}); threshold crossed: {num(thr['value'], u)}; thresholds of warehouse/config/scanner.yaml: {cfg_words}. "
            + (f"The other series: {c['x_table']}, {c['x_series_key']}; fit y = {common.fmt(c['intercept'], 3)} + {common.fmt(c['slope'], 4)} x. " if rule == "pair" else "")
            + f"Sub-daily series are read by UTC day; the newest {settle_days(cfg, fl['table'])} days are not evaluated (they can still be revised). Method: {METHOD}.")
    card = {"id": "scanner_flag", "card_id": fl["id"], "title": title, "kind": "visual", "subtitle": sub, "draft": True,
            "params": {"rule": rule, "table": fl["table"], "date": day}, "inputs_words": {"table": fl["table"], "flagged": day},
            "chart": chart_for(fl, s, cfg), "callouts": calls, "why": "", "footnote": foot, "numbers": numbers_from_flag(fl),
            "source_line": f"Source: ERW table {fl['table']}" + (f" ({fl['source']})" if fl["source"] else "") + ". Found by the scanner.",
            "tables": [fl["table"]] + ([c["x_table"]] if rule == "pair" else []), "computed_at": common.now_iso(), "method": METHOD_URL,
            "scanner": {"version": fl["scanner_version"], "rule": rule, "date": day, "flag_id": fl["id"], "strength": fl["strength"], "full_card": full_card_for(fl)}}
    return card


# ---------------------------------------------------------------------------------------------------------------------
# the scan
# ---------------------------------------------------------------------------------------------------------------------
def cap_drafts(flags, cfg):
    """The day's drafts: the strongest first, within the caps of scanner.yaml."""
    per_table, per_rule, per_entity, out = {}, {}, {}, []
    for fl in sorted(flags, key=lambda f: -f["strength"]):
        if len(out) >= cfg["max_drafts_per_day"]:
            break
        ent = (fl["rule"], fl["table"], fl["series"].get("entity"))
        if (per_table.get(fl["table"], 0) >= cfg["max_drafts_per_table"] or per_rule.get(fl["rule"], 0) >= cfg["max_drafts_per_rule"]
                or per_entity.get(ent, 0) >= cfg["max_drafts_per_entity_rule"]):
            continue
        per_entity[ent] = per_entity.get(ent, 0) + 1
        per_table[fl["table"]] = per_table.get(fl["table"], 0) + 1
        per_rule[fl["rule"]] = per_rule.get(fl["rule"], 0) + 1
        out.append(fl)
    return out


def drop_repeats(flags, tiers):
    """A derived table repeats its source table's numbers: the same rule, date, direction and value flagged in two
    tables is one flag, kept in the source table (coverage.csv's tier) where there is one. Returns (kept, dropped)."""
    best = {}
    for fl in flags:
        k = (fl["rule"], fl["date"], fl["direction"], round(fl["value"], 6))
        if fl["rule"] == "pair" or k not in best or (tiers.get(best[k]["table"]) != "source" and tiers.get(fl["table"]) == "source"):
            best[k if fl["rule"] != "pair" else fl["id"]] = fl
    kept = {id(f) for f in best.values()}
    return [f for f in flags if id(f) in kept], len(flags) - len(kept)


def scan(in_dir, cfg, scan_date=None, meta_dir=None, tables=None, log=print):
    """Scan every public time table. Returns (flags, suppressed, drafts, summary)."""
    t0 = time.time()
    scan_date = scan_date or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    meta_dir = meta_dir or META_DIR
    todo, skipped, not_series = public_time_tables(cfg, in_dir, meta_dir)
    if tables:
        todo = [(n, c) for n, c in todo if re.search(tables, n)]
    paused = paused_patterns(meta_dir) if cfg.get("skip_paused", True) else []
    faults = known_faults(in_dir) if cfg.get("suppress_known_faults", True) else []
    pair_tables = [r["table"] for r in (cfg.get("pairs") or {}).get("same_table") or []] + [r["table"] for r in ((cfg.get("pairs") or {}).get("against_gas") or {}).get("price") or []]
    gas_table = (((cfg.get("pairs") or {}).get("against_gas") or {}).get("gas") or {}).get("table")
    stats = {k: 0 for k in ("repeats_of_a_source_table", "series_seen", "series_scanned", "stale", "too_short", "unit_change", "key_incomplete", "source_change", "no_grain", "paused", "pairs_tested")}
    flags, kept, cards_src, per_table = [], {}, {}, []
    for name, cols in todo:
        t1 = time.time()
        before = dict(stats)
        try:
            ss = read_series(name, cols, in_dir, cfg, stats)
        except Exception as exc:
            skipped.append((name, f"could not be read: {type(exc).__name__}: {str(exc)[:120]}"))
            log(f"  {name}: NOT READ: {exc}")
            continue
        n_flags = 0
        for s in ss:
            if any(rx.search(s.key.get("entity", "")) or rx.search(s.source or "") for _, rx in paused):
                stats["paused"] += 1
                continue
            for fl in scan_series(s, cfg, scan_date, stats):
                flags.append(fl)
                cards_src[fl["id"]] = s
                n_flags += 1
        if name == gas_table or any(re.search(p, name) for p in pair_tables):
            kept[name] = [s for s in ss if s.grain == "daily" and not any(rx.search(s.key.get("entity", "")) or rx.search(s.source or "") for _, rx in paused)]
        per_table.append({"table": name, "series": stats["series_seen"] - before["series_seen"], "scanned": stats["series_scanned"] - before["series_scanned"],
                          "flags": n_flags, "seconds": round(time.time() - t1, 1)})
        log(f"  {name}: {per_table[-1]['series']} series, {per_table[-1]['scanned']} scanned, {n_flags} flags, {per_table[-1]['seconds']} s")
    for y, x, rule_name in pair_candidates(kept, cfg):
        stats["pairs_tested"] += 1
        for fl in rule_pair(y, x, rule_name, cfg, scan_date):
            flags.append(fl)
            cards_src[fl["id"]] = y
    tiers = {r["table"]: r.get("tier", "") for _, r in read_meta_csv(os.path.join(meta_dir, "coverage.csv")).iterrows()}
    flags, repeats = drop_repeats(flags, tiers)
    stats["repeats_of_a_source_table"] = repeats
    raised, suppressed = [], []
    for fl in flags:
        fid = fault_for(faults, fl["table"], fl["window"][0], fl["window"][1]) or (fault_for(faults, fl["compared"]["x_table"], fl["window"][0], fl["window"][1]) if fl["rule"] == "pair" else None)
        if fid:
            fl["suppressed_by"] = fid
            suppressed.append(fl)
        else:
            raised.append(fl)
    raised.sort(key=lambda f: -f["strength"])
    chosen = cap_drafts(raised, cfg)
    chosen_ids = {f["id"] for f in chosen}
    drafts = []
    for fl in chosen:
        card = flag_card(fl, cards_src[fl["id"]], cfg)
        drafts.append({"id": fl["id"], "flag_key": fl["flag_key"], "rule": fl["rule"], "table_name": fl["table"], "series_key": fl["series_key"], "flag_date": fl["date"],
                       "value": fl["value"], "strength": fl["strength"], "scanner_version": fl["scanner_version"], "flag": clean(fl), "card": card})
    for fl in raised:
        fl["draft"] = fl["id"] in chosen_ids
    summary = {"scanner_version": str(cfg["version"]), "scan_date": scan_date, "in_dir": in_dir, "tables_scanned": len(per_table), "tables": per_table,
               "not_scanned": [{"table": n, "reason": r} for n, r in skipped], "public_tables_not_series": not_series, **stats,
               "flags_raised": len(raised), "flags_suppressed_by_known_faults": len(suppressed), "drafts": len(drafts),
               "by_rule": {r: sum(1 for f in raised if f["rule"] == r) for r in RULES}, "seconds": round(time.time() - t0, 1), "computed_at": common.now_iso()}
    return [clean(f) for f in raised], [clean(f) for f in suppressed], drafts, summary


def clean(fl):
    return {k: v for k, v in fl.items() if not k.startswith("_")}


def write_run(out_dir, flags, suppressed, drafts, summary):
    os.makedirs(out_dir, exist_ok=True)
    for name, obj in (("flags.json", flags), ("suppressed.json", suppressed), ("drafts.json", drafts), ("scan_summary.json", summary)):
        with open(os.path.join(out_dir, name), "w", encoding="utf-8", newline="\n") as f:
            json.dump(obj, f, indent=1, ensure_ascii=False, default=common.round6)
            f.write("\n")


# ---------------------------------------------------------------------------------------------------------------------
# the review list (public.scanner_drafts, migration 029) and the daily request
# ---------------------------------------------------------------------------------------------------------------------
def supabase():
    """(rest base, headers) with the service role, as the worker reads them; None when this machine has no key."""
    sys.path.insert(0, os.path.join(ROOT, "warehouse"))
    import lock
    import urllib.parse
    url, key = lock.env("SUPABASE_URL"), lock.env("SUPABASE_SERVICE_KEY")
    if not url or not key:
        return None
    u = urllib.parse.urlparse(url)
    return f"{u.scheme}://{u.netloc}/rest/v1", {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def new_rows(drafts, existing):
    """The drafts to add: not raised before under the same id (any state), and no open draft of the same flag key."""
    ids = {r["id"] for r in existing}
    open_keys = {r["flag_key"] for r in existing if r.get("state") in ("draft", "full_card_asked")}
    out = []
    for d in drafts:
        if d["id"] in ids or d["flag_key"] in open_keys:
            continue
        open_keys.add(d["flag_key"])
        out.append(d)
    return out


def load_drafts(drafts, dry_run=False, log=print):
    """Add the run's drafts to the review list. Returns the count added. --dry-run asks nothing of the network."""
    if dry_run:
        for d in drafts:
            log(f"  would add {d['id']} ({d['rule']}, {d['table_name']}, {d['flag_date']}, strength {d['strength']})")
        log(f"dry run: {len(drafts)} draft(s) in the file; nothing was sent (a real load adds those not already in {DRAFT_TABLE})")
        return 0
    import requests
    sb = supabase()
    if sb is None:
        raise SystemExit("the load needs SUPABASE_URL and SUPABASE_SERVICE_KEY (.env or the environment)")
    base, h = sb
    r = requests.get(f"{base}/{DRAFT_TABLE}", params={"select": "id,flag_key,state", "limit": "5000"}, headers=h, timeout=30)
    r.raise_for_status()
    rows = new_rows(drafts, r.json())
    if rows:
        body = [{k: d[k] for k in ("id", "flag_key", "rule", "table_name", "series_key", "flag_date", "value", "strength", "scanner_version", "flag", "card")} for d in rows]
        # allow_nan=False: a value that is not a number is an error here, never a row the database refuses half way
        w = requests.post(f"{base}/{DRAFT_TABLE}", data=json.dumps(body, default=common.round6, allow_nan=False), headers={**h, "Prefer": "return=minimal"}, timeout=60)
        w.raise_for_status()
    log(f"{len(rows)} draft(s) added to {DRAFT_TABLE}; {len(drafts) - len(rows)} already there or with an open draft")
    return len(rows)


def daily_request(params, in_dir=None, log=print):
    """What the worker runs for a `scanner_daily` request: the scan over this machine's tables, the run kept under
    runs/scanner/<date>/, the drafts added to the review list. Returns {flags, drafts, loaded, note}."""
    cfg = load_config()
    date = str((params or {}).get("date") or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d"))
    flags, suppressed, drafts, summary = scan(in_dir or common.DEFAULT_IN_DIR, cfg, date, log=lambda m: None)
    write_run(os.path.join(ROOT, "runs", "scanner", date), flags, suppressed, drafts, summary)
    loaded = load_drafts(drafts, log=log)
    note = (f"scan of {date}: {summary['tables_scanned']} tables, {summary['series_scanned']} series, {len(flags)} flags, "
            f"{len(suppressed)} suppressed by known faults, {len(drafts)} drafts, {loaded} added, {summary['seconds']} s")
    return {"flags": len(flags), "drafts": len(drafts), "loaded": loaded, "note": note}


HISTORIES = ("ercot_all_hub_prices_history", "ercot_zone_prices_history", "iso_zone_prices_history")


def daily_scan(in_dir=None, log=print):
    """The data machine's daily soft step (warehouse/run_data_machine.sh, after its sync): scan this machine's tables,
    keep the run under runs/scanner/<date>/, add the drafts to the review list. Where the price histories are not on
    the machine (GitHub's runner holds rolling windows: every rule that compares with years of history would have
    nothing to compare with) it does not scan: exit ERW_SKIP_EXIT with the reason. It calls no model."""
    skip = int(os.environ.get("ERW_SKIP_EXIT", "75"))
    in_dir = in_dir or common.DEFAULT_IN_DIR
    missing = [t for t in HISTORIES if not os.path.exists(os.path.join(in_dir, t + ".csv"))]
    if os.environ.get("GITHUB_ACTIONS") == "true" or missing:
        log("scanner SKIPPED: " + ("this is GitHub's runner, which holds rolling windows and not the histories the rules compare with"
                                   if not missing else f"the price histories are not on this machine ({', '.join(missing)})")
            + "; the scan runs on the data machine (the worker takes the request `scanner_daily`)")
        return skip
    out = daily_request({}, in_dir, log)
    log(f"scanner: {out['note']}")
    return 0


def request_scan(log=print):
    """The daily soft step (warehouse/run_daily.sh): queue today's scan for the data machine's worker. The full
    histories are on the data machine only, so the runner does not scan; it asks. Exit ERW_SKIP_EXIT with the reason
    when this machine has no service key."""
    skip = int(os.environ.get("ERW_SKIP_EXIT", "75"))
    try:
        sb = supabase()
    except Exception as exc:
        log(f"scanner_request SKIPPED: the queue cannot be reached from here ({type(exc).__name__})")
        return skip
    if sb is None:
        log("scanner_request SKIPPED: SUPABASE_URL or SUPABASE_SERVICE_KEY is not on this machine, so the scan cannot be queued")
        return skip
    import requests
    base, h = sb
    day = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    row = {"id": "scanner-" + day.replace("-", ""), "kind": "run", "finding": REQUEST_FINDING, "params": {"date": day}, "status": "queued"}
    r = requests.post(f"{base}/analysis_requests", data=json.dumps(row), headers={**h, "Prefer": "return=minimal,resolution=ignore-duplicates"}, timeout=30)
    if r.status_code >= 400:
        log(f"scanner_request FAILED: HTTP {r.status_code} {r.text[:160]}")
        return 1
    log(f"scanner_request: the scan of {day} is queued for the data machine ({row['id']}); it runs when the worker is awake")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW scanner (session 181)")
    ap.add_argument("--in-dir", default=common.DEFAULT_IN_DIR, help="the warehouse's output directory")
    ap.add_argument("--out-dir", help="where flags.json, suppressed.json, drafts.json and scan_summary.json are written")
    ap.add_argument("--meta-dir", default=META_DIR, help="coverage.csv, paused_sources.csv, known_gaps.csv")
    ap.add_argument("--config", default=CONFIG)
    ap.add_argument("--date", help="the scan's date, YYYY-MM-DD (default today, UTC)")
    ap.add_argument("--tables", help="a pattern: scan only the tables it matches")
    ap.add_argument("--daily", action="store_true", help="the data machine's daily soft step: scan, keep the run, add the drafts")
    ap.add_argument("--request", action="store_true", help="queue today's scan for the data machine (the runner's daily soft step)")
    ap.add_argument("--load", metavar="DRAFTS_JSON", help="add a run's drafts to the review list")
    ap.add_argument("--dry-run", action="store_true", help="with --load: print what would be added, send nothing")
    a = ap.parse_args(argv)
    if a.daily:
        return daily_scan(a.in_dir)
    if a.request:
        return request_scan()
    if a.load:
        with open(a.load, encoding="utf-8") as f:
            load_drafts(json.load(f), dry_run=a.dry_run)
        return 0
    if not a.out_dir:
        ap.error("--out-dir (or --request, or --load)")
    cfg = load_config(a.config)
    flags, suppressed, drafts, summary = scan(a.in_dir, cfg, a.date, a.meta_dir, a.tables)
    write_run(a.out_dir, flags, suppressed, drafts, summary)
    print(f"scanner {cfg['version']} on {summary['scan_date']}: {summary['tables_scanned']} tables, {summary['series_seen']} series seen, {summary['series_scanned']} scanned, "
          f"{summary['pairs_tested']} pairs; {len(flags)} flags raised {summary['by_rule']}, {len(suppressed)} suppressed by known faults, {len(drafts)} drafts; {summary['seconds']} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
