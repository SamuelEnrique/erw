#!/usr/bin/env python3
"""Texas Railroad Commission (RRC) production by lease, every county (session 57): the statewide lease-month table for
the severance refund finder (warehouse/derived/severance_screen.py).

Energy Research Warehouse (ERW) connector. No download: it reads the RRC Production Data Query dump already on disk
(warehouse/raw/rrc_pdq/<run>/PDQ_DSV.zip, fetched by rrc_production.py in session 49; the RRC's "Production Data Query
Dump" user manual), table OG_COUNTY_LEASE_CYCLE: each lease's production in each county and month, as its operator
reported it.

    python warehouse/connectors/rrc_statewide.py            # split (once per dump), then build
    python warehouse/connectors/rrc_statewide.py --resplit  # split again

Two steps, never the whole table in memory:
1. split: one streamed pass over the zip's table (12.75 GB, about 77 million lines), keeping the lines of the latest 48
   production months the dump holds and writing them to one gzip file per county beside the dump
   (counties48/<COUNTY>.dsv.gz, not in git). 48 months: the latest 24 are the table; the 24 before them let the finder
   see whether a lease resuming in the window had been inactive for two years.
2. build: one county at a time, the latest 24 months, written to

    warehouse/output/rrc_lease_production_statewide/<COUNTY>.csv.gz   one row per lease, county and production month
    warehouse/output/rrc_lease_production_statewide/_index.csv         each county's rows and leases

   partitioned by county (a page reads one county's file to open a lease), a wide table, not the series shape: county, district, lease, operator, field, the four volumes (oil, casinghead
   gas, gas, condensate), whether a report was filed, the wells the RRC lists on the lease and those not shut in. At
   5.4 million lease-county-months (the build of 2026-10-01: 5,443,427), the series shape (one row per volume, with provenance on every row) would be
   several GB; the provenance is in the header instead. The finder reads the 48 months from the county files.

License: internal (session 49): the RRC offers its data sets "free of charge"; no page read grants reuse or
redistribution. The table goes nowhere public: not git, not the public database, not public Redivis, no committed JSON.
"""

import argparse
import datetime as dt
import glob
import gzip
import io
import os
import sys
import time
import traceback
import zipfile

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

NAME = "rrc_lease_production_statewide"
TABLE = "OG_COUNTY_LEASE_CYCLE_DATA_TABLE.dsv"
SHARE = "https://mft.rrc.texas.gov/link/1f5ddb8d-329a-4459-b7f8-177b4f5ee60d"
PAGE = "https://www.rrc.texas.gov/resource-center/research/data-sets-available-for-download/"
SOURCE = "rrc:pdq_dump"
MONTHS_SPLIT, MONTHS_TABLE = 48, 24
VOLS = {"CNTY_LSE_OIL_PROD_VOL": "oil_bbl", "CNTY_LSE_CSGD_PROD_VOL": "casinghead_gas_mcf", "CNTY_LSE_GAS_PROD_VOL": "gas_mcf",
        "CNTY_LSE_COND_PROD_VOL": "condensate_bbl"}


def dump_path():
    p = sorted(glob.glob(os.path.join(ip.RAW_DIR, "rrc_pdq", "*", "PDQ_DSV.zip")))
    if not p:
        raise RuntimeError("no saved dump under warehouse/raw/rrc_pdq/ (rrc_production.py --download)")
    return p[-1]


def read_dsv(z, name, **kw):
    return pd.read_csv(z.open(name), sep="}", dtype=str, encoding="latin-1", keep_default_na=False, **kw)


def months_of(z, n):
    rng = read_dsv(z, "GP_DATE_RANGE_CYCLE_DATA_TABLE.dsv").iloc[0]
    newest = rng["NEWEST_PROD_CYCLE_YEAR_MONTH"]
    ms = [p.strftime("%Y%m") for p in pd.period_range(end=pd.Period(f"{newest[:4]}-{newest[4:]}", "M"), periods=n, freq="M")]
    return ms, rng


def split_dir(path):
    return os.path.join(os.path.dirname(path), "counties48")


def split(path, log):
    """Stream the table once; route the latest 48 months' lines to one gzip per county. Returns {county: lines}."""
    z = zipfile.ZipFile(path)
    months, _ = months_of(z, MONTHS_SPLIT)
    want = {m.encode() for m in months}
    out = split_dir(path)
    tmp = out + ".partial"
    os.makedirs(tmp, exist_ok=True)
    files, counts, n, t0 = {}, {}, 0, time.time()
    with z.open(TABLE) as f:
        head = f.readline()
        for line in io.BufferedReader(f, 1 << 22):
            n += 1
            parts = line.split(b"}", 9)
            if len(parts) < 10 or parts[8] not in want:
                continue
            county = line.rstrip(b"\r\n").rsplit(b"}", 1)[-1].decode("latin-1").strip() or "UNKNOWN"
            fh = files.get(county)
            if fh is None:
                fh = files[county] = gzip.open(os.path.join(tmp, f"{county.replace(' ', '_').replace('/', '_')}.dsv.gz"), "wb", compresslevel=3)
                fh.write(head)
            fh.write(line)
            counts[county] = counts.get(county, 0) + 1
            if n % 10_000_000 == 0:
                log(f"  {n:,} lines read, {sum(counts.values()):,} kept, {time.time() - t0:.0f} s")
    for fh in files.values():
        fh.close()
    if os.path.exists(out):
        for x in glob.glob(os.path.join(out, "*")):
            os.remove(x)
        os.rmdir(out)
    os.rename(tmp, out)
    with open(os.path.join(out, "_split.csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("county,lines\n")
        for c in sorted(counts):
            f.write(f"{c},{counts[c]}\n")
    log(f"split: {n:,} lines of {TABLE} read in {time.time() - t0:.0f} s; {sum(counts.values()):,} lines of {months[0]} to {months[-1]} "
        f"kept in {len(counts)} county files under {os.path.relpath(out, ip.ROOT)}")
    return counts, n


def county_frame(fp, months=None):
    """One county's lines as a frame (strings), optionally only some months."""
    df = pd.read_csv(fp, sep="}", dtype=str, encoding="latin-1", keep_default_na=False, compression="gzip")
    return df[df["CYCLE_YEAR_MONTH"].isin(months)] if months is not None else df


def wells_table(z):
    """(code, district, lease) -> (wells listed, wells not shut in) from OG_WELL_COMPLETION (any status). A well is
    counted shut in when the RRC gives a well shut-in date (WELL_SHUTIN_DT not 000000 or empty) at the extract."""
    wc = read_dsv(z, "OG_WELL_COMPLETION_DATA_TABLE.dsv", usecols=["OIL_GAS_CODE", "DISTRICT_NO", "LEASE_NO", "WELL_NO", "WELL_SHUTIN_DT"])
    wc = wc.drop_duplicates(["OIL_GAS_CODE", "DISTRICT_NO", "LEASE_NO", "WELL_NO"])
    wc["open"] = wc["WELL_SHUTIN_DT"].str.strip().isin(["", "000000", "0"])
    g = wc.groupby(["OIL_GAS_CODE", "DISTRICT_NO", "LEASE_NO"])
    return pd.DataFrame({"wells": g.size(), "wells_open": g["open"].sum()})


def build(path, log):
    z = zipfile.ZipFile(path)
    months, rng = months_of(z, MONTHS_TABLE)
    man = pd.read_csv(os.path.join(os.path.dirname(path), "manifest.csv"), dtype=str).iloc[-1]
    wells = wells_table(z)
    dists = dict(zip(read_dsv(z, "GP_DISTRICT_DATA_TABLE.dsv")["DISTRICT_NO"], read_dsv(z, "GP_DISTRICT_DATA_TABLE.dsv")["DISTRICT_NAME"]))
    files = sorted(glob.glob(os.path.join(split_dir(path), "*.dsv.gz")))
    out = os.path.join(ip.OUT_DIR, NAME)
    tmp = out + ".partial"
    os.makedirs(tmp, exist_ok=True)
    cols = ["county", "district", "oil_gas_code", "lease_no", "lease_id", "month", "filed", "oil_bbl", "casinghead_gas_mcf", "gas_mcf",
            "condensate_bbl", "operator_no", "operator_name", "field_no", "field_name", "lease_name", "gas_well_no", "wells", "wells_open"]
    rows, leases, t0 = 0, set(), time.time()
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rel = os.path.relpath(path, ip.ROOT).replace("\\", "/")
    header = [
        "Energy Research Warehouse (ERW): Texas Railroad Commission monthly production by lease, county and month, every county, "
        f"{months[0][:4]}-{months[0][4:]} to {months[-1][:4]}-{months[-1][4:]} (session 57, internal)",
        "Shape: a wide working table, not docs/datastandard.md's series shape (5.4 million lease-county-months (the build of 2026-10-01: 5,443,427); the series shape "
        "would hold one row per volume with provenance on each). One row per lease (oil_gas_code-district-lease_no, the RRC's lease id; "
        "a gas lease is one gas well), county and production month, as OG_COUNTY_LEASE_CYCLE reports it.",
        "Columns: filed is PROD_REPORT_FILED_FLAG (Y: a report was filed; the volumes of an unfiled month are the RRC's zeros); "
        "oil_bbl and casinghead_gas_mcf (oil leases), gas_mcf and condensate_bbl (gas leases), BBL and MCF as reported; wells: the wells "
        "OG_WELL_COMPLETION lists on the lease (any status, any county; 0 where none), wells_open: those with no well shut-in date at the extract.",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/rrc_statewide.py from the dump downloaded {man['retrieved_at']}; no new download",
        f"Raw files: {rel} (not in git; {int(man['bytes']):,} bytes, sha256 {man['sha256']}) and the county files of the latest 48 months beside it (counties48/)",
        f"Source: {SOURCE} RRC Production Data Query dump (PDQ_DSV.zip), {SHARE}",
        f"  the data sets page: {PAGE}; the dump's extracts: {rng['OIL_EXTRACT_DATE']} (oil), {rng['GAS_EXTRACT_DATE']} (gas)",
        "Recent months may be incomplete: operators file late and the RRC revises.",
        "License: internal. The RRC offers its data sets \"free of charge\"; no page read grants reuse or redistribution. Not in git, the "
        "public database, public Redivis or any committed JSON.",
    ]
    index = []
    for fp in files:
        df = county_frame(fp, months)
        if not len(df):
            continue
        with gzip.open(os.path.join(tmp, os.path.basename(fp).replace(".dsv.gz", ".csv.gz")), "wt", encoding="utf-8", newline="\n", compresslevel=5) as f:
            for h in header:
                f.write(f"# {h}\n")
            f.write(",".join(cols) + "\n")
            x = pd.DataFrame({
                "county": df["COUNTY_NAME"].str.strip(), "district": df["DISTRICT_NO"].map(lambda d: dists.get(d, d)), "oil_gas_code": df["OIL_GAS_CODE"],
                "lease_no": df["LEASE_NO"], "lease_id": df["OIL_GAS_CODE"] + "-" + df["DISTRICT_NO"] + "-" + df["LEASE_NO"],
                "month": df["CYCLE_YEAR_MONTH"].str[:4] + "-" + df["CYCLE_YEAR_MONTH"].str[4:], "filed": df["PROD_REPORT_FILED_FLAG"],
                **{v: pd.to_numeric(df[c], errors="coerce").fillna(0).astype("int64") for c, v in VOLS.items()},
                "operator_no": df["OPERATOR_NO"], "operator_name": df["OPERATOR_NAME"].str.strip(), "field_no": df["FIELD_NO"],
                "field_name": df["FIELD_NAME"].str.strip(), "lease_name": df["LEASE_NAME"].str.strip(), "gas_well_no": df["GAS_WELL_NO"].str.strip()})
            k = list(zip(df["OIL_GAS_CODE"], df["DISTRICT_NO"], df["LEASE_NO"]))
            w = wells.reindex(k)
            x["wells"] = w["wells"].fillna(0).astype(int).values
            x["wells_open"] = w["wells_open"].fillna(0).astype(int).values
            x[cols].to_csv(f, header=False, index=False)
        rows += len(x)
        leases.update(x["lease_id"].unique())
        index.append((x["county"].iloc[0], os.path.basename(fp).replace(".dsv.gz", ".csv.gz"), len(x), x["lease_id"].nunique()))
    pd.DataFrame(index, columns=["county", "file", "rows", "leases"]).to_csv(os.path.join(tmp, "_index.csv"), index=False)
    if os.path.exists(out):
        for f_old in glob.glob(os.path.join(out, "*")):
            os.remove(f_old)
        os.rmdir(out)
    os.rename(tmp, out)
    old = os.path.join(ip.OUT_DIR, NAME + ".csv.gz")
    if os.path.exists(old):
        os.remove(old)  # an earlier single-file build of this session
    log(f"build: {rows:,} lease-county-months, {len(leases):,} leases, {len(files)} counties, {months[0]} to {months[-1]}, "
        f"in {time.time() - t0:.0f} s: {os.path.relpath(out, ip.ROOT)}")
    return rows, len(leases), len(files), months


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW RRC lease production, every county (session 57)")
    ap.add_argument("--resplit", action="store_true")
    args = ap.parse_args(argv)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"rrc_statewide_{run_id}.log"))
    results = []
    try:
        path = dump_path()
        log(f"ERW rrc_statewide {run_id}: {os.path.relpath(path, ip.ROOT)}; no download")
        if args.resplit or not os.path.exists(os.path.join(split_dir(path), "_split.csv")):
            split(path, log)
        else:
            log(f"split: kept from an earlier run ({os.path.relpath(split_dir(path), ip.ROOT)})")
        rows, n_leases, n_counties, months = build(path, log)
        results.append(dict(table=NAME, market="statewide", status="ok", detail=f"{rows} lease-county-months, {n_leases} leases, {n_counties} counties, {months[0]} to {months[-1]}"))
        print(f"rrc_statewide: {rows:,} lease-county-months, {n_leases:,} leases in {n_counties} counties")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"rrc_statewide FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="statewide", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status("rrc_statewide", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
