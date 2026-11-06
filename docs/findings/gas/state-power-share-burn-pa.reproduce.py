# Expected: 2001 3.799874, 2025 61.63988, change 57.840006 (percent of delivered gas); tolerance 0.5 percent of the change.
"""ERW findings hunt (chain 164): reproduce candidate state_power_share for burn_PA from the ERW's public table.

    python {this file} <eia_gas_consumption_state_monthly.csv>

Gas delivered to a state's power plants as a percent of its gas delivered to the four consuming sectors. A year's figure: the numerator's rows summed times 100.0 over the denominator's rows summed, with the year's count of the numerator's months.
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
num = d[d["entity"].str.contains(':SPA$', regex=True) & d["variable"].isin(['consumption_electric_power'])]
den = d[d["entity"].str.contains(':SPA$', regex=True) & d["variable"].isin(['consumption_residential', 'consumption_commercial', 'consumption_industrial', 'consumption_electric_power'])]
for y, s in num.groupby("year"):
    b = den.loc[den["year"] == y, "value"].sum()
    if b != 0:
        print(y, round(float(s["value"].sum() * 100.0 / b), 6), s["ts_utc"].nunique())
