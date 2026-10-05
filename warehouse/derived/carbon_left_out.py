#!/usr/bin/env python3
"""The months of carbon intensity the rule for impossible values would not write, for the pages that still read the
held tables (session 118).

Energy Research Warehouse (ERW). carbon_intensity_hourly, _daily and _monthly are behind a live page (the network shows
each grid's newest hour, and the home page counts their rows), so the rule of docs/methods/impossible_hours.md is in
their builder and HELD until a person approves the numbers it moves (impossible_hours.HELD). Until then the tables
carry months computed on an impossible hour, and California's months of the hydro gap. A page in review must not show a
figure the faults register calls wrong, so this script writes which months those are, and the pages leave them out and
say so (site/lib/carbonLeftOut.ts; /emissions and the grid pages).

A month is listed for a balancing authority and a variable when the held monthly table holds it and

  - an hour of it fails rule A in the denominator of that variable (demand for intensity_demand, net generation for
    intensity_generation), or
  - for California, an hour of it lies in the hydro gap (impossible_hours.CISO_NO_HYDRO), either variable.

The table's own rule writes a month only when every hour of every day is held, so these are exactly the months the
held build would stop writing for those two reasons. Nothing is computed here but the list: no intensity, no average.
When the hold is lifted the tables no longer hold these months and the list is empty by itself.

    python warehouse/derived/carbon_left_out.py            # writes site/data/carbon_left_out.json
    python warehouse/derived/carbon_left_out.py --check    # prints the list, writes nothing
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
import eia930_emissions as em  # noqa: E402
import impossible_hours as ih  # noqa: E402
import iso_prices as ip  # noqa: E402

MONTHLY = "carbon_intensity_monthly"
SITE_FILE = os.path.join(ROOT, "site", "data", "carbon_left_out.json")
DENOMINATOR = {"intensity_demand": "demand_mwh", "intensity_generation": "net_generation_mwh"}


def months_with_impossible_hours(x):
    """{variable: {month: [the hours not used, as the source gave them]}} of one balancing authority's extract."""
    idx = pd.DatetimeIndex(pd.to_datetime(x["ts_utc"], utc=True))
    out = {}
    for var, col in DENOMINATOR.items():
        raw = pd.Series(pd.to_numeric(x[col], errors="coerce").to_numpy(), index=idx)
        full = raw.reindex(pd.date_range(idx.min(), idx.max(), freq="h"))
        lo = ih.left_out(full)
        lo = lo[lo["reason"] != ih.REASONS[0]]   # a blank is already a missing hour to the table
        by = {}
        for ts, r in lo.iterrows():
            by.setdefault(ts.strftime("%Y-%m"), []).append(
                dict(hour=ts.strftime("%Y-%m-%dT%H:%M:%SZ"), value=float(r["value"]), reason=r["reason"]))
        out[var] = by
    return out


def build(monthly_path=None, extracts=None):
    """The site's file as a dict. monthly_path: the held monthly table; extracts: {ba code: extract frame}, else the
    newest extract of each on this machine."""
    path = monthly_path or os.path.join(ip.OUT_DIR, MONTHLY + ".csv")
    held = pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False, usecols=["entity", "variable", "ts_utc", "ba"])
    held["month"] = held["ts_utc"].str[:7]
    if extracts is None:
        extracts = {}
        for code in em.FILE:
            p = em.latest_extract(code)
            if p is None:
                raise RuntimeError(f"no extract of {code} under warehouse/raw/eia930_emissions/; nothing written")
            extracts[code] = em.read_extract(p)[["ts_utc", "demand_mwh", "net_generation_mwh"]]
    gap_months = sorted(set(pd.date_range(ih.CISO_NO_HYDRO[0], ih.CISO_NO_HYDRO[1], freq="h").strftime("%Y-%m")))
    rows = []
    for code, x in sorted(extracts.items()):
        bad = months_with_impossible_hours(x)
        h = held[held["ba"] == code]
        for var in sorted(DENOMINATOR):
            have = h[h["variable"] == var]
            entity = have["entity"].iloc[0] if len(have) else None
            for month in sorted(set(have["month"])):
                hours = bad[var].get(month, [])
                in_gap = code == "ciso" and month in gap_months
                if not hours and not in_gap:
                    continue
                why = []
                if in_gap:
                    why.append("EIA's file holds no hydro for California in this month's hours")
                if hours:
                    why.append(f"{len(hours)} impossible hour{'s' if len(hours) != 1 else ''} of {'demand' if var == 'intensity_demand' else 'net generation'}")
                rows.append(dict(entity=entity, ba=code, variable=var, month=month, why="; ".join(why), hours=hours[:6], hours_total=len(hours)))
    return dict(table=MONTHLY, built=ip.utc_iso(pd.Timestamp.now(tz="UTC")), held=sorted(t for t in ih.HELD if t.startswith("carbon_intensity")),
                hydro_gap=dict(entity="eia930:CISO", first_hour=ih.CISO_NO_HYDRO[0], last_hour=ih.CISO_NO_HYDRO[1],
                               hours=len(pd.date_range(ih.CISO_NO_HYDRO[0], ih.CISO_NO_HYDRO[1], freq="h"))),
                rule=dict(jump=ih.JUMP, range=[round(ih.RANGE[0], 4), ih.RANGE[1]]), months=rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the months of carbon intensity the pages leave out while the tables are held")
    ap.add_argument("--check", action="store_true", help="print the list and write nothing")
    a = ap.parse_args(argv)
    out = build()
    for r in out["months"]:
        print(f"{r['entity']} {r['variable']} {r['month']}: {r['why']}")
    print(f"{len(out['months'])} months of {MONTHLY} the pages leave out")
    if not a.check:
        with open(SITE_FILE, "w", encoding="utf-8", newline="\n") as f:
            json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")
        print("written", os.path.relpath(SITE_FILE, ROOT).replace(os.sep, "/"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
