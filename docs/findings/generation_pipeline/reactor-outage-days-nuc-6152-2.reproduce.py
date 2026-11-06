# Expected: 2007 4.0, 2025 186.0, change 182.0 (days); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate reactor_outage_days for nuc_6152_2 from the ERW's public table.

    python {this file} <eia_nuclear_outages_generator_daily.csv>

The days of the year on which at least half the reactor's capacity was out, by calendar year (entity eia_nuclear_outages_gen:6152:2).
"""
import sys

import pandas as pd

with open(sys.argv[1], encoding="utf-8") as f:
    skip = 0
    for line in f:
        if not line.startswith("#"):
            break
        skip += 1
d = pd.read_csv(sys.argv[1], skiprows=skip, usecols=['entity', 'variable', 'ts_utc', 'value'], dtype=str)
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"])
d["year"] = d["ts_utc"].str[:4].astype(int)
d = d[(d['entity'] == 'eia_nuclear_outages_gen:6152:2') & d['variable'].isin(['capacity', 'outage'])]
w = d.pivot_table(index=['ts_utc', 'year'], columns='variable', values='value').reset_index().dropna(subset=['capacity'])
w = w[w['capacity'] > 0]
w['out'] = w['outage'].fillna(0.0) >= 0.5 * w['capacity']
for y, s in w.groupby('year'):
    print(y, int(s['out'].sum()), len(s))
