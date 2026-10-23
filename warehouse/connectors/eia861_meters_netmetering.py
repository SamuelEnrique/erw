#!/usr/bin/env python3
"""EIA-861: each utility's advanced meters and its net metering, by state, sector and year (session 869, chain 047),
beside the state tables the ERW holds (eia_meters_state_annual, eia_net_metering_state_annual).

Energy Research Warehouse (ERW) connector. Two series tables from the U.S. Energy Information Administration's Form
EIA-861 annual files (in f861<year>.zip; the zips eia861_sales.py saved):

    eia861_advanced_meters    Advanced_Meters_<year>.xlsx, its States and Territories sheets
    eia861_net_metering       Net_Metering_<year>.xlsx, its utility-level sheets only (EIA's TPO and state-level sheets
                              are aggregates and are not taken)

    entity    eia861_am:<utility>:<state>:<ba> or eia861_nm:<utility>:<state>:<ba> (ba empty where EIA gives none)
    variable  EIA's own headings joined: the group (a meter kind, or a technology and its measure) and the sector, for
              example number_ami_advanced_metering_infrastructure_residential, photovoltaic_capacity_mw_total,
              battery_pv_paired_energy_capacity_mwh_total; the names follow EIA's, which changed over the years (EIA's
              "customers" became "installations" in 2023)
    unit      MW where the heading names MW, MWh where it names MWh, else count
    ts_utc    the data year's 1 January; freq P1Y; geo US-<state>; node the utility's name

Every column is found by its stacked headings; a column whose last heading is not a sector (a type, a text field) is
read past and named in the header. EIA's aggregates 88888 and 99999 are left out; a "." cell has no row; nothing is
filled. Two rows under one key with different figures have no key and are both left out whole, named in the header
(chain 030's rule).

    python warehouse/connectors/eia861_meters_netmetering.py --years 2015 ... 2025 --offline

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
from eia861_programs import paths, text  # noqa: E402  the stacked-heading reader of session 868
from eia861_sales import NOT_UTILITIES, PAGE, UA, held_text, zip_url  # noqa: E402

CONNECTOR = "eia861"
SECTORS = ["residential", "commercial", "industrial", "transportation", "total"]
CHARS = {"data year": "year", "year": "year", "utility number": "utility", "utility name": "name", "state": "state", "ba code": "ba"}
TABLES = {
    "Advanced_Meters": dict(name="eia861_advanced_meters", prefix="eia861_am", source="eia:eia861:advanced_meters"),
    "Net_Metering": dict(name="eia861_net_metering", prefix="eia861_nm", source="eia:eia861:net_metering"),
}
X_COLS = ["x_utility_number", "x_state", "x_ba_code"]


def slug(v):
    return re.sub(r"[^a-z0-9]+", "_", v.lower()).strip("_")


def unit_of(heading):
    h = heading.lower()
    if re.search(r"\b(customers|installations|number|meters)\b", h):
        return "count"                         # "virtual customers, 1 MW and over" is a count, not MW
    if re.search(r"\bmwh\b", h):
        return "MWh"
    if re.search(r"\bmw\b", h):
        return "MW"
    return "count"


def utility_sheets(kind, names):
    if kind == "Advanced_Meters":
        return names
    return [n for n in names if "tpo" not in n.lower() and "state level" not in n.lower()]


def sheet_rows(frame, kind, year, url, retrieved, notes):
    meta = TABLES[kind]
    hr, cols = paths(frame)
    chars, figs = {}, {}
    for c, p in cols:
        p = [x for x in p if x and not x.startswith("utility level data")]
        if not p:
            continue
        if p[0] == "utility characteristics" or (len(p) == 1 and p[-1] in CHARS):
            if p[-1] in CHARS:
                chars[CHARS[p[-1]]] = c
            continue
        if p[-1] in SECTORS and len(p) >= 2:
            group = "_".join(slug(x) for x in p[:-1])
            figs[c] = (f"{group}_{p[-1]}", unit_of(" ".join(p[:-1])))
        else:
            notes.setdefault("read past", set()).add(" / ".join(p))
    for k in ("year", "utility", "name", "state"):
        if k not in chars:
            raise RuntimeError(f"{kind} {year}: the heading '{k}' is missing")
    if not figs:
        raise RuntimeError(f"{kind} {year}: no figure column found")
    d = frame.iloc[hr + 1:]
    d = d[pd.to_numeric(d[chars["year"]], errors="coerce").eq(year)]
    d = d[~pd.to_numeric(d[chars["utility"]], errors="coerce").isin(NOT_UTILITIES)]
    out = []
    for _, r in d.iterrows():
        util, state = text(r[chars["utility"]]), text(r[chars["state"]])
        ba = text(r[chars["ba"]]) if "ba" in chars else ""
        base = dict(entity=f"{meta['prefix']}:{util}:{state}:{ba}", ts_utc=f"{year}-01-01T00:00:00Z", freq="P1Y",
                    geo=f"US-{state}" if state else "US", market="", node=text(r[chars["name"]]), source=meta["source"],
                    source_url=url, retrieved_at=retrieved, vintage="", x_utility_number=util, x_state=state, x_ba_code=ba)
        for c, (var, unit) in figs.items():
            v = pd.to_numeric(r[c], errors="coerce")
            if pd.isna(v):
                continue
            out.append(dict(base, variable=var, value=float(v), unit=unit))
    t = pd.DataFrame(out)
    if len(t):
        t = t.drop_duplicates()
        twice = t.duplicated(["entity", "variable", "ts_utc"], keep=False)
        if twice.any():
            bad = set(t.loc[twice, "entity"])
            notes.setdefault("no key", set()).update(f"{e} {year}" for e in bad)
            t = t[~t["entity"].isin(bad)]
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA-861 utilities' advanced meters and net metering")
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
    log = ip.Log(os.path.join(ip.LOG_DIR, f"eia861_meters_netmetering_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, headers=UA)
        html = page.decode("utf-8", errors="replace")
        frames = {k: [] for k in TABLES}
        notes = {k: {} for k in TABLES}
        urls = []
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
                for sheet in utility_sheets(kind, xl.sheet_names):
                    t = sheet_rows(pd.read_excel(xl, sheet, header=None), kind, year, url, rec["retrieved_at"], notes[kind])
                    log(f"{year} {kind} {sheet}: {len(t):,} rows")
                    frames[kind].append(t)
            urls.append(url)
        for kind, meta in TABLES.items():
            s = pd.concat([f for f in frames[kind] if len(f)], ignore_index=True)
            if s.duplicated(["entity", "variable", "ts_utc"]).any():
                raise RuntimeError(f"{kind}: a row in two sheets")
            cols = ip.SERIES_COLS + X_COLS
            s = s[cols]
            years = sorted({int(t[:4]) for t in s["ts_utc"]})
            n = notes[kind]
            header = [
                f"Energy Research Warehouse (ERW): EIA-861 {kind.replace('_', ' ').lower()}, each utility by state and sector, a year (session 869)",
                f"Shape: series (docs/datastandard.md v0). entity {meta['prefix']}:<utility>:<state>:<balancing authority>; variable EIA's headings joined (group and sector); unit MW, MWh or count as the heading names it; "
                "ts_utc the data year's 1 January; freq P1Y; node the utility's name; x_* EIA's fields.",
                f"Years held: {held_text(years)}; {len(s):,} rows, {s['x_utility_number'].nunique():,} utilities, {s['variable'].nunique()} variables (EIA's names, which changed over the years). "
                "EIA's aggregates 88888 and 99999 left out; a '.' cell has no row; nothing is filled."
                + (" EIA's TPO and state-level sheets are not taken." if kind == "Net_Metering" else "")
                + (f" Read past (not a sector's figure): {'; '.join(sorted(n['read past']))}." if n.get("read past") else "")
                + (f" Left out, no key (two rows, two values): {', '.join(sorted(n['no key']))}." if n.get("no key") else ""),
                f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia861_meters_netmetering.py (the zips as saved by earlier runs)",
                f"Run log: warehouse/output/logs/eia861_meters_netmetering_{run_id}.log",
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
            print(f"{meta['name']}: {held_text(years)}, {len(s):,} rows, {s['x_utility_number'].nunique():,} utilities, {s['variable'].nunique()} variables")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"eia861_meters_netmetering FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table="eia861_advanced_meters", market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status("eia861_meters_netmetering", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
