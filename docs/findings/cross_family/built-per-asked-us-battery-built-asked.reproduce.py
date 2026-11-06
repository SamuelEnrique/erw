# Expected: 2010 0.0, 2024 7.029207, change 7.029207 (percent of MW requested); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate built_per_asked for us_battery_built_asked from the ERW's public tables.

    python {this file} <eia860m_operating_generators.csv> <lbnl_interconnection_queue.csv>

The US MW of a type that entered service in the year (and still operate) as a percent of the MW of the type requested in the year, battery.
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


op = read(sys.argv[1], ['technology', 'nameplate_mw', 'operating_year'])
op = op[op['technology'] == 'Batteries']
op = op.assign(mw=pd.to_numeric(op['nameplate_mw'], errors='coerce'), year=pd.to_numeric(op['operating_year'], errors='coerce')).dropna(subset=['mw', 'year'])
lq = read(sys.argv[2], ['type_clean', 'mw_1', 'q_year'])
lq = lq[lq['type_clean'] == 'Battery']
lq = lq.assign(mw=pd.to_numeric(lq['mw_1'], errors='coerce'), year=pd.to_numeric(lq['q_year'], errors='coerce')).dropna(subset=['mw', 'year'])
built, asked = op.groupby('year')['mw'].sum(), lq.groupby('year')['mw'].sum()
for y in range(2010, 2025):
    if asked.get(y, 0) > 0:
        print(y, round(float(100 * built.get(y, 0.0) / asked[y]), 6), 1)
