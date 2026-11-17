"""ERW replication: the Flex Alert scorecard, /grid/caiso/alerts (session 7532, chain 304, 16 November 2026).

Written from docs/methods/caiso_alerts.md and docs/methods/flex_alert_scorecard.md and the public tables alone, not from
the page's code. Python standard library only.

What it does:
  1. Rebuilds every figure the page shows that the public tables can rebuild:
     - the alert days, from CAISO's notices (caiso_grid_emergencies) by the note's rule, and each day's notice types;
     - each day's alert hours from the notices' windows by the note's rule (the first Flex Alert window, else the
       emergency notices', else the Warnings', each local hour covered for at least 30 minutes);
     - each day's, year's and the pooled cut in MW, MWh and percent, from the hourly rows of flex_alert_effects (actual
       and predicted demand in each alert hour): the mean, the sum, and the sum over predicted;
     - the value at the day-ahead price, from caiso_dam_alert_day_hub_prices (the mean of SP15 and NP15, an hour only with
       both) times each alert hour's cut;
     - the model's check from its held-out rows: the days, the bias (their mean error), the threshold, the alert days
       at least that hot, the training days as hot as an alert day at or above the threshold, the mean evening price;
     - the words that turn on a figure, and the charts' axis labels.
  2. Sets each beside the figure the page draws (page_figures.json, written by site/scripts/caiso-alerts-figures.mjs,
     which draws the page with the site's own code on the same tables) and counts N of N inside half the page's last
     shown digit. A figure the public tables cannot rebuild (the bootstrap's intervals, the robustness variants, the
     model's error over hours, a day's temperature) is named with its reason, never counted as agreeing.
  3. Sets the notices table's day counts by year and type beside CAISO's own yearly counts (gehr_summary_2026-10-09.csv,
     transcribed from the report's pages 1 and 3, revision 10/09/2026, read on 16 November 2026).

Usage:
  python replicate.py                                   # on the public rows beside this file
  python replicate.py --tables <warehouse/output> --figures <page_figures.json> --write
                                                        # on the warehouse's tables; --write copies the public rows the
                                                        # page reads beside this file and writes page_figures.csv
Exit 0 when every rebuilt figure agrees, 1 when one does not.
"""
import argparse
import csv
import datetime as dt
import json
import math
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
EFFECTS, MODEL, EMERG, PRICES = "flex_alert_effects", "flex_alert_model", "caiso_grid_emergencies", "caiso_dam_alert_day_hub_prices"
E, M = "eia930:CISO", "erw:flex_alert_model"
T0 = "2018-07-01T00:00:00Z"
SAMPLE = ("2018-07-01", "2025-10-31")  # the scorecard's sample, May to October of each year (method, section 2)
# the alert-day types (method, section 3); RMO and transmission emergencies are not alert days
ALERT = ["flex_alert", "eea_watch", "eea1", "eea2", "eea3", "alert", "warning", "stage1", "stage2", "stage3", "load_interruption"]
EMERGENCY = ["eea_watch", "eea1", "eea2", "eea3", "alert", "stage1", "stage2", "stage3", "load_interruption"]
ISO_WIDE = {"ISO", "CAISO Grid"}  # the report's two spellings of the whole area (2016 to 2023, 2024 on)
# the notice names the page's ranked table prints (all regions; RMO and transmission emergencies left out)
SHORT = {"flex_alert": "Flex Alert", "eea_watch": "EEA Watch", "eea1": "EEA 1", "eea2": "EEA 2", "eea3": "EEA 3", "alert": "Alert",
         "warning": "Warning", "stage1": "Stage 1", "stage2": "Stage 2", "stage3": "Stage 3", "load_interruption": "Load interruption"}
VARIANTS = ["minimal", "base", "base_prev24sq", "base_cdh_dew", "chosen"]
# Differences found and explained (docs/reviews/caiso-alerts-faults-2026-11-16.md): each is printed as named, never as agreeing
NAMED_DIFF = {
    "series|flex_alert_effects|eia930:CISO|reduction_pct|2021-07-29T00:00:00Z":
        "rounded twice: the table holds -0.175 (three decimals) of -0.17497, and the page rounds that to -0.18; from the hours, -0.17 (faults, row 6)",
    "series|flex_alert_effects|eia930:CISO|year_reduction_mwh|2024-01-01T00:00:00Z":
        "rounded twice: the table holds -16,893.325 of -16,893.3249, and the page rounds that to -16,893.33; from the hours, -16,893.32 (faults, row 6)",
    "series|flex_alert_effects|eia930:CISO|train_days_as_hot|2023-07-26T00:00:00Z":
        "a tie: two held-out days have the day's own high, 87.926 F, at the table's three decimals; the builder compared unrounded highs and counted one (faults, row 7)",
    "notices|2020-10-01|types":
        "the Flex Alert for 1 October 2020 is dated 30 September in caiso_grid_emergencies (the day it was issued), so the page's notices cell for 2020-10-01 lacks it (faults, row 3, data machine)",
}
MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], 1)}


def read_table(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))


def load(args):
    """The four tables: from the warehouse's files (--tables) or from the public rows beside this file."""
    if args.tables:
        T = {n: read_table(os.path.join(args.tables, n + ".csv")) for n in (EFFECTS, MODEL, EMERG, PRICES)}
        series = {n: [{k: r[k] for k in ("entity", "variable", "ts_utc", "value", "unit", "freq")} for r in T[n]] for n in (EFFECTS, MODEL, PRICES)}
        notices = [{k: r.get(k, "") for k in ("event_id", "event_date", "event_type", "x_region", "x_time_frame", "x_start", "x_end", "x_label")}
                   for r in T[EMERG] if r["event_date"][:10] >= "2018-01-01"]
        return series, notices
    rows = read_table(os.path.join(HERE, "public_rows.csv"))
    series = defaultdict(list)
    for r in rows:
        series[r.pop("table")].append(r)
    return series, read_table(os.path.join(HERE, "notices_rows.csv"))


# ---------------------------------------------------------------- the notices: alert days, types and hours

def clock(s):
    """HH:MM or HH:MM:SS or H:MM AM/PM to minutes after midnight; 23:59 is midnight's 24:00 (method, section 3)."""
    s = s.strip()
    m = re.match(r"(\d{1,2}):(\d{2})(?::\d{2})?\s*(AM|PM)?$", s, re.I)
    if not m:
        raise ValueError(f"no clock in {s!r}")
    h, mi = int(m.group(1)), int(m.group(2))
    if m.group(3):
        h = h % 12 + (12 if m.group(3).upper() == "PM" else 0)
    t = h * 60 + mi
    return 1440 if t == 1439 else t


def window(n):
    """A notice's start and end as (date, minutes): x_start and x_end where the table holds them, else its time frame's
    text in the report's forms (method, section 3). None when no form is found."""
    if n["x_start"] and n["x_end"]:
        a, b = n["x_start"].split(" "), n["x_end"].split(" ")
        return (a[0], clock(a[1])), (b[0], clock(b[1]))
    tf = n["x_time_frame"]
    m = re.match(r"(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) through (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})", tf)
    if m:
        return (m.group(1), clock(m.group(2))), (m.group(3), clock(m.group(4)))
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})(?: at)? (\d{1,2}:\d{2}) through (\d{1,2})/(\d{1,2})/(\d{4})(?: at)? (\d{1,2}:\d{2})", tf)
    if m:
        g = m.groups()
        return (f"{g[2]}-{int(g[0]):02d}-{int(g[1]):02d}", clock(g[3])), (f"{g[6]}-{int(g[4]):02d}-{int(g[5]):02d}", clock(g[7]))
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4}) (\d{1,2}:\d{2}):\d{2} through (\d{1,2}:\d{2}):\d{2}", tf)
    if m:  # the day is the text's, not the row's (method, section 3: the Flex Alert dated 2020-09-30 is for 2020-10-01)
        g = m.groups()
        d = f"{g[2]}-{int(g[0]):02d}-{int(g[1]):02d}"
        return (d, clock(g[3])), (d, clock(g[4]))
    m = re.match(r"([A-Z][a-z]+) (\d{1,2}) at (\d{1,2}:\d{2} [AP]M) to ([A-Z][a-z]+) (\d{1,2}) at (\d{1,2}:\d{2} [AP]M)", tf)
    if m:
        y = n["event_date"][:4]
        return (f"{y}-{MONTHS[m.group(1)]:02d}-{int(m.group(2)):02d}", clock(m.group(3))), (f"{y}-{MONTHS[m.group(4)]:02d}-{int(m.group(5)):02d}", clock(m.group(6)))
    return None


def alert_days(notices):
    """{day: {"types": set of every type that day (all regions), "iso": set of alert types ISO-wide, "rows": [...]}}."""
    out = defaultdict(lambda: {"types": set(), "iso": set(), "rows": []})
    for n in notices:
        d = n["event_date"][:10]
        w = window(n) if n["event_type"] in ALERT else None
        if w and w[0][0] == w[1][0] and w[0][0] != d and not n["x_start"]:
            d = w[0][0]  # a single-day window whose text names another day than the row's: the text's day
        out[d]["types"].add(n["event_type"])
        out[d]["rows"].append(n)
        if n["event_type"] in ALERT and n["x_region"] in ISO_WIDE:
            out[d]["iso"].add(n["event_type"])
    return out


def hours_of(day, rows):
    """The local hours of an alert day, by the first of: its Flex Alerts, its emergency notices, its Warnings. Each
    notice covers the day with its daily clock window; an hour counts when covered for at least 30 minutes."""
    for kinds in (["flex_alert"], EMERGENCY, ["warning"]):
        spans = []
        for n in rows:
            if n["event_type"] in kinds and n["x_region"] in ISO_WIDE:
                w = window(n)
                if w:
                    (d0, a), (d1, b) = w
                    if d0 != d1:  # several days: each covered day takes the clock window
                        pass
                    spans.append((a, b if b > a else 1440))
        if spans:
            hrs = [h for h in range(24) if sum(max(0, min(b, 60 * h + 60) - max(a, 60 * h)) for a, b in merge(spans)) >= 30]
            return hrs, False
    return list(range(16, 21)), True


def merge(spans):
    out = []
    for a, b in sorted(spans):
        if out and a <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


# ---------------------------------------------------------------- the effects' rows

def pacific(ts):
    """The Pacific (daylight time, UTC-7) day and hour of a UTC instant (every hour of the sample is daylight time)."""
    t = dt.datetime.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S") - dt.timedelta(hours=7)
    return t.strftime("%Y-%m-%d"), t.hour


def key(table, entity, variable, ts):
    return f"series|{table}|{entity}|{variable}|{ts}"


def rebuild(series, notices):
    """Every figure the tables can rebuild, by its page key (or a key of this file for figures with none), and the named."""
    ours, named, notes = {}, {}, []
    eff = series[EFFECTS]
    p1d = defaultdict(dict)
    hourly = defaultdict(lambda: defaultdict(dict))
    p1y = defaultdict(dict)
    for r in eff:
        if r["freq"] == "P1D":
            p1d[r["ts_utc"][:10]][r["variable"]] = (r["ts_utc"], float(r["value"]))
        elif r["freq"] == "PT1H":
            d, h = pacific(r["ts_utc"])
            hourly[d][h][r["variable"]] = float(r["value"])
            hourly[d][h]["ts"] = r["ts_utc"]
        elif r["freq"] == "P1Y":
            p1y[r["ts_utc"][:4]][r["variable"]] = (r["ts_utc"], float(r["value"]))
    mod = {}
    held = defaultdict(dict)
    for r in series[MODEL]:
        if r["variable"].startswith("coef_"):
            continue
        if r["ts_utc"] == T0:
            mod[r["variable"]] = float(r["value"])
        else:
            held[r["ts_utc"][:10]][r["variable"]] = float(r["value"])
    days = sorted(p1d)

    # --- the alert days, from the notices by the rule, against the days the table holds
    ad = alert_days(notices)
    rule_days = sorted(d for d, x in ad.items() if x["iso"] and SAMPLE[0] <= d <= SAMPLE[1])
    left_out = [d for d in rule_days if d not in p1d]
    extra = [d for d in days if d not in rule_days]
    notes.append(f"alert days by the rule from the notices, {SAMPLE[0]} to {SAMPLE[1]}: {len(rule_days)}; held by the table: {len(days)}; "
                 f"by the rule and not held: {', '.join(left_out) or 'none'}; held and not by the rule: {', '.join(extra) or 'none'}")
    later = sorted(d for d, x in ad.items() if x["iso"] and d > SAMPLE[1])
    notes.append(f"alert days in the notices after the sample ({SAMPLE[1]}): {len(later)}; notices of any type after 2024-12-31: "
                 f"{sum(1 for n in notices if n['event_date'][:10] > '2024-12-31')} ({', '.join(sorted({n['event_type'] for n in notices if n['event_date'][:10] > '2024-12-31'}))})")

    # --- each day
    alert_hours_of = {}
    for d in days:
        hrs = sorted(h for h, v in hourly[d].items() if v.get("alert_hour") == 1)
        alert_hours_of[d] = hrs
        ts = p1d[d]["reduction_mw"][0]
        cut = [hourly[d][h]["predicted_mw"] - hourly[d][h]["actual_mw"] for h in hrs]
        pred = sum(hourly[d][h]["predicted_mw"] for h in hrs)
        ours[key(EFFECTS, E, "reduction_mw", ts)] = sum(cut) / len(cut)
        ours[key(EFFECTS, E, "reduction_pct", ts)] = 100 * sum(cut) / pred
        ours[key(EFFECTS, E, "alert_first_hour", ts)] = hrs[0]
        ours[key(EFFECTS, E, "alert_last_hour", ts)] = hrs[-1] + 1
        # the same hours from the notices alone
        nh, assumed = hours_of(d, ad[d]["rows"]) if d in ad else (list(range(16, 21)), True)
        ours[f"notices|{d}|alert_hours"] = f"{nh[0]}:00 to {nh[-1] + 1}:00" + (" (assumed)" if assumed else "") if nh else "none"
        ours[f"notices|{d}|types"] = ", ".join(sorted(SHORT[t] for t in ad[d]["types"] if t in SHORT)) if d in ad else ""
        ours[f"chart|{d}|alert_boxes"] = len(hrs)
        vals = [v[k] for v in hourly[d].values() for k in ("actual_mw", "predicted_mw_lo", "predicted_mw_hi") if k in v]
        ours[f"chart|{d}|gw_top"] = f"{round_half_up(max(vals) / 1000)} GW"
        ours[f"chart|{d}|gw_bottom"] = f"{round_half_up(min(vals) / 1000)} GW"
        ours[f"panel|{d}|cut"] = sum(cut) / len(cut)
        for v in ("temp_max_f",):
            named[key(EFFECTS, E, v, ts)] = "the day's population-weighted high: NOAA's hourly readings (noaa_isd_hourly) are not on this machine; the notebook rebuilds it"
        for v in ("reduction_mw_lo", "reduction_mw_hi"):
            named[key(EFFECTS, E, v, ts)] = "the bootstrap's 90 percent interval: 1,000 refits of the 24 hourly models on resampled weeks (seed 20261002) need the panel; the notebook rebuilds it"
        if "value_usd" in p1d[d]:
            for v in ("value_usd_lo", "value_usd_hi"):
                named[key(EFFECTS, E, v, ts)] = "the bootstrap's interval of the value (as above)"
    # the training days as hot: for an alert day at or above the held-out threshold, every training day as hot is in the
    # hottest tenth, whose highs the model's rows hold
    thr = min(v["heldout_temp_max_f"] for v in held.values() if "heldout_temp_max_f" in v)
    for d in days:
        ts = p1d[d]["reduction_mw"][0]
        t = p1d[d]["temp_max_f"][1]
        if t >= mod["heldout_threshold_temp_f"]:
            ours[key(EFFECTS, E, "train_days_as_hot", ts)] = sum(1 for v in held.values() if v.get("heldout_temp_max_f", -1) >= t)
        else:
            named[key(EFFECTS, E, "train_days_as_hot", ts)] = "below the held-out threshold the training days' highs are not in the tables (they are in the panel)"

    # --- the value at the day-ahead price
    price = defaultdict(dict)
    for r in series[PRICES]:
        if r["variable"] == "lmp_dam":
            price[r["ts_utc"]][r["entity"]] = float(r["value"])
    hub = {}
    for ts, v in price.items():
        if "caiso:TH_SP15_GEN-APND" in v and "caiso:TH_NP15_GEN-APND" in v:
            hub[ts] = (v["caiso:TH_SP15_GEN-APND"] + v["caiso:TH_NP15_GEN-APND"]) / 2
    pooled_value, value_hours = 0.0, 0
    for d in days:
        vh = [h for h in alert_hours_of[d] if hourly[d][h]["ts"] in hub]
        if not vh:
            continue
        val = sum((hourly[d][h]["predicted_mw"] - hourly[d][h]["actual_mw"]) * hub[hourly[d][h]["ts"]] for h in vh)
        ours[key(EFFECTS, E, "value_usd", p1d[d]["reduction_mw"][0])] = val
        pooled_value += val
        value_hours += len(vh)
    ours[key(MODEL, M, "pooled_value_usd", T0)] = pooled_value
    ours[key(MODEL, M, "pooled_value_hours", T0)] = value_hours
    ours["words|days_priced"] = sum(1 for d in days if any(hourly[d][h]["ts"] in hub for h in alert_hours_of[d]))
    ours["words|days_shown"] = len(days)

    # --- each year and the pooled figures
    by_year = defaultdict(list)
    for d in days:
        by_year[d[:4]].append(d)
    for y, ds in sorted(by_year.items()):
        ts = f"{y}-01-01T00:00:00Z"
        cut = [hourly[d][h]["predicted_mw"] - hourly[d][h]["actual_mw"] for d in ds for h in alert_hours_of[d]]
        ours[key(EFFECTS, E, "year_days", ts)] = len(ds)
        ours[key(EFFECTS, E, "year_hours", ts)] = len(cut)
        ours[key(EFFECTS, E, "year_reduction_mw", ts)] = sum(cut) / len(cut)
        ours[key(EFFECTS, E, "year_reduction_mwh", ts)] = sum(cut)
        for v in ("year_reduction_mw_lo", "year_reduction_mw_hi"):
            named[key(EFFECTS, E, v, ts)] = "the bootstrap's 90 percent interval (as for a day)"
    cut = [hourly[d][h]["predicted_mw"] - hourly[d][h]["actual_mw"] for d in days for h in alert_hours_of[d]]
    pred = sum(hourly[d][h]["predicted_mw"] for d in days for h in alert_hours_of[d])
    ours[key(MODEL, M, "pooled_days", T0)] = len(days)
    ours[key(MODEL, M, "pooled_hours", T0)] = len(cut)
    ours[key(MODEL, M, "pooled_reduction_mw", T0)] = sum(cut) / len(cut)
    ours[key(MODEL, M, "pooled_reduction_mwh", T0)] = sum(cut)
    ours[key(MODEL, M, "pooled_reduction_pct", T0)] = 100 * sum(cut) / pred
    ours[key(MODEL, M, "variant_chosen_pooled_reduction_mw", T0)] = sum(cut) / len(cut)  # the chosen variant is the model used
    ours["words|ran"] = "below" if sum(cut) >= 0 else "above"
    ours["words|last_alert"] = days[-1]
    ours["words|h1_years"] = f"{days[0][:4]} to {days[-1][:4]}"
    ours["words|report_ends"] = max(n["event_date"][:10] for n in notices)
    ours["words|later_alert_days"] = len({n["event_date"][:10] for n in notices if n["event_type"] in ALERT and n["event_date"][:10] > days[-1]})
    for v in ("pooled_reduction_mw_lo", "pooled_reduction_mw_hi", "pooled_reduction_mwh_lo", "pooled_reduction_mwh_hi", "pooled_value_usd_lo", "pooled_value_usd_hi"):
        named[key(MODEL, M, v, T0)] = "the bootstrap's 90 percent interval (as for a day)"
    lo, hi = mod["pooled_reduction_mw_lo"], mod["pooled_reduction_mw_hi"]
    ours["words|zero"] = "includes zero" if lo < 0 < hi else "excludes zero"

    # --- the model's check, from its held-out rows
    errs = [v["heldout_error_mw"] for v in held.values() if "heldout_error_mw" in v]
    ours[key(MODEL, M, "oos_days", T0)] = len(errs)
    ours[key(MODEL, M, "oos_bias_mw", T0)] = sum(errs) / len(errs)
    ours[key(MODEL, M, "variant_chosen_oos_bias_mw", T0)] = sum(errs) / len(errs)
    ours[key(MODEL, M, "heldout_threshold_temp_f", T0)] = thr
    ours[key(MODEL, M, "alert_days_hotter_than_threshold", T0)] = sum(1 for d in days if p1d[d]["temp_max_f"][1] >= mod["heldout_threshold_temp_f"])
    pr = [v["heldout_price_usd_mwh"] for v in held.values() if "heldout_price_usd_mwh" in v]
    ours[key(MODEL, M, "heldout_price_mean_usd_mwh", T0)] = sum(pr) / len(pr)
    temps = [v["heldout_temp_max_f"] for v in held.values() if "heldout_error_mw" in v and "heldout_temp_max_f" in v]
    em = max(abs(e) for e in errs)
    ours["chart|check|labels"] = [f"{-em:,.0f}" if round_half_up(-em) != 0 else "0", "0", f"{round_half_up(em):,}", f"{min(temps):.1f} F", f"{max(temps):.1f} F, the day's highest weighted temperature"]
    ours["chart|check|dots"] = len(temps)
    for v in ("oos_rmse_mw", "oos_mape_pct"):
        named[key(MODEL, M, v, T0)] = "an error over the held-out hours: the tables hold each held-out day's mean error, not its hours"
    for vid in VARIANTS:
        for v in ("oos_bias_mw", "oos_rmse_mw", "pooled_reduction_mw", "pooled_reduction_mw_lo", "pooled_reduction_mw_hi"):
            k = key(MODEL, M, f"variant_{vid}_{v}", T0)
            if k not in ours:
                named[k] = "a robustness specification's figure: its 24 refits and 200 replicates need the panel; the method's table, section 6, prints it"
    # the year chart's ticks and bars
    ylo = [p1y[y]["year_reduction_mw_lo"][1] for y in sorted(p1y)]
    yhi = [p1y[y]["year_reduction_mw_hi"][1] for y in sorted(p1y)]
    mn, mx = min([0] + ylo), max([0] + yhi)
    ticks = []
    for t in (mn, mn / 2, 0, mx / 2, mx):
        if t not in ticks:
            ticks.append(t)
    ours["chart|year|labels"] = [f"{round_half_up(t):,}" for t in ticks] + sorted(p1y)
    return ours, named, notes, {"days": days, "rule_days": rule_days, "left_out": left_out, "notices": ad}


def round_half_up(x):
    """JavaScript's Math.round."""
    return int(math.floor(x + 0.5))


# ---------------------------------------------------------------- the comparison

def parse_shown(s):
    """A figure as the page prints it: its value and half its last digit."""
    s = s.strip()
    mult = 1.0
    for w, f in ((" billion", 1e9), (" million", 1e6)):
        if s.endswith(w):
            s, mult = s[: -len(w)], f
    t = s.replace(",", "")
    dec = len(t.split(".")[1]) if "." in t else 0
    return float(t) * mult, 0.5 * 10 ** (-dec) * mult


def compare(ours, named, fig):
    out = []
    by_key = defaultdict(list)
    for n in fig["nums"]:
        by_key[n["key"]].append(n)
    for k, ns in by_key.items():
        for i, n in enumerate(ns):
            v, half = parse_shown(n["shown"])
            if k in ours:
                o = ours[k]
                # a day's cut appears twice (the ranked table and its panel): both are held to the same figure
                diff = o - v
                out.append((k, n["section"], n["shown"], f"{o:.6f}", f"{diff:.6f}", "agrees" if abs(diff) <= half + 1e-9 else "DIFFERS"))
            elif k in named:
                out.append((k, n["section"], n["shown"], "", "", "named: " + named[k]))
            else:
                out.append((k, n["section"], n["shown"], "", "", "NOT REBUILT"))
    # the figures without a key
    for r in fig["ranked"]:
        d = r["day"]
        hrs = re.sub(r"\s+", "", r["hours"]).replace("to", " to ").replace("(assumed)", " (assumed)")
        out.append((f"notices|{d}|alert_hours", "Every alert day, ranked", hrs, ours[f"notices|{d}|alert_hours"], "", "agrees" if hrs == ours[f"notices|{d}|alert_hours"] else "DIFFERS"))
        page_types = ", ".join(sorted(t.strip() for t in r["notices"].split(",") if t.strip()))
        out.append((f"notices|{d}|types", "Every alert day, ranked", r["notices"], ours[f"notices|{d}|types"], "", "agrees" if page_types == ours[f"notices|{d}|types"] else "DIFFERS"))
    days_svg = [s for s in fig["svgs"] if s["label"].startswith("Actual and predicted")]
    for p, s in zip(fig["panels"], days_svg):
        d = p["day"]
        for k, got in ((f"chart|{d}|gw_top", s["texts"][0]), (f"chart|{d}|gw_bottom", s["texts"][1])):
            out.append((k, "Each alert day through the evening", got, ours[k], "", "agrees" if got == ours[k] else "DIFFERS"))
        out.append((f"chart|{d}|alert_boxes", "Each alert day through the evening", str(s["rects"]), str(ours[f"chart|{d}|alert_boxes"]), "", "agrees" if s["rects"] == ours[f"chart|{d}|alert_boxes"] else "DIFFERS"))
    for label, k in (("Model error", "chart|check|labels"), ("Estimated demand reduction by year", "chart|year|labels")):
        s = next(x for x in fig["svgs"] if x["label"].startswith(label))
        out.append((k, "chart", " / ".join(s["texts"]), " / ".join(ours[k]), "", "agrees" if s["texts"] == ours[k] else "DIFFERS"))
    s = next(x for x in fig["svgs"] if x["label"].startswith("Model error"))
    out.append(("chart|check|dots", "chart", str(s["circles"]), str(ours["chart|check|dots"]), "", "agrees" if s["circles"] == ours["chart|check|dots"] else "DIFFERS"))
    w = fig["words"]
    for k, got in (("words|days_priced", w["days_priced"]), ("words|days_shown", w["days_shown"]), ("words|ran", w["ran"]), ("words|zero", w["zero"]), ("words|last_alert", w["last_alert"]),
                   ("words|report_ends", w.get("report_ends")), ("words|later_alert_days", w.get("later_alert_days"))):
        out.append((k, "words", str(got), str(ours[k]), "", "agrees" if str(got) == str(ours[k]) else "DIFFERS"))
    h1y = (re.search(r"(\d{4} to \d{4})", w["h1"]) or [None, None])[1] if w["h1"] else None
    out.append(("words|h1_years", "head", str(h1y), ours["words|h1_years"], "", "agrees" if h1y == ours["words|h1_years"] else "DIFFERS"))
    return [r[:5] + ("named difference: " + NAMED_DIFF[r[0]],) if r[5] == "DIFFERS" and r[0] in NAMED_DIFF else r for r in out]


def crosscheck(notices):
    """The notices table's distinct days by year and type, beside CAISO's own yearly counts."""
    days = defaultdict(set)
    iso = defaultdict(set)
    for n in notices:
        k = (n["event_date"][:4], n["event_type"])
        days[k].add(n["event_date"][:10])
        if n["x_region"] in ISO_WIDE:
            iso[k].add(n["event_date"][:10])
    rows = []
    for r in read_table(os.path.join(HERE, "gehr_summary_2026-10-09.csv")):
        k = (r["year"], r["event_type"])
        ours = len(days.get(k, ()))
        rows.append({"year": r["year"], "event_type": r["event_type"], "caiso_days": int(r["caiso_days"]), "table_days_any_region": ours,
                     "table_days_iso_wide": len(iso.get(k, ())), "report_page": r["page"], "agrees": "yes" if ours == int(r["caiso_days"]) else "no"})
    return rows


def write_public(series, notices, info):
    """The rows the page reads, beside this file, so the replication runs without the warehouse."""
    with open(os.path.join(HERE, "public_rows.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["table", "entity", "variable", "ts_utc", "value", "unit", "freq"])
        days = set(info["days"])
        for t in (EFFECTS, MODEL, PRICES):
            for r in series[t]:
                if t == MODEL and r["variable"].startswith("coef_"):
                    continue
                if t == PRICES and pacific(r["ts_utc"])[0] not in days:
                    continue
                w.writerow([t, r["entity"], r["variable"], r["ts_utc"], r["value"], r["unit"], r["freq"]])
    with open(os.path.join(HERE, "notices_rows.csv"), "w", encoding="utf-8", newline="") as f:
        cols = ["event_id", "event_date", "event_type", "x_region", "x_time_frame", "x_start", "x_end", "x_label"]
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for n in sorted(notices, key=lambda n: (n["event_date"], n["event_id"])):
            w.writerow({c: n[c] for c in cols})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", help="the warehouse's tables (warehouse/output)")
    ap.add_argument("--figures", default=os.path.join(HERE, "page_figures.json"), help="the page's figures (site/scripts/caiso-alerts-figures.mjs)")
    ap.add_argument("--write", action="store_true", help="write the public rows and page_figures.csv beside this file")
    args = ap.parse_args()
    series, notices = load(args)
    ours, named, notes, info = rebuild(series, notices)
    with open(args.figures, encoding="utf-8") as f:
        fig = json.load(f)
    rows = compare(ours, named, fig)
    cc = crosscheck(notices)
    if args.write:
        if args.tables:
            write_public(series, notices, info)
        with open(os.path.join(HERE, "page_figures.csv"), "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["key", "section", "page", "ours", "difference", "status"])
            w.writerows(rows)
        with open(os.path.join(HERE, "crosscheck_rows.csv"), "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(cc[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(cc)
    agree = sum(1 for r in rows if r[5] == "agrees")
    nd = [r for r in rows if r[5].startswith("named difference")]
    nm = sum(1 for r in rows if r[5].startswith("named: "))
    bad = [r for r in rows if r[5] in ("DIFFERS", "NOT REBUILT")]
    print(f"tables as retrieved: {', '.join(f'{k} {v}' for k, v in fig['tables'].items())}")
    for n in notes:
        print(n)
    print(f"figures of the page: {len(rows)}. Rebuilt from the public tables: {agree + len(nd) + len(bad)}, of which {agree} agree inside half the "
          f"page's last shown digit, {len(nd)} differ and are named, {len(bad)} fail. Not rebuildable from the public tables, named: {nm}.")
    for r in nd + bad:
        print("  " + " | ".join(r))
    ok_cc = sum(1 for r in cc if r["agrees"] == "yes")
    print(f"CAISO's own yearly day counts (revision 10/09/2026), 2018 to 2026: {ok_cc} of {len(cc)} year-type counts equal the notices table's")
    for r in cc:
        if r["agrees"] != "yes":
            print(f"  {r['year']} {r['event_type']}: CAISO {r['caiso_days']}, table {r['table_days_any_region']}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
