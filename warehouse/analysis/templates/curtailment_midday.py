"""Curtailment against midday prices (CAISO)."""
import pandas as pd

from common import NoData, fetch, r2, render, result  # noqa: F401

NAME = "curtailment_midday"
TITLE = "Curtailment against midday prices"
PUBLIC = True
PARAMS = {"hub": {"default": "TH_SP15_GEN-APND", "choices": ["TH_SP15_GEN-APND", "TH_NP15_GEN-APND", "TH_ZP26_GEN-APND"]},
          "window": {"default": 30, "choices": [7, 30]}}
TABLES = ["caiso_curtailment_daily", "caiso_rtm_hub_prices"]
TZ = "America/Los_Angeles"
CURT = ["curtailed_solar_local_mwh", "curtailed_solar_system_mwh", "curtailed_wind_local_mwh", "curtailed_wind_system_mwh"]
METHOD = """CAISO only: it is the ISO that publishes curtailment with real-time prices in the warehouse (ERCOT's figure is
the ERW's estimate; SPP's real-time table is days old). For each day, wind and solar curtailed (CAISO's own figure: local
plus system, MWh, caiso_curtailment_daily) against the mean real-time price at the hub from 10:00 to 16:00 Pacific, when
solar output is highest (caiso_rtm_hub_prices, 15-minute means; the day counts only with all 24 of those intervals).
The chart is a scatter of the last `window` days that have both. The headline is the curtailment summed over the latest
7 days of the curtailment table; its history is the same sum for each earlier 7-day window since the table begins
(2022), so it is a long record even where prices are short."""


def compute(hub="TH_SP15_GEN-APND", window=30, history=True):
    c = fetch("caiso_curtailment_daily")
    c = c[c["variable"].isin(CURT)]
    daily = c.groupby(c["ts_utc"].dt.date)["value"].sum()
    daily = daily[daily.index <= max(daily.index)]
    p = fetch("caiso_rtm_hub_prices", node=hub)
    loc = p["ts_utc"].dt.tz_convert(TZ)
    mid = p[(loc.dt.hour >= 10) & (loc.dt.hour < 16)]
    g = mid.groupby(mid["ts_utc"].dt.tz_convert(TZ).dt.date)["value"]
    price = g.mean()[g.count() == 24]
    both = sorted(set(daily.index) & set(price.index))
    if len(both) < min(window, 7):
        raise NoData(f"{len(both)} days with both curtailment and midday prices")
    use = both[-window:]
    frame = pd.DataFrame({"day": [str(d) for d in use], "curtailed_mwh": [r2(daily[d]) for d in use],
                          "midday_price_usd_mwh": [r2(price[d]) for d in use], "hub": hub,
                          "tables": "caiso_curtailment_daily, caiso_rtm_hub_prices"})
    days = sorted(daily.index)
    hist = []
    for i in range(len(days) - 7, -1, -7):
        chunk = days[i:i + 7]
        if (pd.Timestamp(chunk[-1]) - pd.Timestamp(chunk[0])).days == 6:
            hist.append([f"{chunk[0]} to {chunk[-1]}", r2(daily.loc[chunk].sum())])
    hist = hist[::-1]
    cur = hist[-1]
    corr = pd.Series([daily[d] for d in use]).corr(pd.Series([price[d] for d in use]))
    top = max(use, key=lambda d: daily[d])
    chart = {"kind": "scatter", "x": [r2(daily[d]) for d in use], "x_label": "Wind and solar curtailed, MWh per day",
             "y_label": "Mean real-time price 10:00 to 16:00 Pacific, USD/MWh",
             "series": [{"name": hub, "values": [r2(price[d]) for d in use]}]}
    facts = [f"CAISO, {use[0]} to {use[-1]} ({len(use)} days): the most curtailment in a day was {r2(daily[top])} MWh on "
             f"{top}, when the mean midday real-time price at {hub} was {r2(price[top])} USD/MWh; the correlation of daily "
             f"curtailment with the midday price over these days was {r2(corr)}.",
             f"Wind and solar curtailed, {cur[0]}: {cur[1]} MWh."]
    return result(NAME, {"hub": hub, "window": window}, "CAISO: curtailment against midday prices",
                  f"Each point is a day, {use[0]} to {use[-1]}", frame, TABLES, chart,
                  {"label": "wind and solar curtailed, latest 7 days", "value": cur[1], "unit": "MWh", "period": cur[0],
                   "history": hist[:-1]}, facts)
