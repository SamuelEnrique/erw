# Expected: 2001 9.387254, 2024 7.47912, change -1.908134 (MMBtu per MWh); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate gas_heat_rate for hr_gas_FL from the ERW's public table.

    python {this file} <eia923_plant_fuel_annual.csv>

The gas-fired fleet's fuel consumed over its net generation, EIA-923, by calendar year, Florida; MMBtu = TBtu times 1,000,000.
"""
import sys

import pandas as pd

with open(sys.argv[1], encoding="utf-8") as f:
    skip = 0
    for line in f:
        if not line.startswith("#"):
            break
        skip += 1
d = pd.read_csv(sys.argv[1], skiprows=skip, usecols=['entity', 'variable', 'ts_utc', 'value', 'geo'], dtype=str)
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"])
d["year"] = d["ts_utc"].str[:4].astype(int)
p = d['entity'].str.split(':', expand=True)
d = d[p[2].isin(['NG']) & (p[2] != 'ALL')]
d = d[d['geo'] == 'US-FL']
t = d.pivot_table(index='year', columns='variable', values='value', aggfunc='sum')
for y, r in t.iterrows():
    if r.get('net_generation', 0) > 0 and r.get('fuel_consumed', 0) > 0:
        print(y, round(float(r['fuel_consumed'] * 1e6 / r['net_generation']), 6), 1)
