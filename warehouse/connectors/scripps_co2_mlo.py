#!/usr/bin/env python3
"""Carbon dioxide in the air at Mauna Loa, a month from March 1958, as the Scripps CO2 Program measures it (session 2137,
chain 090: the atmosphere's concentration beside the emissions the ERW holds).

Energy Research Warehouse (ERW) connector. One series table from the Scripps CO2 Program's monthly in situ record (the
Keeling Curve), which its Primary Mauna Loa CO2 Record page links:

    https://keelinglabsites.ucsd.edu/websitedataco2/monthly_in_situ_co2_mlo.csv   quoted header lines, three lines of
        column names, then one line a month: Yr, Mn, two dates, CO2, seasonally adjusted, fit, seasonally adjusted fit,
        CO2 filled, seasonally adjusted filled, station; -99.99 a month without a measurement

    scripps_co2_mlo_monthly   entity scripps:mlo; variables co2 (column 5, the monthly mean adjusted to the 15th) and
                              co2_seasonally_adjusted (column 6), unit ppm (Decision 67, micromoles per mole of dry air, the
                              2012 SIO manometric scale); ts_utc the month's first day; freq P1M; geo empty; x_station MLO,
                              or MKO for the months Maunakea's summit stood in for Mauna Loa after its 2022 eruption

The fitted and filled columns (7 to 10) are not taken: they are a curve and a fill, not measurements. A month marked
-99.99 has no row and is counted in the header. A line not of the form above, a month given twice, or a station not MLO
or MKO stops the run. Nothing is filled. NOAA's Global Monitoring Laboratory's Mauna Loa and global marine files are not
taken: gml.noaa.gov's robots file disallows /webdata/ and /aftp/, where they are (session 2137).

    python warehouse/connectors/scripps_co2_mlo.py [--offline] [--out-dir DIR]

Ceiling: one request, saved in warehouse/raw/scripps_co2_mlo/ and reused offline (asked fresh when not offline: the file
keeps its address as it grows). keelinglabsites.ucsd.edu has no robots file; scrippsco2.ucsd.edu's disallows /wp-admin/
only. License: public (CC BY 4.0, the Scripps CO2 Program's Usage Restrictions page, read in session 2137).
"""

import argparse
import datetime as dt
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "scripps_co2_mlo"
SOURCE = "scripps:co2_mlo_monthly"
URL = "https://keelinglabsites.ucsd.edu/websitedataco2/monthly_in_situ_co2_mlo.csv"
PAGE = "https://scrippsco2.ucsd.edu/data/primary-mauna-loa-co2-record/"
TERMS = "https://scrippsco2.ucsd.edu/usage-restrictions/"
TABLE = "scripps_co2_mlo_monthly"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
X_COLS = ["x_station"]
NUM = r"(-?\d+\.\d+)"
LINE = re.compile(r"^(\d{4}), (\d\d), +\d+, +\d{4}\.\d+, +" + r", +".join([NUM] * 6) + r", ([A-Z]{3})$")
MISSING = -99.99


def parse(text, base):
    """The data lines as rows (the quoted header and the column names skipped), and the count of months without a
    measurement."""
    rows, missing, started = [], 0, False
    for ln in text.replace("\r\n", "\n").split("\n"):
        s = ln.strip()
        if not s or s.startswith('"'):
            continue
        if not started:
            if re.match(r"^\d{4},", s):
                started = True
            else:
                continue  # the three lines of column names
        m = LINE.match(s)
        if not m:
            raise RuntimeError(f"a line not of the Scripps form: {s[:90]!r}")
        y, mo, co2, sa = m.group(1), m.group(2), float(m.group(3)), float(m.group(4))
        sta = m.group(9)
        if sta not in ("MLO", "MKO"):
            raise RuntimeError(f"a station not MLO or MKO: {s[:90]!r}")
        ts = f"{y}-{mo}-01T00:00:00Z"
        for var, v in (("co2", co2), ("co2_seasonally_adjusted", sa)):
            if v == MISSING:
                missing += 1
                continue
            rows.append(dict(entity="scripps:mlo", variable=var, ts_utc=ts, value=v, unit="ppm", freq="P1M", geo="", market="",
                             node="Mauna Loa Observatory", **base, x_station=sta))
    if not rows:
        raise RuntimeError("no month in the file")
    return pd.DataFrame(rows), missing


def main(argv=None):
    ap = argparse.ArgumentParser(description="The Scripps CO2 Program's monthly Mauna Loa CO2, from 1958")
    ap.add_argument("--offline", action="store_true", help="the saved file only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if ip.paused(CONNECTOR) or ip.paused_host("keelinglabsites.ucsd.edu"):
        print(f"{TABLE}: the publisher is paused (warehouse/metadata/paused_sources.csv); nothing asked")
        return 0
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=60, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        text = content.decode("utf-8", errors="replace")
        s, missing = parse(text, base)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a month given twice")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["variable", "ts_utc"]).reset_index(drop=True)
        co2 = s[s.variable == "co2"]
        last = co2.iloc[-1]
        archive = re.search(r"Baseline data in this file through ([^ ]+) from archive dated ([^ ]+ [0-9:]+)", text)
        mko = s[s.x_station == "MKO"].ts_utc.str[:7]
        head = [
            "Energy Research Warehouse (ERW): the Scripps CO2 Program (Scripps Institution of Oceanography, UC San Diego), atmospheric CO2 at Mauna Loa "
            "Observatory, Hawaii, from in situ air measurements, a month from 1958 (session 2137)",
            "Shape: series (docs/datastandard.md v0). entity scripps:mlo; variables co2 (the monthly mean, adjusted to the 15th) and co2_seasonally_adjusted; "
            "unit ppm (Decision 67, micromoles per mole of dry air, the 2012 SIO manometric scale); ts_utc the month's first day; freq P1M; x_station MLO, "
            "or MKO (Maunakea's summit) for the months after Mauna Loa's 2022 eruption.",
            f"{len(co2)} months of co2, {co2.ts_utc.min()[:7]} to {last.ts_utc[:7]} ({last.value:.2f} ppm); {missing} values marked -99.99 have no row; "
            f"MKO months {mko.min() if len(mko) else 'none'} to {mko.max() if len(mko) else 'none'} ({mko.nunique()}). The fitted and filled columns are not "
            "taken. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/scripps_co2_mlo.py; the file retrieved {base['retrieved_at']}"
            + (f"; the file says: baseline data through {archive.group(1)} from archive dated {archive.group(2)}" if archive else ""),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Scripps CO2 Program, monthly_in_situ_co2_mlo.csv, {URL} (linked from {PAGE})",
            f"License: public (CC BY 4.0, {TERMS}; credit the Scripps Institution of Oceanography at UC San Diego, and cite as the file asks: "
            "C. D. Keeling et al., Exchanges of atmospheric CO2 and 13CO2 with the terrestrial biosphere and oceans from 1978 to 2000, "
            "SIO Reference Series No. 01-06, 2001).",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s)} rows, {missing} missing values")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Scripps CO2 Program (Scripps Institution of Oceanography, UC San Diego)",
                                    report="Primary Mauna Loa CO2 Record: monthly in situ CO2", report_url=PAGE, document_list=URL,
                                    license="public", tables=[TABLE])])  # CC BY 4.0: the registry's word for an open license
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
