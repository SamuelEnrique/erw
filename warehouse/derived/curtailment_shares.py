#!/usr/bin/env python3
"""The share of available wind and solar output curtailed, by month: CAISO and SPP (session 144).

Energy Research Warehouse (ERW). Until this session a share was computed on the page from the monthly sums, and only
for a month in which the daily curtailment table held the output of every day: ten CAISO months read "not computable"
(December 2019, where CAISO's workbook lacks intervals of one day, and every month of 2026, where the Daily Renewable
Report's five-minute output could not be read whole for every day), and SPP had no share at all. This module computes
both, from data the warehouse already holds. No request is made.

    python warehouse/derived/curtailment_shares.py                  # the site's copy: site/data/curtailment/shares.json
    python warehouse/derived/curtailment_shares.py --out-dir DIR    # a trial: shares.json and share_rows.csv under DIR

The rows of the table (variables share_* of iso_curtailment_monthly) are written by iso_curtailment_monthly.py, which
calls build() here; this script alone never writes into warehouse/output.

The share, for both grids:   curtailed MWh / (curtailed MWh + wind and solar output MWh)
over the days of the month for which BOTH are held, and written only when those days hold at least 95 percent of the
month's hours (NEAR_HOURS). The numerator is cut to the same days as the denominator, so a share is never written from
a partial denominator, and with neither side negative it cannot pass 100 percent. Nothing is scaled up or filled.

CAISO (Pacific days), the output is CAISO's own, one source for a whole month, never two in one month:
    caiso_curtailment_daily     the Production sheet of CAISO's "Production and curtailments data" workbooks (to 2025):
                                the day's MWh from its five-minute output
    caiso_fuel_supply_history   CAISO's Today's Outlook supply by fuel, hourly means of its five-minute values
    caiso_fuel_supply           the same report, from June 2025
    The source that holds the most hours of the month is used; a tie goes to the first in this order. CAISO states
    that curtailed energy is not in its production figures, so the two add.
    Not used: the five-minute output read from the Daily Renewable Report (the daily table's output rows from 2026).
    On the days of 2026 that both it and Today's Outlook hold, Today's Outlook is higher by 11 to 20 percent a month
    for solar and by up to 33 percent for wind, while in June to December 2025 Today's Outlook and the workbook's
    Production sheet agree within 1 percent for solar and 0.1 percent for wind. A denominator from the report would
    step the share up at the turn of the year for a reason that is not curtailment, so every month of 2026 rests on
    Today's Outlook. Which of the two is CAISO's settled figure is an open question for a person.

SPP (Central days), entity spp:SPP against the balancing authority SWPP of Form EIA-930:
    the curtailed MWh are SPP's own (spp_curtailment_daily, a day held only with all its five-minute intervals); the
    output is EIA-930's hourly net generation from wind and from solar for SWPP, for every hour of the same days: a day
    counts only when each of its 24 hours (23 or 25 on a clock change) holds both. The hours come from EIA's workbook
    of the balancing authority (the file the energy mix reads, warehouse/derived/mix_profile.py eia_hourly) where it is
    on this machine, or from eia930_all_generation; the one that holds more of the month is used whole. An hour
    whose wind figure is exactly zero is not held: EIA's first weeks of generation by source, July and August 2018,
    print zero wind for SPP in 1,464 hours, and no hour after them does (the lowest is 148 MW). A month whose output
    sums to nothing has no share. Before July 2018 EIA-930 gives no generation by source, so SPP has no share then. SPP's western area (spp:SWPW) has no share: no hourly output for
    it is held.
"""

import argparse
import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

SITE_FILE = os.path.join(ROOT, "site", "data", "curtailment", "shares.json")
NEAR_HOURS = 0.95
VARS = {"share_curtailed_pct": "pct", "share_curtailed_mwh": "MWh", "share_output_mwh": "MWh", "share_hours_held": "count", "share_hours_in_month": "count"}
CAISO_TZ, SPP_TZ = "America/Los_Angeles", "America/Chicago"
WORKBOOK_SOURCE = "caiso:production_curtailments"
CAISO_BASES = ["caiso_curtailment_daily", "caiso_fuel_supply_history", "caiso_fuel_supply"]
BASIS_WORDS = {
    "caiso_curtailment_daily": "CAISO's five-minute output, from the Production sheet of its Production and curtailments workbook (to 2025)",
    "caiso_fuel_supply_history": "CAISO's Today's Outlook supply by fuel, hourly (June 2018 to May 2025)",
    "caiso_fuel_supply": "CAISO's Today's Outlook supply by fuel, hourly (from June 2025)",
    "eia930_workbook": "EIA-930's hourly net generation from wind and solar for SWPP, from EIA's workbook of the balancing authority (adjusted values)",
    "eia930_all_generation": "EIA-930's hourly net generation from wind and solar for SWPP (eia930_all_generation)",
}
DEFINITIONS = {
    "caiso": "CAISO: the wind and solar energy CAISO reports curtailed, over that energy plus CAISO's own wind and solar output of the same days; the operator's figures on both sides.",
    "spp": "SPP: the wind and solar energy SPP reports curtailed in its balancing authority area, over that energy plus EIA-930's hourly wind and solar net generation "
           "for SPP in the same hours; the operator's curtailment over a denominator the ERW builds from EIA's hours.",
    "ercot": "ERCOT: output below the High Sustained Limit over the High Sustained Limit, wind and solar together; the ERW's estimate, not a curtailment figure of ERCOT's.",
}


def day_hours(day, tz):
    """The hours of a local day: 24, or 23 or 25 on a clock change."""
    a = pd.Timestamp(day).tz_localize(tz)
    b = (pd.Timestamp(day) + pd.Timedelta(days=1)).tz_localize(tz)
    return int(round((b - a) / pd.Timedelta(hours=1)))


def month_days(month):
    p = pd.Period(month)
    return [f"{month}-{d:02d}" for d in range(1, p.days_in_month + 1)]


def share_pct(curtailed, output):
    """curtailed / (curtailed + output), percent, or None when either is missing or negative or both are nothing.
    With neither side negative the share is from 0 to 100, never above."""
    if curtailed is None or output is None or pd.isna(curtailed) or pd.isna(output):
        return None
    if curtailed < 0 or output < 0 or curtailed + output <= 0:
        return None
    return 100.0 * curtailed / (curtailed + output)


def month_share(month, tz, curtailed_by_day, output_by_day):
    """One month's share over the days both hold. curtailed_by_day, output_by_day: {YYYY-MM-DD: MWh}, a day absent when
    not held whole. Returns the record, with "share_pct" only when the days both hold cover NEAR_HOURS of the month's
    hours; otherwise "missing" says why."""
    days = month_days(month)
    due = sum(day_hours(d, tz) for d in days)
    both = [d for d in days if d in curtailed_by_day and d in output_by_day]
    held = sum(day_hours(d, tz) for d in both)
    rec = {"hours_held": held, "hours_in_month": due, "days_held": len(both), "days_in_month": len(days)}
    if held < NEAR_HOURS * due:
        rec["missing"] = (f"curtailment and output are both held for {len(both)} of {len(days)} days ({held} of {due} hours), "
                          f"under {NEAR_HOURS:.0%} of the month")
        return rec
    cur = float(sum(curtailed_by_day[d] for d in both))
    out = float(sum(output_by_day[d] for d in both))
    s = share_pct(cur, out) if out > 0 else None  # a month whose output sums to nothing has no share
    if s is None:
        rec["missing"] = f"the output of the days held sums to {out:.1f} MWh and the curtailment to {cur:.1f} MWh: no share"
        return rec
    rec.update(share_pct=round(s, 4), curtailed_mwh=round(cur, 3), output_mwh=round(out, 3))
    return rec


def best_month(month, tz, curtailed_by_day, outputs):
    """The month's share on the output source that holds the most hours of it. outputs: [(basis, {day: MWh})] in order of
    preference; a tie goes to the first. One source for the whole month, never two."""
    best = None
    for basis, by_day in outputs:
        r = month_share(month, tz, curtailed_by_day, by_day)
        r["basis"] = basis
        if best is None or r["hours_held"] > best["hours_held"]:
            best = r
    return best


def whole_days(hours, tz):
    """{day: MWh} from an hourly series (UTC index, MW over the hour), a local day kept only with every one of its hours
    held (no NaN among them)."""
    s = hours.dropna()
    if s.empty:
        return {}
    local = s.index.tz_convert(tz)
    g = s.groupby(local.strftime("%Y-%m-%d"))
    n, tot = g.size(), g.sum()
    return {d: float(tot[d]) for d in n.index if n[d] == day_hours(d, tz)}


def read_vars(path, variables, entity=None, extra=()):
    """A table's rows of some variables, read in chunks with only the columns needed."""
    cols = ["entity", "variable", "ts_utc", "value"] + list(extra)
    got = []
    for chunk in pd.read_csv(path, skiprows=ip.header_rows(path), usecols=cols, chunksize=400_000):
        chunk = chunk[chunk["variable"].isin(variables)]
        if entity:
            chunk = chunk[chunk["entity"] == entity]
        if len(chunk):
            got.append(chunk)
    return pd.concat(got) if got else pd.DataFrame(columns=cols)


def daily_sum(d, variables):
    """{day: the sum of the variables} for the days that hold every one of them (a daily table)."""
    w = d[d["variable"].isin(variables)].pivot_table(index="ts_utc", columns="variable", values="value", aggfunc="last")
    w = w.reindex(columns=variables).dropna()
    return {t[:10]: float(v) for t, v in w.sum(axis=1).items()}


def caiso_inputs(in_dir, log):
    """CAISO: the curtailed MWh by day, and the output by day from each of the three sources held."""
    path = os.path.join(in_dir, "caiso_curtailment_daily.csv")
    d = read_vars(path, ["curtailed_solar_mwh", "curtailed_wind_mwh", "solar_generation_mwh", "wind_generation_mwh"], "caiso:ISO", extra=("source",))
    cur = daily_sum(d, ["curtailed_solar_mwh", "curtailed_wind_mwh"])
    # the output of the daily table counts only where it is the workbook's Production sheet (WORKBOOK_SOURCE): the Daily
    # Renewable Report's output of 2026 is held and not used (the docstring says why)
    outputs = [("caiso_curtailment_daily", daily_sum(d[d["source"] == WORKBOOK_SOURCE], ["solar_generation_mwh", "wind_generation_mwh"]))]
    for t in CAISO_BASES[1:]:
        p = os.path.join(in_dir, f"{t}.csv")
        if not os.path.exists(p):
            log(f"  shares: {t} is not on this machine")
            continue
        f = read_vars(p, ["solar_mw", "wind_mw"], "caiso:ISO")
        w = f.pivot_table(index="ts_utc", columns="variable", values="value", aggfunc="last").reindex(columns=["solar_mw", "wind_mw"]).dropna()
        w.index = pd.to_datetime(w.index, utc=True)
        outputs.append((t, whole_days(w.sum(axis=1).sort_index(), CAISO_TZ)))
    log("  shares, caiso: curtailment held for {:,} days; output by day: {}".format(len(cur), ", ".join(f"{b} {len(x):,}" for b, x in outputs)))
    return cur, outputs


def eia_workbook_hours(ba, log, extract=None):
    """EIA-930's hourly wind plus solar net generation of a balancing authority from EIA's workbook (the mix's reader),
    NaN where either is blank; None when the workbook is not on this machine. extract: a small saved copy of the two
    columns (ts_utc, wind, solar), read when it exists and written when it does not, so a second run need not reopen
    a 100 MB workbook."""
    if extract and os.path.exists(extract):
        e = pd.read_csv(extract, skiprows=ip.header_rows(extract))
        e.index = pd.to_datetime(e["ts_utc"], utc=True)
        log(f"  shares: EIA's {ba} hours read from the saved extract {extract} ({len(e):,} hours)")
        return wind_solar(e["wind"], e["solar"], log)
    try:
        import mix_profile as mp
        x, path = mp.eia_hourly(ba)
    except FileNotFoundError as err:
        log(f"  shares: {err}; EIA's workbook is not read")
        return None
    if extract:
        os.makedirs(os.path.dirname(extract), exist_ok=True)
        with open(extract, "w", encoding="utf-8", newline="") as f:
            f.write(f"# ERW extract of {os.path.relpath(path, ROOT)}, sheet Published Hourly Data: EIA's Adjusted wind (WND, WNB) and solar (SUN, SNB) net generation, MW, by hour start (UTC); blank where EIA's is\n")
            x[["wind", "solar"]].rename_axis("ts_utc").to_csv(f, date_format="%Y-%m-%dT%H:%M:%SZ", lineterminator="\n")
    log(f"  shares: EIA's {ba} hours read from {os.path.relpath(path, ROOT)} ({len(x):,} hours)")
    return wind_solar(x["wind"], x["solar"], log)


def wind_solar(wind, solar, log=None):
    """Wind plus solar by hour, NaN (not held) where either is blank or where the wind figure is exactly zero: a zero
    for a whole balancing authority's wind is a figure not reported, not a calm hour (for SPP: 1,464 hours, every one in
    July and August 2018, EIA's first weeks of generation by source; the lowest hour of wind after them is 148 MW)."""
    zero = wind == 0
    if log is not None and zero.any():
        z = wind.index[zero]
        log(f"  shares: {int(zero.sum()):,} hours with wind of exactly zero are not held ({z.min():%Y-%m-%d} to {z.max():%Y-%m-%d})")
    return (wind + solar).where(~zero)


def spp_inputs(in_dir, log, extract=None):
    """SPP: the curtailed MWh by day (spp:SPP), and EIA-930's wind and solar output by day from each source held."""
    d = read_vars(os.path.join(in_dir, "spp_curtailment_daily.csv"), ["curtailed_solar_mwh", "curtailed_wind_mwh"], "spp:SPP")
    cur = daily_sum(d, ["curtailed_solar_mwh", "curtailed_wind_mwh"])
    outputs = []
    wb = eia_workbook_hours("SWPP", log, extract)
    if wb is not None:
        outputs.append(("eia930_workbook", whole_days(wb, SPP_TZ)))
    p = os.path.join(in_dir, "eia930_all_generation.csv")
    if os.path.exists(p):
        g = read_vars(p, ["net_generation_wind_mw", "net_generation_solar_mw"], "eia930:SWPP")
        w = g.pivot_table(index="ts_utc", columns="variable", values="value", aggfunc="last").reindex(columns=["net_generation_wind_mw", "net_generation_solar_mw"]).dropna()
        w.index = pd.to_datetime(w.index, utc=True)
        w = w.sort_index()
        outputs.append(("eia930_all_generation", whole_days(wind_solar(w["net_generation_wind_mw"], w["net_generation_solar_mw"], log), SPP_TZ)))
    log("  shares, spp: curtailment held for {:,} days; output by day: {}".format(len(cur), ", ".join(f"{b} {len(x):,}" for b, x in outputs)))
    return cur, outputs


def grid_months(tz, cur, outputs, this_month):
    """{month: record} for every whole month the curtailment touches, before the month in progress."""
    out = {}
    if not outputs:
        return out
    for month in sorted({d[:7] for d in cur}):
        if month >= this_month:
            continue
        out[month] = best_month(month, tz, cur, outputs)
    return out


def build(in_dir, log, this_month=None, extract=None):
    """{"caiso": {month: record}, "spp": {month: record}}: every month's share or the reason it has none."""
    this_month = this_month or pd.Timestamp.now(tz="UTC").strftime("%Y-%m")
    cur, outputs = caiso_inputs(in_dir, log)
    grids = {"caiso": grid_months(CAISO_TZ, cur, outputs, this_month)}
    cur, outputs = spp_inputs(in_dir, log, extract)
    grids["spp"] = grid_months(SPP_TZ, cur, outputs, this_month)
    for g, months in grids.items():
        n = sum("share_pct" in r for r in months.values())
        log(f"  shares, {g}: {n} of {len(months)} months with a share; none for: {', '.join(m for m, r in months.items() if 'share_pct' not in r) or 'no month'}")
    return grids


ENTITY = {"caiso": ("caiso:ISO", "US-CA"), "spp": ("spp:SPP", "")}


def rows(grids):
    """The share rows of iso_curtailment_monthly: five variables a month, only for a month with a share."""
    out = []
    for g, months in grids.items():
        entity, geo = ENTITY[g]
        for month, r in months.items():
            if "share_pct" not in r:
                continue
            vals = {"share_curtailed_pct": r["share_pct"], "share_curtailed_mwh": r["curtailed_mwh"], "share_output_mwh": r["output_mwh"],
                    "share_hours_held": r["hours_held"], "share_hours_in_month": r["hours_in_month"]}
            for v, unit in VARS.items():
                out.append({"entity": entity, "variable": v, "ts_utc": f"{month}-01T00:00:00Z", "value": float(vals[v]), "unit": unit, "freq": "P1M", "geo": geo})
    return out


def site_view(grids, built):
    view = {"built": built, "near_hours": NEAR_HOURS, "table": "iso_curtailment_monthly", "variables": list(VARS),
            "definition": "curtailed MWh over curtailed plus wind and solar output MWh, over the days of the month both are held; written when those days hold at least 95 percent of the month's hours",
            "definitions": DEFINITIONS, "basis_words": BASIS_WORDS, "grids": {}}
    for g, months in grids.items():
        have = {m: r for m, r in months.items() if "share_pct" in r}
        view["grids"][g] = {"entity": ENTITY[g][0], "months_with_share": len(have), "months": have,
                            "missing": {m: r["missing"] for m, r in months.items() if "share_pct" not in r},
                            "by_basis": {b: sum(r["basis"] == b for r in have.values()) for b in sorted({r["basis"] for r in have.values()})}}
    view["grids"]["spp"]["not_covered"] = {"spp:SWPW": "SPP's western balancing authority area: no hourly wind and solar output for it is held, so it has no share"}
    return view


def main(argv=None):
    ap = argparse.ArgumentParser(description="The share of available wind and solar output curtailed, by month: CAISO and SPP")
    ap.add_argument("--out-dir", help="a trial run: shares.json and share_rows.csv under this directory; nothing in site/data")
    ap.add_argument("--in-dir", help="read the tables from this directory instead of warehouse/output")
    ap.add_argument("--eia-extract", help="a saved copy of EIA's SWPP wind and solar hours: read when it exists, written when not")
    a = ap.parse_args(argv)
    lines = []

    def log(s):
        lines.append(s)
        print(s)
    grids = build(a.in_dir or ip.OUT_DIR, log, extract=a.eia_extract)
    built = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    target = os.path.join(a.out_dir, "shares.json") if a.out_dir else SITE_FILE
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as f:
        json.dump(site_view(grids, built), f, separators=(",", ":"), allow_nan=False)
    if a.out_dir:
        pd.DataFrame(rows(grids)).to_csv(os.path.join(a.out_dir, "share_rows.csv"), index=False, lineterminator="\n")
        with open(os.path.join(a.out_dir, "shares.log"), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines) + "\n")
    print(f"curtailment shares: caiso {sum('share_pct' in r for r in grids['caiso'].values())} months, spp {sum('share_pct' in r for r in grids['spp'].values())} months; written {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
