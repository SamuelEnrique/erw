"""Session 73: the numbers of SESSION_73_REPORT.md and docs/methods/eia930_caiso_break.md, from runs/session73/<ba>_daily.csv
(warehouse/analysis/eia930_break.py) and warehouse/output/caiso_fuel_supply.csv. python warehouse/analysis/eia930_break_numbers.py"""
# Session 73: the numbers of the report and the method note, from runs/session73/<ba>_daily.csv and caiso_fuel_supply
import pandas as pd
pd.set_option("display.width", 250)
e = pd.read_csv("runs/session73/ciso_daily.csv", comment="#")
e = e[e["hours"] == 24].set_index("day")
c = pd.read_csv("warehouse/output/caiso_fuel_supply.csv", comment="#", usecols=["variable", "ts_utc", "value"])
c["day"] = c["ts_utc"].str.slice(0, 10)
n = c.groupby(["day", "variable"]).size().unstack()
c = c.groupby(["day", "variable"])["value"].sum().unstack()
c = c[(n == 24).all(axis=1)]
m = pd.DataFrame(index=c.index)
pairs = {"gas": ("natural_gas_mw", "ng_ng"), "geo": ("geothermal_mw", "ng_geo"), "nuc": ("nuclear_mw", "ng_nuc"), "solar": ("solar_mw", "ng_sun"), "wind": ("wind_mw", "ng_wnd")}
for k, (cc, ee) in pairs.items():
    m[f"caiso_{k}"] = c[cc]; m[f"eia_{k}"] = e[ee]
m["caiso_hydro"] = c["large_hydro_mw"] + c["small_hydro_mw"]; m["eia_hydro"] = e["ng_wat"]
m["caiso_batt"] = c["batteries_mw"]
m["caiso_imports"] = c["imports_mw"]; m["eia_imports"] = -e["total_interchange"]
m["caiso_gen_ex_imports"] = c.drop(columns=["imports_mw"]).sum(axis=1); m["eia_netgen"] = e["net_generation"]
m["eia_demand"] = e["demand"]
m = m.dropna(subset=["eia_netgen"])
m["eia_resid"] = m["eia_demand"] - m["eia_netgen"] - m["eia_imports"]
after = m.index >= "2025-12-16"
m.to_csv("runs/session73/ciso_eia_vs_caiso_daily.csv")
t = (pd.DataFrame({"before": m[~after].mean(), "after": m[after].mean()}) / 1000).round(1)
print(f"GWh per UTC day; before {m[~after].index.min()} to {m[~after].index.max()} ({(~after).sum()} days); after {m[after].index.min()} to {m[after].index.max()} ({after.sum()} days)")
print(t.to_string())
d = pd.read_csv("runs/session73/ciso_daily.csv", comment="#")
print(d[(d["day"] >= "2025-12-14") & (d["day"] <= "2025-12-18")][["day", "hours", "hours_ng_geo", "net_generation", "ng_ng", "ng_geo"]].to_string(index=False))
out = []
for ba in ["ciso", "erco", "isne", "miso", "nyis", "pjm", "swpp"]:
    d = pd.read_csv(f"runs/session73/{ba}_daily.csv", comment="#")
    d = d[(d["hours"] == 24) & (d["day"] >= "2024-10-01")]
    d["resid_pct"] = 100 * (d["demand"] - (d["net_generation"] - d["total_interchange"])) / d["demand"]
    d["m"] = d["day"].str.slice(0, 7)
    out.append(d.groupby("m")["resid_pct"].mean().round(2).rename(ba.upper()))
w = pd.concat(out, axis=1)
w.to_csv("runs/session73/residual_by_month.csv")
print(w.to_string())
for ba in ["erco"]:
    d = pd.read_csv(f"runs/session73/{ba}_daily.csv", comment="#")
    print(ba, "UES last day with a value:", d.loc[d["ng_ues"].fillna(0).abs() > 0, "day"].max(), "; first:", d.loc[d["ng_ues"].fillna(0).abs() > 0, "day"].min())

# --- the carbon comparison ---
# Session 73: California's carbon intensity, EIA's against one on CAISO's own generation (EIA's own gas factor)
x = pd.read_csv("warehouse/raw/eia930_emissions/20260930T000657Z/ciso_hours.csv", comment="#")
x["day"] = x["ts_utc"].str.slice(0, 10)
co2 = x.groupby("day")[["co2_emissions_generated", "co2_emissions_natural_gas", "co2_emissions_consumed"]].sum(min_count=24)
m = pd.read_csv("runs/session73/ciso_eia_vs_caiso_daily.csv", index_col=0).join(co2, how="inner").dropna(subset=["co2_emissions_generated"])
after = m.index >= "2025-12-16"
for lab, s in (("before", m[~after]), ("after", m[after])):
    f = s["co2_emissions_natural_gas"].sum() / s["eia_gas"].sum()
    print(lab, len(s), "days; EIA gas factor %.3f t/MWh; EIA intensity of generation %.0f kg/MWh; on CAISO's own generation %.0f; EIA consumed intensity %.0f; CO2 generated %.1f kt/day" % (
        f, 1000 * s["co2_emissions_generated"].sum() / s["eia_netgen"].sum(),
        1000 * (s["co2_emissions_generated"].sum() - s["co2_emissions_natural_gas"].sum() + f * s["caiso_gas"].sum()) / s["caiso_gen_ex_imports"].sum(),
        1000 * s["co2_emissions_consumed"].sum() / s["eia_demand"].sum(), s["co2_emissions_generated"].mean() / 1000))
