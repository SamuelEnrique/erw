# Expected: 1997 2.013445, 2025 3.188406, change 1.17496 (percent a day); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate henry_hub_volatility from the ERW's public table.

    python {this file} <eia_fuel_spot_prices.csv>

The median absolute change of Henry Hub's spot close from one trading day to the next, in percent, by calendar year.
"""
import sys

import numpy as np
import pandas as pd

with open(sys.argv[1], encoding="utf-8") as f:
    skip = 0
    for line in f:
        if not line.startswith("#"):
            break
        skip += 1
g = pd.read_csv(sys.argv[1], skiprows=skip, usecols=["entity", "variable", "ts_utc", "value"], dtype=str)
g = g[(g["entity"] == "eia:henry_hub") & (g["variable"] == "spot_price")].copy()
g["value"] = pd.to_numeric(g["value"], errors="coerce")
g = g[g["value"] > 0].sort_values("ts_utc")
g["change"] = (g["value"] / g["value"].shift(1) - 1).abs() * 100
g = g.dropna(subset=["change"])
g["year"] = g["ts_utc"].str[:4].astype(int)
for y, s in g.groupby("year"):
    print(y, round(float(np.median(s["change"])), 6), len(s))
