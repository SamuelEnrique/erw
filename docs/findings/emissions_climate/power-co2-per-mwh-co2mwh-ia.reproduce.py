# Expected: 2001 895.259915, 2022 281.778606, change -613.481309 (kg CO2 per MWh); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 166): reproduce candidate power_co2_per_mwh for co2mwh_IA from the ERW's public tables.

    python {this file} <eia_co2_state_annual.csv> <eia_state_generation_monthly.csv>

The electric power sector's CO2 over the state's net generation, Iowa.
"""
import sys

import pandas as pd


def read(path, cols):
    with open(path, encoding="utf-8") as f:
        skip = 0
        for line in f:
            if not line.startswith("#"):
                break
            skip += 1
    d = pd.read_csv(path, skiprows=skip, usecols=cols, dtype=str)
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    return d.dropna(subset=["value"])


d = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value'])
d = d[d['variable'] == 'co2']
p = d['entity'].str.split(':', expand=True)
d['st'], d['sec'], d['fuel'], d['year'] = p[1], p[2], p[3], d['ts_utc'].str[:4].astype(int)
d = d[d['year'] >= 2001]
co2 = d[(d['st'] == 'IA') & (d['sec'] == 'EC') & (d['fuel'] == 'TO')].groupby('year')['value'].sum()
g = read(sys.argv[2], ['entity', 'variable', 'ts_utc', 'value'])
g = g[(g['entity'] == 'eia:generation:IA:ALL') & (g['variable'] == 'net_generation')]
g['year'] = g['ts_utc'].str[:4].astype(int)
gen = g.groupby('year').agg(mwh=('value', 'sum'), months=('value', 'size'))
for y, v in co2.items():
    if y in gen.index and gen.loc[y, 'months'] == 12 and gen.loc[y, 'mwh'] > 0:
        print(y, round(float(1000 * v / gen.loc[y, 'mwh']), 6), 1)
