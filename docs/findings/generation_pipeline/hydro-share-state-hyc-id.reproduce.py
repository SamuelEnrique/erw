# Expected: 2001 77.27797, 2025 43.630824, change -33.647146 (percent of net generation); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate hydro_share for state_hyc_ID from the ERW's public table.

    python {this file} <eia_state_generation_monthly.csv>

Conventional hydro's share of the state's net generation over the year, by calendar year, for Idaho. Series eia:generation:ID:HYC over eia:generation:ID:ALL (net generation,
MWh, every sector); a month without the source's row counts as zero for it.
"""
import sys

import pandas as pd

with open(sys.argv[1], encoding="utf-8") as f:
    skip = 0
    for line in f:
        if not line.startswith("#"):
            break
        skip += 1
d = pd.read_csv(sys.argv[1], skiprows=skip, usecols=["entity", "variable", "ts_utc", "value"], dtype=str)
d = d[d["entity"].isin(["eia:generation:ID:ALL", "eia:generation:ID:HYC"]) & (d["variable"] == "net_generation")].copy()
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"])
d["src"] = d["entity"].str.split(":").str[3]
w = d.pivot_table(index="ts_utc", columns="src", values="value")
w = w.dropna(subset=["ALL"])
w = w[w["ALL"] > 0]
w["v"] = w["HYC"].fillna(0.0) if "HYC" in w else 0.0
w["year"] = w.index.str[:4].astype(int)
for y, s in w.groupby("year"):
    print(y, round(float(100 * s["v"].sum() / s["ALL"].sum()), 6), len(s))
