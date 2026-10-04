#!/usr/bin/env python3
"""California from the join, before and after: every affected figure, each way (session 78).

Energy Research Warehouse (ERW). Analysis for review: reads the held tables and the join (warehouse/derived/caiso_join.py),
writes CSV files under runs/session78/ and prints a summary. It writes nothing in warehouse/output and makes no request.

    python warehouse/analysis/caiso_join_before_after.py

Files (each line of each file is a figure computed both ways on the same hours, never an estimate):
    before_after_carbon_monthly.csv    California's intensity of generation by UTC month from the join: EIA's CO2 over EIA's
                                       generation, and over CAISO's own, on the hours both hold; and the monthly table's rows
    before_after_mix.csv               generation by fuel, EIA against CAISO's own, mean MW over the hours both tables hold
    caiso_mix_monthly.csv              CAISO's own generation by fuel by UTC month from the join (mean MW; complete days only)
    before_after_cost_carbon.csv       cost_of_power_carbon's California intensity_generation by Pacific month, the builder's
                                       rule replicated; the EIA column is checked against the held table
    before_after_other.csv             the network's California number, ai_power_regions' two California figures, and the
                                       import share by EIA's balance
"""

import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in ("warehouse/connectors", "warehouse/derived"):
    sys.path.insert(0, os.path.join(ROOT, p))
import caiso_join as cj  # noqa: E402
import cost_of_power as cp  # noqa: E402
import price_board as pb  # noqa: E402

OUT = os.path.join(ROOT, "runs", "session78")
AI_WINDOW = ("2025-09-01", "2026-09-01")  # ai_power_regions.WINDOW
# EIA's fuel variables of eia930_all_generation against CAISO's sources
FUELS = [("natural gas", ["net_generation_natural_gas_mw"], ["natural_gas_mw"]),
         ("geothermal", ["net_generation_geothermal_mw"], ["geothermal_mw"]),
         ("hydro (CAISO: large and small)", ["net_generation_hydro_mw"], ["large_hydro_mw", "small_hydro_mw"]),
         ("nuclear", ["net_generation_nuclear_mw"], ["nuclear_mw"]),
         ("solar", ["net_generation_solar_mw"], ["solar_mw"]),
         ("wind", ["net_generation_wind_mw"], ["wind_mw"]),
         ("coal", ["net_generation_coal_mw"], ["coal_mw"]),
         ("oil (CAISO: no such source)", ["net_generation_oil_mw"], []),
         ("other (EIA) against biogas, biomass, other and batteries (CAISO)", ["net_generation_other_mw"],
          ["biogas_mw", "biomass_mw", "other_mw", "batteries_mw"]),
         ("all generation (CAISO: every source but imports)", ["net_generation_mw"], cj.OWN)]


def held(name, entity, variable):
    d = pd.read_csv(os.path.join(cj.OUT_DIR, name + ".csv"), comment="#", dtype=str, keep_default_na=False)
    d = d[(d["entity"] == entity) & (d["variable"] == variable)]
    return pd.Series(d["value"].astype(float).values, index=d["ts_utc"].values)


def main():
    os.makedirs(OUT, exist_ok=True)
    eia, caiso = cj.eia_hours(), cj.caiso_hours()
    j = cj.joined(eia, caiso)
    post = eia[eia.index >= cj.JOIN].join(caiso[["net_generation_mwh"]].rename(columns={"net_generation_mwh": "caiso_mwh"}), how="inner")
    post = post.dropna(subset=["co2_emissions_generated", "net_generation_mwh", "caiso_mwh"])

    # 1. carbon by month, the same hours both ways
    g = post.assign(month=post.index.str[:7]).groupby("month")
    m = pd.DataFrame({"hours_both_hold": g.size(),
                      "eia_generation_gwh_per_day": (g["net_generation_mwh"].sum() / g.size() * 24 / 1000).round(1),
                      "caiso_generation_gwh_per_day": (g["caiso_mwh"].sum() / g.size() * 24 / 1000).round(1),
                      "intensity_generation_eia": (g["co2_emissions_generated"].sum() * 1000 / g["net_generation_mwh"].sum()).round(2),
                      "intensity_generation_joined": (g["co2_emissions_generated"].sum() * 1000 / g["caiso_mwh"].sum()).round(2)})
    m["change_pct"] = ((m["intensity_generation_joined"] / m["intensity_generation_eia"] - 1) * 100).round(1)
    tab_eia = held("carbon_intensity_monthly", cj.ENTITY, cj.VARIABLE)
    scratch = pd.read_csv(os.path.join(OUT, "carbon_intensity_monthly.csv"), comment="#", dtype=str, keep_default_na=False)
    scratch = scratch[(scratch["entity"] == cj.ENTITY) & (scratch["variable"] == cj.VARIABLE)]
    tab_join = pd.Series(scratch["value"].astype(float).values, index=scratch["ts_utc"].values)
    m["monthly_table_eia"] = [tab_eia.get(k + "-01T00:00:00Z") for k in m.index]
    m["monthly_table_joined"] = [tab_join.get(k + "-01T00:00:00Z") for k in m.index]
    m.to_csv(os.path.join(OUT, "before_after_carbon_monthly.csv"))
    whole = (post["co2_emissions_generated"].sum() * 1000 / post["net_generation_mwh"].sum(),
             post["co2_emissions_generated"].sum() * 1000 / post["caiso_mwh"].sum(), len(post))

    # 2. the mix: EIA against CAISO's own on the hours both tables hold
    gen = pd.read_csv(os.path.join(cj.OUT_DIR, "eia930_all_generation.csv"), comment="#", usecols=["entity", "variable", "ts_utc", "value"])
    gen = gen[gen["entity"] == cj.ENTITY].pivot(index="ts_utc", columns="variable", values="value")
    both = gen.join(caiso, how="inner")
    both = both[both.index >= cj.JOIN]
    mix = pd.DataFrame([dict(fuel=name, eia_mean_mw=round(float(both[e].sum(axis=1).mean()), 1),
                             caiso_mean_mw=round(float(both[c].sum(axis=1).mean()), 1) if c else None) for name, e, c in FUELS])
    mix["caiso_less_eia_mw"] = (mix["caiso_mean_mw"] - mix["eia_mean_mw"]).round(1)
    mix["hours"], mix["first_hour"], mix["last_hour"] = len(both), both.index.min(), both.index.max()
    mix.to_csv(os.path.join(OUT, "before_after_mix.csv"), index=False)

    # CAISO's own mix by UTC month from the join, complete UTC days only
    c2 = caiso[caiso.index >= cj.JOIN]
    days = c2.assign(day=c2.index.str[:10]).groupby("day").size()
    full = c2[c2.index.str[:10].isin(days[days == 24].index)]
    cm = full.assign(month=full.index.str[:7]).groupby("month")[cj.OWN + ["imports_mw", "net_generation_mwh"]].mean().round(1)
    cm.insert(0, "complete_utc_days", full.assign(month=full.index.str[:7], day=full.index.str[:10]).groupby("month")["day"].nunique())
    cm.to_csv(os.path.join(OUT, "caiso_mix_monthly.csv"))

    # 3. cost_of_power_carbon's California intensity_generation, the builder's rule: over the hours with a real-time price
    # and demand, by Pacific month; written only when every such hour holds the CO2 and the generation
    quiet = lambda msg: None  # noqa: E731
    price = cp.hourly(cp.prices_of("caiso", "rtm", quiet)[0])
    price.index = price.index.strftime("%Y-%m-%dT%H:%M:%SZ")
    x = pd.DataFrame({"price": price}).join(eia[["demand_mwh", "co2_emissions_generated", "net_generation_mwh"]], how="inner")
    x = x.dropna(subset=["price", "demand_mwh"]).join(j[["net_generation_mwh", "side"]].rename(columns={"net_generation_mwh": "joined_mwh"}), how="left")
    x["month"] = pd.to_datetime(x.index, utc=True).tz_convert(pb.TZ["caiso"]).strftime("%Y-%m")
    tab = held("cost_of_power_carbon", "caiso:TH_SP15_GEN-APND", cj.VARIABLE)
    rows = []
    for month, d in x.groupby("month"):
        ok_e = d["co2_emissions_generated"].notna().all() and d["net_generation_mwh"].notna().all()
        sides = set(d["side"].dropna())
        ok_j = d["co2_emissions_generated"].notna().all() and d["joined_mwh"].notna().all() and len(sides) == 1
        rows.append(dict(month=month, hours=len(d),
                         eia_replicated=cj.r4(d["co2_emissions_generated"].sum() * 1000 / d["net_generation_mwh"].sum()) if ok_e else None,
                         held_table=tab.get(month + "-01T00:00:00Z"),
                         joined=cj.r4(d["co2_emissions_generated"].sum() * 1000 / d["joined_mwh"].sum()) if ok_j else None,
                         side="; ".join(sorted(sides)) if sides else "",
                         hours_without_caiso=int(d["joined_mwh"].isna().sum())))
    cc = pd.DataFrame(rows)
    cc = cc[cc["month"] >= "2025-06"]
    cc.to_csv(os.path.join(OUT, "before_after_cost_carbon.csv"), index=False)
    chk = cc.dropna(subset=["eia_replicated", "held_table"])
    worst = float((chk["eia_replicated"] - chk["held_table"]).abs().max()) if len(chk) else None

    # 4. the network's number, ai_power_regions, the import share by EIA's balance
    other = []
    nodes = pd.read_csv(os.path.join(cj.OUT_DIR, "grid_network_nodes.csv"), comment="#", dtype=str, keep_default_na=False)
    n = nodes[(nodes["entity"] == cj.ENTITY) & (nodes["variable"] == cj.VARIABLE)].iloc[0]
    hj = j.loc[n["ts_utc"]] if n["ts_utc"] in j.index else None
    other.append(dict(figure="the network: California's intensity of generation, the hour grid_network_nodes holds",
                      period=n["ts_utc"], before=float(n["value"]), unit="kgCO2/MWh",
                      after=cj.r4(hj["co2_generated"] * 1000 / hj["net_generation_mwh"]) if hj is not None and hj["side"] == "caiso" else None))
    last = post.index.max()
    other.append(dict(figure="the network: the same, the newest hour both sources hold", period=last, unit="kgCO2/MWh",
                      before=cj.r4(post.loc[last, "co2_emissions_generated"] * 1000 / post.loc[last, "net_generation_mwh"]),
                      after=cj.r4(post.loc[last, "co2_emissions_generated"] * 1000 / post.loc[last, "caiso_mwh"])))
    ai = pd.read_csv(os.path.join(cj.OUT_DIR, "ai_power_regions.csv"), comment="#", dtype=str, keep_default_na=False)
    ai = ai[ai["entity"] == "iso:caiso"].set_index("variable")["value"].astype(float)
    other.append(dict(figure="ai_power_regions: carbon_intensity_kg_mwh (consumed, the year's daily mean)",
                      period=f"{AI_WINDOW[0]} to {AI_WINDOW[1]}", before=ai["carbon_intensity_kg_mwh"],
                      after=ai["carbon_intensity_kg_mwh"], unit="kgCO2/MWh"))
    # the import share by EIA's balance: demand less net generation over demand, the hours that hold both
    w = eia[(eia.index >= AI_WINDOW[0]) & (eia.index < AI_WINDOW[1])].dropna(subset=["demand_mwh", "net_generation_mwh"])
    rep = (w["demand_mwh"].sum() - w["net_generation_mwh"].sum()) / w["demand_mwh"].sum() * 100
    wj = w.join(j[["net_generation_mwh", "side"]].rename(columns={"net_generation_mwh": "joined_mwh"}), how="inner").dropna(subset=["joined_mwh"])
    aft = (wj["demand_mwh"].sum() - wj["joined_mwh"].sum()) / wj["demand_mwh"].sum() * 100
    same = (wj["demand_mwh"].sum() - wj["net_generation_mwh"].sum()) / wj["demand_mwh"].sum() * 100
    other.append(dict(figure="ai_power_regions: net_import_share_pct, held table", period=f"{AI_WINDOW[0]} to {AI_WINDOW[1]}",
                      before=ai["net_import_share_pct"], after=None, unit="pct"))
    other.append(dict(figure=f"the same, replicated from the recovered hours ({len(w)} hours)", period=f"{AI_WINDOW[0]} to {AI_WINDOW[1]}",
                      before=round(rep, 4), after=None, unit="pct"))
    other.append(dict(figure=f"the same on the hours the join holds ({len(wj)} hours: EIA's generation before the join, CAISO's own from it)",
                      period=f"{AI_WINDOW[0]} to {AI_WINDOW[1]}", before=round(same, 4), after=round(aft, 4), unit="pct"))
    wp = wj[wj["side"] == "caiso"]
    other.append(dict(figure=f"the import share by EIA's balance, from the join only ({len(wp)} hours)",
                      period=f"{cj.JOIN} to {AI_WINDOW[1]}", unit="pct",
                      before=round((wp["demand_mwh"].sum() - wp["net_generation_mwh"].sum()) / wp["demand_mwh"].sum() * 100, 4),
                      after=round((wp["demand_mwh"].sum() - wp["joined_mwh"].sum()) / wp["demand_mwh"].sum() * 100, 4)))
    pd.DataFrame(other)[["figure", "period", "before", "after", "unit"]].to_csv(os.path.join(OUT, "before_after_other.csv"), index=False)

    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 90)
    print(f"from the join, the {whole[2]:,} hours both hold: intensity of generation {whole[0]:.2f} (EIA) against {whole[1]:.2f} (joined)")
    print(m.to_string())
    print(mix.drop(columns=["first_hour", "last_hour"]).to_string(index=False))
    print(cm.to_string())
    print(cc.to_string(index=False))
    print(f"cost_of_power_carbon: the replicated EIA column against the held table, largest difference {worst} over {len(chk)} months")
    print(pd.DataFrame(other)[["figure", "period", "before", "after", "unit"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
