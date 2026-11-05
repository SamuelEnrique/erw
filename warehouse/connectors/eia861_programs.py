#!/usr/bin/env python3
"""EIA-861: each utility's demand response and dynamic pricing programs, by state and year (session 868, chain 047).

Energy Research Warehouse (ERW) connector. Two series tables from the U.S. Energy Information Administration's Form
EIA-861 annual files (in f861<year>.zip; the zips eia861_sales.py saved):

    eia861_demand_response    Demand_Response_<year>.xlsx: by sector (residential, commercial, industrial,
                              transportation, total), customers_enrolled (count), energy_savings (MWh),
                              potential_peak_savings and actual_peak_savings (MW), customer_incentives and other_costs (USD,
                              EIA's thousand dollars times 1,000); variable <measure>_<sector>
    eia861_dynamic_pricing    Dynamic_Pricing_<year>.xlsx: customers_enrolled_<sector> (count); and on every row of a
                              utility, the kinds of program EIA marks by sector (x_tou_, x_rtp_, x_vpp_, x_cpp_, x_cpr_
                              <sector>: time of use, real time, variable peak, critical peak pricing, critical peak rebate;
                              Y, N or empty as EIA gives them)

    entity    eia861_dr:<utility>:<state>:<ba> or eia861_dp:<utility>:<state>:<ba> (ba empty before 2017); ts_utc the data year's 1 January; freq P1Y;
              geo US-<state>; node the utility's name; x_utility_number, x_state, x_ba_code (from 2017) as EIA gives them

Every column is found by its stacked headings (a group, a measure, a sector), not by position: 2017 adds a BA Code
column and 2019 a Short Form column. EIA's aggregates 88888 and 99999 are left out, as eia861_sales.py leaves them; a "."
cell has no row; nothing is filled. Two rows EIA gives under one utility, state and balancing authority with
different values have no key: both are left out and named in the header (chain 030's rule). A heading the map does not know stops the run (the demand response file's "DSM
Program" flags are read past, named in the header); so does a key given twice.

    python warehouse/connectors/eia861_programs.py --years 2015 ... 2025 --offline

Ceiling: two requests a year (the page and the zip), none when both are saved in warehouse/raw/eia861/. EIA's robots
file disallows /archive/ (session 666): a year there is read only from a zip already saved. License: public (EIA, record 1
of license_reads.csv; cite "U.S. Energy Information Administration, Form EIA-861").
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402
from eia861_sales import NOT_UTILITIES, PAGE, UA, held_text, zip_url  # noqa: E402  the same page, zips and aggregates

CONNECTOR = "eia861"
SECTORS = ["residential", "commercial", "industrial", "transportation", "total"]
DR_MEASURES = {"number of customers enrolled": ("customers_enrolled", "count", 1.0), "energy savings (mwh)": ("energy_savings", "MWh", 1.0),
               "potential peak demand savings (mw)": ("potential_peak_savings", "MW", 1.0),
               "actual peak demand savings (mw)": ("actual_peak_savings", "MW", 1.0),
               "customer incentives (thousand dollars)": ("customer_incentives", "USD", 1000.0),
               "all other costs (thousand dollars)": ("other_costs", "USD", 1000.0)}
DP_FLAGS = {"time of use pricing": "tou", "real time pricing": "rtp", "variable peak pricing": "vpp",
            "critical peak pricing": "cpp", "critical peak rebate": "cpr"}
TABLES = {
    "Demand_Response": dict(name="eia861_demand_response", prefix="eia861_dr", source="eia:eia861:demand_response"),
    "Dynamic_Pricing": dict(name="eia861_dynamic_pricing", prefix="eia861_dp", source="eia:eia861:dynamic_pricing"),
}
BASE_X = ["x_utility_number", "x_state", "x_ba_code"]
DP_X = [f"x_{f}_{s}" for f in DP_FLAGS.values() for s in SECTORS[:4]]


def text(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return re.sub(r"\s+", " ", str(v)).strip()


def paths(frame):
    """(heading row, [(column, [heading of each row above, carried right])]); a row's heading carries right until the
    row names another, and a higher row's new heading clears the lower ones."""
    heads = [r for r in range(min(5, len(frame))) if any(text(v) == "Utility Number" for v in frame.iloc[r])]
    if not heads:
        raise RuntimeError("no heading row names 'Utility Number'")
    hr = heads[0]
    cur = [""] * (hr + 1)
    out = []
    for c in range(frame.shape[1]):
        for r in range(hr + 1):
            v = text(frame.iloc[r, c])
            if v:
                cur[r] = v
                for lower in range(r + 1, hr + 1):
                    cur[lower] = text(frame.iloc[lower, c])
                break
        out.append((c, [x.lower() for x in cur]))
    return hr, out


def sheet_rows(frame, kind, year, url, retrieved, skipped):
    meta = TABLES[kind]
    hr, cols = paths(frame)
    chars = {p[-1]: c for c, p in cols if p[-1] in ("data year", "utility number", "utility name", "state", "ba code")}
    for k in ("data year", "utility number", "utility name", "state"):
        if k not in chars:
            raise RuntimeError(f"{kind} {year}: the heading '{k}' is missing")
    figs, flags = {}, {}
    for c, p in cols:
        sector = p[-1]
        if c in chars.values() or sector in ("short form",):
            continue
        if kind == "Demand_Response":
            measure = next((m for m in DR_MEASURES if m in p), None)
            if measure and sector in SECTORS:
                figs[(measure, sector)] = c
            elif any("dsm program" in x for x in p):
                skipped["DSM Program flags"] = True
            else:
                raise RuntimeError(f"{kind} {year}: column {c} {p} is not in the map")
        else:
            if any("customers enrolled" in x for x in p) and sector in SECTORS:
                figs[("customers enrolled", sector)] = c
            else:
                flag = next((f for f in DP_FLAGS if f in p), None)
                if flag and sector in SECTORS[:4]:
                    flags[f"x_{DP_FLAGS[flag]}_{sector}"] = c
                else:
                    raise RuntimeError(f"{kind} {year}: column {c} {p} is not in the map")
    want = len(DR_MEASURES) * 5 if kind == "Demand_Response" else 5
    if len(figs) != want or (kind == "Dynamic_Pricing" and len(flags) != len(DP_X)):
        raise RuntimeError(f"{kind} {year}: {len(figs)} figures and {len(flags)} flags found")
    d = frame.iloc[hr + 1:]
    d = d[pd.to_numeric(d[chars["data year"]], errors="coerce").eq(year)]
    d = d[~pd.to_numeric(d[chars["utility number"]], errors="coerce").isin(NOT_UTILITIES)]
    out = []
    for _, r in d.iterrows():
        util, state = text(r[chars["utility number"]]), text(r[chars["state"]])
        ba = text(r[chars["ba code"]]) if "ba code" in chars else ""
        base = dict(entity=f"{meta['prefix']}:{util}:{state}:{ba}", ts_utc=f"{year}-01-01T00:00:00Z", freq="P1Y",
                    geo=f"US-{state}" if state else "US", market="", node=text(r[chars["utility name"]]), source=meta["source"],
                    source_url=url, retrieved_at=retrieved, vintage="", x_utility_number=util, x_state=state,
                    x_ba_code=ba)
        if kind == "Dynamic_Pricing":
            base.update({k: text(r[c]) for k, c in flags.items()})
        for (measure, sector), c in figs.items():
            v = pd.to_numeric(r[c], errors="coerce")
            if pd.isna(v):
                continue
            if kind == "Demand_Response":
                var, unit, scale = DR_MEASURES[measure]
            else:
                var, unit, scale = "customers_enrolled", "count", 1.0
            out.append(dict(base, variable=f"{var}_{sector}", value=float(v) * scale, unit=unit))
    t = pd.DataFrame(out)
    if len(t):
        # chain 030's rule: a row EIA gives twice with every field the same is kept once; two different rows under one
        # utility, state and balancing authority have no key and are both left out, counted (2015: Wabash Valley, IN)
        t = t.drop_duplicates()
        twice = t.duplicated(["entity", "variable", "ts_utc"], keep=False)
        if twice.any():
            bad = set(t.loc[twice, "entity"])                      # the whole record goes, not only the figures that differ
            skipped.setdefault("no key", set()).update(f"{e} {year}" for e in bad)
            t = t[~t["entity"].isin(bad)]
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA-861 utilities' demand response and dynamic pricing programs")
    ap.add_argument("--years", type=int, nargs="+", required=True, help="the data years")
    ap.add_argument("--offline", action="store_true", help="never a request: the saved page and zips, or nothing")
    ap.add_argument("--out-dir", help="a trial: the tables under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"eia861_programs_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, headers=UA)
        html = page.decode("utf-8", errors="replace")
        frames = {k: [] for k in TABLES}
        urls, skipped = [], {}
        for y in sorted(args.years):
            url, year = zip_url(html, y)
            if "/archive/" in url and not ip.raw_cached(CONNECTOR, url):
                raise RuntimeError(f"{url} is under /archive/, which EIA's robots file disallows (session 666), and is not saved; not asked")
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=600)
            zf = zipfile.ZipFile(io.BytesIO(content))
            for kind in TABLES:
                name = next((n for n in zf.namelist() if n in (f"{kind}_{year}.xlsx", f"{kind}{year}.xlsx")), None)
                if not name:
                    raise RuntimeError(f"f861{year}.zip holds no {kind} file")
                xl = pd.ExcelFile(io.BytesIO(zf.read(name)))
                for sheet in xl.sheet_names:
                    t = sheet_rows(pd.read_excel(xl, sheet, header=None), kind, year, url, rec["retrieved_at"], skipped)
                    log(f"{year} {kind} {sheet}: {len(t):,} rows")
                    frames[kind].append(t)
            urls.append(url)
        for kind, meta in TABLES.items():
            s = pd.concat([f for f in frames[kind] if len(f)], ignore_index=True)
            if s.duplicated(["entity", "variable", "ts_utc"]).any():
                raise RuntimeError(f"{kind}: a row in both sheets")
            cols = ip.SERIES_COLS + BASE_X + (DP_X if kind == "Dynamic_Pricing" else [])
            s = s[cols]
            years = sorted({int(t[:4]) for t in s["ts_utc"]})
            what = ("customers enrolled, energy savings (MWh), potential and actual peak savings (MW), customer incentives and other costs (USD)"
                    if kind == "Demand_Response" else "customers enrolled (count), with the kinds of program EIA marks by sector in x_tou_, x_rtp_, x_vpp_, x_cpp_, x_cpr_<sector>")
            header = [
                f"Energy Research Warehouse (ERW): EIA-861 {kind.replace('_', ' ').lower()} programs, each utility by state and sector, a year (session 868)",
                f"Shape: series (docs/datastandard.md v0). entity {meta['prefix']}:<utility>:<state>:<balancing authority, empty before 2017>; variable <measure>_<sector>: {what}; ts_utc the data year's 1 January; freq P1Y; node the utility's name; x_* EIA's fields.",
                f"Years held: {held_text(years)}; {len(s):,} rows, {s['x_utility_number'].nunique():,} utilities. EIA's aggregates 88888 and 99999 left out; a '.' cell has no row; nothing is filled."
                + (" The file's DSM Program flags are not taken." if "DSM Program flags" in skipped and kind == "Demand_Response" else "")
                + (f" Rows EIA gives twice with two values, left out (no key): {', '.join(sorted(x for x in skipped.get('no key', ()) if x.startswith(meta['prefix'])))}." if any(x.startswith(meta['prefix']) for x in skipped.get('no key', ())) else ""),
                f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia861_programs.py (the zips as saved by earlier runs)",
                f"Run log: warehouse/output/logs/eia861_programs_{run_id}.log",
                f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
                f"Source: {meta['source']} U.S. Energy Information Administration, Form EIA-861 Annual Electric Power Industry Report ({kind}_<year>.xlsx), {PAGE}",
                f"  access: {'; '.join(urls)}",
                'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Form EIA-861").',
            ]
            ip.write_snapshot(s, meta["name"], header, log, cols)
            if not args.out_dir:
                ip.update_sources([dict(source=meta["source"], publisher="U.S. Energy Information Administration (EIA)",
                                        report=f"Form EIA-861 Annual Electric Power Industry Report, {kind.replace('_', ' ').lower()}",
                                        report_url=PAGE, document_list=PAGE, license="public", tables=[meta["name"]])])
            results.append(dict(table=meta["name"], market="all", status="ok", detail=f"{held_text(years)}: {len(s):,} rows"))
            print(f"{meta['name']}: {held_text(years)}, {len(s):,} rows, {s['x_utility_number'].nunique():,} utilities")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"eia861_programs FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table="eia861_demand_response", market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status("eia861_programs", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
