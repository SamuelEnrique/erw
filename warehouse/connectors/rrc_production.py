#!/usr/bin/env python3
"""Texas Railroad Commission (RRC) monthly oil and gas production by lease, one county (session 49, approved pull e).

Energy Research Warehouse (ERW) connector. Writes one series table,

    warehouse/output/rrc_lease_production_monthly.csv    oil_bbl and casinghead_gas_mcf (oil leases), gas_mcf and
                                                        condensate_bbl (gas leases), per lease and production month

from the RRC's Production Data Query dump (PDQ_DSV.zip, '}'-delimited tables; the RRC's "Production Data Query Dump"
user manual), table OG_COUNTY_LEASE_CYCLE: each lease's production in each county and month, as reported by its
operator. The approved pilot: one major Permian county, the latest 24 production months the dump holds; ceiling
500,000 rows. Martin County, the county of RRC districts 08, 7C and 8A (the Permian Basin) with the most oil produced
over those months in the dump's own county table (OG_COUNTY_CYCLE).

    python warehouse/connectors/rrc_production.py --download            # fetch the dump (3.85 GB), then build
    python warehouse/connectors/rrc_production.py [--county MARTIN] [--months 24]   # the newest saved dump

The dump is fetched from the RRC's public file share (GoAnywhere MFT) with a plain form post, streamed to
warehouse/raw/rrc_pdq/<run>/PDQ_DSV.zip with a manifest (bytes, SHA-256). The table is read line by line from the
zip; only the county's lines are kept, and those are saved beside the dump as <county>_lines.dsv.gz.

Rows: a report the operator did not file (PROD_REPORT_FILED_FLAG not Y) is not written; a filed zero is (the RRC's
value). Volumes: the RRC's whole barrels (BBL) and thousand cubic feet (MCF); the manual calls them "estimated"
values, as reported by the operator. License: internal. The RRC states its data sets are "available ... free of
charge" and its site policies disclaim liability, but no page read grants reuse or redistribution, so the table is
built internal (Decision 23) and goes only to the internal Redivis dataset.
"""

import argparse
import datetime as dt
import glob
import gzip
import hashlib
import io
import os
import re
import sys
import time
import traceback
import zipfile

import pandas as pd
import requests  # imported before iso_prices: its capture hook would hold the whole dump in memory

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

NAME = "rrc_lease_production_monthly"
SHARE = "https://mft.rrc.texas.gov/link/1f5ddb8d-329a-4459-b7f8-177b4f5ee60d"
PAGE = "https://www.rrc.texas.gov/resource-center/research/data-sets-available-for-download/"
SOURCE = "rrc:pdq_dump"
TABLE = "OG_COUNTY_LEASE_CYCLE_DATA_TABLE.dsv"
CEILING = 500_000
PERMIAN = {"08", "7C", "8A"}  # RRC district names of the Permian Basin
# OIL_GAS_CODE O (oil lease): oil and casinghead gas; G (gas lease, one gas well): gas and condensate
PRODUCTS = {"O": [("CNTY_LSE_OIL_PROD_VOL", "oil_bbl", "bbl"), ("CNTY_LSE_CSGD_PROD_VOL", "casinghead_gas_mcf", "Mcf")],
            "G": [("CNTY_LSE_GAS_PROD_VOL", "gas_mcf", "Mcf"), ("CNTY_LSE_COND_PROD_VOL", "condensate_bbl", "bbl")]}


def download(log):
    """Stream the dump from the RRC's file share; returns the zip's path."""
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = os.path.join(ip.RAW_DIR, "rrc_pdq", run_id)
    os.makedirs(out, exist_ok=True)
    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0 (ERW research; github.com/SamuelEnrique/erw)"
    h = s.get(SHARE, timeout=120).text
    i = h.find('<form id="fileList"')
    form = h[i:h.find("</form>", i)]
    if i < 0 or "PDQ_DSV.zip" not in form:
        raise RuntimeError(f"{SHARE}: the file list does not name PDQ_DSV.zip")
    data = {m.group(1): m.group(2) for m in re.finditer(r'<input[^>]*type="hidden"[^>]*name="([^"]+)"[^>]*value="([^"]*)"', form)}
    data.update({"fileList": "fileList", "fileTable:0:j_id_2f": "fileTable:0:j_id_2f"})
    vs = re.search(r'name="javax.faces.ViewState"[^>]*value="([^"]+)"', h)
    if vs:
        data["javax.faces.ViewState"] = vs.group(1)
    url = "https://mft.rrc.texas.gov" + re.search(r'action="([^"]+)"', form).group(1)
    path, sha, n, t0 = os.path.join(out, "PDQ_DSV.zip"), hashlib.sha256(), 0, time.time()
    with s.post(url, data=data, stream=True, timeout=600) as r:
        if r.status_code != 200 or "zip" not in (r.headers.get("content-type") or "") + (r.headers.get("content-disposition") or ""):
            raise RuntimeError(f"RRC share: HTTP {r.status_code}, {r.headers.get('content-type')}: not the zip")
        with open(path, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
                sha.update(chunk)
                n += len(chunk)
    with open(os.path.join(out, "manifest.csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("retrieved_at,status,bytes,sha256,last_modified,file,url\n")
        f.write(f"{ip.utc_iso(pd.Timestamp.now(tz='UTC'))},200,{n},{sha.hexdigest()},,PDQ_DSV.zip,{SHARE}\n")
    log(f"downloaded {SHARE}: {n:,} bytes in {time.time() - t0:.0f} s to {os.path.relpath(path, ip.ROOT)}")
    return path


def read_dsv(z, name, **kw):
    return pd.read_csv(z.open(name), sep="}", dtype=str, encoding="latin-1", keep_default_na=False, **kw)


def county_lines(z, county, log):
    """The header line and every line of OG_COUNTY_LEASE_CYCLE whose last field (COUNTY_NAME) is the county."""
    tail, kept, n, t0 = ("}" + county).encode("latin-1"), [], 0, time.time()
    with z.open(TABLE) as f:
        head = f.readline()
        for line in io.BufferedReader(f, 1 << 22):
            n += 1
            if line.rstrip(b"\r\n").endswith(tail):
                kept.append(line)
    log(f"  {TABLE}: {n:,} lines read in {time.time() - t0:.0f} s, {len(kept):,} in {county}")
    return head, kept, n


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW RRC lease production, one county (session 49)")
    ap.add_argument("--download", action="store_true", help="fetch the dump first (3.85 GB)")
    ap.add_argument("--county", default="MARTIN")
    ap.add_argument("--months", type=int, default=24)
    ap.add_argument("--out-dir")
    args = ap.parse_args(argv)
    if args.out_dir:
        ip.set_out_dir(args.out_dir)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"rrc_production_{run_id}.log"))
    results = []
    try:
        path = download(log) if args.download else (sorted(glob.glob(os.path.join(ip.RAW_DIR, "rrc_pdq", "*", "PDQ_DSV.zip"))) or [None])[-1]
        if not path:
            raise RuntimeError("no saved dump under warehouse/raw/rrc_pdq/; run with --download")
        man = pd.read_csv(os.path.join(os.path.dirname(path), "manifest.csv"), dtype=str).iloc[-1]
        retrieved, rel = man["retrieved_at"], os.path.relpath(path, ip.ROOT).replace("\\", "/")
        log(f"ERW rrc_production {run_id}: {rel} (downloaded {retrieved}, {int(man['bytes']):,} bytes, sha256 {man['sha256']})")
        z = zipfile.ZipFile(path)
        rng = read_dsv(z, "GP_DATE_RANGE_CYCLE_DATA_TABLE.dsv").iloc[0]
        newest = rng["NEWEST_PROD_CYCLE_YEAR_MONTH"]
        months = [p.strftime("%Y%m") for p in pd.period_range(end=pd.Period(f"{newest[:4]}-{newest[4:]}", "M"), periods=args.months, freq="M")]
        log(f"  the dump: production months {rng['OLDEST_PROD_CYCLE_YEAR_MONTH']} to {newest}, extracts of {rng['OIL_EXTRACT_DATE']} (oil) "
            f"and {rng['GAS_EXTRACT_DATE']} (gas); this run: {months[0]} to {months[-1]}")
        # the pilot county, by the dump's own county table: the Permian county with the most oil over the months
        cc = read_dsv(z, "OG_COUNTY_CYCLE_DATA_TABLE.dsv")
        cc = cc[cc["CYCLE_YEAR_MONTH"].isin(months)]
        cc["oil"] = pd.to_numeric(cc["CNTY_OIL_PROD_VOL"], errors="coerce").fillna(0)
        perm = cc[cc["DISTRICT_NAME"].isin(PERMIAN)].groupby("COUNTY_NAME")["oil"].sum().sort_values(ascending=False)
        log("  Permian counties by oil produced over the months (bbl): " + "; ".join(f"{c} {v:,.0f}" for c, v in perm.head(5).items()))
        county = args.county.upper()
        if county not in perm.index:
            raise RuntimeError(f"{county} is not a county of districts {sorted(PERMIAN)} in the dump")
        head, kept, nlines = county_lines(z, county, log)
        with gzip.open(os.path.join(os.path.dirname(path), f"{county.lower()}_lines.dsv.gz"), "wb") as f:
            f.write(head)
            f.writelines(kept)
        df = pd.read_csv(io.BytesIO(head + b"".join(kept)), sep="}", dtype=str, encoding="latin-1", keep_default_na=False)
        df = df[df["CYCLE_YEAR_MONTH"].isin(months)]
        unfiled = int((df["PROD_REPORT_FILED_FLAG"] != "Y").sum())
        df = df[df["PROD_REPORT_FILED_FLAG"] == "Y"]
        frames = []
        for code, prods in PRODUCTS.items():
            part = df[df["OIL_GAS_CODE"] == code]
            for col, var, unit in prods:
                v = pd.to_numeric(part[col], errors="coerce")
                frames.append(part.assign(variable=var, unit=unit, value=v)[v.notna()])
        x = pd.concat(frames, ignore_index=True)
        if len(x) > CEILING:
            raise RuntimeError(f"{len(x):,} rows, over the {CEILING:,} ceiling: not written")
        # the wells the RRC lists on each lease (OG_WELL_COMPLETION, any status, any county): the lease tool treats a
        # lease as one well, so a lease of several wells is marked there
        wc = read_dsv(z, "OG_WELL_COMPLETION_DATA_TABLE.dsv", usecols=["OIL_GAS_CODE", "DISTRICT_NO", "LEASE_NO", "WELL_NO"])
        wells = wc.drop_duplicates().groupby(["OIL_GAS_CODE", "DISTRICT_NO", "LEASE_NO"]).size()
        x["x_wells"] = [wells.get((c, d, n), 0) for c, d, n in zip(x["OIL_GAS_CODE"], x["DISTRICT_NO"], x["LEASE_NO"])]
        dists = dict(zip(read_dsv(z, "GP_DISTRICT_DATA_TABLE.dsv")["DISTRICT_NO"], read_dsv(z, "GP_DISTRICT_DATA_TABLE.dsv")["DISTRICT_NAME"]))
        s = pd.DataFrame({
            "entity": "rrc:" + x["OIL_GAS_CODE"] + "-" + x["DISTRICT_NO"] + "-" + x["LEASE_NO"], "variable": x["variable"],
            "ts_utc": x["CYCLE_YEAR_MONTH"].str[:4] + "-" + x["CYCLE_YEAR_MONTH"].str[4:] + "-01T00:00:00Z", "value": x["value"],
            "unit": x["unit"], "freq": "P1M", "geo": "US-TX", "market": "", "node": "", "source": SOURCE,
            "source_url": SHARE, "retrieved_at": retrieved, "vintage": "",
            "x_county": x["COUNTY_NAME"], "x_district": x["DISTRICT_NO"].map(lambda d: dists.get(d, d)),
            "x_oil_gas_code": x["OIL_GAS_CODE"], "x_lease_no": x["LEASE_NO"], "x_lease_name": x["LEASE_NAME"].str.strip(),
            "x_operator_no": x["OPERATOR_NO"], "x_operator_name": x["OPERATOR_NAME"].str.strip(),
            "x_field_no": x["FIELD_NO"], "x_field_name": x["FIELD_NAME"].str.strip(), "x_gas_well_no": x["GAS_WELL_NO"].str.strip(),
            "x_wells": x["x_wells"]})
        s["vintage"] = pd.to_datetime(rng["OIL_EXTRACT_DATE"], format="%d-%b-%y").strftime("%Y-%m-%dT00:00:00Z")
        cols = list(s.columns)
        header = [
            "Energy Research Warehouse (ERW): Texas Railroad Commission monthly oil and gas production by lease, "
            f"{county.title()} County, {months[0][:4]}-{months[0][4:]} to {months[-1][:4]}-{months[-1][4:]} (session 49, internal)",
            "Shape: series (docs/datastandard.md v0). entity rrc:<oil or gas code>-<district no>-<lease no> (the RRC's lease id; a "
            "gas lease is one gas well). Oil leases (O): oil_bbl and casinghead_gas_mcf; gas leases (G): gas_mcf and condensate_bbl. "
            "The lease's production in this county (OG_COUNTY_LEASE_CYCLE). ts_utc is the production month's first day. x_wells: the "
            "wells the RRC lists on the lease in OG_WELL_COMPLETION (any status; 0 where it lists none).",
            f"Pilot county: {county.title()}, the county of the Permian districts (08, 7C, 8A) with the most oil over these months in "
            "the dump's OG_COUNTY_CYCLE (" + "; ".join(f"{c.title()} {v:,.0f} bbl" for c, v in perm.head(3).items()) + ").",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/rrc_production.py; dump downloaded {retrieved}",
            f"Run log: warehouse/output/logs/rrc_production_{run_id}.log",
            f"Raw files: {rel} (not in git; manifest.csv: {int(man['bytes']):,} bytes, sha256 {man['sha256']}) and the county's lines "
            f"beside it ({county.lower()}_lines.dsv.gz)",
            f"Source: {SOURCE} RRC Production Data Query dump (PDQ_DSV.zip), {SHARE}",
            f"  the data sets page: {PAGE}; vintage: the dump's oil extract date, {rng['OIL_EXTRACT_DATE']}",
            f"Not written: {unfiled:,} lease-months with no report filed (PROD_REPORT_FILED_FLAG not Y). Recent months may "
            "be incomplete: operators file late and the RRC revises.",
            "Values: the RRC's BBL and MCF as reported by operators (the manual: \"estimated\" values).",
            f"Rows: {len(s):,} of the {CEILING:,} ceiling.",
            "License: internal. The RRC offers its data sets \"free of charge\"; no page read grants reuse or redistribution.",
        ]
        out = os.path.join(ip.OUT_DIR, NAME + ".csv")
        if os.path.exists(out):
            os.remove(out)  # a snapshot of the dump's latest 24 months: replaced whole, as the dump revises
        ip.write_csv(s[cols], NAME, header, log, cols=cols, key=["entity", "variable", "ts_utc"])
        ip.update_sources([dict(source=SOURCE, publisher="Railroad Commission of Texas (RRC)",
                                report="Production Data Query dump (PDQ_DSV.zip)", report_url=PAGE, document_list=SHARE,
                                license="internal", tables=[NAME])])
        results.append(dict(table=NAME, market=county.lower(), status="ok",
                            detail=f"{len(s)} rows, {s['entity'].nunique()} leases, {months[0]} to {months[-1]}; {unfiled} unfiled lease-months"))
        print(f"rrc_production: {len(s):,} rows, {s['entity'].nunique():,} leases in {county}, {nlines:,} lines read")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"rrc_production FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market=args.county.lower(), status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status("rrc_production", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
