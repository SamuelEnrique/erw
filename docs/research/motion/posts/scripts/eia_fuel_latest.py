"""B3, session 9900: ask the EIA API v2 for the newest weeks of US regular gasoline and No. 2 diesel retail prices.
Read only: saves the response (key removed) to runs/posts9900/b3/, writes no warehouse table."""
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
          ("facets[series][]", "EMD_EPD2D_PTE_NUS_DPG"), ("start", "2026-11-01"), ("sort[0][column]", "period"),
          ("sort[0][direction]", "desc"), ("length", "20")]
at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
r = requests.get(url, params=params, headers={"User-Agent": "ERW research project, github.com/SamuelEnrique/erw"}, timeout=60)
print(f"retrieved_at={at} status={r.status_code}")
body = r.json()
body.get("request", {}).get("params", {}).pop("api_key", None)
json.dump({"retrieved_at": at, "url": url, "response": body}, open(sys.argv[1], "w"), indent=1)
for row in body["response"]["data"]:
    print(row["period"], row["series"], row["value"], row.get("units"))
