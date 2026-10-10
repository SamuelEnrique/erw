#!/usr/bin/env python3
"""The battery model's hourly dispatch as one CSV, for replication (session 178).

Energy Research Warehouse (ERW). "What a battery earns" (/cost-of-power/battery) shows months; its model
(warehouse/derived/battery_stack.py) decides hours. This script writes the hours of the page's default case, one row an
hour, so that a reader can rebuild every headline number of the page without the model:

    site/public/battery/erw_2026_battery_dispatch.csv

The default case is the page's own: ERCOT (HB_HUBAVG), a 4-hour battery, perfect foresight, per MW of rated power. The
window is the 36 local months the page's "bad month" reads, which end with the last month of the page's "last twelve
months"; the column in_last_twelve marks the twelve. Both windows are found from battery_stack_monthly by the page's own
rule (lib/batterystack.ts: a month counts when at least 90 percent of its days are held; the last twelve months are the
newest held month whose eleven months before it are all held).

Nothing is estimated and nothing is re-modelled: every day is solved by battery_stack.solve_day itself, from the same
price tables, and the script refuses to write unless each month's sums equal the rows of battery_stack_monthly to within
half a cent per MW. A day the model leaves out (an hour of a price not held) has no rows here, as it has none there.

    python warehouse/derived/battery_dispatch_export.py --in-dir C:/.../warehouse/output
    python warehouse/derived/battery_dispatch_export.py --in-dir DIR --out C:/scratch/trial.csv

It writes nothing under warehouse/output and needs no data lock: the inputs are read, the CSV is a site file.
Method: docs/methods/battery_earns_algorithm.md.
"""

import argparse
import datetime as dt
import hashlib
import os
import subprocess
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import battery_stack as bs  # noqa: E402
import iso_prices as ip  # noqa: E402
import price_board as pb  # noqa: E402

CSV_NAME = "erw_2026_battery_dispatch.csv"
OUT = os.path.join(ROOT, "site", "public", "battery", CSV_NAME)
GRID, DURATION, STRATEGY = "ercot", 4, "foresight"   # the page's defaults (lib/batterystack.ts, inputsOf)
NEAR = 0.9                                             # lib/batterystack.ts, NEAR
HEADER_LINES = 14                                      # the do-file reads the column names from line 15
SENTINEL = -999                                        # a product not bought on the day: no price, no award
PRODUCTS = [p["key"] for p in bs.MARKETS[GRID]["products"]]
COLUMNS = (["hour_utc", "hour_local", "local_day", "local_month", "hour_of_day", "in_last_twelve", "switch_used",
            "price_energy_usd_mwh"] + [f"price_{k}_usd_mw" for k in PRODUCTS]
           + ["charge_mw", "discharge_mw", "soc_mwh"] + [f"award_{k}_mw" for k in PRODUCTS]
           + ["revenue_energy_usd"] + [f"revenue_{k}_usd" for k in PRODUCTS] + ["revenue_ancillary_usd", "revenue_total_usd"])


def prev_month(m, k):
    """The month k months before m (YYYY-MM)."""
    y, mo = int(m[:4]), int(m[5:7]) - 1 - k
    return f"{y + mo // 12:04d}-{mo % 12 + 1:02d}"


def months_of(table, entity, strat, dur):
    """{month: {metric: value}} of one hub, strategy and duration from battery_stack_monthly's rows (a frame)."""
    pre = f"{strat}_{dur}h_"
    t = table[(table["entity"] == entity) & table["variable"].str.startswith(pre)]
    out = {}
    for v, ts, x in zip(t["variable"], t["ts_utc"], t["value"]):
        out.setdefault(ts[:7], {})[v[len(pre):]] = float(x)
    return dict(sorted(out.items()))


def held(v):
    """The page's rule for a month that counts (lib/batterystack.ts, monthsOf)."""
    return ("revenue_total_usd_per_mw" in v and v.get("days_in_month", 0) > 0
            and v.get("days_held", 0) / v["days_in_month"] >= NEAR - 1e-9)


def last_twelve(months):
    """The page's last twelve months: the newest held month whose eleven months before it are all held; else None."""
    for m in sorted(months, reverse=True):
        if not held(months[m]):
            continue
        twelve = [prev_month(m, k) for k in range(12)]
        if all(t in months and held(months[t]) for t in twelve):
            return twelve[::-1]
    return None


def last_36(months):
    """The page's 36-month window: (first month, last month, the held months in it)."""
    l12 = last_twelve(months)
    hs = [m for m in months if held(months[m])]
    if not hs:
        return None
    to = l12[-1] if l12 else hs[-1]
    frm = prev_month(to, 35)
    return frm, to, [m for m in hs if frm <= m <= to]


def read_monthly(in_dir):
    path = os.path.join(in_dir, bs.NAME + ".csv")
    return pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False)


def header_value(path, start):
    """The first header comment of a table that begins with `start`, without the prefix; "" when there is none."""
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            if line[2:].startswith(start):
                return line[2 + len(start):].strip()
    return ""


def fmt(v, places):
    """A number as the CSV writes it: fixed places, trailing zeros dropped, never an exponent, never minus zero."""
    s = f"{v:.{places}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def model_version():
    """The model's file as it stands: the sha256 of its bytes with LF line ends, and the commit that last changed it."""
    path = os.path.join(HERE, "battery_stack.py")
    with open(path, "rb") as f:
        sha = hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()
    try:
        commit = subprocess.run(["git", "-C", ROOT, "log", "-1", "--format=%H", "--", "warehouse/derived/battery_stack.py"],
                                capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception:
        commit = ""
    return sha, commit or "unknown"


def build(in_dir, log=print):
    """(rows, facts): the hourly rows of the window, and what the header states."""
    ip.OUT_DIR = os.path.abspath(in_dir)   # the readers of price_board and cost_of_power read ip.OUT_DIR; nothing is written there
    m = bs.MARKETS[GRID]
    tz = pb.TZ[GRID]
    entity = f"{GRID}:{pb.MAIN[GRID]}"
    months = months_of(read_monthly(in_dir), entity, STRATEGY, DURATION)
    l12 = last_twelve(months)
    win = last_36(months)
    if l12 is None or win is None:
        raise RuntimeError("battery_stack_monthly holds no twelve consecutive months for the default case: nothing written")
    first, last, held_months = win
    mk = bs.STRATEGIES[STRATEGY]
    energy, tables = bs.energy_prices(GRID, mk, log)
    reserve = bs.as_prices(m["as_table"], m["products"])
    a = pd.Timestamp(first + "-01")
    b = pd.Timestamp(last + "-01") + pd.offsets.MonthBegin(1) - pd.Timedelta(days=1)
    rows, left, n_switch = [], [], 0
    for ts in pd.date_range(a, b, freq="D"):
        day = ts.strftime("%Y-%m-%d")
        hrs = bs.day_hours(day, tz)
        prods = [p for p in m["products"] if p["first"] is None or p["first"] <= day]
        pr = [reserve[p["key"]].reindex(hrs) for p in prods]
        ep = energy.reindex(hrs)
        short = [p["key"] for p, s in zip(prods, pr) if s.isna().any()]
        if short:
            left.append(f"{day} ancillary {' '.join(short)}")
            continue
        if ep.isna().any():
            left.append(f"{day} energy {int(ep.isna().sum())} of {len(hrs)} hours not held")
            continue
        spec = tuple((p["up"], bs.required_hours(p, day)[0]) for p in prods)
        sol = bs.solve_day(ep.values, [s.values for s in pr], spec, DURATION)
        bad = bs.check_day(sol, spec, DURATION)
        if bad:
            raise RuntimeError(f"{day}: a constraint does not hold: {bad[0]}")
        n_switch += int(sol["mip"])
        bought = {p["key"]: j for j, p in enumerate(prods)}
        local = hrs.tz_convert(tz)
        for t, (u, lt) in enumerate(zip(hrs, local)):
            r = dict(hour_utc=u.strftime("%Y-%m-%dT%H:%M:%SZ"), hour_local=lt.strftime("%Y-%m-%dT%H:%M:%S%z"), local_day=day,
                     local_month=day[:7], hour_of_day=t, in_last_twelve=int(day[:7] in l12), switch_used=int(sol["mip"]),
                     price_energy_usd_mwh=float(ep.values[t]), charge_mw=float(sol["charge"][t]),
                     discharge_mw=float(sol["discharge"][t]), soc_mwh=float(sol["soc"][t]))
            r["revenue_energy_usd"] = r["price_energy_usd_mwh"] * (r["discharge_mw"] - r["charge_mw"])
            anc = 0.0
            for k in PRODUCTS:
                if k in bought:
                    j = bought[k]
                    price, award = float(pr[j].values[t]), float(sol["awards"][j][t])
                    r[f"price_{k}_usd_mw"], r[f"award_{k}_mw"], r[f"revenue_{k}_usd"] = price, award, price * award
                    anc += price * award
                else:
                    r[f"price_{k}_usd_mw"] = r[f"award_{k}_mw"] = r[f"revenue_{k}_usd"] = None
            r["revenue_ancillary_usd"] = anc
            r["revenue_total_usd"] = r["revenue_energy_usd"] + anc
            rows.append(r)
    facts = dict(entity=entity, first=first, last=last, l12=l12, held=held_months, left=left, n_switch=n_switch,
                 tables=tables, months=months, days=len({r["local_day"] for r in rows}))
    return rows, facts


def agree(rows, facts, tol=0.005):
    """Each month's sums of the hourly rows beside battery_stack_monthly's rows; the list of differences over tol
    (USD per MW). Empty when the export is the page's own data, hour by hour."""
    df = pd.DataFrame(rows)
    bad = []
    for mo, g in df.groupby("local_month"):
        t = facts["months"].get(mo, {})
        pairs = [("energy", g["revenue_energy_usd"].sum()), ("ancillary", g["revenue_ancillary_usd"].sum()),
                 ("total", g["revenue_total_usd"].sum())]
        pairs += [(k, g[f"revenue_{k}_usd"].sum()) for k in PRODUCTS if g[f"revenue_{k}_usd"].notna().any()]
        for k, v in pairs:
            want = t.get(f"revenue_{k}_usd_per_mw")
            if want is None or abs(v - want) > tol:
                bad.append(f"{mo} {k}: the hours sum to {v:.4f}, the table holds {want}")
        if t.get("days_held") != g["local_day"].nunique():
            bad.append(f"{mo} days: {g['local_day'].nunique()} here, {t.get('days_held')} in the table")
    return bad


def write(rows, facts, in_dir, out, run_at):
    sha, commit = model_version()

    def got(t):
        return header_value(os.path.join(in_dir, t + ".csv"), "Retrieved: ").split(" (UTC)")[0] or "not stated"
    m = bs.MARKETS[GRID]
    head = [
        "Energy Research Warehouse (ERW): the battery model's hourly dispatch; the default case of /cost-of-power/battery (session 178)",
        f"Case: ERCOT; energy at {pb.MAIN[GRID]}; a {DURATION}-hour battery; strategy {STRATEGY} (energy at the hourly mean of the "
        f"real-time price; ancillary services at day-ahead clearing prices); round trip {bs.RTE}; per 1 MW of rated power",
        f"Window: local (Central) months {facts['first']} to {facts['last']}; the 36 months of the page's bad month. "
        f"in_last_twelve = 1 marks {facts['l12'][0]} to {facts['l12'][-1]}; the page's last twelve months",
        "Rows: one per local hour of every day the model solved; a local day holds 24 hours; 23 on the spring daylight-saving day; "
        "25 on the autumn one. hour_of_day counts from 0 within the local day",
        "Prices: price_energy_usd_mwh in USD per MWh; price_<product>_usd_mw in USD per MW for the hour. Decisions per MW of rated "
        "power: charge_mw and discharge_mw at the grid; soc_mwh the stored energy at the end of the hour; award_<product>_mw",
        "Revenue: USD per MW of rated power for the hour; revenue_energy_usd = price x (discharge - charge); revenue_<product>_usd = "
        "price x award; revenue_ancillary_usd their sum; revenue_total_usd energy plus ancillary. switch_used = 1: the day needed "
        "the charge-or-discharge switch",
        f"Sentinel: {SENTINEL} in a product's price; award and revenue columns means the product was not bought on that day. "
        f"Days left out by the model (an hour of a price not held): {len(facts['left'])}" + (": " + " | ".join(facts["left"]) if facts["left"] else ""),
        f"Source tables (ERW; warehouse/output): {facts['tables']}; {m['as_table']}; {bs.NAME} (the window and the check below)",
        "Retrieved (UTC) as each table's own header states: " + "; ".join(
            f"{t} {got(t)}" for t in (pb.TABLES[(GRID, 'rtm')][0], pb.HISTORY, m["as_table"], bs.NAME)),
        f"Model: warehouse/derived/battery_stack.py; sha256 {sha}; last changed by commit {commit}. Every day here is solved by its "
        "solve_day and passes its check_day",
        f"Check at export: each month's sums of these hours equal the rows of {bs.NAME} to within 0.005 USD per MW "
        f"({len(facts['held'])} months; {facts['days']} days; {facts['n_switch']} days used the switch)",
        f"Exported: {run_at} (UTC) by warehouse/derived/battery_dispatch_export.py. Method: "
        "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/battery_earns_algorithm.md",
        "License: public. Derived by the ERW from ERCOT's public prices (https://www.ercot.com/help/terms). Not a forecast; not what "
        "any battery earned: an upper bound under perfect foresight",
        f"Stata: import delimited using {CSV_NAME}; varnames({HEADER_LINES + 1}) rowrange({HEADER_LINES + 2}) stringcols(_all). "
        "These comment lines hold no comma and no double quote",
    ]
    if len(head) != HEADER_LINES:
        raise RuntimeError(f"the header holds {len(head)} lines, the do-file expects {HEADER_LINES}")
    for h in head:
        if "," in h or '"' in h or "\n" in h:
            raise RuntimeError(f"a header line holds a comma, a quote or a line break: {h[:80]}")
    places = {c: 6 for c in COLUMNS if c.endswith("_mw") or c == "soc_mwh"}
    places.update({c: 8 for c in COLUMNS if c.startswith("revenue_")})
    places.update({c: 6 for c in COLUMNS if c.startswith("price_")})
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out + ".tmp", "w", encoding="utf-8", newline="\n") as f:
        for h in head:
            f.write("# " + h + "\n")
        f.write(",".join(COLUMNS) + "\n")
        for r in rows:
            cells = []
            for c in COLUMNS:
                v = r[c]
                cells.append(str(SENTINEL) if v is None else fmt(v, places[c]) if c in places else str(v))
            f.write(",".join(cells) + "\n")
    os.replace(out + ".tmp", out)
    return os.path.getsize(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the battery model's hourly dispatch for the page's default case, as one CSV")
    ap.add_argument("--in-dir", default=ip.OUT_DIR, help="read the tables from this directory (another copy's warehouse/output); "
                    "nothing is written there")
    ap.add_argument("--out", default=OUT, help="the CSV to write")
    a = ap.parse_args(argv)
    in_dir = os.path.abspath(a.in_dir)
    need = [bs.NAME, bs.MARKETS[GRID]["as_table"], pb.TABLES[(GRID, "rtm")][0]]
    missing = [t for t in need if not os.path.exists(os.path.join(in_dir, t + ".csv"))]
    if missing:
        print(f"battery_dispatch_export SKIPPED: input tables not on this machine: {', '.join(missing)}")
        return 0
    run_at = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rows, facts = build(in_dir)
    bad = agree(rows, facts)
    if bad:
        print(f"battery_dispatch_export FAILED: {len(bad)} monthly sums differ from {bs.NAME}; nothing written", file=sys.stderr)
        for line in bad[:40]:
            print("  " + line, file=sys.stderr)
        return 1
    size = write(rows, facts, in_dir, os.path.abspath(a.out), run_at)
    print(f"{os.path.basename(a.out)}: rows={len(rows)} days={facts['days']} months={len(facts['held'])} bytes={size} "
          f"window={facts['first']}..{facts['last']} last_twelve={facts['l12'][0]}..{facts['l12'][-1]} "
          f"left_out={len(facts['left'])} switch_days={facts['n_switch']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
