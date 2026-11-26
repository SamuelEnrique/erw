"""Window D's data request 44 (the supply audit): measured gas burned for power against the supply page's estimate at one
heat rate (7.6 MMBtu per MWh, supply_page.HEAT_RATE). Measured: EIA's natural gas consumption by the electric power
sector by state, monthly (eia_gas_consumption_state_monthly, consumption_electric_power, MMcf), turned to MMBtu at EIA's
US average heat content of 1,036 Btu per cubic foot (an assumption stated: no state heat content is held). Estimated:
EIA-930's natural gas generation of the region (eia930_region_fuel_hourly, net_generation_natural_gas_mw, the hours
summed to MWh) times 7.6. Only the areas where a region and states match closely: TEX (Texas; ERCOT is most of it),
CAL (California), NY (New York), NE (the six New England states). PJM, MISO and SPP span parts of many states and are
not compared. 2024 and 2025, months with every hour held. Counts only."""
import sys

import pandas as pd

sys.path.insert(0, "warehouse/connectors")
import iso_prices as ip  # noqa: E402

AREAS = {"TEX": ["TX"], "CAL": ["CA"], "NY": ["NY"], "NE": ["CT", "MA", "ME", "NH", "RI", "VT"]}
HC = 1.036   # MMBtu per Mcf
HR = 7.6


def read(name, cols, keep):
    p = f"warehouse/output/{name}.csv"
    parts = []
    for ch in pd.read_csv(p, skiprows=ip.header_rows(p), dtype=str, keep_default_na=False, chunksize=500000, usecols=cols):
        parts.append(keep(ch))
    return pd.concat(parts)


g = read("eia930_region_fuel_hourly", ["entity", "variable", "ts_utc", "value"],
         lambda c: c[(c["variable"] == "net_generation_natural_gas_mw") & c["entity"].isin([f"eia930:{a}" for a in AREAS])
                     & c["ts_utc"].str[:4].isin(["2024", "2025"])])
g["month"] = g["ts_utc"].str[:7]
g["v"] = pd.to_numeric(g["value"], errors="coerce")
hours = g.groupby(["entity", "month"]).agg(mwh=("v", "sum"), n=("v", "count"))
hours["need"] = [pd.Period(m).days_in_month * 24 for _, m in hours.index]
hours = hours[hours["n"] >= hours["need"] - 1]   # every hour held (the spring hour that does not exist allowed)
c = read("eia_gas_consumption_state_monthly", ["entity", "variable", "ts_utc", "value"],
         lambda x: x[(x["variable"] == "consumption_electric_power") & x["ts_utc"].str[:4].isin(["2024", "2025"])])
c["st"] = c["entity"].str.split(":").str[2].str[1:]
c["month"] = c["ts_utc"].str[:7]
c["v"] = pd.to_numeric(c["value"], errors="coerce")
rows = []
for a, sts in AREAS.items():
    meas = c[c["st"].isin(sts)].groupby("month")["v"].sum(min_count=len(sts))
    est = hours.loc[f"eia930:{a}"]["mwh"] if f"eia930:{a}" in hours.index.get_level_values(0) else pd.Series(dtype=float)
    j = pd.DataFrame({"measured_mmbtu": meas * 1000 * HC, "estimated_mmbtu": est * HR, "gen_mwh": est}).dropna()
    for yr in ("2024", "2025"):
        y = j[j.index.str[:4] == yr]
        if y.empty:
            continue
        rows.append(dict(area=a, states="+".join(sts), year=yr, months=len(y),
                         measured_tbtu=round(y["measured_mmbtu"].sum() / 1e6, 1), estimated_tbtu=round(y["estimated_mmbtu"].sum() / 1e6, 1),
                         estimate_error_pct=round(100 * (y["estimated_mmbtu"].sum() / y["measured_mmbtu"].sum() - 1), 1),
                         implied_heat_rate=round(y["measured_mmbtu"].sum() / y["gen_mwh"].sum(), 2),
                         worst_month_error_pct=round((100 * (y["estimated_mmbtu"] / y["measured_mmbtu"] - 1)).abs().max(), 1)))
pd.set_option("display.width", 250)
print(pd.DataFrame(rows).to_string(index=False))
