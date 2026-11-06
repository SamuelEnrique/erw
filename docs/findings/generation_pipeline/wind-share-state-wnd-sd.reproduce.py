# Expected: 2001 0.011769, 2025 58.209507, change 58.197738 (percent of net generation); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate wind_share for state_wnd_SD from the ERW's public table.

    python {this file} <eia_state_generation_monthly.csv>

Wind's share of the state's net generation over the year, by calendar year, for South Dakota. Series eia:generation:SD:WND over eia:generation:SD:ALL (net generation,
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
d = d[d["entity"].isin(["eia:generation:SD:ALL", "eia:generation:SD:WND"]) & (d["variable"] == "net_generation")].copy()
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"])
d["src"] = d["entity"].str.split(":").str[3]
w = d.pivot_table(index="ts_utc", columns="src", values="value")
w = w.dropna(subset=["ALL"])
w = w[w["ALL"] > 0]
w["v"] = w["WND"].fillna(0.0) if "WND" in w else 0.0
w["year"] = w.index.str[:4].astype(int)
for y, s in w.groupby("year"):
    print(y, round(float(100 * s["v"].sum() / s["ALL"].sum()), 6), len(s))
