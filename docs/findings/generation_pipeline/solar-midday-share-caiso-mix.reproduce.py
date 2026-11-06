# Expected: 2019 36.961051, 2025 47.894097, change 10.933046 (percent of generation); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate solar_midday_share for caiso_mix from the ERW's public table.

    python {this file} <generation_mix_hourly_profile.csv>

Solar's share of the grid's generation from 11 AM to 4 PM local, the mean over the year's months, by calendar year, for CAISO (entity iso:caiso). A month's share: the source's mean MW in local hours 11 to 15
over the sum of every source's mean MW in those hours (storage counted when it discharges, not when it charges).
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
d = d[(d["entity"] == "iso:caiso") & d["variable"].str.match(r"^avg_[a-z_]+_mw_h[0-9][0-9]$")].copy()
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"])
d["src"] = d["variable"].str[4:].str.rsplit("_mw_h", n=1).str[0]
d["hour"] = d["variable"].str[-2:].astype(int)
d = d[d["src"].isin(['natural_gas', 'coal', 'nuclear', 'wind', 'solar', 'hydro', 'storage', 'other']) & d["hour"].between(11, 15)]
d["value"] = d["value"].clip(lower=0)
m = d.groupby(["ts_utc", "src"])["value"].sum().unstack("src").dropna(subset=["solar"])
gen = m.sum(axis=1)
share = 100 * m["solar"] / gen
for y, s in share.groupby(share.index.str[:4].astype(int)):
    print(y, round(float(s.mean()), 6), len(s))
