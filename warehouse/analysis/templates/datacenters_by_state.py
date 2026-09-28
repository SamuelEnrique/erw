"""Datacenter facilities by state."""
import pandas as pd

from common import fetch, render, result  # noqa: F401

NAME = "datacenters_by_state"
TITLE = "Datacenter facilities by state"
PUBLIC = True
PARAMS = {"top": {"default": 15, "choices": [10, 15, 25]}}
TABLES = ["datacenter_facilities"]
METHOD = """The facilities in datacenter_facilities (docs/methods/datacenter_facilities.md: news facilities, nine
operators' own site lists and ISO queue positions that name a datacenter, deduplicated by operator plus location),
counted by stated US state and by the kind of source, for the `top` states with the most; a facility with no stated
state is not counted. It is the ERW's scope, not a census of every datacenter. The headline is the number of
facilities with a stated state, what the chart shows; the table is a snapshot, so the headline's history is the value
each earlier weekly run stored (docs/analysis/history.csv), and the template becomes eligible for the chart of the week
after 8 weekly runs."""


def compute(top=15, history=True):
    d = fetch("datacenter_facilities")
    s = d[d["state"].astype(str).str.len() == 2]
    ct = s.groupby(["state", "kind"]).size().unstack(fill_value=0)
    order = ct.sum(axis=1).sort_values(ascending=False).index[:top].tolist()
    kinds = [k for k in ("operator", "news", "queue") if k in ct.columns]
    frame = ct.loc[order, kinds].reset_index().melt(id_vars="state", var_name="kind", value_name="facilities")
    frame["table"] = "datacenter_facilities"
    # the headline is what the chart shows: facilities with a stated US state. The table is a snapshot, so its
    # history is only what earlier weekly runs stored in docs/analysis/history.csv (none in the data itself)
    now = pd.Timestamp.now(tz="UTC")
    cur = [f"{now:%Y-%m-%d}", int(len(s))]
    hist = []
    tot = ct.sum(axis=1)
    chart = {"kind": "bar", "stacked": True, "x": order, "x_label": "State", "y_label": "Facilities",
             "series": [{"name": k, "values": [int(ct.loc[s_, k]) for s_ in order]} for k in kinds]}
    facts = [f"Of {len(d)} datacenter facilities in the table, {len(s)} state a US state; {order[0]} has the most, "
             f"{int(tot[order[0]])}, then {order[1]} with {int(tot[order[1]])} and {order[2]} with {int(tot[order[2]])}.",
             f"Facilities with a stated US state on {cur[0]}: {cur[1]}."]
    return result(NAME, {"top": top}, "Where the ERW's datacenter facilities are",
                  f"Facilities by stated state and source, the {top} states with the most", frame, TABLES, chart,
                  {"label": "facilities with a stated US state", "value": cur[1], "unit": "facilities",
                   "period": cur[0], "history": hist[:-1]}, facts)
