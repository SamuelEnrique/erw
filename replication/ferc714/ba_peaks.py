#!/usr/bin/env python3
"""ERW, FERC-714 forecast growth: the cross-check of eleven planning areas outside the ISOs (session 3796, chain 215).

docs/methods/ferc714_forecast_growth.md, "Cross-check, eleven planning areas outside the ISOs". For each balancing
authority below: EIA-930's hourly demand (type D) of 2025 in UTC hours, the hours kept by the neighbour and range tests
of warehouse/derived/demand_growth.py (an hour is used when it is held, above zero, within 25 percent of the median of
the four hours around it, and within a third to three times the area's median hour), the highest used hour; beside it
the higher of the summer and winter peak that the respondent's 2024 FERC-714 filing gives for 2025
(ferc714_planning_area_forecasts in warehouse/output).

    python replication/ferc714/ba_peaks.py                 # EIA's API (EIA_API_KEY), at most 30 requests; pages saved
    python replication/ferc714/ba_peaks.py --raw DIR       # no request: the pages a run saved in DIR

Writes the table to standard output as CSV. The raw pages go under warehouse/raw/eia930_ba_peaks/<run>/ (not in git).
Standard library, pandas and requests.
"""
import argparse
import csv
import datetime as dt
import glob
import json
import os
import statistics as st
import sys
import time

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

# the balancing authority EIA-930 names for each respondent's own utility (Southern Company has no 2024 filing)
AREAS = {"TVA": "ferc714:152", "DUK": "ferc714:51", "CPLE": "ferc714:214", "FPL": "ferc714:63", "FPC": "ferc714:215",
         "AZPS": "ferc714:16", "SRP": "ferc714:133", "BPAT": "ferc714:21", "PSCO": "ferc714:124", "NEVP": "ferc714:99",
         "LDWP": "ferc714:84"}
API = "https://api.eia.gov/v2/electricity/rto/region-data/data/"
CEILING, JUMP = 30, 0.25


def pull(raw):
    import requests
    key = ip.load_key("EIA_API_KEY", lambda *a: None)
    if not key:
        raise SystemExit("EIA_API_KEY is not set")
    os.makedirs(raw, exist_ok=True)
    asked = 0
    for ba in AREAS:
        offset = 0
        while True:
            if asked >= CEILING:
                raise SystemExit(f"the ceiling of {CEILING} requests is reached at {ba}")
            params = {"api_key": key, "frequency": "hourly", "data[0]": "value", "facets[respondent][]": ba, "facets[type][]": "D",
                      "start": "2025-01-01T00", "end": "2025-12-31T23", "sort[0][column]": "period", "sort[0][direction]": "asc",
                      "length": 5000, "offset": offset}
            time.sleep(3)
            r = requests.get(API, params=params, timeout=120)
            asked += 1
            r.raise_for_status()
            body = r.json()
            with open(os.path.join(raw, f"{ba}_{offset}.json"), "w", encoding="utf-8") as f:
                json.dump(body, f)
            n = len(body["response"]["data"])
            offset += n
            if n < 5000:
                break
    return asked


def peak(raw, ba):
    rows = []
    for f in sorted(glob.glob(os.path.join(raw, f"{ba}_*.json"))):
        with open(f, encoding="utf-8") as h:
            rows += json.load(h)["response"]["data"]
    per = {str(r["period"]): float(r["value"]) for r in rows if r.get("value") not in (None, "")}
    med = st.median([v for v in per.values() if v > 0])
    used = []
    for k, v in per.items():
        if v <= 0 or not (med / 3 <= v <= 3 * med):
            continue
        t = dt.datetime.strptime(k, "%Y-%m-%dT%H")
        nb = [per.get((t + dt.timedelta(hours=h)).strftime("%Y-%m-%dT%H")) for h in (-2, -1, 1, 2)]
        nb = [n for n in nb if n is not None and n > 0]
        if nb and abs(v - st.median(nb)) <= JUMP * st.median(nb):
            used.append((v, k))
    v, k = max(used)
    return len(per), len(used), v, k


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raw", help="read the pages saved in this folder; no request")
    a = ap.parse_args(argv)
    raw = a.raw or os.path.join(ROOT, "warehouse", "raw", "eia930_ba_peaks", dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    if not a.raw:
        print(f"# {pull(raw)} requests; pages under {raw}", file=sys.stderr)
    path = os.path.join(ROOT, "warehouse", "output", "ferc714_planning_area_forecasts.csv")
    fc = pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False)
    fc = fc[(fc["x_report_year"] == "2024") & (fc["ts_utc"].str[:4] == "2025")]
    w = csv.writer(sys.stdout, lineterminator="\n")
    w.writerow(["ba", "respondent", "hours", "hours_used", "peak_mw", "peak_hour_utc", "forecast_mw", "forecast_season", "forecast_less_actual_pct"])
    for ba, ent in AREAS.items():
        hours, used, v, k = peak(raw, ba)
        x = fc[fc["entity"] == ent]
        f = {r.variable.split("_")[0]: float(r.value) for r in x.itertuples() if r.variable in ("summer_peak_forecast_mw", "winter_peak_forecast_mw")}
        season = max(f, key=f.get)
        w.writerow([ba, ent, hours, used, round(v), k, round(f[season]), season, round(100 * (f[season] - v) / v, 1)])
    return 0


if __name__ == "__main__":
    sys.exit(main())
