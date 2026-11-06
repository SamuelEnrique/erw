# Expected: 2019 0.181353, 2025 19.923571, change 19.742219 (percent of peak-day demand); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate battery_per_peak for ercot_bat_peak from the ERW's public tables.

    python {this file} <storage_buildout_monthly.csv> <eia930_daily_demand.csv>

The battery fleet at the year's end as a percent of the grid's peak days (the mean of its ten highest days of demand, as average GW), ERCOT.
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
    return pd.read_csv(path, skiprows=skip, usecols=cols, dtype=str)


f = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value'])
f = f[(f['entity'] == 'iso:ercot') & (f['variable'] == 'battery_operating_mw') & (f['ts_utc'].str[5:7] == '12')]
fleet = {int(t[:4]): float(v) for t, v in zip(f['ts_utc'], f['value'])}
d = read(sys.argv[2], ['entity', 'variable', 'ts_utc', 'value'])
d = d[(d['entity'] == 'eia930:ERCO') & (d['variable'] == 'demand_mwh')].copy()
d['value'] = pd.to_numeric(d['value'], errors='coerce')
d = d[d['value'] > 0].drop_duplicates(['entity', 'ts_utc'])
d['year'] = d['ts_utc'].str[:4].astype(int)
med = d.groupby('year')['value'].transform('median')
d = d[(d['value'] >= med / 3) & (d['value'] <= med * 3)]
for y, s in d.groupby('year'):
    if y in fleet:
        print(y, round(100 * fleet[y] / (s['value'].nlargest(10).mean() / 24.0), 6), len(s))
