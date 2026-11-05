#!/usr/bin/env python3
"""Session 1114: a second set of thirty questions for Ask, each key computed from the live set before any model is asked.

Energy Research Warehouse (ERW). No model call of any kind. Reads only: the live set's `series` view (Supabase REST,
the anon key from the repository's .env), paged 1,000 rows at a time. Writes questions_s1114.yaml beside this file.

    python expected_s1114.py

Modelled on warehouse/chat/eval/regrade_s539.py (its rows, aggregate and build_keys). Each question id has a SPEC row
(table, entity, variable, aggregation, period, divisor), or a DIFF row (a difference of two values). The grain of a
period is read from its form:

    "YYYY-MM"            a month (the table's own monthly row, ts_utc YYYY-MM-01)
    "YYYY-MM-DD"         a day (the table's own daily row, ts_utc YYYY-MM-DDT00:00:00Z: the publisher's local day)
    "YYYY-MM-DDTHH"      an hour, by its ts_utc (UTC), both ends included

Aggregations: month (the one period's value), mean, sum, max and min (with the month, day or hour they occur in), and
mean_weekdays (a daily series of trading days: every Monday to Friday of the period must be held, a weekend is not
expected). Every month, day or hour of a period must be held, or the run stops: nothing is filled. A tie at a max or a
min stops the run too (the "which month" would have two answers). COMPLETE names the rows that must show a whole
period (the hours held equal to the hours in the month, or no day left out); ALSO names the other tables that may
hold the same figure: a table is added to `tables` only when its own figure is within the question's tolerance.
"""

import datetime as dt
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if not os.path.exists(os.path.join(ROOT, ".env")):   # a worktree has no .env: the main checkout beside it holds the keys
    ROOT = os.path.join(os.path.dirname(ROOT), "erw")
OUT = os.path.join(HERE, "questions_s1114.yaml")
KEYS_JSON = os.path.join(HERE, "keys_s1114.json")
TODAY = "2026-10-23"

CP, MR, BS, SB = "cost_of_power_monthly", "merchant_revenue_monthly", "battery_stack_monthly", "storage_buildout_monthly"
PBS, PP, ASM, ASH, ASD = "price_board_spreads", "ercot_peak_premium_monthly", "ercot_as_prices_monthly", "ercot_as_prices", "ercot_as_prices_daily"
CI, CU, SG, RS = "carbon_intensity_monthly", "iso_curtailment_monthly", "state_generation_mix_monthly", "eia_retail_sales_monthly"
DAM, DEM, FUEL, TRD = "iso_dam_hub_prices", "eia930_all_demand", "eia_fuel_spot_prices", "iso_trader_daily"
E, SP15, SPPN = "ercot:HB_HUBAVG", "caiso:TH_SP15_GEN-APND", "spp:SPPNORTH_HUB"
SEP26 = ("2026-09", "2026-09")
SEP26_DAYS = ("2026-09-01", "2026-09-30")
Y2025 = ("2025-01", "2025-12")
JS26 = ("2026-01", "2026-09")
L12 = ("2025-10", "2026-09")
AUG26 = ("2026-08", "2026-08")

# id: (table, entity, variable, aggregation, period, divisor)
SPEC = {
    "t01": (CP, SPPN, "da_simple_mean", "month", SEP26, 1),
    "t02": (PBS, E, "spark_spread_7", "mean", SEP26_DAYS, 1),
    "t03": (ASM, "ercot:REGUP", "mcpc_dam_mean", "month", SEP26, 1),
    "t04": (PP, E, "all_max", "max", Y2025, 1),
    "t05": (PP, E, "n_negative", "sum", JS26, 1),
    "t07": (DAM, SP15, "lmp_dam", "mean", ("2026-10-01T00", "2026-10-14T23"), 1),
    "t08": (PBS, SP15, "spark_spread_7", "min", SEP26_DAYS, 1),
    "t09": (ASM, "ercot:ECRS", "mcpc_dam_mean", "max", Y2025, 1),
    "f01": (BS, E, "foresight_4h_revenue_total_usd_per_mw", "sum", JS26, 1),
    "f02": (BS, SP15, "dayahead_4h_revenue_total_usd_per_mw", "month", SEP26, 1),
    "f03": (MR, E, "solar_revenue_per_mw", "sum", L12, 1),
    "f04": (MR, SPPN, "wind_revenue_per_mw", "max", Y2025, 1),
    "f05": (SB, "iso:ercot", "battery_operating_mw", "month", AUG26, 1),
    "f07": (SB, "iso:caiso", "battery_operating_mwh_per_mw", "month", AUG26, 1),
    "f08": (MR, SP15, "battery_4h_revenue_per_mw", "sum", Y2025, 1),
    "f10": (MR, E, "solar_capture_rate", "min", L12, 1),
    "p01": (CI, "eia930:ERCO", "intensity_generation", "month", SEP26, 1),
    "p02": (CI, "eia930:US48", "intensity_demand", "mean", JS26, 1),
    "p03": (CU, "caiso:ISO", "curtailed_solar_mwh", "sum", JS26, 1),
    "p04": (CU, "spp:SPP", "curtailed_wind_mwh", "max", Y2025, 1),
    "p05": (SG, "eia:TX", "net_generation_wind_mwh", "month", AUG26, 1),
    "p06": (SG, "eia:CA", "net_generation_solar_mwh", "sum", Y2025, 1),
    "p07": (RS, "eia:retail_sales:TX:ALL", "retail_sales", "month", AUG26, 1),
    "p09": (DEM, "eia930:US48", "demand_mw", "max", ("2026-10-01T00", "2026-10-21T23"), 1),
    "p10": (FUEL, "eia:henry_hub", "spot_price", "mean_weekdays", SEP26_DAYS, 1),
}
# id: ((table, entity, variable, period), (table, entity, variable, period)): the first less the second
DIFF = {
    "t06": ((CP, E, "da_simple_mean", "2026-09"), (CP, SP15, "da_simple_mean", "2026-09")),
    "t10": ((CP, E, "rt_simple_mean", "2026-09"), (CP, E, "da_simple_mean", "2026-09")),
    "f06": ((SB, "iso:ercot", "battery_operating_mw", "2026-08"), (SB, "iso:ercot", "battery_operating_mw", "2025-08")),
    "f09": ((BS, E, "foresight_4h_revenue_total_usd_per_mw", "2026-08"), (BS, SP15, "foresight_4h_revenue_total_usd_per_mw", "2026-08")),
    "p08": ((RS, "eia:retail_sales:TX:COM", "retail_sales", "2026-08"), (RS, "eia:retail_sales:TX:COM", "retail_sales", "2025-08")),
}
# id: [(table, entity, held, whole, period)]: held must equal whole in every month of the period (whole None: held must be 0)
COMPLETE = {
    "t01": [(CP, SPPN, "da_hours", "hours_in_month", SEP26)],
    "t03": [(ASM, "ercot:REGUP", "mcpc_dam_hours", "mcpc_dam_hours_in_month", SEP26)],
    "t06": [(CP, E, "da_hours", "hours_in_month", SEP26), (CP, SP15, "da_hours", "hours_in_month", SEP26)],
    "t09": [(ASM, "ercot:ECRS", "mcpc_dam_hours", "mcpc_dam_hours_in_month", Y2025)],
    "t10": [(CP, E, "rt_hours", "hours_in_month", SEP26), (CP, E, "da_hours", "hours_in_month", SEP26)],
    "f01": [(BS, E, "foresight_4h_days_left_out", None, JS26)],
    "f02": [(BS, SP15, "dayahead_4h_days_left_out", None, SEP26)],
    "f09": [(BS, E, "foresight_4h_days_left_out", None, AUG26), (BS, SP15, "foresight_4h_days_left_out", None, AUG26)],
}
# id: [(table, entity, variable, aggregation, period)]: other tables that may hold the figure (checked, never required)
ALSO = {
    "t01": [(PBS, SPPN, "da_daily_mean", "mean", SEP26_DAYS), (TRD, SPPN, "da_mean_usd", "mean", SEP26_DAYS)],
    "t03": [(ASH, "ercot:REGUP", "mcpc_dam", "mean_local:America/Chicago", SEP26), (ASD, "ercot:REGUP", "mcpc_dam_mean", "mean", SEP26_DAYS)],
    "f05": [("storage_owners_monthly", "iso:ercot", "ercot_operating_mw", "month", AUG26)],
    "p10": [(PBS, "eia:henry_hub", "henry_hub", "mean_weekdays", SEP26_DAYS)],
}

# id: (grid, via, question, unit words for the note)
Q = {
    "t01": ("SPP", "grid", "What was the simple average day-ahead price at SPP's North hub in September 2026 (the local calendar month), in USD per MWh?"),
    "t02": ("ERCOT", "grid", "What was the average of the daily indicative spark spreads at ERCOT's hub average (the day-ahead daily mean less 7.0 MMBtu/MWh times Henry Hub) over the 30 operating days of September 2026, in USD per MWh?"),
    "t03": ("ERCOT", "grid", "What was the mean day-ahead clearing price of ERCOT's Regulation Up service in September 2026 (the Central-time month), in USD per MW per hour?"),
    "t04": ("ERCOT", "grid", "Which calendar month of 2025 (Central time) had the highest single 15-minute real-time price at ERCOT's hub average, and what was that price, in USD per MWh?"),
    "t05": ("ERCOT", "grid", "How many 15-minute real-time intervals at ERCOT's hub average had a price at or below zero from January to September 2026 (the nine Central-time months summed)?"),
    "t06": ("ERCOT", "general", "In September 2026, how much higher or lower was the simple average day-ahead price at ERCOT's hub average than at CAISO's SP15 hub, in USD per MWh?"),
    "t07": ("CAISO", "grid", "What was the mean of the hourly day-ahead prices at CAISO's SP15 hub over the 336 hours starting 1 October 2026 00:00 UTC through the hour starting 14 October 2026 23:00 UTC, in USD per MWh?"),
    "t08": ("CAISO", "grid", "On which operating day of September 2026 was the daily indicative spark spread at CAISO's SP15 hub (day-ahead daily mean less 7.0 MMBtu/MWh times Henry Hub) lowest, and what was it, in USD per MWh?"),
    "t09": ("ERCOT", "grid", "Which month of 2025 had the highest mean day-ahead price for ERCOT Contingency Reserve Service (ECRS), and what was that monthly mean, in USD per MW per hour?"),
    "t10": ("ERCOT", "grid", "In September 2026, by how much did the simple average real-time price at ERCOT's hub average differ from the simple average day-ahead price (real-time less day-ahead), in USD per MWh?"),
    "f01": ("ERCOT", "grid", "For a 4-hour battery at ERCOT's hub average with perfect foresight, what was the total revenue (energy plus ancillary services) summed over January to September 2026, in USD per MW?"),
    "f02": ("CAISO", "grid", "What did a 4-hour battery at CAISO's SP15 hub earn in total on the day-ahead strategy in September 2026, in USD per MW?"),
    "f03": ("ERCOT", "grid", "How much did solar at ERCOT's hub average earn per MW over the twelve months from October 2025 to September 2026 (the monthly revenues per MW summed), in USD per MW?"),
    "f04": ("SPP", "grid", "Which month of 2025 was best for wind at SPP's North hub by revenue per MW, and how much did wind earn that month, in USD per MW?"),
    "f05": ("ERCOT", "grid", "How many MW of battery storage were operating in ERCOT as of August 2026?"),
    "f06": ("ERCOT", "grid", "By how many MW did ERCOT's operating battery storage capacity change from August 2025 to August 2026?"),
    "f07": ("CAISO", "grid", "What was the average duration of CAISO's operating battery fleet in August 2026, in MWh of energy per MW of power?"),
    "f08": ("CAISO", "grid", "Over calendar year 2025, how much did a 4-hour battery at CAISO's SP15 hub earn per MW on the generator page's rule (the twelve monthly revenues per MW summed), in USD per MW?"),
    "f09": ("ERCOT", "general", "In August 2026, how much more or less did a 4-hour battery with perfect foresight earn in total at ERCOT's hub average than at CAISO's SP15 hub, in USD per MW?"),
    "f10": ("ERCOT", "grid", "Over the twelve months from October 2025 to September 2026, which month had the lowest solar capture rate at ERCOT's hub average, and what was that rate, as a percent of the flat price?"),
    "p01": ("ERCOT", "grid", "What was the carbon intensity of ERCOT's generation in September 2026, in kg of CO2 per MWh?"),
    "p02": ("US48", "general", "What was the average of the nine monthly carbon intensities of US Lower 48 demand from January to September 2026, in kg of CO2 per MWh?"),
    "p03": ("CAISO", "grid", "How many MWh of solar did CAISO curtail in total from January to September 2026 (the nine monthly totals summed)?"),
    "p04": ("SPP", "grid", "Which month of 2025 had the most wind curtailment in SPP, and how many MWh of wind were curtailed that month?"),
    "p05": ("ERCOT", "general", "How many MWh did wind generate in Texas in August 2026, by EIA's monthly state net generation figures?"),
    "p06": ("CAISO", "general", "How many MWh of solar did California generate over calendar year 2025, by EIA's monthly state net generation figures (the twelve months summed)?"),
    "p07": ("ERCOT", "general", "What were total retail electricity sales in Texas, all sectors, in August 2026, in MWh?"),
    "p08": ("ERCOT", "general", "By how many MWh did Texas commercial-sector retail electricity sales change from August 2025 to August 2026?"),
    "p09": ("US48", "general", "What was the highest hourly demand in the US Lower 48 over the hours starting 1 October 2026 00:00 UTC through 21 October 2026 23:00 UTC, in MW, and on which day (UTC) did it occur?"),
    "p10": ("US48", "general", "What was the average Henry Hub natural gas spot price over the trading days of September 2026, in USD per MMBtu?"),
}
ORDER = [f"{p}{i:02d}" for p in "tfp" for i in range(1, 11)]


def env(name):
    if os.environ.get(name):
        return os.environ[name].strip()
    for line in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
        m = re.match(rf"^{name}=(.*)$", line.strip())
        if m:
            return m.group(1).strip().strip('"')
    raise SystemExit(f"{name} not in .env")


def base_url():
    u = env("SUPABASE_URL").rstrip("/")
    return u if u.endswith("/rest/v1") else u + "/rest/v1"


URL = base_url()
KEY = env("SUPABASE_ANON_KEY")
HEAD = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
CACHE = {}


def rows(table, entity, variable, since=None, until=None):
    """Every (ts_utc, value) row of one series, ordered, 1,000 a page. since and until bound ts_utc (until excluded)."""
    ck = (table, entity, variable, since, until)
    if ck in CACHE:
        return CACHE[ck]
    out, off = [], 0
    while True:
        q = [("table_name", f"eq.{table}"), ("entity", f"eq.{entity}"), ("variable", f"eq.{variable}"),
             ("select", "ts_utc,value"), ("order", "ts_utc"), ("limit", "1000"), ("offset", str(off))]
        if since:
            q.append(("ts_utc", f"gte.{since}"))
        if until:
            q.append(("ts_utc", f"lt.{until}"))
        req = urllib.request.Request(f"{URL}/series?" + urllib.parse.urlencode(q), headers=HEAD)
        with urllib.request.urlopen(req, timeout=120) as r:
            page = json.loads(r.read())
        out += page
        if len(page) < 1000:
            break
        off += 1000
    if not out:
        raise SystemExit(f"no rows: {table} {entity} {variable} {since} {until}")
    res = [(r["ts_utc"], float(r["value"])) for r in out if r["value"] is not None]
    CACHE[ck] = res
    return res


def grain(p):
    return {7: "month", 10: "day", 13: "hour"}[len(p)]


def slots(a, b):
    """Every month, day or hour from a to b, both included, in the form of a and b."""
    g = grain(a)
    out = []
    if g == "month":
        y, m = int(a[:4]), int(a[5:])
        while f"{y:04d}-{m:02d}" <= b:
            out.append(f"{y:04d}-{m:02d}")
            y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    elif g == "day":
        d, end = dt.date.fromisoformat(a), dt.date.fromisoformat(b)
        while d <= end:
            out.append(d.isoformat())
            d += dt.timedelta(days=1)
    else:
        h, end = dt.datetime.fromisoformat(a + ":00"), dt.datetime.fromisoformat(b + ":00")
        while h <= end:
            out.append(h.strftime("%Y-%m-%dT%H"))
            h += dt.timedelta(hours=1)
    return out


def bounds(period):
    """The ts_utc range to read for a period: from its first slot to just after its last."""
    a, b = period
    g = grain(a)
    if g == "month":
        y, m = int(b[:4]), int(b[5:])
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
        return f"{a}-01", f"{y:04d}-{m:02d}-01"
    if g == "day":
        return a, (dt.date.fromisoformat(b) + dt.timedelta(days=1)).isoformat()
    return a + ":00:00Z", (dt.datetime.fromisoformat(b + ":00") + dt.timedelta(hours=1)).strftime("%Y-%m-%dT%H:00:00Z")


def keyed(series, g):
    n = {"month": 7, "day": 10, "hour": 13}[g]
    got = {}
    for ts, v in series:
        k = ts[:n]
        if k in got and got[k] != v:
            raise SystemExit(f"two values for {k}: {got[k]} and {v}")
        got[k] = v
    return got


def label(slot):
    g = grain(slot)
    if g == "month":
        d = dt.date(int(slot[:4]), int(slot[5:]), 1)
        return d.strftime("%B"), d.strftime("%B %Y")
    if g == "day":
        d = dt.date.fromisoformat(slot)
        return f"{d.strftime('%B')} {d.day}", f"{d.strftime('%B')} {d.day}, {d.year}"
    h = dt.datetime.fromisoformat(slot + ":00")
    return f"{h.strftime('%B')} {h.day}", f"{h.strftime('%B')} {h.day}, {h.year}, hour starting {h.hour:02d}:00 UTC"


def mean_local(table, entity, variable, period, tz):
    """The mean of an hourly series over the hours whose start falls in the period's months on the local clock tz.
    Every local hour must be held."""
    zone = ZoneInfo(tz)
    a, b = period
    y, m = int(b[:4]), int(b[5:])
    y2, m2 = (y + 1, 1) if m == 12 else (y, m + 1)
    start = dt.datetime(int(a[:4]), int(a[5:]), 1, tzinfo=zone).astimezone(dt.timezone.utc)
    end = dt.datetime(y2, m2, 1, tzinfo=zone).astimezone(dt.timezone.utc)
    want = []
    h = start
    while h < end:
        want.append(h.strftime("%Y-%m-%dT%H"))
        h += dt.timedelta(hours=1)
    got = keyed(rows(table, entity, variable, start.strftime("%Y-%m-%dT%H:00:00Z"), end.strftime("%Y-%m-%dT%H:00:00Z")), "hour")
    missing = [k for k in want if k not in got]
    if missing:
        raise SystemExit(f"hours missing: {table} {entity} {variable} {missing[:6]} ({len(missing)})")
    return sum(got[k] for k in want) / len(want), None, len(want)


def aggregate(table, entity, variable, how, period):
    """(value, the slot of a max or min or None, the number of slots used)."""
    if how.startswith("mean_local:"):
        return mean_local(table, entity, variable, period, how.split(":", 1)[1])
    g = grain(period[0])
    since, until = bounds(period)
    got = keyed(rows(table, entity, variable, since, until), g)
    want = slots(*period)
    if how == "mean_weekdays":
        want = [d for d in want if dt.date.fromisoformat(d).weekday() < 5]
        extra = [d for d in got if d in slots(*period) and d not in want]
        if extra:
            raise SystemExit(f"a weekend day held in a trading-day series: {table} {entity} {extra}")
    missing = [s for s in want if s not in got]
    if missing:
        raise SystemExit(f"{g}s missing: {table} {entity} {variable} {missing[:6]} ({len(missing)})")
    vals = [got[s] for s in want]
    if how == "month":
        if len(want) != 1:
            raise SystemExit(f"month asks one period: {period}")
        return vals[0], None, 1
    if how == "sum":
        return sum(vals), None, len(vals)
    if how in ("mean", "mean_weekdays"):
        return sum(vals) / len(vals), None, len(vals)
    if how in ("max", "min"):
        best = max(vals) if how == "max" else min(vals)
        at = [s for s in want if got[s] == best]
        if len(at) != 1:
            raise SystemExit(f"a tie at the {how}: {table} {entity} {variable} {at}")
        return best, at[0], len(vals)
    raise ValueError(how)


def tolerance(x):
    return 0.5 if abs(x) >= 1000 else 0.01


def complete(qid):
    for t, e, held, whole, period in COMPLETE.get(qid, []):
        h = keyed(rows(t, e, held, *bounds(period)), "month")
        w = keyed(rows(t, e, whole, *bounds(period)), "month") if whole else None
        for m in slots(*period):
            if m not in h or (w is not None and m not in w):
                raise SystemExit(f"completeness row missing: {t} {e} {held} {m}")
            if (w is None and h[m] != 0) or (w is not None and h[m] != w[m]):
                raise SystemExit(f"a partial period: {t} {e} {held}={h[m]} {whole}={w[m] if w else 0} in {m}")


def per_text(period):
    a, b = period
    if a == b:
        return a
    return f"{a} to {b}"


def what(how, period, n):
    g = grain(period[0])
    if how == "month":
        return per_text(period)
    if how.startswith("mean_local:"):
        return f"the mean of the {n} hourly values whose hour starts in {per_text(period)} on the {how.split(':', 1)[1]} clock"
    if how == "mean_weekdays":
        return f"the mean of the {n} trading-day (Monday to Friday) values {per_text(period)}"
    if g == "hour":
        rule = f"the {n} hourly values whose ts_utc (the hour's start, UTC) falls from {period[0]}:00 to {period[1]}:00, both included"
    elif g == "day":
        rule = f"the {n} daily values (each the publisher's local operating day, ts_utc the day at 00:00Z) {per_text(period)}"
    else:
        rule = f"the {n} monthly values {per_text(period)}"
    return {"sum": "the sum of ", "mean": "the mean of ", "max": "the largest of ", "min": "the smallest of "}[how] + rule


def build():
    keys = {}
    for qid in ORDER:
        if qid in SPEC:
            t, e, v, how, period, div = SPEC[qid]
            complete(qid)
            val, at, n = aggregate(t, e, v, how, period)
            val = val / div
            tol = tolerance(val)
            rec = {"table": t, "entity": e, "variable": v, "aggregation": how, "period": list(period), "n": n,
                   "expected": [round(val, 4)], "tolerance": tol, "text": [], "tables": [t], "also": {}}
            note = f"{t}, {e}, {v}: {what(how, period, n)}"
            if at:
                short, long_ = label(at)
                rec["at"] = at
                g = grain(at)
                if g == "month":
                    rec["text"] = [short] if period[0][:4] == period[1][:4] else [short, at[:4]]
                else:
                    rec["text"] = [short]
                note += f", {long_}"
            for (t2, e2, v2, how2, period2) in ALSO.get(qid, []):
                try:
                    alt, _, n2 = aggregate(t2, e2, v2, how2, period2)
                except SystemExit as err:
                    rec["also"][f"{t2} {e2} {v2}"] = f"not held: {err}"
                    continue
                rec["also"][f"{t2} {e2} {v2}"] = round(alt, 4)
                if abs(alt - val) <= tol and t2 not in rec["tables"]:
                    rec["tables"].append(t2)
                    note += f"; {t2} ({e2}, {v2}, {what(how2, period2, n2)}) holds the same figure, {round(alt, 4)}"
            rec["note"] = note
        else:
            (t1, e1, v1, m1), (t2, e2, v2, m2) = DIFF[qid]
            complete(qid)
            a = aggregate(t1, e1, v1, "month", (m1, m1))[0]
            b = aggregate(t2, e2, v2, "month", (m2, m2))[0]
            d = a - b
            tol = tolerance(d)
            tables = [t1] if t1 == t2 else [t1, t2]
            rec = {"table": t1, "entity": f"{e1} less {e2}", "variable": v1 if v1 == v2 else f"{v1} less {v2}", "aggregation": "difference",
                   "period": [m1, m2], "expected": [round(d, 4), round(a, 4), round(b, 4)], "tolerance": tol, "text": [], "tables": tables, "also": {}}
            rec["note"] = f"{t1}: {e1} {v1} {m1} ({round(a, 4)}) less {e2} {v2} {m2} ({round(b, 4)}), the difference first and its two parts after"
            if qid == "f06":
                alt = aggregate(SB, "iso:ercot", "battery_operating_mw_net_added_12m", "month", AUG26)[0]
                rec["also"][f"{SB} iso:ercot battery_operating_mw_net_added_12m"] = round(alt, 4)
                if abs(alt - d) <= tol:
                    rec["note"] += f"; the same table's battery_operating_mw_net_added_12m for 2026-08 holds the same figure, {round(alt, 4)}"
                else:
                    rec["note"] += f"; the same table's battery_operating_mw_net_added_12m for 2026-08 is {round(alt, 4)}, not the difference asked"
        if COMPLETE.get(qid):
            rec["note"] += "; checked whole: " + ", ".join(f"{h} {'= ' + w if w else '= 0'}" for _, _, h, w, _ in COMPLETE[qid])
        keys[qid] = rec
        print(qid, rec["expected"], rec.get("at", ""), rec["tables"], flush=True)
    return keys


def yaml_out(keys):
    lines = [
        "# Energy Research Warehouse (ERW): 30 questions for Ask (/api/ask) a lab's energy team would ask, session 1114 (the chain of 23 October 2026).",
        "# Ten from a power trading lead (t), ten from an infrastructure-finance lead (f), ten from a policy lead (p); grids ERCOT, CAISO and SPP and",
        "# national series only (no ISO-NE, NYISO or MISO row is a key: they are held for a license; PJM is not held). Every expected number was computed",
        f"# before any model call from the live set (Supabase, the series view, the anon key, reads only) on {keys['_at'][:10]} by expected_s1114.py, which",
        "# writes this file; each note names the table, the entity, the variable, the period and the aggregation. A difference lists the difference first",
        "# and its two parts after. Monthly and daily rows are the publisher's local months and days as the tables write them; an hourly aggregate is over",
        "# ts_utc (UTC hour starts), as its note says. `via` as in questions_s302.yaml (grid: the grid's scoped chat; general: no grid). tolerance:",
        "# 0.01 under 1,000, 0.5 from 1,000. `tables` lists every live-set table found holding the figure (checked, see each note).",
        f"today: '{TODAY}'",
        "questions:",
    ]
    for qid in ORDER:
        k = keys[qid]
        grid, via, question = Q[qid]
        lines += [
            f"- id: {qid}",
            f"  grid: {grid}",
            f"  via: {via}",
            f"  question: {json.dumps(question)}",
            f"  expected: {json.dumps(k['expected'])}",
            f"  tolerance: {k['tolerance']}",
            f"  text: {json.dumps(k['text'])}",
            f"  tables: {json.dumps(k['tables'])}",
            "  refuse: false",
            f"  note: {json.dumps(k['note'])}",
        ]
    text = "\n".join(lines) + "\n"
    if chr(0x2014) in text:
        raise SystemExit("an em dash in the output")
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def main():
    if set(ORDER) != set(SPEC) | set(DIFF) or set(SPEC) & set(DIFF) or set(Q) != set(ORDER):
        raise SystemExit("SPEC, DIFF and Q must name the thirty ids once each")
    at = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    keys = build()
    keys["_at"] = at
    yaml_out(keys)
    with open(KEYS_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"computed_at_utc": at, "source": f"{URL.split('//')[1].split('.')[0]} series view, anon key", "keys": {q: keys[q] for q in ORDER}}, f, indent=1)
        f.write("\n")
    print(f"wrote {OUT}: {len(ORDER)} questions, keys computed at {at}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
