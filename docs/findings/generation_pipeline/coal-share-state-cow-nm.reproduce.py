# Expected: 2001 84.501037, 2025 20.744718, change -63.756319 (percent of net generation); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate coal_share for state_cow_NM from the ERW's public table.

    python {this file} <eia_state_generation_monthly.csv>

Coal's share of the state's net generation over the year, by calendar year, for New Mexico. Series eia:generation:NM:COW over eia:generation:NM:ALL (net generation,
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
d = d[d["entity"].isin(["eia:generation:NM:ALL", "eia:generation:NM:COW"]) & (d["variable"] == "net_generation")].copy()
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"])
d["src"] = d["entity"].str.split(":").str[3]
w = d.pivot_table(index="ts_utc", columns="src", values="value")
w = w.dropna(subset=["ALL"])
w = w[w["ALL"] > 0]
w["v"] = w["COW"].fillna(0.0) if "COW" in w else 0.0
w["year"] = w.index.str[:4].astype(int)
for y, s in w.groupby("year"):
    print(y, round(float(100 * s["v"].sum() / s["ALL"].sum()), 6), len(s))
