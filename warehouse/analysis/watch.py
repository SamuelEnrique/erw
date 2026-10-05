"""The watch list of Automated Analysis: one measure a line, so that the chart of the week draws on the public tables
and not on ten hand-built charts alone (session 119).

Energy Research Warehouse (ERW). Session 23 gave the engine ten templates, each a module with its own chart. They read
8 of the public tables. A measure here needs no module: a line of WATCH names a public table, an entity, a variable
and how a period is made of its rows, and WatchTemplate turns it into the same result a template returns (a frame, a
line chart, a headline with its history, facts). warehouse/analysis/run.py runs the templates and the watch list
together and chooses among them by one rule (its docstring).

A line of WATCH:
    name      the measure's name, unique among templates
    title     what the chart is called
    table     the public table
    entity    the entity, or a list of entities whose values are added up (two fuels, several terminals)
    variable  the variable, or a list of variables added up
    over      optional: a variable (or list) the sum is divided by, times 100: a share in percent
    optional  optional: variables of `over` that count as zero in a period with no row for them (EIA writes its
              "not itemized" generation only in the months it withholds something)
    by        "week" (Monday to Sunday, UTC) or "month"
    how       "mean" or "sum" of the period's rows, or "last" (the period's one row: a monthly table, a stock)
    need      by "week": the fewest rows a week needs to count (default: 4 of a business week for a daily series,
              1 for a weekly one). A week with fewer is not a week: nothing is filled.
    whole     optional (held, in_month): two variables of the same entity; a month counts only when they are equal
              (a month every day of which is held)
    compare   "previous": the change from the period before. "year": the change from the same month a year earlier,
              for a monthly figure with a season in it
    unit      the unit as shown
    label     the headline's words
    about     "system": a measurement of the energy system. Every line here is one; the word is stated so that the
              chooser's rule reads the same for a template and for a line

A measure whose table is not on the machine is skipped and named, like a template (NoData). Tables that are behind a
fix held for approval are not watched: the carbon intensity tables carry months the faults register calls wrong
(docs/methods/impossible_hours.md), so no line reads them until the hold is lifted. docs/analysis/tables.json says, for
every public table, which template or line reads it, or why none does.
"""
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "templates"))
from common import NoData, fetch, r2, render, result  # noqa: E402

WATCH = [
    # fuels: the prices that move US power
    dict(name="watch_henry_hub", title="Henry Hub natural gas", table="eia_fuel_spot_prices", entity="eia:henry_hub", variable="spot_price",
         by="week", how="mean", compare="previous", unit="USD/MMBtu", label="Henry Hub spot price, weekly mean"),
    dict(name="watch_wti", title="WTI crude oil", table="eia_fuel_spot_prices", entity="eia:wti_cushing", variable="spot_price",
         by="week", how="mean", compare="previous", unit="USD/bbl", label="WTI spot price at Cushing, weekly mean"),
    dict(name="watch_brent", title="Brent crude oil", table="eia_fuel_spot_prices", entity="eia:brent", variable="spot_price",
         by="week", how="mean", compare="previous", unit="USD/bbl", label="Brent spot price, weekly mean"),
    dict(name="watch_gasoline_retail", title="US regular gasoline at the pump", table="eia_retail_fuel_prices", entity="eia:EMM_EPMR_PTE_NUS_DPG",
         variable="retail_price", by="week", how="last", need=1, compare="previous", unit="USD/gal", label="US regular gasoline retail price"),
    dict(name="watch_diesel_retail", title="US diesel at the pump", table="eia_retail_fuel_prices", entity="eia:EMD_EPD2D_PTE_NUS_DPG",
         variable="retail_price", by="week", how="last", need=1, compare="previous", unit="USD/gal", label="US on-highway diesel retail price"),
    dict(name="watch_crude_stocks", title="US commercial crude oil stocks", table="eia_petroleum_stocks_weekly", entity="eia:WCESTUS1",
         variable="stocks", by="week", how="last", need=1, compare="previous", unit="kbbl", label="US commercial crude oil stocks"),
    dict(name="watch_crude_imports", title="US crude oil imports", table="eia_crude_imports_by_country", entity="eia:MCRIMUS2", variable="imports",
         by="month", how="last", compare="year", unit="kbbl/d", label="US crude oil imports"),
    dict(name="watch_ulsd_ny", title="Diesel at New York Harbor", table="eia_product_spot_prices", entity="eia:EER_EPD2F_PF4_Y35NY_DPG",
         variable="spot_price", by="week", how="mean", compare="previous", unit="USD/gal", label="New York Harbor ultra-low sulfur diesel spot price, weekly mean"),
    dict(name="watch_crude_exports", title="US crude oil exports", table="eia_petroleum_trade_weekly", entity="eia:WCREXUS2", variable="flow",
         by="week", how="last", need=1, compare="previous", unit="kbbl/d", label="US crude oil exports"),
    # power prices and what they pay
    dict(name="watch_ercot_da_price", title="ERCOT day-ahead price, hub average", table="ercot_hub_prices_daily", entity="ercot:HB_HUBAVG",
         variable="da_mean", by="week", how="mean", need=7, compare="previous", unit="USD/MWh", label="ERCOT hub average day-ahead price, weekly mean"),
    dict(name="watch_ercot_cost_of_power", title="What a MWh cost in Texas, weighted by when the grid uses it", table="cost_of_power_monthly",
         entity="ercot:HB_HUBAVG", variable="rt_load_weighted", by="month", how="last", compare="year", unit="USD/MWh",
         label="ERCOT load-weighted real-time price"),
    dict(name="watch_battery_model_ercot", title="What a 2-hour battery could earn in Texas (a model's upper bound)", table="battery_stack_monthly",
         entity="ercot:HB_HUBAVG", variable="foresight_2h_revenue_total_usd_per_mw", by="month", how="last",
         whole=("foresight_2h_days_held", "foresight_2h_days_in_month"), compare="year", unit="USD/MW",
         label="modelled revenue of a 2-hour battery at the ERCOT hub average"),
    dict(name="watch_dam_awards", title="What Texas's storage resources were awarded day-ahead", table="ercot_storage_dam_awards_monthly",
         entity="ercot:esr_fleet", variable="revenue_total_usd_per_mw", by="month", how="last", whole=("days_held", "days_in_month"),
         compare="previous", unit="USD/MW", label="day-ahead awards of ERCOT's storage fleet per MW"),
    dict(name="watch_retail_price", title="US retail electricity price, all sectors", table="eia_retail_electricity_prices",
         entity="eia:retail_price:US:ALL", variable="retail_price", by="month", how="last", compare="year", unit="USD/MWh",
         label="US average retail electricity price"),
    dict(name="watch_ercot_regup", title="ERCOT Regulation Up, day-ahead", table="ercot_as_prices", entity="ercot:REGUP", variable="mcpc_dam",
         by="week", how="mean", need=160, compare="previous", unit="USD/MW", label="ERCOT Regulation Up day-ahead clearing price, weekly mean"),
    dict(name="watch_caiso_regup", title="CAISO Regulation Up, day-ahead", table="caiso_as_prices", entity="caiso:AS_CAISO_EXP",
         variable="as_price_dam_ru", by="week", how="mean", need=160, compare="previous", unit="USD/MW",
         label="CAISO Regulation Up day-ahead price, weekly mean"),
    dict(name="watch_nyiso_reg", title="NYISO regulation, day-ahead", table="nyiso_as_prices", entity="nyiso:NYCA",
         variable="as_price_dam_reg", by="week", how="mean", need=160, compare="previous", unit="USD/MW",
         label="NYISO day-ahead regulation price, weekly mean"),
    dict(name="watch_spp_regup", title="SPP Regulation Up, day-ahead", table="spp_as_prices", entity="spp:SPP", variable="as_price_dam_regup",
         by="week", how="mean", need=160, compare="previous", unit="USD/MW", label="SPP Regulation Up day-ahead price, weekly mean"),
    # demand and what is built
    dict(name="watch_large_load_ercot", title="Large load approved to energize in Texas", table="ercot_large_load_status", entity="ercot:large_load",
         variable="approved_to_energize_mw", by="month", how="last", compare="previous", unit="MW", label="ERCOT large load approved to energize"),
    dict(name="watch_retail_sales", title="Electricity sold in the US", table="eia_retail_sales_monthly", entity="eia:retail_sales:US:ALL",
         variable="retail_sales", by="month", how="last", compare="year", unit="MWh", label="US retail electricity sales"),
    dict(name="watch_storage_buildout", title="US battery storage in operation", table="storage_buildout_monthly", entity="us:total",
         variable="battery_operating_mw", by="month", how="last", compare="previous", unit="MW", label="US operating battery storage"),
    dict(name="watch_storage_buildout_ercot", title="Battery storage in operation in Texas", table="storage_buildout_monthly", entity="iso:ercot",
         variable="battery_operating_mw", by="month", how="last", compare="previous", unit="MW", label="ERCOT operating battery storage"),
    dict(name="watch_shoulder_caiso", title="California's shoulder hours", table="shoulder_hours_monthly", entity="iso:caiso_own",
         variable="shoulder_hours_needed", by="month", how="last", compare="previous", unit="hours", label="California shoulder hours needed"),
    dict(name="watch_shoulder_ercot", title="Texas's shoulder hours", table="shoulder_hours_monthly", entity="iso:ercot",
         variable="shoulder_hours_needed", by="month", how="last", compare="year", unit="hours", label="Texas shoulder hours needed"),
    dict(name="watch_battery_discharge_us", title="Batteries discharging, Lower 48", table="storage_daily_cycle", entity="eia930:US48",
         variable="mwh_discharged", by="week", how="mean", need=7, compare="previous", unit="MWh a day", label="Lower 48 battery discharge, daily mean of the week"),
    # what is thrown away, and what is made
    dict(name="watch_curtailment_caiso", title="California wind and solar curtailed", table="iso_curtailment_monthly", entity="caiso:ISO",
         variable=["curtailed_solar_mwh", "curtailed_wind_mwh"], by="month", how="last", compare="year", unit="MWh",
         label="California wind and solar curtailed"),
    dict(name="watch_caiso_solar", title="California solar output", table="caiso_fuel_supply", entity="caiso:ISO", variable="solar_mw",
         by="week", how="mean", need=160, compare="previous", unit="MW", label="California solar output, mean of the week's hours"),
    dict(name="watch_ercot_wind_held_back", title="Texas wind held below what it could make", table="ercot_wind_solar_hsl_daily", entity="ercot:system",
         variable="wind_below_hsl_mwh", by="week", how="sum", need=7, compare="previous", unit="MWh", label="ERCOT wind output below its high sustained limit"),
    dict(name="watch_curtailment_spp", title="SPP wind curtailed", table="spp_curtailment_daily", entity="spp:SPP", variable="curtailed_wind_mwh",
         by="week", how="sum", need=7, compare="previous", unit="MWh", label="SPP wind curtailed"),
    dict(name="watch_us_solar_share", title="Solar's share of US generation", table="state_generation_mix_monthly", entity="eia:US",
         variable="net_generation_solar_mwh",
         over=["net_generation_coal_mwh", "net_generation_hydro_mwh", "net_generation_natural_gas_mwh", "net_generation_not_itemized_mwh",
               "net_generation_nuclear_mwh", "net_generation_oil_and_other_mwh", "net_generation_other_renewables_mwh",
               "net_generation_solar_mwh", "net_generation_wind_mwh"], optional=["net_generation_not_itemized_mwh"],
         by="month", how="last", compare="year", unit="percent", label="utility-scale solar's share of US net generation"),
    dict(name="watch_us_gas_share", title="Natural gas's share of US generation", table="state_generation_mix_monthly", entity="eia:US",
         variable="net_generation_natural_gas_mwh",
         over=["net_generation_coal_mwh", "net_generation_hydro_mwh", "net_generation_natural_gas_mwh", "net_generation_not_itemized_mwh",
               "net_generation_nuclear_mwh", "net_generation_oil_and_other_mwh", "net_generation_other_renewables_mwh",
               "net_generation_solar_mwh", "net_generation_wind_mwh"], optional=["net_generation_not_itemized_mwh"],
         by="month", how="last", compare="year", unit="percent", label="natural gas's share of US net generation"),
]
SHOWN = {"week": 104, "month": 60}   # how many periods the chart draws

# Public tables no template and no line reads, each with the reason, for docs/analysis/tables.json. A table that is
# neither read nor named here is reported as "no template or watch line reads it yet", which is the plain truth of it.
NOT_WATCHED = {
    "an input of a table that is read: its rows reach the chooser through that table": [
        "ercot_dam_esr_awards", "caiso_curtailment_intervals", "eia930_all_storage", "iso_hub_prices_history", "isone_rtm_zone_prices_hourly",
        "ercot_storage_dam_offers_daily", "fred_daily_spot_prices", "ercot_as_quantities", "spp_as_quantities"],
    "a study of past events or a fitted model: it does not change from one week to the next": [
        "event_study_estimates", "flex_alert_effects", "flex_alert_model", "eia930_event_hourly_interchange", "caiso_dam_alert_day_hub_prices",
        "battery_stack_stress_daily", "noaa_isd_hourly", "eia930_all_history"],
    "yearly figures: there is no week or month to compare": [
        "ercot_peak_premium_annual", "interconnection_queue_summary", "eia930_demand_growth", "generation_mix_records", "hub_price_comparison"],
    "figures by hour of the day or by owner, not one series over time": [
        "caiso_curtailment_profile", "cost_of_power_hourly_profile", "generation_mix_hourly_profile", "storage_owners_monthly",
        "price_board_peak_offpeak"],
    "the latest values or a short rolling window only: too little past to rank a change against": [
        "eia930_generation_latest", "eia930_all_generation", "eia930_all_interchange", "grid_network_links", "grid_network_nodes",
        "iso_rt_top_intervals", "price_board_latest", "price_board_spreads", "weather_forecast_hourly", "weather_obs_hourly"],
    "EIA's daily sums, which can hold a faulty hour or an impossible day (the faults register): not watched until they are screened": [
        "eia930_daily_demand", "eia930_daily_interchange", "eia930_daily_total_interchange", "eia930_all_emissions"],
}
PERIOD_WORD = {"week": "week", "month": "month"}


def _as_list(v):
    return list(v) if isinstance(v, (list, tuple)) else [v]


def periods(df, spec, now=None):
    """The measure by period: a list of [label, value], oldest first, complete periods only. df: the table's rows
    (entity, variable, ts_utc as UTC timestamps, value). Nothing is filled: a period short of its rows is left out."""
    now = pd.Timestamp.now(tz="UTC") if now is None else now
    ents = _as_list(spec["entity"])
    d = df[df["entity"].isin(ents)]
    num_vars, den_vars = _as_list(spec["variable"]), _as_list(spec.get("over") or [])
    whole = list(spec.get("whole") or [])
    optional = set(spec.get("optional") or [])
    d = d[d["variable"].isin(num_vars + den_vars + whole)].dropna(subset=["value"])
    if d.empty:
        return []
    ts = d["ts_utc"]
    if spec["by"] == "week":
        start = (ts.dt.normalize() - pd.to_timedelta(ts.dt.weekday, unit="D"))
        d = d.assign(p=start)
        last_full = (now.normalize() - pd.to_timedelta(now.weekday(), unit="D"))  # this week's Monday: weeks before it have ended
        d = d[d["p"] < last_full]
        label = lambda p: f"{p.date()} to {(p + pd.Timedelta(days=6)).date()}"  # noqa: E731
        need = int(spec.get("need", 4 if spec["how"] != "last" else 1))
    else:
        d = d.assign(p=ts.dt.strftime("%Y-%m"))
        d = d[d["p"] < now.strftime("%Y-%m")]  # the month under way is not a month yet
        label = lambda p: p  # noqa: E731
        need = 1
    how = {"mean": "mean", "sum": "sum", "last": "last"}[spec["how"]]
    d = d.sort_values("ts_utc")
    g = d.groupby(["p", "variable", "entity"])["value"].agg([how, "size"]).reset_index()
    out = []
    for p, gp in g.groupby("p", sort=True):
        have = {(r["variable"], r["entity"]): (r[how], r["size"]) for r in gp.to_dict("records")}
        if whole:
            w = [have.get((v, ents[0])) for v in whole]
            if any(x is None for x in w) or w[0][0] != w[1][0]:
                continue
        def total(vs):
            got = [have.get((v, e)) for v in vs for e in ents if not (v in optional and (v, e) not in have)]
            if not got or any(x is None or x[1] < need for x in got):
                return None
            return float(sum(x[0] for x in got))
        num = total(num_vars)
        if num is None:
            continue
        if den_vars:
            den = total(den_vars)
            if not den:
                continue
            num = num / den * 100
        out.append([label(p), r2(num) if abs(num) < 1e6 else float(round(num))])
    return out


class WatchTemplate:
    """A line of WATCH with the attributes and methods the engine asks of a template module."""
    PUBLIC = True
    PARAMS = {}
    ABOUT = "system"

    def __init__(self, spec):
        self.spec = spec
        self.NAME, self.TITLE = spec["name"], spec["title"]
        self.TABLES = [spec["table"]]
        self.COMPARE = spec["compare"]
        ents, vs = _as_list(spec["entity"]), _as_list(spec["variable"])
        self.METHOD = (
            f"From the watch list (warehouse/analysis/watch.py). Table {spec['table']}, "
            f"{'entity' if len(ents) == 1 else 'entities, added up,'} {', '.join(ents)}; "
            f"{'variable' if len(vs) == 1 else 'variables, added up,'} {', '.join(vs)}"
            + (f", as a percent of {' + '.join(_as_list(spec['over']))}" if spec.get("over") else "")
            + (f" ({', '.join(spec['optional'])} counting as zero in a period with no row for it)" if spec.get("optional") else "")
            + f". One value a {spec['by']}: "
            + {"mean": "the mean of its rows", "sum": "the sum of its rows", "last": "its row"}[spec["how"]]
            + (f"; a week counts with at least {spec.get('need', 4 if spec['how'] != 'last' else 1)} rows" if spec["by"] == "week" else "")
            + (f"; a month counts only when {spec['whole'][0]} equals {spec['whole'][1]}" if spec.get("whole") else "")
            + ". The period under way is not shown. The headline is the newest complete period; it is compared with "
            + ("the period before it." if spec["compare"] == "previous" else "the same month a year earlier.")
            + " Nothing is filled or smoothed.")

    def compute(self, **_):
        spec = self.spec
        df = fetch(spec["table"])
        ps = periods(df, spec)
        if len(ps) < 3:
            raise NoData(f"{spec['table']}: {len(ps)} complete {spec['by']}s of {spec['name']}, 3 needed")
        return self.result(ps)

    def result(self, ps):
        spec = self.spec
        shown = ps[-SHOWN[spec["by"]]:]
        cur = ps[-1]
        frame = pd.DataFrame({"period": [p for p, _ in shown], "value": [v for _, v in shown], "unit": spec["unit"], "table": spec["table"]})
        chart = {"kind": "line", "x": [p[:10] if spec["by"] == "week" else p for p, _ in shown],
                 "x_label": "Week starting (Monday, UTC)" if spec["by"] == "week" else "Month", "y_label": spec["unit"],
                 "series": [{"name": spec["label"], "values": [v for _, v in shown]}]}
        lo, hi = min(ps, key=lambda x: x[1]), max(ps, key=lambda x: x[1])
        facts = [f"{spec['label']}, {cur[0]}: {cur[1]} {spec['unit']}.",
                 f"Over the {len(ps)} {spec['by']}s held, {ps[0][0]} to {cur[0]}, it ran from {lo[1]} ({lo[0]}) to {hi[1]} ({hi[0]}) {spec['unit']}."]
        return result(self.NAME, {}, spec["title"],
                      f"{spec['label']}, by {spec['by']}, {shown[0][0][:10] if spec['by'] == 'week' else shown[0][0]} to {cur[0][-10:] if spec['by'] == 'week' else cur[0]}",
                      frame, self.TABLES, chart,
                      {"label": spec["label"], "value": cur[1], "unit": spec["unit"], "period": cur[0], "history": ps[:-1]}, facts)

    def render(self, res, size, path=None):
        return render(res, size, path)


def tables():
    """Every table a line reads, as one regular expression for scripts/sync.py --tables."""
    return "^(" + "|".join(sorted({s["table"] for s in WATCH})) + ")$"


def load():
    names = [s["name"] for s in WATCH]
    if len(set(names)) != len(names):
        raise ValueError("watch.py: a name is used twice")
    return [WatchTemplate(s) for s in WATCH]


if __name__ == "__main__":
    if "--tables" in sys.argv:
        print(tables())
    else:
        for spec in WATCH:
            print(spec["name"], spec["table"], sep="\t")
