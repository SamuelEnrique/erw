#!/usr/bin/env python3
"""EIA-861: each utility's distributed generation that is not net metered, by technology and sector, a year (session 883, chain 048).

Energy Research Warehouse (ERW) connector. One series table from the U.S. Energy Information Administration's Form
EIA-861 annual files (Non_Net_Metering_Distributed_<year>.xlsx in f861<year>.zip, 2016 on; the zips eia861_sales.py
saved): the generators on customers' or the utility's distribution system that are not net metered.

    eia861_distributed_generation   number_of_generators (count), total_capacity, capacity_backup_only and
                                    capacity_utility_owned (MW); and <technology>_capacity_<sector> (MW) for the
                                    technologies pv, battery, wind, hydro, fuel_cell, internal_combustion,
                                    combustion_turbine, steam, other and total, the sectors residential, commercial,
                                    industrial, transportation, direct_connected and total; battery_energy_<sector>
                                    (MWh, 2023 on)

    entity    eia861_dg:<utility>:<state>:<ba>; ts_utc the data year's 1 January; freq P1Y; geo US-<state>; node the
              utility's name; x_utility_number, x_state, x_ba_code and x_capacity_type (AC or DC: EIA's column "Type", whether
              the utility gives the capacity in alternating or direct current) as EIA gives them

Every column is found by its stacked headings (a technology, a sector), not by position, with the reader of
eia861_programs.py: EIA's 2016 file has a title row over the headings, its "Storage" became "Battery" in 2023 beside a
new "Battery Energy (MWh)", and 2023 on add a state-level sheet with no utility (not read). 2015's file is of another form
(technology totals without sectors, and dispersed generation) and is not taken. A heading the map does not know stops the
run. EIA's aggregates 88888 and 99999 are left out, as eia861_sales.py leaves them; a "." cell has no row; nothing is
filled. Two rows EIA gives under one utility, state and balancing authority with different values have no key: both are
left out and named in the header (chain 030's rule).

    python warehouse/connectors/eia861_distributed_generation.py --years 2016 ... 2025 --offline

Ceiling: two requests a year (the page and the zip), none when both are saved in warehouse/raw/eia861/. EIA's robots
file disallows /archive/ (session 666): a year there is read only from a zip already saved. License: public (EIA, record 1
of license_reads.csv; cite "U.S. Energy Information Administration, Form EIA-861").
"""

import argparse
import datetime as dt
import io
import os
import sys
import traceback
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402
from eia861_sales import NOT_UTILITIES, PAGE, UA, held_text, zip_url  # noqa: E402  the same page, zips and aggregates
from eia861_programs import paths, text  # noqa: E402  the stacked-heading reader

CONNECTOR = "eia861"
NAME = "eia861_distributed_generation"
PREFIX = "eia861_dg"
SOURCE = "eia:eia861:distributed_generation"
# the technology groups as prefixes, the longer first ("battery energy" before "battery")
TECHS = [("photovoltaic", "pv"), ("storage", "battery"), ("battery energy", "battery_energy"), ("battery", "battery"),
         ("wind", "wind"), ("hydroelectric", "hydro"), ("fuel cell", "fuel_cell"), ("internal combustion", "internal_combustion"),
         ("combustion turbine", "combustion_turbine"), ("steam", "steam"), ("other", "other"), ("total", "total")]
SECTORS = {"residential": "residential", "commercial": "commercial", "industrial": "industrial",
           "transportation": "transportation", "direct connected": "direct_connected", "total": "total"}
COUNTS = {"number of generators": ("number_of_generators", "count"), "total capacity": ("total_capacity", "MW"),
          "capacity back-up only": ("capacity_backup_only", "MW"), "capacity utility owned": ("capacity_utility_owned", "MW")}
CHARS = {"data year": "data year", "year": "data year", "utility number": "utility number", "utility name": "utility name",
         "state": "state", "ba code": "ba code", "ba_code": "ba code"}
X = ["x_utility_number", "x_state", "x_ba_code", "x_capacity_type"]


def tech_of(p):
    """The technology a column's headings name above its own, or None."""
    for h in p[:-1]:
        for start, tech in sorted(TECHS, key=lambda t: -len(t[0])):
            if h.startswith(start):
                return tech
    return None


def sheet_rows(frame, year, url, retrieved, skipped):
    hr, cols = paths(frame)
    chars, figs = {}, {}
    for c, p in cols:
        head = p[-1]
        if head in CHARS:
            chars[CHARS[head]] = c
        elif head == "type":                    # AC or DC (session 891: read before as a data type, which it is not)
            chars["capacity type"] = c
        elif head == "short form":
            continue
        elif head in COUNTS:
            figs[COUNTS[head][0]] = (c, COUNTS[head][1])
        else:
            tech = tech_of(p)
            if tech is None or head not in SECTORS:
                raise RuntimeError(f"{year}: column {c} {p} is not in the map")
            var = f"battery_energy_{SECTORS[head]}" if tech == "battery_energy" else f"{tech}_capacity_{SECTORS[head]}"
            if var in figs:
                raise RuntimeError(f"{year}: {var} found twice")
            figs[var] = (c, "MWh" if tech == "battery_energy" else "MW")
    for k in ("data year", "utility number", "utility name", "state"):
        if k not in chars:
            raise RuntimeError(f"{year}: the heading '{k}' is missing")
    if len([v for v in figs if v.endswith("_capacity_total")]) != 10 or len(figs) < 4 + 60:
        raise RuntimeError(f"{year}: {len(figs)} figures found")
    d = frame.iloc[hr + 1:]
    d = d[pd.to_numeric(d[chars["data year"]], errors="coerce").eq(year)]
    d = d[~pd.to_numeric(d[chars["utility number"]], errors="coerce").isin(NOT_UTILITIES)]
    out = []
    for _, r in d.iterrows():
        util, state = text(r[chars["utility number"]]), text(r[chars["state"]])
        ba = text(r[chars["ba code"]]) if "ba code" in chars else ""
        base = dict(entity=f"{PREFIX}:{util}:{state}:{ba}", ts_utc=f"{year}-01-01T00:00:00Z", freq="P1Y",
                    geo=f"US-{state}" if state else "US", market="", node=text(r[chars["utility name"]]), source=SOURCE,
                    source_url=url, retrieved_at=retrieved, vintage="", x_utility_number=util, x_state=state, x_ba_code=ba,
                    x_capacity_type=text(r[chars["capacity type"]]) if "capacity type" in chars else "")
        for var, (c, unit) in figs.items():
            v = pd.to_numeric(r[c], errors="coerce")
            if pd.isna(v):
                continue
            out.append(dict(base, variable=var, value=float(v), unit=unit))
    t = pd.DataFrame(out)
    if len(t):
        # chain 030's rule: a row EIA gives twice with every field the same is kept once; two different rows under one
        # utility, state and balancing authority have no key and are both left out, the whole record, counted
        t = t.drop_duplicates()
        twice = t.duplicated(["entity", "variable", "ts_utc"], keep=False)
        if twice.any():
            bad = set(t.loc[twice, "entity"])
            skipped.setdefault("no key", set()).update(f"{e} {year}" for e in bad)
            t = t[~t["entity"].isin(bad)]
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA-861 utilities' distributed generation not net metered")
    ap.add_argument("--years", type=int, nargs="+", required=True, help="the data years, 2016 on")
    ap.add_argument("--offline", action="store_true", help="never a request: the saved page and zips, or nothing")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if min(args.years) < 2016:
        ap.error("2015's file is of another form and is not taken; give 2016 on")
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"eia861_distributed_generation_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, headers=UA)
        html = page.decode("utf-8", errors="replace")
        frames, urls, skipped = [], [], {}
        for y in sorted(args.years):
            url, year = zip_url(html, y)
            if "/archive/" in url and not ip.raw_cached(CONNECTOR, url):
                raise RuntimeError(f"{url} is under /archive/, which EIA's robots file disallows (session 666), and is not saved; not asked")
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=600)
            zf = zipfile.ZipFile(io.BytesIO(content))
            name = next((n for n in zf.namelist() if n in (f"Non_Net_Metering_Distributed_{year}.xlsx", f"Non_Net_Metering_Distributed{year}.xlsx")), None)
            if not name:
                raise RuntimeError(f"f861{year}.zip holds no Non_Net_Metering_Distributed file")
            xl = pd.ExcelFile(io.BytesIO(zf.read(name)))
            for sheet in xl.sheet_names:
                if "state level" in sheet.lower():
                    log(f"{year} {sheet}: the state-level sheet, not read")
                    continue
                t = sheet_rows(pd.read_excel(xl, sheet, header=None), year, url, rec["retrieved_at"], skipped)
                log(f"{year} {sheet}: {len(t):,} rows")
                frames.append(t)
            urls.append(url)
        s = pd.concat([f for f in frames if len(f)], ignore_index=True)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a row in both sheets")
        cols = ip.SERIES_COLS + X
        s = s[cols]
        years = sorted({int(t[:4]) for t in s["ts_utc"]})
        nokey = sorted(skipped.get("no key", ()))
        header = [
            "Energy Research Warehouse (ERW): EIA-861 distributed generation not net metered, each utility by state, technology and sector, a year (session 883)",
            f"Shape: series (docs/datastandard.md v0). entity {PREFIX}:<utility>:<state>:<balancing authority>; variables number_of_generators (count), "
            "total_capacity, capacity_backup_only, capacity_utility_owned (MW), <technology>_capacity_<sector> (MW; technologies pv, battery (EIA's "
            "Storage to 2022), wind, hydro, fuel_cell, internal_combustion, combustion_turbine, steam, other, total; sectors residential, commercial, "
            "industrial, transportation, direct_connected, total: a sum leaves total out) and battery_energy_<sector> (MWh, 2023 on); ts_utc the "
            "data year's 1 January; freq P1Y; node the utility's name; x_capacity_type AC or DC, as EIA's column Type gives the capacity.",
            f"Years held: {held_text(years)}; {len(s):,} rows, {s['x_utility_number'].nunique():,} utilities. EIA's aggregates 88888 and 99999 left out; "
            "a '.' cell has no row; nothing is filled. 2015's file, of another form, not taken; the state-level sheets of 2023 on not read."
            + (f" Rows EIA gives twice with two values, left out (no key): {', '.join(nokey)}." if nokey else ""),
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia861_distributed_generation.py (the zips as saved by earlier runs)",
            f"Run log: warehouse/output/logs/eia861_distributed_generation_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Form EIA-861 Annual Electric Power Industry Report (Non_Net_Metering_Distributed_<year>.xlsx), {PAGE}",
            f"  access: {'; '.join(urls)}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Form EIA-861").',
        ]
        ip.write_snapshot(s, NAME, header, log, cols)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Form EIA-861 Annual Electric Power Industry Report, distributed generation not net metered",
                                    report_url=PAGE, document_list=PAGE, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{held_text(years)}: {len(s):,} rows"))
        print(f"{NAME}: {held_text(years)}, {len(s):,} rows, {s['x_utility_number'].nunique():,} utilities")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"eia861_distributed_generation FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status("eia861_distributed_generation", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
