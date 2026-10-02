#!/usr/bin/env python3
"""A helper for eia930_daily_interchange.py (session 62): fill month checkpoints backwards from a month, so a long pull
goes in parallel. The main pull reads a month's checkpoint when it reaches it and skips the request.

    python warehouse/connectors/eia930_daily_interchange_fill.py 2026-08 2023-01    # from 2026-08 back to 2023-01

Same route, facets, paging, raw capture (its own run folder) and checkpoint format as the main connector; past, complete
months only; a month that already has a checkpoint is skipped.
"""

import datetime as dt
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eia930_daily_interchange as x  # noqa: E402
import iso_prices as ip  # noqa: E402


def main():
    hi, lo = sys.argv[1], sys.argv[2]
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"eia930_daily_interchange_fill_{run_id}.log"))
    key = ip.load_key("EIA_API_KEY", log)
    ip.RAW.open("eia930_daily_interchange", run_id)
    ck = os.path.join(ip.RAW_DIR, "eia930_daily_interchange", "checkpoints")
    os.makedirs(ck, exist_ok=True)
    today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m")
    for m in reversed(pd.period_range(lo, hi, freq="M")):
        path = os.path.join(ck, f"{m}.csv")
        if os.path.exists(path) or str(m) >= today:
            continue
        df = x.month(key, m.start_time.strftime("%Y-%m-%d"), m.end_time.strftime("%Y-%m-%d"), log)
        if len(df):
            df.astype(str).to_csv(path + ".part", index=False)
            os.replace(path + ".part", path)
        log(f"  {m}: {len(df):,} rows (checkpoint)")
    log.close()


if __name__ == "__main__":
    main()
