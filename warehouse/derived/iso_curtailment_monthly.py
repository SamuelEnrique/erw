#!/usr/bin/env python3
"""Curtailment by ISO, monthly: sums of the daily curtailment tables over complete months.

Energy Research Warehouse (ERW), session 18 (platform tool 22, the curtailment tracker).
Implements the monthly part of docs/methods/curtailment.md. Inputs: caiso_curtailment_daily,
spp_curtailment_daily and ercot_wind_solar_hsl_daily (warehouse/connectors/curtailment.py).
Output, through the merge writer, one derived `series` table:

    iso_curtailment_monthly   freq P1M, MWh, the input's entity and variable names

    python warehouse/derived/iso_curtailment_monthly.py
    python warehouse/derived/iso_curtailment_monthly.py --out-dir DIR   # a trial run: the table under DIR, nothing in warehouse/output

A variable's month is written only when the daily table has that variable for every day of
the calendar month; a month with a day missing is not written (the log names it), and the
month in progress never is. The value is the exact decimal sum of the daily values.
In CI the daily tables hold only the days the run pulled, so the script there writes the
months it can complete and the merge writer keeps the earlier months.

Session 144: the share of available wind and solar output curtailed is written too, for caiso:ISO and spp:SPP, as five
more variables of the same table (every earlier row and column is as it was): share_curtailed_pct (pct),
share_curtailed_mwh and share_output_mwh (MWh, over the days both are held), share_hours_held and
share_hours_in_month (count). The rule and the sources are warehouse/derived/curtailment_shares.py's; a share is
written only when curtailment and output are both held for at least 95 percent of the month's hours. If the shares
cannot be built (an input missing on the machine), the monthly sums are written as before and the log says why.
"""

import argparse
import datetime as dt
import os
import sys
import traceback
from decimal import Decimal

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "connectors"))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402
import curtailment_shares as shares  # noqa: E402

NAME = "iso_curtailment_monthly"
INPUTS = ["caiso_curtailment_daily", "spp_curtailment_daily", "ercot_wind_solar_hsl_daily"]
METHOD = "docs/methods/curtailment.md"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/curtailment.md"
SOURCE = "erw:iso_curtailment_monthly"


def share_rows(in_dir, log, retrieved):
    """Session 144: the share rows (curtailment_shares.rows), in the table's columns; [] with the reason in the log when
    they cannot be built, so that the monthly sums are written all the same."""
    try:
        grids = shares.build(in_dir, log)
    except Exception:
        log("  shares NOT written this run: " + ip.redact(traceback.format_exc()))
        return []
    return [{**r, "market": "", "node": "", "source": SOURCE, "source_url": METHOD_URL, "retrieved_at": retrieved, "vintage": ""} for r in shares.rows(grids)]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Curtailment by ISO, monthly")
    ap.add_argument("--out-dir", help="a trial run: the table, its log and the registry under this directory; nothing in warehouse/output")
    a = ap.parse_args(argv)
    in_dir = ip.OUT_DIR
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"curtailment_monthly_{run_id}.log"))
    try:
        present = [n for n in INPUTS if os.path.exists(os.path.join(in_dir, n + ".csv"))]
        if not present:
            raise RuntimeError(f"no input table: {INPUTS}")
        frames, srcs = [], set()
        for n in present:
            d = ip.read_series(os.path.join(in_dir, n + ".csv"), ip.SERIES_COLS)
            srcs |= set(d["source"])
            frames.append(d)
        df = pd.concat(frames, ignore_index=True)
        reg = pd.read_csv(os.path.join(ip.ROOT, "warehouse", "metadata", "sources.csv"), dtype=str, keep_default_na=False)
        lic = dict(zip(reg["source"], reg["license"]))
        missing = [s for s in srcs if s not in lic]
        if missing:
            raise RuntimeError(f"input sources {missing} are not in the registry; cannot set the license")
        license_ = "internal" if any(lic[s] == "internal" for s in srcs) else "public"
        df["month"] = df["ts_utc"].str[:7]
        this_month = pd.Timestamp.now(tz="UTC").strftime("%Y-%m")
        rows, skipped = [], 0
        for (entity, variable, month), g in df.groupby(["entity", "variable", "month"]):
            if month >= this_month:
                continue
            days = pd.Period(month).days_in_month
            if g["ts_utc"].nunique() != days:
                skipped += 1
                if skipped <= 20:
                    log(f"  {entity} {variable} {month}: {g['ts_utc'].nunique()} of {days} days; not written")
                continue
            total = sum((Decimal(v) for v in g["value"]), Decimal(0))
            geo = g["geo"].iloc[0]
            rows.append({"entity": entity, "variable": variable, "ts_utc": f"{month}-01T00:00:00Z",
                         "value": float(total), "unit": "MWh", "freq": "P1M", "geo": geo, "market": "",
                         "node": "", "source": SOURCE, "source_url": METHOD_URL,
                         "retrieved_at": ip.utc_iso(pd.Timestamp.now(tz="UTC")), "vintage": ""})
        if not rows:
            raise ip.SourceGap("no complete month in the daily tables")
        sums = len(rows)
        rows += share_rows(in_dir, log, ip.utc_iso(pd.Timestamp.now(tz="UTC")))
        s = pd.DataFrame(rows, columns=ip.SERIES_COLS).sort_values(["entity", "variable", "ts_utc"])
        log(f"{sums} rows of monthly sums; {len(s) - sums} rows of shares (session 144)")
        log(f"{len(s)} rows; {skipped} entity-variable-months not complete, not written")
        header = [
            "Energy Research Warehouse (ERW): Wind and solar curtailment by ISO, monthly, MWh (derived from the "
            "daily curtailment tables; platform tool 22)",
            "Shape: series (docs/datastandard.md v0). freq P1M: ts_utc is the first of the month, 00:00:00Z; the "
            "month is the daily tables' local operating days. Method and meaning: docs/methods/curtailment.md.",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/iso_curtailment_monthly.py",
            f"Run log: warehouse/output/logs/curtailment_monthly_{run_id}.log",
            f"Source: {SOURCE} ERW derived table, curtailment method ({METHOD}), {METHOD_URL}",
            "Derived from: " + "; ".join(present),
            "  input sources: " + "; ".join(sorted(srcs)),
            "A variable's month is the exact sum of its daily values, written only when every day of the month "
            f"is present; the month in progress is never written. {skipped} entity-variable-months were not "
            "complete in this run.",
            "Session 144: share_curtailed_pct, share_curtailed_mwh, share_output_mwh, share_hours_held, share_hours_in_month for caiso:ISO and "
            "spp:SPP: curtailed MWh over curtailed plus wind and solar output MWh, over the days both are held, written when they hold at least 95 percent "
            "of the month's hours (warehouse/derived/curtailment_shares.py). CAISO's output is CAISO's own; SPP's is EIA-930's hourly net generation.",
            f"License: {license_}. A derived table inherits the most restrictive license of its inputs (Decision 23).",
        ]
        ip.write_csv(s, NAME, header, log)
        ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                report="Curtailment by ISO, monthly (docs/methods/curtailment.md)",
                                report_url=METHOD_URL, document_list=METHOD, license=license_, tables=[NAME])])
        status = [dict(table=NAME, market="", status="ok", detail=f"{len(s)} rows")]
    except Exception:
        tb = ip.redact(traceback.format_exc())
        last = tb.strip().splitlines()[-1]
        log(f"FAILED, no output file written:\n{tb}")
        print(f"iso_curtailment_monthly FAILED, no output file written: {last}", file=sys.stderr)
        status = [dict(table=NAME, market="", status="failed", detail=last[:300])]
    ip.write_status("iso_curtailment_monthly", run_id, status)
    log.close()
    print(f"iso_curtailment_monthly run log: {os.path.relpath(log.path, ip.ROOT)}")
    return 1 if status[0]["status"] == "failed" else 0


if __name__ == "__main__":
    sys.exit(main())
