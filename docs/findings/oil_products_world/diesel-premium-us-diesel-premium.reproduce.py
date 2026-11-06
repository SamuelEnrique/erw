# Expected: 1995 -0.001712, 2025 0.562635, change 0.564346 (USD per gallon); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate diesel_premium for us_diesel_premium from the ERW's tables.

    python {this file} <eia_retail_fuel_prices.csv>

The US retail diesel price less the retail regular gasoline price, the year's mean of the weeks with both.
"""
import sys

import pandas as pd


def read(path, entities, variable):
    with open(path, encoding="utf-8") as f:
        skip = 0
        for line in f:
            if not line.startswith("#"):
                break
            skip += 1
    d = pd.read_csv(path, skiprows=skip, usecols=["entity", "variable", "ts_utc", "value"], dtype=str)
    d = d[d["entity"].isin(entities) & (d["variable"] == variable)].copy()
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    d = d.dropna(subset=["value"])
    d["day"] = d["ts_utc"].str[:10]
    return d


d = read(sys.argv[1], ['eia:EMM_EPMR_PTE_NUS_DPG', 'eia:EMD_EPD2D_PTE_NUS_DPG'], 'retail_price')
w = d.pivot_table(index='day', columns='entity', values='value').dropna()
gap = w['eia:EMD_EPD2D_PTE_NUS_DPG'] - w['eia:EMM_EPMR_PTE_NUS_DPG']
for y, s in gap.groupby(gap.index.str[:4].astype(int)):
    print(y, round(float(s.mean()), 6), len(s))
