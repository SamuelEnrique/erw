#!/usr/bin/env python3
"""EIA-861: each utility's energy efficiency programs, by state, sector and year (session 881, chain 048).

Energy Research Warehouse (ERW) connector. One series table from the U.S. Energy Information Administration's Form
EIA-861 annual files (Energy_Efficiency_<year>.xlsx in f861<year>.zip; the zips eia861_sales.py saved):

    eia861_energy_efficiency  by sector (residential, commercial, industrial, transportation, total):
                              the reporting year's incremental savings, annual_energy_savings (MWh) and
                              annual_peak_savings (MW); the same programs' savings over their life, life_energy_savings
                              (MWh) and life_peak_savings (MW); the reporting year's costs, annual_customer_incentives and
                              annual_other_costs, and the life cycle's, life_customer_incentives and life_other_costs
                              (USD, EIA's thousand dollars times 1,000); weighted_average_life (year, no total);
                              variable <measure>_<sector>

    entity    eia861_ee:<utility>:<state>:<ba>; ts_utc the data year's 1 January; freq P1Y; geo US-<state>;
              node the utility's name; x_utility_number, x_state, x_ba_code and x_website as EIA gives them

Every column is found by its stacked headings (a group, a measure, a sector), not by position, with the reader of
eia861_programs.py. EIA's aggregates 88888 and 99999 are left out, as eia861_sales.py leaves them; a "." cell has no row;
nothing is filled. Two rows EIA gives under one utility, state and balancing authority with different values have no
key: both are left out and named in the header (chain 030's rule). A heading the map does not know stops the run.

    python warehouse/connectors/eia861_efficiency.py --years 2015 ... 2025 --offline

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
NAME = "eia861_energy_efficiency"
PREFIX = "eia861_ee"
SOURCE = "eia:eia861:energy_efficiency"
SECTORS = ["residential", "commercial", "industrial", "transportation", "total"]
# the group headings as prefixes: EIA writes "Cost" in some years and "Costs" in others
GROUPS = {"reporting year incremental annual saving": "annual", "incremental life cycle saving": "life",
          "reporting year incremental cost": "annual", "incremental life cycle cost": "life"}
MEASURES = {"energy savings (mwh)": ("energy_savings", "MWh", 1.0), "peak demand savings (mw)": ("peak_savings", "MW", 1.0),
            "customer incentives (thousand dollars)": ("customer_incentives", "USD", 1000.0),
            "all other costs (thousand dollars)": ("other_costs", "USD", 1000.0)}
X = ["x_utility_number", "x_state", "x_ba_code", "x_website"]


def sheet_rows(frame, year, url, retrieved, skipped):
    hr, cols = paths(frame)
    chars = {p[-1]: c for c, p in cols if p[-1] in ("data year", "utility number", "utility name", "state", "ba code", "website")}
    for k in ("data year", "utility number", "utility name", "state"):
        if k not in chars:
            raise RuntimeError(f"{year}: the heading '{k}' is missing")
    figs = {}
    for c, p in cols:
        sector = p[-1]
        if c in chars.values() or sector in ("short form",):
            continue
        group = next((GROUPS[g] for g in GROUPS if any(x.startswith(g) for x in p)), None)
        measure = next((m for m in MEASURES if m in p), None)
        if group and measure and sector in SECTORS:
            var, unit, scale = MEASURES[measure]
            figs[f"{group}_{var}_{sector}"] = (c, unit, scale)
        elif any(x.startswith("weighted average life") for x in p) and sector in SECTORS[:4]:
            figs[f"weighted_average_life_{sector}"] = (c, "year", 1.0)
        else:
            raise RuntimeError(f"{year}: column {c} {p} is not in the map")
    if len(figs) != 8 * 5 + 4:
        raise RuntimeError(f"{year}: {len(figs)} figures found, not 44")
    d = frame.iloc[hr + 1:]
    d = d[pd.to_numeric(d[chars["data year"]], errors="coerce").eq(year)]
    d = d[~pd.to_numeric(d[chars["utility number"]], errors="coerce").isin(NOT_UTILITIES)]
    out = []
    for _, r in d.iterrows():
        util, state = text(r[chars["utility number"]]), text(r[chars["state"]])
        ba = text(r[chars["ba code"]]) if "ba code" in chars else ""
        base = dict(entity=f"{PREFIX}:{util}:{state}:{ba}", ts_utc=f"{year}-01-01T00:00:00Z", freq="P1Y",
                    geo=f"US-{state}" if state else "US", market="", node=text(r[chars["utility name"]]), source=SOURCE,
                    source_url=url, retrieved_at=retrieved, vintage="", x_utility_number=util, x_state=state,
                    x_ba_code=ba, x_website=text(r[chars["website"]]) if "website" in chars else "")
        for var, (c, unit, scale) in figs.items():
            v = pd.to_numeric(r[c], errors="coerce")
            if pd.isna(v):
                continue
            out.append(dict(base, variable=var, value=float(v) * scale, unit=unit))
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
    ap = argparse.ArgumentParser(description="EIA-861 utilities' energy efficiency programs")
    ap.add_argument("--years", type=int, nargs="+", required=True, help="the data years")
    ap.add_argument("--offline", action="store_true", help="never a request: the saved page and zips, or nothing")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"eia861_efficiency_{run_id}.log"))
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
            name = next((n for n in zf.namelist() if n in (f"Energy_Efficiency_{year}.xlsx", f"Energy_Efficiency{year}.xlsx")), None)
            if not name:
                raise RuntimeError(f"f861{year}.zip holds no Energy_Efficiency file")
            xl = pd.ExcelFile(io.BytesIO(zf.read(name)))
            for sheet in xl.sheet_names:
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
            "Energy Research Warehouse (ERW): EIA-861 energy efficiency programs, each utility by state and sector, a year (session 881)",
            f"Shape: series (docs/datastandard.md v0). entity {PREFIX}:<utility>:<state>:<balancing authority>; variable <measure>_<sector>: "
            "annual_ (the reporting year's incremental savings or costs) or life_ (the same programs over their life) energy_savings (MWh), "
            "peak_savings (MW), customer_incentives or other_costs (USD, EIA's thousand dollars times 1,000), and weighted_average_life (year, "
            "no total); sectors residential, commercial, industrial, transportation, total (a sum leaves total out); ts_utc the data year's "
            "1 January; freq P1Y; node the utility's name; x_* EIA's fields.",
            f"Years held: {held_text(years)}; {len(s):,} rows, {s['x_utility_number'].nunique():,} utilities. EIA's aggregates 88888 and 99999 left out; a '.' cell has no row; nothing is filled."
            + (f" Rows EIA gives twice with two values, left out (no key): {', '.join(nokey)}." if nokey else ""),
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia861_efficiency.py (the zips as saved by earlier runs)",
            f"Run log: warehouse/output/logs/eia861_efficiency_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Form EIA-861 Annual Electric Power Industry Report (Energy_Efficiency_<year>.xlsx), {PAGE}",
            f"  access: {'; '.join(urls)}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Form EIA-861").',
        ]
        ip.write_snapshot(s, NAME, header, log, cols)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Form EIA-861 Annual Electric Power Industry Report, energy efficiency",
                                    report_url=PAGE, document_list=PAGE, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{held_text(years)}: {len(s):,} rows"))
        print(f"{NAME}: {held_text(years)}, {len(s):,} rows, {s['x_utility_number'].nunique():,} utilities")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"eia861_efficiency FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status("eia861_efficiency", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
