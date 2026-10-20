#!/usr/bin/env python3
"""EIA's annual net generation by balancing authority, summed from Form EIA-923's plant-level files (session 323).

Energy Research Warehouse (ERW) connector. The Electric Power Annual has no table by balancing authority: its index
(https://www.eia.gov/electricity/annual/, read on 19 October 2026) gives net generation by energy source, sector and
state only (Tables 3.1 to 3.27). Form EIA-923's annual file does: its sheet "Page 1 Generation and Fuel Data" names
each plant's "Balancing Authority Code" and its "Net Generation (Megawatthours)" for the year, and "Page 1 Energy
Storage" the storage plants'. This connector sums them by balancing authority and year:

    warehouse/output/eia_annual_generation_ba.csv     series, P1Y: entity eia923:<BA code>, variables
        net_generation_mwh          the sum of Page 1 Generation and Fuel Data's annual net generation (every plant,
                                    prime mover and fuel row, nuclear units included)
        storage_net_generation_mwh  the sum of Page 1 Energy Storage's annual net generation (negative: storage takes
                                    more than it returns)
        plants                      the number of plants with a row (count)
    A plant with no balancing authority code is entity eia923:none; EIA's "State-Fuel Level Increment" rows are
    eia923:state_fuel_increment.

Files: https://www.eia.gov/electricity/data/eia923/ lists one zip a year (archive/xls/f923_YYYY.zip for the closed years,
xls/f923_YYYY.zip for the newest); 2023, 2024 and 2025 were read on 19 October 2026, each "Final".

License: public. EIA's data are in the public domain (U.S. government work; https://www.eia.gov/about/copyrights_reuse.php).

    python warehouse/connectors/eia923_annual_ba.py --from-raw DIR      # the zips saved in DIR (manifest.csv names them)
"""

import argparse
import datetime as dt
import glob
import io
import os
import re
import sys
import traceback
import zipfile

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

NAME = "eia_annual_generation_ba"
PAGE = "https://www.eia.gov/electricity/data/eia923/"
EPA = "https://www.eia.gov/electricity/annual/"
SOURCE = "eia:eia923_annual"
GEN, STORE = "Page 1 Generation and Fuel Data", "Page 1 Energy Storage"


def header_row(raw):
    """The row of a sheet's column names: the first that holds "Plant Id"."""
    for i in range(min(len(raw), 20)):
        if any(str(v).strip() == "Plant Id" for v in raw.iloc[i].tolist()):
            return i
    raise RuntimeError("no header row with 'Plant Id'")


def sheet(book, name):
    raw = pd.read_excel(book, sheet_name=name, header=None, nrows=20)
    h = header_row(raw)
    df = pd.read_excel(book, sheet_name=name, header=h)
    df.columns = [re.sub(r"\s+", " ", str(c)).strip() for c in df.columns]
    return df


def sums(df, year, variable, col="Net Generation (Megawatthours)"):
    # EIA's "State-Fuel Level Increment" rows (its estimate for plants outside the monthly sample) are entity
    # eia923:state_fuel_increment; a plant with no code is eia923:none
    ba = df["Balancing Authority Code"].fillna("").astype(str).str.strip().replace(
        {"": "none", ".": "none", "State-Fuel Level Increment": "state_fuel_increment"})
    v = pd.to_numeric(df[col], errors="coerce")
    g = pd.DataFrame({"ba": ba, "v": v, "plant": df["Plant Id"]}).groupby("ba").agg(v=("v", "sum"), plants=("plant", "nunique"))
    return [(b, year, variable, float(r.v), int(r.plants)) for b, r in g.iterrows()]


def read_zip(path):
    """[(ba, year, variable, value, plants)] and the workbook's name, from one f923_YYYY.zip."""
    z = zipfile.ZipFile(path)
    name = next(n for n in z.namelist() if n.startswith("EIA923_Schedules_2_3_4_5"))
    year = int(re.search(r"_(\d{4})_", name)[1])
    book = io.BytesIO(z.read(name))
    rows = sums(sheet(book, GEN), year, "net_generation_mwh")
    try:
        rows += sums(sheet(book, STORE), year, "storage_net_generation_mwh")
    except ValueError:  # no storage sheet in this year's file
        pass
    return rows, name, year


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA-923 annual net generation by balancing authority (session 323)")
    ap.add_argument("--from-raw", required=True, help="the folder of f923_YYYY.zip files and their manifest.csv")
    ap.add_argument("--out-dir")
    args = ap.parse_args(argv)
    if args.out_dir:
        ip.set_out_dir(args.out_dir)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"eia923_annual_ba_{run_id}.log"))
    results = []
    try:
        meta = {}
        for line in open(os.path.join(args.from_raw, "manifest.csv"), encoding="utf-8"):
            p = line.rstrip("\n").split(",", 6)  # the Last-Modified date holds commas
            if len(p) >= 6:
                meta[p[4]] = dict(at=p[0], url=p[5], lm=p[6] if len(p) > 6 else "")
        rows, used = [], []
        for path in sorted(glob.glob(os.path.join(args.from_raw, "f923_*.zip"))):
            name = os.path.basename(path)
            r, book, year = read_zip(path)
            m = meta.get(name, {})
            vintage = ip.utc_iso(pd.Timestamp(m["lm"])) if m.get("lm") else ""
            rows += [dict(row=x, url=m.get("url", PAGE), at=m.get("at", ""), vintage=vintage) for x in r]
            used.append(f"{year}: {m.get('url', name)} ({book}; Last-Modified {m.get('lm', '')})")
            log(f"  {year}: {book}, {len(r)} BA-variable rows")
        out = pd.DataFrame([dict(entity=f"eia923:{x['row'][0]}", variable=x["row"][2], ts_utc=f"{x['row'][1]}-01-01T00:00:00Z",
                                 value=round(x["row"][3], 3), unit="MWh", freq="P1Y", geo="US", market="", node="", source=SOURCE,
                                 source_url=x["url"], retrieved_at=x["at"], vintage=x["vintage"], x_plants=x["row"][4])
                            for x in rows])
        plants = out[out["variable"] == "net_generation_mwh"].assign(variable="plants", value=lambda d: d["x_plants"].astype(float), unit="count")
        out = pd.concat([out, plants], ignore_index=True).drop(columns=["x_plants"])
        header = [
            "Energy Research Warehouse (ERW): EIA's annual net generation by balancing authority, summed from Form EIA-923's plant-level annual files (session 323)",
            "Shape: series (docs/datastandard.md v0), P1Y; entity eia923:<balancing authority code> (eia923:none: plants with no code); variables "
            "net_generation_mwh (Page 1 Generation and Fuel Data), storage_net_generation_mwh (Page 1 Energy Storage), plants (count); ts_utc the year's 1 January",
            f"The Electric Power Annual has no table by balancing authority (its index, {EPA}, read on 19 October 2026: net generation by source, "
            "sector and state only), so the sums are of EIA-923's plant rows by their Balancing Authority Code. Values are EIA's, summed, not rounded beyond 0.001 MWh",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia923_annual_ba.py from the files saved in {os.path.relpath(args.from_raw, ip.ROOT).replace(os.sep, '/')}",
            f"Run log: warehouse/output/logs/eia923_annual_ba_{run_id}.log",
            "Files: " + "; ".join(used),
            f"Source: {SOURCE} U.S. Energy Information Administration, Form EIA-923 Power Plant Operations Report, annual files, {PAGE}",
            "License: public. EIA's data are in the public domain (https://www.eia.gov/about/copyrights_reuse.php). Credit: U.S. Energy Information Administration.",
            "Method: docs/methods/eia_annual_crosscheck.md",
        ]
        path = os.path.join(ip.OUT_DIR, NAME + ".csv")
        if os.path.exists(path):
            os.remove(path)  # rebuilt whole from the files each run
        ip.write_csv(out, NAME, header, log, cols=ip.SERIES_COLS)
        ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                report="Form EIA-923 Power Plant Operations Report, annual files (net generation by plant, summed by balancing authority)",
                                report_url=PAGE, document_list=PAGE, license="public", tables=[NAME])])
        msg = f"{len(out)} rows, {out['entity'].nunique()} balancing authorities, years {sorted(out['ts_utc'].str[:4].unique())}"
        results.append(dict(table=NAME, market="all", status="ok", detail=msg))
        print(f"eia923_annual_ba: {msg}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"eia923_annual_ba {NAME} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status("eia923_annual_ba", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
