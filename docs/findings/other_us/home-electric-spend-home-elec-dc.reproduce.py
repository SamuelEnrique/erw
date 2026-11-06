# Expected: 1990 42.918251, 2024 69.76482, change 26.846569 (percent of home energy spending); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 166): reproduce candidate home_electric_spend for home_elec_DC from the ERW's public table.

    python {this file} <eia_seds_residential_annual.csv>

Electricity's share of the residential sector's energy expenditures.
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
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"])
d["year"] = d["ts_utc"].str[:4].astype(int)
d = d[d['entity'].isin(['eia_seds_res:ESRCV:DC', 'eia_seds_res:TERCV:DC']) & (d['variable'] == 'expenditures')]
w = d.pivot_table(index='year', columns='entity', values='value').dropna()
for y, r in w.iterrows():
    if r['eia_seds_res:TERCV:DC'] > 0:
        print(y, round(float(100 * r['eia_seds_res:ESRCV:DC'] / r['eia_seds_res:TERCV:DC']), 6), 1)
