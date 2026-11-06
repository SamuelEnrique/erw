# Expected: 2019 0.998231, 2025 1.312192, change 0.313962 (USD per gallon); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate gas_premium for gasprem_SCA from the ERW's tables.

    python {this file} <eia_regional_retail_fuel_prices.csv>

An area's retail regular gasoline price less the US price, the year's mean of the weeks with both, California.
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


d = read(sys.argv[1], ['eia:EMM_EPMR_PTE_NUS_DPG', 'eia:EMM_EPMR_PTE_SCA_DPG'], 'retail_price')
w = d.pivot_table(index='day', columns='entity', values='value')[['eia:EMM_EPMR_PTE_SCA_DPG', 'eia:EMM_EPMR_PTE_NUS_DPG']].dropna()
gap = w['eia:EMM_EPMR_PTE_SCA_DPG'] - w['eia:EMM_EPMR_PTE_NUS_DPG']
for y, s in gap.groupby(gap.index.str[:4].astype(int)):
    print(y, round(float(s.mean()), 6), len(s))
