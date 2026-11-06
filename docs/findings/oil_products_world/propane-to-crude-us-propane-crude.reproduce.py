# Expected: 1993 71.018373, 2025 48.023539, change -22.994834 (percent of WTI); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate propane_to_crude for us_propane_crude from the ERW's tables.

    python {this file} <eia_product_spot_prices.csv> <eia_fuel_spot_prices.csv>

Mont Belvieu propane in dollars a barrel as a percent of WTI, the year's mean of the days with both.
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


p = read(sys.argv[1], ['eia:EER_EPLLPA_PF4_Y44MB_DPG'], 'spot_price').set_index('day')['value'] * 42.0
w = read(sys.argv[2], ['eia:wti_cushing'], 'spot_price').set_index('day')['value']
b = p.to_frame('p').join(w.rename('w'), how='inner')
b = b[b['w'] > 0]
r = 100 * b['p'] / b['w']
for y, s in r.groupby(r.index.str[:4].astype(int)):
    print(y, round(float(s.mean()), 6), len(s))
