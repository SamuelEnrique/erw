#!/usr/bin/env python3
"""Session 228: erw_2026_datacenter_carbon.csv, the second file of the replication of "What a datacenter pays": the
grid's carbon intensity of consumed electricity by month (carbon_intensity_monthly, every month held) and by hour over
the window the live set holds (carbon_intensity_hourly, the last 430 days since session 245; 35 until then), for the default case's balancing authority
(ERCOT, eia930:ERCO), read from the live set with the anon key. The do-file and the Python mirror read it beside
erw_2026_datacenter_hourly.csv to rebuild the answer "How clean" (docs/methods/datacenter_pays_algorithm.md, 4.16).

    python site/scripts/write-datacenter-carbon.py [--ba ERCO] [--out site/public/datacenter/erw_2026_datacenter_carbon.csv]

A code machine writes no warehouse data: this reads the cloud copy (Supabase) and writes a site file beside the page's
other replication files. Provenance in '#' lines, as the hourly file has them.
"""
import argparse
import datetime as dt
import os
import sys

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def env(name):
    if os.environ.get(name):
        return os.environ[name]
    for f in (os.path.join(ROOT, "site", ".env.local"), os.path.join(ROOT, ".env")):
        if os.path.exists(f):
            for line in open(f, encoding="utf-8"):
                if line.startswith(name + "="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ba", default="ERCO")
    ap.add_argument("--out", default=os.path.join(ROOT, "site", "public", "datacenter", "erw_2026_datacenter_carbon.csv"))
    a = ap.parse_args()
    url = env("SUPABASE_URL").rstrip("/")
    if not url.endswith("/rest/v1"):
        url += "/rest/v1"
    key = env("SUPABASE_ANON_KEY")
    if not url or not key:
        sys.exit("SUPABASE_URL or SUPABASE_ANON_KEY is not set")
    H = {"apikey": key, "Authorization": f"Bearer {key}"}

    def rows(table, variable):
        out, off = [], 0
        while True:
            r = requests.get(f"{url}/series", headers=H, timeout=120, params={"select": "ts_utc,value", "table_name": f"eq.{table}", "entity": f"eq.eia930:{a.ba}",
                                                                              "variable": f"eq.{variable}", "order": "ts_utc", "limit": "1000", "offset": str(off)})
            r.raise_for_status()
            b = r.json()
            out.extend(b)
            if len(b) < 1000:
                return out
            off += 1000

    monthly = rows("carbon_intensity_monthly", "intensity_demand")
    hourly = rows("carbon_intensity_hourly", "intensity_demand")
    if not monthly or not hourly:
        sys.exit(f"the live set holds no rows for eia930:{a.ba}: monthly {len(monthly)}, hourly {len(hourly)}")
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    head = [
        f"# Energy Research Warehouse (ERW): the carbon behind What a datacenter pays; the default case's grid (session 228)",
        f"# Balancing authority: eia930:{a.ba} (ERCOT). Variable intensity_demand: kg CO2 per MWh of consumed electricity (generation plus imports less exports), the ERW's from EIA-930's hourly CO2 estimates (docs/methods/emissions.md)",
        f"# Rows: kind month, one per month held of carbon_intensity_monthly ({len(monthly)} rows, {monthly[0]['ts_utc'][:7]} to {monthly[-1]['ts_utc'][:7]}); kind hour, one per hour of carbon_intensity_hourly the live set holds ({len(hourly)} rows, {hourly[0]['ts_utc'][:13]} to {hourly[-1]['ts_utc'][:13]} UTC, its rolling window of 430 days (session 245; 35 until then)). ts_utc is the month's or the hour's start",
        "# A month or an hour not in the table is not a row: nothing is filled",
        f"# Source tables (ERW, the live set in Supabase, read with the public key at {now}): carbon_intensity_monthly, carbon_intensity_hourly (warehouse/derived/carbon_intensity.py on eia930_all_emissions)",
        "# The page's arithmetic (docs/methods/datacenter_pays_algorithm.md, 4.16): the load's carbon over the last twelve months is each month's energy times the month's intensity, over the months whose intensity is held; its own hours' intensity over the hourly window is the sum of weight x intensity over the sum of weights, over the hours the price and the intensity are both held",
        "# Written by site/scripts/write-datacenter-carbon.py; read by erw_2026_datacenter_replication.do and erw_2026_datacenter_replication.py beside erw_2026_datacenter_hourly.csv",
    ]
    lines = head + ["kind,ts_utc,kg_co2_per_mwh"]
    for r in monthly:
        lines.append(f"month,{r['ts_utc'][:19].replace('+00:00', '')}Z,{float(r['value']):.4f}")
    for r in hourly:
        lines.append(f"hour,{r['ts_utc'][:19]}Z,{float(r['value']):.4f}")
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print(f"{a.out}: {len(monthly)} months, {len(hourly)} hours; {len(head)} header lines, names on line {len(head) + 1}")


if __name__ == "__main__":
    main()
