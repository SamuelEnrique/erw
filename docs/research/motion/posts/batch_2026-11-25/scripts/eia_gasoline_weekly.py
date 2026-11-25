"""Session 9901: ask the EIA API v2 (the ERW's registered source eia:petroleum/pri/gnd, free, public domain) for the
weekly U.S. regular retail gasoline price from 2020-01-01, to add the week of 23 November 2026, which the ERW table
eia_retail_fuel_prices (retrieved 20261120T150214Z) does not yet hold, and to check every overlapping week against
that table. Read only: saves the response (key removed) beside this script's data folder; writes no warehouse table.
Usage: python eia_gasoline_weekly.py <out.json>"""
import json
import sys
from datetime import datetime, timezone

import requests

key = None
for line in open("C:/Users/Shared/Documents/erw/.env", encoding="utf-8"):
    if line.startswith("EIA_API_KEY="):
        key = line.split("=", 1)[1].strip().strip('"')
url = "https://api.eia.gov/v2/petroleum/pri/gnd/data/"
params = [("api_key", key), ("frequency", "weekly"), ("data[0]", "value"), ("facets[series][]", "EMM_EPMR_PTE_NUS_DPG"),
          ("start", "2020-01-01"), ("sort[0][column]", "period"), ("sort[0][direction]", "asc"), ("length", "1000")]
at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
r = requests.get(url, params=params, headers={"User-Agent": "ERW research project, github.com/SamuelEnrique/erw"}, timeout=60)
print(f"retrieved_at={at} status={r.status_code}")
r.raise_for_status()
body = r.json()
body.get("request", {}).get("params", {}).pop("api_key", None)
json.dump({"retrieved_at": at, "url": url, "series": "EMM_EPMR_PTE_NUS_DPG", "response": body}, open(sys.argv[1], "w"), indent=1)
data = body["response"]["data"]
print("rows", len(data), "first", data[0]["period"], "last", data[-1]["period"], data[-1]["value"])
