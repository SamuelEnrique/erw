"""Window D's data request 47 (the events audit, finding 2), the counting half: for ERCOT and PJM, every December to
February held in noaa_grid_weather_daily (the grids' station sets, base 65 F, from January 2019), how many days reach
Uri's 50 and Elliott's 55 heating degree days, and the warmest of those days' demand served (eia930_ba_demand_hourly,
the grid's local day). The refit of the weather share on such days is not done here. Counts only."""
import sys

import pandas as pd

sys.path.insert(0, "warehouse/connectors")
import iso_prices as ip  # noqa: E402

p = "warehouse/output/noaa_grid_weather_daily.csv"
w = pd.read_csv(p, skiprows=ip.header_rows(p), dtype=str, keep_default_na=False)
w = w[(w["variable"] == "heating_degree_days") & w["entity"].isin(["iso:ercot", "iso:pjm"])].copy()
w["day"] = w["ts_utc"].str[:10]
w["m"] = w["day"].str[5:7]
w = w[w["m"].isin(["12", "01", "02"])]
w["hdd"] = w["value"].astype(float)
w["winter"] = [f"{int(d[:4]) - (0 if m == '12' else 1)}-{int(d[:4]) + (1 if m == '12' else 0)}" for d, m in zip(w["day"], w["m"])]
pd.set_option("display.width", 250)
for g in ("iso:ercot", "iso:pjm"):
    x = w[w["entity"] == g]
    t = x.groupby("winter").agg(days=("hdd", "size"), max_hdd=("hdd", "max"), at_30=("hdd", lambda s: int((s >= 30).sum())),
                                at_40=("hdd", lambda s: int((s >= 40).sum())), at_50=("hdd", lambda s: int((s >= 50).sum())),
                                at_55=("hdd", lambda s: int((s >= 55).sum())))
    print("==", g); print(t.to_string())
    top = x.nlargest(8, "hdd")[["day", "hdd"]]
    print("  coldest days:", ", ".join(f"{d} {h:.1f}" for d, h in zip(top["day"], top["hdd"])))
