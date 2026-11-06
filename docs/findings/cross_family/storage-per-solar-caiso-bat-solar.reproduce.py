# Expected: 2015 0.0038, 2025 2.1695, change 2.1657 (MWh per MW of solar); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate storage_per_solar for caiso_bat_solar from the ERW's public tables.

    python {this file} <storage_buildout_monthly.csv>

The battery fleet's MWh per MW of solar in operation at the year's end, CAISO.
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
f = f[(f['entity'] == 'iso:caiso') & (f['variable'] == 'battery_mwh_per_solar_mw') & (f['ts_utc'].str[5:7] == '12')]
for t, v in sorted(zip(f['ts_utc'], f['value'])):
    print(int(t[:4]), round(float(v), 6), 1)
