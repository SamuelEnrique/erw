"""Window D's data request 39 (the states audit, finding 3): EIA's small-scale solar (fueltypeid DPV, an EIA estimate,
not in its all-fuels total) beside utility-scale solar (SUN), by state, from eia_state_generation_monthly (already
pulled, Form EIA-923 and EIA's estimate). For the newest twelve months held: utility solar's share of the state's
generation (ALL), and solar's share with rooftop panels in (SUN + DPV over ALL + DPV). Also the first month DPV is held."""
import sys

import pandas as pd

sys.path.insert(0, "warehouse/connectors")
import iso_prices as ip  # noqa: E402

p = "warehouse/output/eia_state_generation_monthly.csv"
d = pd.read_csv(p, skiprows=ip.header_rows(p), dtype=str, keep_default_na=False, usecols=["entity", "ts_utc", "value"])
parts = d["entity"].str.split(":")
d["loc"], d["fuel"], d["v"] = parts.str[2], parts.str[3], pd.to_numeric(d["value"], errors="coerce")
d = d[d["fuel"].isin(["ALL", "SUN", "DPV"])]
print("DPV held from", d[d["fuel"] == "DPV"]["ts_utc"].min()[:7], "to", d[d["fuel"] == "DPV"]["ts_utc"].max()[:7],
      "| SUN to", d[d["fuel"] == "SUN"]["ts_utc"].max()[:7])
months = sorted(set(d[d["fuel"] == "DPV"]["ts_utc"]))[-12:]
x = d[d["ts_utc"].isin(months)].pivot_table(index="loc", columns="fuel", values="v", aggfunc="sum")
x = x[x.index.str.len() == 2].fillna(0)
x["utility_share_pct"] = 100 * x["SUN"] / x["ALL"]
x["with_rooftop_pct"] = 100 * (x["SUN"] + x["DPV"]) / (x["ALL"] + x["DPV"])
x["rooftop_part_of_solar_pct"] = 100 * x["DPV"] / (x["SUN"] + x["DPV"])
x["points_added"] = x["with_rooftop_pct"] - x["utility_share_pct"]
pd.set_option("display.width", 250)
print(f"twelve months {months[0][:7]} to {months[-1][:7]}; {len(x)} locations")
print(x.sort_values("points_added", ascending=False).head(12).round(2).to_string())
print("US:" if "US" in x.index else "", x.loc[["US"]].round(2).to_string() if "US" in x.index else "")
print("states where rooftop solar is more than half of all solar:", ", ".join(x[x["rooftop_part_of_solar_pct"] > 50].index))
