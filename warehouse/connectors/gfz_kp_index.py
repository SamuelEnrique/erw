#!/usr/bin/env python3
"""The planetary geomagnetic index Kp, every three hours from 1932, as GFZ Potsdam publishes it (session 2135, chain 090:
the geomagnetic storms that drive currents into transformers and long lines).

Energy Research Warehouse (ERW) connector. One series table from GFZ Helmholtz Centre for Geosciences' Kp file, the
record NOAA's Space Weather Prediction Center's storm scale reads (SWPC's own products hold only recent days):

    https://kp.gfz-potsdam.de/fileadmin/files_for_gfz_cms/Kp_ap_since_1932.txt   one line an interval: YYYY MM DD, the
        interval's start and middle hour, the days since 1932 at each, Kp, ap and the status D (1 definitive, 0
        preliminary)

    gfz_kp_index_3h   entity gfz:kp; variable kp, unit index (Kp in thirds: 5- is 4.667, 5o 5.000, 5+ 5.333); ts_utc the
                      interval's start; freq PT3H; geo empty; x_ap the interval's ap (GFZ's equivalent amplitude, unitless,
                      times 2 nT the disturbance at 50 degrees geomagnetic latitude); x_status definitive or preliminary

GFZ revises the latest intervals as observatories report; each run replaces the table whole. An interval GFZ marks
missing (Kp -1) is not written and is counted in the header. A line not of the form above, an interval not three hours
after the one before, a status not 0 or 1, or an interval given twice stops the run. Nothing is filled.

    python warehouse/connectors/gfz_kp_index.py [--offline] [--out-dir DIR]

Ceiling: one request, saved in warehouse/raw/gfz_kp_index/ and reused offline (asked fresh when not offline: the file
keeps its address as it grows). kp.gfz-potsdam.de has no robots file. License: CC BY 4.0, as the file's header states it
(read in session 2135).
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

CONNECTOR = "gfz_kp_index"
SOURCE = "gfz:kp_ap_since_1932"
URL = "https://kp.gfz-potsdam.de/fileadmin/files_for_gfz_cms/Kp_ap_since_1932.txt"
PAGE = "https://kp.gfz-potsdam.de/en/data"
TABLE = "gfz_kp_index_3h"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
X_COLS = ["x_ap", "x_status"]
STATUS = {"0": "preliminary", "1": "definitive"}
LINE = re.compile(r"^(\d{4}) (\d\d) (\d\d) +(\d+\.\d) +(\d+\.\d+) +\d+\.\d+ +\d+\.\d+ +(-?\d+\.\d+) +(-?\d+) +(\d)$")


def parse(text, base):
    """The file's lines as rows, its # lines returned apart (the header, which states the license), and the count of
    intervals GFZ marks missing."""
    head, rows, missing, prev = [], [], 0, None
    for ln in text.replace("\r\n", "\n").split("\n"):
        if not ln.strip():
            continue
        if ln.startswith("#"):
            head.append(ln)
            continue
        m = LINE.match(ln.strip())
        if not m:
            raise RuntimeError(f"a line not of GFZ's form: {ln[:80]!r}")
        y, mo, d, hh, _, kp, ap, st = m.groups()
        if st not in STATUS:
            raise RuntimeError(f"a status not 0 or 1: {ln[:80]!r}")
        hour = float(hh)
        if hour % 3:
            raise RuntimeError(f"an interval not on a three-hour boundary: {ln[:80]!r}")
        t = dt.datetime(int(y), int(mo), int(d), int(hour), tzinfo=dt.timezone.utc)
        if prev is not None and t - prev != dt.timedelta(hours=3):
            raise RuntimeError(f"an interval not three hours after the one before: {prev:%Y-%m-%d %H} then {t:%Y-%m-%d %H}")
        prev = t
        if float(kp) < 0:
            missing += 1
            continue
        rows.append(dict(entity="gfz:kp", variable="kp", ts_utc=t.strftime("%Y-%m-%dT%H:%M:%SZ"), value=round(float(kp), 3), unit="index",
                         freq="PT3H", geo="", market="", node="planetary", **base, x_ap=ap if int(ap) >= 0 else "", x_status=STATUS[st]))
    if not rows:
        raise RuntimeError("no interval in the file")
    return pd.DataFrame(rows), head, missing


def main(argv=None):
    ap = argparse.ArgumentParser(description="GFZ Potsdam's Kp, every three hours from 1932")
    ap.add_argument("--offline", action="store_true", help="the saved file only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if ip.paused(CONNECTOR) or ip.paused_host("kp.gfz-potsdam.de"):
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=180, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        s, gfz_head, missing = parse(content.decode("utf-8", errors="strict"), base)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("an interval given twice")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values("ts_utc").reset_index(drop=True)
        lic = [h.lstrip("# ").strip() for h in gfz_head if re.search(r"^# (LICENSE|SOURCE):", h)]
        n_status = s.x_status.value_counts().to_dict()
        top = s.value.max()
        head = [
            "Energy Research Warehouse (ERW): GFZ Helmholtz Centre for Geosciences, the planetary geomagnetic index Kp, every three hours from 1932 "
            "(session 2135)",
            "Shape: series (docs/datastandard.md v0). entity gfz:kp; variable kp, unit index (Kp in thirds, 5- 4.667, 5o 5.000, 5+ 5.333); ts_utc the "
            "three-hour interval's start; freq PT3H; x_ap the interval's ap (unitless; times 2 nT the disturbance at 50 degrees geomagnetic latitude); x_status definitive or preliminary.",
            f"{len(s)} intervals, {s.ts_utc.min()[:10]} to {s.ts_utc.max()[:16]}: " + ", ".join(f"{k} {v}" for k, v in sorted(n_status.items()))
            + f"; {missing} intervals GFZ marks missing are not written; the highest Kp {top:.3f}. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/gfz_kp_index.py; the file retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} GFZ Potsdam, Kp_ap_since_1932.txt, {URL} (listed on {PAGE})",
        ] + [f"  the file: {x}" for x in lic[:4]] + [
            'License: public (CC BY 4.0, as the file\'s header states it; cite Matzka, J., Stolle, C., Yamazaki, Y., Bronkalla, O. and Morschhauser, A., '
            '2021, Space Weather, doi:10.1029/2020SW002641, and the data publication, GFZ Data Services, doi:10.5880/Kp.0001).',
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s)} intervals, {missing} missing; license lines in the file: {lic[:4]}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="GFZ Helmholtz Centre for Geosciences (Potsdam)",
                                    report="Geomagnetic Kp index (Kp and ap since 1932)", report_url=PAGE, document_list=URL,
                                    license="public", tables=[TABLE])])  # CC BY 4.0: the registry's word for an open license
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
