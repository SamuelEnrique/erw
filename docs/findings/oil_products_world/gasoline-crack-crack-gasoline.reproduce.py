# Expected: 1987 2.036968, 2025 19.32996, change 17.292991 (USD per barrel); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate gasoline_crack for crack_gasoline from the ERW's public tables.

    python {this file} <eia_product_spot_prices.csv> <eia_fuel_spot_prices.csv>

Gulf Coast conventional gasoline in dollars a barrel less WTI, the year's mean of the days with both.
"""
import sys

import pandas as pd


def read(path):
    with open(path, encoding="utf-8") as f:
        skip = 0
        for line in f:
            if not line.startswith("#"):
                break
            skip += 1
    d = pd.read_csv(path, skiprows=skip, usecols=["entity", "variable", "ts_utc", "value"], dtype=str)
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    return d.dropna(subset=["value"])


p = read(sys.argv[1])
p = p[(p['entity'] == 'eia:EER_EPMRU_PF4_RGC_DPG') & (p['variable'] == 'spot_price')]
p = p.assign(day=p['ts_utc'].str[:10]).set_index('day')['value'] * 42.0
w = read(sys.argv[2])
w = w[(w['entity'] == 'eia:wti_cushing') & (w['variable'] == 'spot_price')]
w = w.assign(day=w['ts_utc'].str[:10]).set_index('day')['value']
b = p.to_frame('p').join(w.rename('w'), how='inner')
for y, s in b.groupby(b.index.str[:4].astype(int)):
    print(y, round(float((s['p'] - s['w']).mean()), 6), len(s))
