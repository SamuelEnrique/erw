"""Data request 10 of docs/state/data_requests_five_tools.md (the severance audit): each state's crude oil first purchase
price (EIA, petroleum/pri/dfp1; eia_crude_first_purchase_prices: F003048__3 Texas, F003022__3 Louisiana, F003035__3 New
Mexico, the state FIPS codes), November 2025 to the latest month; its gap to WTI Cushing's monthly mean of EIA's daily
spot (eia_fuel_spot_prices, eia:wti_cushing, the mean of the month's trading days); and the severance tax on that gap
at 4.6 percent (Texas), 12.5 percent (Louisiana) and 7.14 percent (New Mexico) on 1,000 bbl. Prints and writes a CSV."""
import sys

import pandas as pd

sys.path.insert(0, "warehouse/connectors")
import iso_prices as ip  # noqa: E402

STATES = {"eia:F003048__3": ("Texas", 0.046), "eia:F003022__3": ("Louisiana", 0.125), "eia:F003035__3": ("New Mexico", 0.0714)}
p = "warehouse/output/eia_crude_first_purchase_prices.csv"
f = pd.read_csv(p, skiprows=ip.header_rows(p), dtype=str)
f = f[f["entity"].isin(STATES) & (f["ts_utc"] >= "2025-11-01")]
s = "warehouse/output/eia_fuel_spot_prices.csv"
w = pd.read_csv(s, skiprows=ip.header_rows(s), dtype=str)
w = w[(w["entity"] == "eia:wti_cushing") & (w["variable"] == "spot_price")]
w["month"] = w["ts_utc"].str[:7]
w["v"] = w["value"].astype(float)
wti = w.groupby("month").agg(wti=("v", "mean"), days=("v", "size"))
rows = []
for _, r in f.sort_values(["entity", "ts_utc"]).iterrows():
    name, rate = STATES[r["entity"]]
    m = r["ts_utc"][:7]
    fpp = float(r["value"])
    if m not in wti.index:
        continue
    gap = fpp - wti.loc[m, "wti"]
    rows.append(dict(state=name, month=m, first_purchase=round(fpp, 2), wti_monthly_mean=round(wti.loc[m, "wti"], 4),
                     wti_days=int(wti.loc[m, "days"]), gap_usd_bbl=round(gap, 4), rate=rate, tax_on_gap_per_1000bbl=round(gap * rate * 1000, 2)))
out = pd.DataFrame(rows)
print(out.to_string(index=False))
print()
print(out.groupby("state")[["gap_usd_bbl", "tax_on_gap_per_1000bbl"]].mean().round(3).to_string())
out.to_csv("runs/c701/fpp_gap.csv", index=False)
