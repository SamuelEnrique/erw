"""Window D's data request 21 (the storage audit, finding 3): for ERCO, ISNE, MISO and SWPP over the last 30 days held,
EIA-930's storage-related types beside battery discharge (eia930_all_generation): hourly sums (MWh), the hours each
type is reported, its share of the four's total, and how often it is below zero (charging). Counts only."""
import sys

import pandas as pd

sys.path.insert(0, "warehouse/connectors")
import iso_prices as ip  # noqa: E402

p = "warehouse/output/eia930_all_generation.csv"
d = pd.read_csv(p, skiprows=ip.header_rows(p), dtype=str, keep_default_na=False)
types = ["net_generation_battery_mw", "net_generation_solar_with_battery_mw", "net_generation_wind_with_battery_mw",
         "net_generation_other_storage_mw", "net_generation_unknown_storage_mw", "net_generation_pumped_storage_mw"]
d = d[d["entity"].isin(["eia930:ERCO", "eia930:ISNE", "eia930:MISO", "eia930:SWPP"]) & d["variable"].isin(types)].copy()
d["t"] = pd.to_datetime(d["ts_utc"], utc=True)
end = d["t"].max()
d = d[d["t"] > end - pd.Timedelta(days=30)]
d["v"] = pd.to_numeric(d["value"], errors="coerce")
print("window:", d["t"].min(), "to", end)
g = d.groupby(["entity", "variable"]).agg(hours=("v", "size"), mwh=("v", "sum"), hours_below_zero=("v", lambda s: int((s < 0).sum())),
                                          min_mw=("v", "min"), max_mw=("v", "max")).round(1)
print(g.to_string())
