# Expected: 2001 17.104364, 2025 40.926371, change 23.822007 (percent of net generation); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate gas_share for state_ng_US from the ERW's public table.

    python {this file} <eia_state_generation_monthly.csv>

Natural gas's share of the state's net generation over the year, by calendar year, for the United States. Series eia:generation:US:NG over eia:generation:US:ALL (net generation,
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
d = d[d["entity"].isin(["eia:generation:US:ALL", "eia:generation:US:NG"]) & (d["variable"] == "net_generation")].copy()
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"])
d["src"] = d["entity"].str.split(":").str[3]
w = d.pivot_table(index="ts_utc", columns="src", values="value")
w = w.dropna(subset=["ALL"])
w = w[w["ALL"] > 0]
w["v"] = w["NG"].fillna(0.0) if "NG" in w else 0.0
w["year"] = w.index.str[:4].astype(int)
for y, s in w.groupby("year"):
    print(y, round(float(100 * s["v"].sum() / s["ALL"].sum()), 6), len(s))
