# Expected: 2014 0.496812, 2025 6.346093, change 5.849281 (percent of private nonresidential construction); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate dc_share for us_dc_share from the ERW's public table.

    python {this file} <census_c30_construction_monthly.csv>

Data centers' share of the value of private nonresidential construction put in place over the year.
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
d = d[d['entity'].isin(['census_c30:private:data_center', 'census_c30:private:nonresidential']) & (d['variable'] == 'value_put_in_place')]
w = d.pivot_table(index=['year', 'ts_utc'], columns='entity', values='value').dropna().reset_index()
for y, s in w.groupby('year'):
    print(y, round(float(100 * s['census_c30:private:data_center'].sum() / s['census_c30:private:nonresidential'].sum()), 6), len(s))
