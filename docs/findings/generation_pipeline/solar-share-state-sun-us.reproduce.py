# Expected: 2001 0.014525, 2025 6.786462, change 6.771936 (percent of net generation); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate solar_share for state_sun_US from the ERW's public table.

    python {this file} <eia_state_generation_monthly.csv>

Utility-scale solar's share of the state's net generation over the year, by calendar year, for the United States. Series eia:generation:US:SUN over eia:generation:US:ALL (net generation,
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
d = d[d["entity"].isin(["eia:generation:US:ALL", "eia:generation:US:SUN"]) & (d["variable"] == "net_generation")].copy()
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"])
d["src"] = d["entity"].str.split(":").str[3]
w = d.pivot_table(index="ts_utc", columns="src", values="value")
w = w.dropna(subset=["ALL"])
w = w[w["ALL"] > 0]
w["v"] = w["SUN"].fillna(0.0) if "SUN" in w else 0.0
w["year"] = w.index.str[:4].astype(int)
for y, s in w.groupby("year"):
    print(y, round(float(100 * s["v"].sum() / s["ALL"].sum()), 6), len(s))
