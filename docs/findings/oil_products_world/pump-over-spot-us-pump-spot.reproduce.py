# Expected: 1991 0.462322, 2025 1.080384, change 0.618062 (USD per gallon); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate pump_over_spot for us_pump_spot from the ERW's public tables.

    python {this file} <eia_retail_fuel_prices.csv> <eia_product_spot_prices.csv>

The year's mean retail regular gasoline price less the year's mean Gulf Coast conventional gasoline spot price.
"""
import sys

import pandas as pd


def read(path):
    with open(path, encoding="utf-8") as f:
        skip = 0
        for line in f:
            if not line.startswith("#"):
                break
            skip += 1
    d = pd.read_csv(path, skiprows=skip, usecols=["entity", "variable", "ts_utc", "value"], dtype=str)
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    return d.dropna(subset=["value"])


r = read(sys.argv[1])
r = r[(r['entity'] == 'eia:EMM_EPMR_PTE_NUS_DPG') & (r['variable'] == 'retail_price')]
p = read(sys.argv[2])
p = p[(p['entity'] == 'eia:EER_EPMRU_PF4_RGC_DPG') & (p['variable'] == 'spot_price')]
py = p.groupby(p['ts_utc'].str[:4].astype(int))['value'].mean()
for y, s in r.groupby(r['ts_utc'].str[:4].astype(int)):
    if y in py.index:
        print(y, round(float(s['value'].mean() - py[y]), 6), len(s))
