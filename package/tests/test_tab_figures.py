"""The Python package reproduces four figures of the All grids tab of /cost-of-power from the tables its files were
built from, and names the fifth it cannot (session 1032, chain 071).

Energy Research Warehouse (ERW), docs/methods/packages.md. tab_figures.json holds each figure's check key, the value the
page showed and how it is computed; the package fetches the tables with the local backend (ERW_DATA_DIR, a directory
holding ercot_all_hub_prices_history, iso_dam_hub_prices, node_basis_daily and eia930_subba_demand_hourly_2024 and
_2025) and computes the same. A table not in the directory skips its figure, and says so.

    ERW_DATA_DIR=<dir> python -m pytest package/tests/test_tab_figures.py -v

No request: the local backend reads files. The fifth figure, the second card's all-in, rests on an internal table; the
test checks that the package's license record holds it.
"""

import json
import math
import os
import warnings
from pathlib import Path

import pandas as pd
import pytest

import erw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FIX = json.loads((HERE / "tab_figures.json").read_text(encoding="utf-8"))
FIG = {f["key"]: f for f in FIX["figures"]}


def need(*tables):
    d = os.environ.get("ERW_DATA_DIR")
    missing = [t for t in tables if not (d and (Path(d) / f"{t}.csv").exists())]
    if missing:
        pytest.skip(f"not in ERW_DATA_DIR: {', '.join(missing)}")


def fetch(table, **kw):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", erw.ERWLicenseWarning)
        return erw.fetch(table, backend="local", **kw)


def node_window():
    n = json.loads((ROOT / "site" / "data" / "siting" / "nodes.json").read_text(encoding="utf-8"))
    start = pd.Timestamp(f"{n['pct_from']}-01", tz="UTC")
    end = (pd.Period(n["pct_to"], "M") + 1).to_timestamp().tz_localize("UTC")
    return start, end


def quantile(xs, q):
    """The linear-interpolation quantile pandas uses by default, as the replication computes it."""
    xs = sorted(xs)
    pos = (len(xs) - 1) * q
    lo = math.floor(pos)
    hi = min(lo + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def test_the_hub_s_day_ahead_price():
    f = FIG["allgrids|energy|ercot:HB_HUBAVG|da"]
    need(*f["tables"])
    hours = {}
    for t in f["tables"]:                                   # the first table that holds an hour keeps it
        df = fetch(t, entity=f["entity"], variable=f["variable"], start=f["start"], end=f["end"])
        for ts, v in zip(df["ts_utc"].astype(str), df["value"]):
            hours.setdefault(ts, float(v))
    assert len(hours) == f["hours"]
    assert math.isclose(sum(hours.values()) / len(hours), f["raw"], abs_tol=5e-7)


def test_the_node_s_basis_spread():
    f = FIG["allgrids|nodespread|ercot:7RNCHSLR_ALL"]
    need(*f["tables"])
    start, end = node_window()
    xs = fetch("node_basis_daily", entity=f["entity"], variable=f["variable"], start=start, end=end)["value"].dropna().astype(float).tolist()
    got = round(quantile(xs, 0.9), 4) - round(quantile(xs, 0.1), 4)
    assert math.isclose(got, f["raw"], abs_tol=5e-7)


def test_the_node_s_intraday_swing():
    f = FIG["allgrids|nodeswing|ercot:7RNCHSLR_ALL"]
    need(*f["tables"])
    start, end = node_window()
    xs = fetch("node_basis_daily", entity=f["entity"], variable=f["variable"], start=start, end=end)["value"].dropna().astype(float)
    assert math.isclose(round(float(xs.mean()), 4), f["raw"], abs_tol=5e-7)


def test_the_zone_s_demand_growth():
    f = FIG["allgrids|zonegrowth|nyiso:N.Y.C."]
    need(*f["tables"])
    m = {t[-4:]: float(fetch(t, entity=f["entity"], variable=f["variable"])["value"].dropna().astype(float).mean()) for t in f["tables"]}
    assert math.isclose(round(100 * (m["2025"] / m["2024"] - 1), 4), f["raw"], abs_tol=5e-7)


def test_the_card_s_all_in_rests_on_a_held_table():
    (f,) = FIX["not_reproduced"]
    lic = erw.license(f["held_table"])
    assert lic["verdict"] == "internal", lic
