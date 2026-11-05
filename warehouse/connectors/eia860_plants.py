#!/usr/bin/env python3
"""EIA-860's plants: each power plant's place, operator, balancing authority, NERC region, grid voltage and the
transmission or distribution system owner it connects to (session 873, chain 047: a plant's wires utility, which EIA-860M's
generator tables do not give).

Energy Research Warehouse (ERW) connector. One entities table, warehouse/output/eia860_plants_annual.csv, from the U.S.
Energy Information Administration's Form EIA-860 annual zip (the newest final year the page links outside /archive/,
2___Plant_Y<year>.xlsx):

    page   https://www.eia.gov/electricity/data/eia860/
    file   https://www.eia.gov/electricity/data/eia860/xls/eia860<year>.zip

    entity_id   eia860_plant:<plant code>; entity_type plant; name the plant's name; geo US-<state>; lat, lon as EIA gives
                them; operator the utility's name; status_date the data year's 1 January; vintage the data year
    x_*         every other column of EIA's sheet, its heading as a name (x_utility_id, x_county, x_nerc_region,
                x_balancing_authority_code, x_grid_voltage_kv, x_transmission_or_distribution_system_owner,
                x_transmission_or_distribution_system_owner_id and the rest), as EIA gives it

A plant code given twice stops the run. EIA's early release (ER) zip is not read: only a final year. EIA's robots file
disallows /archive/ (session 666), where EIA moves earlier years; they are not asked for.

    python warehouse/connectors/eia860_plants.py [--offline]

Ceiling: two requests (the page and the zip; a zip saved in warehouse/raw/eia860_plants/ is reused). License: public (EIA,
record 1 of license_reads.csv; cite "U.S. Energy Information Administration, Form EIA-860").
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

NAME = "eia860_plants_annual"
CONNECTOR = "eia860_plants"
SOURCE = "eia:eia860:plant"
PAGE = "https://www.eia.gov/electricity/data/eia860/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
               "source", "source_url", "retrieved_at", "vintage"]
MAIN = {"plant code": "plant", "plant name": "name", "state": "state", "latitude": "lat", "longitude": "lon",
        "utility name": "operator"}


def text(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return re.sub(r"\s+", " ", str(v)).strip()


def slug(v):
    return re.sub(r"[^a-z0-9]+", "_", v.lower()).strip("_")


def newest(page_html):
    """The newest final year's zip the page links outside /archive/: (url, year)."""
    found = [(int(y), h) for h, y in re.findall(r'href="\s*((?<!archive/)xls/eia860(\d{4})\.zip)"', page_html) if "archive" not in h]
    if not found:
        raise RuntimeError("the EIA-860 page links no final year's zip outside /archive/")
    year, href = max(found)
    return PAGE + href, year


def plants(frame, year, url, retrieved):
    heads = [r for r in range(min(5, len(frame))) if any(text(v) == "Plant Code" for v in frame.iloc[r])]
    if not heads:
        raise RuntimeError("no heading row names 'Plant Code'")
    hr = heads[0]
    names = [text(v) for v in frame.iloc[hr]]
    cols = {}
    for c, n in enumerate(names):
        if not n:
            continue
        cols[MAIN.get(n.lower(), "x_" + slug(n))] = c
    for k in ("plant", "name", "state", "lat", "lon"):
        if k not in cols:
            raise RuntimeError(f"the sheet lacks '{k}'")
    out = []
    for _, r in frame.iloc[hr + 1:].iterrows():
        x = {k: text(r[c]) for k, c in cols.items()}
        if not x["plant"]:
            continue
        state = x.pop("state")
        row = dict(entity_id=f"eia860_plant:{x.pop('plant')}", entity_type="plant", name=x.pop("name"),
                   geo=f"US-{state}" if state else "US", lat=x.pop("lat"), lon=x.pop("lon"), capacity_mw="", status="",
                   status_date=f"{year}-01-01", operator=x.pop("operator", ""), source=SOURCE, source_url=url,
                   retrieved_at=retrieved, vintage=str(year), x_state=state, **x)
        out.append(row)
    t = pd.DataFrame(out)
    if t["entity_id"].duplicated().any():
        raise RuntimeError(f"a plant code given twice: {t.loc[t['entity_id'].duplicated(), 'entity_id'].head(3).tolist()}")
    return t.sort_values("entity_id").reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA-860's plants: place, operator, BA, NERC region, grid voltage, wires owner")
    ap.add_argument("--offline", action="store_true", help="the saved page and zip only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, fresh=not args.offline, headers=UA)
        url, year = newest(page.decode("utf-8", errors="replace"))
        content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=600)
        if content[:2] != b"PK":
            raise RuntimeError(f"{url} is not a zip")
        zf = zipfile.ZipFile(io.BytesIO(content))
        name = next((n for n in zf.namelist() if n.startswith("2___Plant")), None)
        if not name:
            raise RuntimeError(f"the zip holds no 2___Plant file: {zf.namelist()}")
        t = plants(pd.read_excel(io.BytesIO(zf.read(name)), header=None), year, url, rec.get("retrieved_at") or "")
        x_cols = [c for c in t.columns if c not in ENTITY_COLS]
        cols = ENTITY_COLS + ["x_state"] + [c for c in x_cols if c != "x_state"]
        t = t[cols]
        header = [
            f"Energy Research Warehouse (ERW): EIA-860, the power plants of {year}: place, operator, balancing authority, NERC region, grid voltage and the transmission or distribution system owner (session 873)",
            "Shape: entities (docs/datastandard.md v0). entity_id eia860_plant:<plant code>; entity_type plant; name the plant's name; geo US-<state>; lat, lon as EIA gives them; operator the utility's name; status_date the data year's 1 January; vintage the data year; "
            "x_* every other column of EIA's sheet, its heading as a name.",
            f"Data year {year} ({name}); {len(t):,} plants, {t['x_state'].nunique()} states. EIA's early release is not read.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia860_plants.py (the zip retrieved {rec.get('retrieved_at', '')})",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Form EIA-860 Annual Electric Generator Report, plant file, {PAGE}",
            f"  access: {url}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Form EIA-860").',
        ]
        ip.write_snapshot(t, NAME, header, log, cols=cols)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Form EIA-860 Annual Electric Generator Report, plant file", report_url=PAGE,
                                    document_list=PAGE, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{year}: {len(t):,} plants"))
        print(f"{NAME}: {year}, {len(t):,} plants, {len(x_cols)} of EIA's columns")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
