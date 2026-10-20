#!/usr/bin/env python3
"""EIA-930's hourly net generation summed by year against EIA's annual figure by balancing authority (session 323).

Energy Research Warehouse (ERW). docs/methods/eia_annual_crosscheck.md. The Grid pack's question 5 (docs/reviews/packs/
grid.md): can the hourly sums be checked against a published annual figure? EIA publishes none by balancing authority in
the Electric Power Annual; eia_annual_generation_ba sums Form EIA-923's plant rows by their balancing authority code
(warehouse/connectors/eia923_annual_ba.py). This compares, per balancing authority and year:

    eia930_net_generation_mwh   the sum of EIA-930's hourly net generation (the BA's workbook, sheet Published Hourly
                                Data, column Net generation; the extract the emissions connector saves), with the hours held
    eia923_net_generation_mwh   EIA-923's annual net generation of the plants coded to the BA, storage included
    gap_mwh, gap_pct            EIA-930 less EIA-923, and as a percent of EIA-923
    eia930_hours, expected_hours

The eight BAs whose workbooks the ERW reads: CISO, ERCO, ISNE, MISO, NYIS, PJM, SWPP, and US48 (EIA-923's sum over the
plants of every Lower 48 code: every code but none, HECO and the state-fuel increment). x_reason is the likely reason, by
rule: a gap within 2 percent; the hours EIA-930 lacks, when filling them at the year's mean brings the gap within 2
percent; else the likely reason by the gap's sign (EIA-930 lower: generation the BA does not meter, such as industrial
self-generation behind a plant's own meter, which EIA-923 counts at the plant; EIA-930 higher: generation the BA meters
from plants EIA-923 codes elsewhere). These are hypotheses for the method note, not EIA's stated reasons.

    python warehouse/derived/eia_annual_crosscheck.py [--extracts DIR]
"""

import argparse
import datetime as dt
import glob
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

NAME = "eia_annual_crosscheck_ba"
ANNUAL = "eia_annual_generation_ba"
SOURCE = "erw:eia_annual_crosscheck_ba"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/eia_annual_crosscheck.md"
BAS = ["CISO", "ERCO", "ISNE", "MISO", "NYIS", "PJM", "SWPP", "US48"]
NOT_L48 = {"none", "HECO", "state_fuel_increment"}
CLOSE = 2.0  # percent


def newest_extracts():
    runs = sorted(glob.glob(os.path.join(ip.ROOT, "warehouse", "raw", "eia930_emissions", "*")))  # not RAW_DIR: --out-dir moves it
    for r in reversed(runs):
        if all(os.path.exists(os.path.join(r, f"{b.lower()}_hours.csv")) for b in BAS):
            return r
    raise RuntimeError("no saved EIA-930 workbook extracts for all eight BAs under warehouse/raw/eia930_emissions/")


def extract_meta(path):
    meta = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            for part in line[1:].strip().split("; "):
                if "=" in part:
                    k, v = part.split("=", 1)
                    meta[k.strip()] = v.strip()
    return meta


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA-930's hourly sums against EIA-923's annual figure (session 323)")
    ap.add_argument("--extracts", help="the folder of <ba>_hours.csv extracts (default: the newest holding all eight)")
    ap.add_argument("--out-dir")
    args = ap.parse_args(argv)
    if args.out_dir:
        ip.set_out_dir(args.out_dir)
    now = dt.datetime.now(dt.timezone.utc)
    run_id, stamp = now.strftime("%Y%m%dT%H%M%SZ"), now.strftime("%Y-%m-%dT%H:%M:%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    ann_path = os.path.join(ip.OUT_DIR, ANNUAL + ".csv")
    if not os.path.exists(ann_path):
        ann_path = os.path.join(ip.ROOT, "warehouse", "output", ANNUAL + ".csv")
    ann = ip.read_series(ann_path)
    ann["value"] = pd.to_numeric(ann["value"])
    ann["year"] = ann["ts_utc"].str[:4].astype(int)
    ann["ba"] = ann["entity"].str.split(":", n=1).str[1]
    gen = ann[ann["variable"].isin(["net_generation_mwh", "storage_net_generation_mwh"])]
    by = gen.groupby(["ba", "year"])["value"].sum()
    l48 = gen[~gen["ba"].isin(NOT_L48)].groupby("year")["value"].sum()
    years = sorted(ann["year"].unique())
    folder = args.extracts or newest_extracts()
    rows, used = [], []
    for ba in BAS:
        path = os.path.join(folder, f"{ba.lower()}_hours.csv")
        meta = extract_meta(path)
        used.append(f"{ba}: {meta.get('workbook_url', '')} (Last-Modified {meta.get('last_modified', '')})")
        x = pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["ts_utc", "net_generation_mwh"])
        x["year"] = x["ts_utc"].str[:4].astype(int)
        x["v"] = pd.to_numeric(x["net_generation_mwh"], errors="coerce")
        for y in years:
            h = x[(x["year"] == y) & x["v"].notna()]
            want = int((pd.Timestamp(f"{y + 1}-01-01") - pd.Timestamp(f"{y}-01-01")) / pd.Timedelta(hours=1))
            e930 = float(h["v"].sum())
            e923 = float(l48[y]) if ba == "US48" else float(by.get((ba, y), float("nan")))
            gap = e930 - e923
            pct = 100 * gap / e923 if e923 else float("nan")
            filled = 100 * (e930 * want / len(h) - e923) / e923 if len(h) and e923 else float("nan")
            short = f" (EIA-930 also lacks {want - len(h)} of the year's {want} hours)" if len(h) < want else ""
            if abs(pct) <= CLOSE:
                why = f"within {CLOSE:g} percent: the two counts agree to the size of what each leaves out{short}"
            elif len(h) < want and abs(filled) <= CLOSE:
                why = (f"EIA-930 lacks {want - len(h)} of the year's {want} hours; at the year's mean hour they would bring "
                       f"the gap to {filled:+.2f} percent")
            elif pct < 0:
                why = ("likely: EIA-930 lower because it counts what the balancing authority meters, while EIA-923 counts each "
                       "plant's own net generation, industrial self-generation consumed on site among it; or plants coded to "
                       "the BA are scheduled into a neighbour" + short)
            else:
                why = ("likely: EIA-930 higher because the BA meters generation from plants EIA-923 codes to another "
                       "balancing authority (dynamic schedules, pseudo-ties), or EIA-930's own reporting" + short)
            base = dict(entity=f"eia930:{ba}", ts_utc=f"{y}-01-01T00:00:00Z", freq="P1Y", geo="US", market="", node="",
                        source=SOURCE, source_url=METHOD_URL, retrieved_at=stamp, vintage="", x_reason=why)
            for var, val, unit in (("eia930_net_generation_mwh", e930, "MWh"), ("eia923_net_generation_mwh", e923, "MWh"),
                                   ("gap_mwh", gap, "MWh"), ("gap_pct", pct, "pct"),
                                   ("eia930_hours", float(len(h)), "count"), ("expected_hours", float(want), "count")):
                rows.append(dict(base, variable=var, value=round(val, 3), unit=unit))
            log(f"  {ba} {y}: EIA-930 {e930:,.0f} MWh ({len(h)} of {want} hours), EIA-923 {e923:,.0f} MWh, gap {pct:+.2f} percent")
    out = pd.DataFrame(rows)
    cols = ip.SERIES_COLS + ["x_reason"]
    header = [
        "Energy Research Warehouse (ERW): EIA-930's hourly net generation summed by year against EIA's annual figure (Form EIA-923, summed by balancing authority), session 323",
        "Shape: series (docs/datastandard.md v0), P1Y; entity eia930:<BA>; variables eia930_net_generation_mwh, eia923_net_generation_mwh (storage "
        "included), gap_mwh (EIA-930 less EIA-923), gap_pct (of EIA-923), eia930_hours, expected_hours; x_reason the likely reason by rule "
        "(docs/methods/eia_annual_crosscheck.md). US48: EIA-923's sum over every Lower 48 code",
        f"Derived from: {ANNUAL}",
        f"EIA-930's hours: the per-BA workbooks (sheet Published Hourly Data; the extracts in {os.path.relpath(folder, ip.ROOT).replace(os.sep, '/')}, "
        "raw files, not in git): " + ", ".join(used),
        f"Source: {SOURCE} ERW cross-check of EIA's hourly and annual generation by balancing authority, {METHOD_URL}",
        f"Retrieved: {run_id} (UTC) by warehouse/derived/eia_annual_crosscheck.py",
        f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
        "License: public (derived from EIA's public-domain data). Credit: U.S. Energy Information Administration.",
    ]
    path = os.path.join(ip.OUT_DIR, NAME + ".csv")
    if os.path.exists(path):
        os.remove(path)
    ip.write_csv(out[cols], NAME, header, log, cols=cols)
    ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW)",
                            report="Cross-check of EIA-930's hourly sums against EIA-923's annual net generation by balancing authority (session 323)",
                            report_url=METHOD_URL, document_list="", license="public", tables=[NAME])])
    print(f"{NAME}: {len(out)} rows, {len(BAS)} BAs, years {years}")
    log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
