#!/usr/bin/env python3
"""EIA-860M: every retired generator EIA lists, for installed capacity by fuel month by month (session 133, approved pull).

Energy Research Warehouse (ERW) connector. eia860.py keeps the generators retired in the vintage's year and the year
before (eia860m_retired_generators, which the storage pages read). Installed capacity in an earlier month needs the
units that have retired since: a coal plant that closed in 2021 was part of the fleet in 2019. This connector reads the
same workbook, the newest monthly EIA-860M (https://www.eia.gov/electricity/data/eia860m/), sheets Retired and
Retired_PR, and writes every row of them to its own table,

    warehouse/output/eia860m_retired_generators_all.csv     entities, one row per retired generator

with the columns of eia860m_retired_generators. That table, and the operating and planned tables, are not touched.

    python warehouse/connectors/eia860m_retired_all.py [--out-dir DIR]

EIA's codes are kept unchanged and labeled as eia860.py labels them (the same tables: a code it does not know stops
the run). A snapshot of one vintage: a new vintage replaces the rows. Ceiling: 400,000 rows (the approved pull); the
workbook's Retired sheets hold about 7,000 generators, and the run stops if they hold more than the ceiling.
License: public (EIA-PD).
"""

import argparse
import datetime as dt
import os
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eia860  # noqa: E402  (the workbook, its sheets, EIA's code tables)
import iso_prices as ip  # noqa: E402

NAME = "eia860m_retired_generators_all"
CONNECTOR = "eia860m_retired_all"
SOURCE = "eia:860m:retired"
SHEETS = ["Retired", "Retired_PR"]
CEILING = 400_000


def build(content, vintage, url, got, log):
    """Every row of the Retired sheets as the table's rows (eia860.build's retired rows, without its two-year filter)."""
    frames, titles = [], []
    for sh in SHEETS:
        d, title = eia860.read_sheet(content, sh)
        want = f"as of {pd.Timestamp(vintage + '-01'):%B %Y}"
        if want not in title:
            raise RuntimeError(f"sheet {sh}: title {title!r} does not say {want!r}")
        titles.append(title)
        frames.append(d)
        log(f"  {sh}: {len(d)} generators ({title})")
    d = pd.concat(frames, ignore_index=True).fillna("")
    d = d.apply(lambda c: c.str.strip())
    if len(d) > CEILING:
        raise RuntimeError(f"{len(d):,} rows exceed the approved ceiling of {CEILING:,}; nothing written")
    for col, table, what in [("Prime Mover Code", eia860.PRIME_MOVERS, "prime mover"), ("Energy Source Code", eia860.ENERGY_SOURCES, "energy source"),
                             ("Technology", eia860.TECH_GROUPS, "technology")]:
        bad = sorted(set(d[col]) - set(table) - {""})
        if bad:
            raise RuntimeError(f"unknown EIA {what} value(s) {bad}; add them to eia860.py from {eia860.INSTRUCTIONS}")
    eid = "eia860:" + d["Plant ID"] + ":" + d["Generator ID"]
    if eid.duplicated().any():
        raise RuntimeError(f"duplicate plant and generator ids {eid[eid.duplicated()].tolist()[:5]}")
    lat, lon = eia860.num(d["Latitude"]), eia860.num(d["Longitude"])
    # EIA's sheet gives a few long-retired units one coordinate without the other: half a location is none, so both are
    # left empty for them (the standard asks for the pair or neither); the count is in the log
    half = lat.isna() != lon.isna()
    if half.any():
        log(f"  {int(half.sum())} generators with a latitude or a longitude but not both: both left empty")
        lat, lon = lat.mask(half), lon.mask(half)
    retired = eia860.month_date(d["Retirement Year"], d["Retirement Month"])
    out = pd.DataFrame({
        "entity_id": eid, "entity_type": "generator", "name": d["Plant Name"], "geo": "US-" + d["Plant State"],
        "lat": lat.map(lambda v: "" if pd.isna(v) else repr(float(v))), "lon": lon.map(lambda v: "" if pd.isna(v) else repr(float(v))),
        "capacity_mw": d["Nameplate Capacity (MW)"], "status": "retired", "status_date": retired, "operator": d["Entity Name"],
        "source": SOURCE, "source_url": url, "retrieved_at": got, "vintage": vintage,
        "plant_id": d["Plant ID"], "generator_id": d["Generator ID"], "utility_id": d["Entity ID"], "state": d["Plant State"], "county": d["County"],
        "balancing_authority": d["Balancing Authority Code"], "sector": d["Sector"],
        "technology": d["Technology"], "technology_group": d["Technology"].map(eia860.TECH_GROUPS).fillna(""),
        "prime_mover": d["Prime Mover Code"], "prime_mover_label": d["Prime Mover Code"].map(eia860.PRIME_MOVERS).fillna(""),
        "energy_source": d["Energy Source Code"], "energy_source_label": d["Energy Source Code"].map(eia860.ENERGY_SOURCES).fillna(""),
        "nameplate_mw": d["Nameplate Capacity (MW)"], "net_summer_mw": d["Net Summer Capacity (MW)"], "net_winter_mw": d["Net Winter Capacity (MW)"],
        "eia_status": "RE", "eia_status_label": "Retired", "retirement_date": retired,
        "operating_year": d["Operating Year"], "operating_month": d["Operating Month"],
    })
    for c in ("capacity_mw", "nameplate_mw", "net_summer_mw", "net_winter_mw"):
        v = eia860.num(out[c])
        bad = out[c][v.isna() & (out[c] != "")]
        if len(bad):
            raise RuntimeError(f"non-numeric {c}: {bad.unique()[:5]}")
    return out.sort_values("entity_id"), titles


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA-860M: every retired generator EIA lists")
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
        vintage, url, content = eia860.newest(log)
        got = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        df, titles = build(content, vintage, url, got, log)
        years = pd.to_numeric(df["retirement_date"].str[:4], errors="coerce")
        header = [
            f"Energy Research Warehouse (ERW): EIA-860M, every retired generator EIA lists, vintage {vintage} (session 133)",
            "Shape: entities (docs/datastandard.md v0). One row per generator; entity_id eia860:<plant id>:<generator id>; capacity_mw is EIA nameplate capacity (MW); "
            "status_date and retirement_date are the first day of EIA's retirement month. The columns of eia860m_retired_generators, which holds only the last two years' retirements.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia860m_retired_all.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/{run_id}/ (not in git)",
            f"Source: {SOURCE} EIA-860M Monthly Update to the Annual Electric Generator Report, sheets {', '.join(SHEETS)} ({'; '.join(titles)}), {url}",
            f"  document list: {eia860.PAGE}",
            f"Rows: {len(df):,} of the {CEILING:,} ceiling; retirements from {int(years.min())} to {int(years.max())}. Snapshot: one vintage; a new vintage replaces the rows.",
            "License: public (EIA-PD).",
        ]
        cols = eia860.ENTITY_COLS + eia860.EXTRA_COLS
        ip.write_snapshot(df, NAME, header, log, cols=cols + [c for c in df.columns if c not in cols])
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Form EIA-860M, Monthly Update to the Annual Electric Generator Report: the Retired sheets, every year",
                                    report_url=eia860.PAGE, document_list=eia860.PAGE, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="monthly", status="ok", detail=f"vintage {vintage}, {len(df)} rows"))
        print(f"{NAME}: {len(df):,} retired generators, vintage {vintage}, retirements {int(years.min())} to {int(years.max())}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        last = tb.strip().splitlines()[-1]
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} FAILED, no output file written: {last}", file=sys.stderr)
        results.append(dict(table=NAME, market="monthly", status="failed", detail=last[:300]))
    if not args.out_dir:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
