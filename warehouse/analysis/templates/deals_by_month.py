"""Energy deals by month and type."""
import pandas as pd

from common import NoData, fetch, render, result  # noqa: F401

NAME = "deals_by_month"
TITLE = "Deals by month and type"
PUBLIC = True
ABOUT = "coverage"  # session 119: a count of what the ERW itself has collected, not a measurement of the energy system: run and shown, never the chart of the week
PARAMS = {"months": {"default": 12, "choices": [6, 12]}, "ai_power": {"default": "all", "choices": ["all", "ai_power"]}}
TABLES = ["energy_deals"]
TYPES = ["m_and_a", "fuel_supply", "equity_raise", "debt", "project_finance", "ppa", "offtake", "joint_venture"]
METHOD = """The deals in energy_deals (extracted from scored news by warehouse/deals/extract.py, every number checked
against its story) counted by the calendar month of their event date (UTC) and deal type; types outside the eight most
common are counted as other. With ai_power, only the deals tagged as AI-power deals. A month counts once it has ended.
The counts follow the news the warehouse has scored, so they measure reported deals, not all deals, and a month whose
backfill was not scored in full is low. The headline is the count in the latest ended month; its history is every
earlier month since the table begins."""


def compute(months=12, ai_power="all", history=True):
    d = fetch("energy_deals")
    if ai_power == "ai_power":
        d = d[d["ai_power"].astype(str).str.lower().isin(["true", "1", "yes"])]
    t = pd.to_datetime(d["event_date"], utc=True, format="ISO8601")
    d = d.assign(month=t.dt.strftime("%Y-%m"), kind=d["deal_type"].where(d["deal_type"].isin(TYPES), "other"))
    now = pd.Timestamp.now(tz="UTC").strftime("%Y-%m")
    d = d[d["month"] < now]
    if d.empty:
        raise NoData("energy_deals: no deal in an ended month")
    first, last = d["month"].min(), d["month"].max()
    allm = pd.period_range(first, last, freq="M").strftime("%Y-%m").tolist()
    use = allm[-months:]
    ct = d.groupby(["month", "kind"]).size().unstack(fill_value=0).reindex(allm, fill_value=0)
    kinds = [k for k in TYPES + ["other"] if k in ct.columns]
    frame = ct.loc[use, kinds].reset_index().melt(id_vars="month", var_name="deal_type", value_name="deals")
    frame["table"] = "energy_deals"
    totals = ct.sum(axis=1)
    hist = [[m, int(totals[m])] for m in allm]
    cur = hist[-1]
    top = max(use, key=lambda m: totals[m])
    lead = ct.loc[use, kinds].sum().idxmax()
    chart = {"kind": "bar", "stacked": True, "x": use, "x_label": "Month (UTC)", "y_label": "Deals",
             "series": [{"name": k.replace("_", " "), "values": [int(ct.loc[m, k]) for m in use]} for k in kinds]}
    facts = [f"From {use[0]} to {use[-1]}, the most deals in a month were {int(totals[top])} in {top}; the most common type "
             f"was {lead.replace('_', ' ')}, with {int(ct.loc[use, lead].sum())}.",
             f"Deals in {cur[0]}: {cur[1]}."]
    title = "Energy deals in the news, by month" + (" (AI power)" if ai_power == "ai_power" else "")
    return result(NAME, {"months": months, "ai_power": ai_power}, title,
                  f"Deals by the month of their event date and type, {use[0]} to {use[-1]}", frame, TABLES, chart,
                  {"label": "deals in the latest ended month", "value": cur[1], "unit": "deals", "period": cur[0],
                   "history": hist[:-1]}, facts)
