"""The Python package reproduces ten figures of the site's pages from the same table and window (session 1012, chain 070).

Energy Research Warehouse (ERW), docs/methods/packages.md. Ten figures of the Grid tool's ERCOT page (five of its own,
two of the price board's tables it shows, one of the generation mix) and of the battery page, each with the check key
the page writes (check-values reads the same keys) and the value it showed (page_figures.json, recorded from a build in
the internal view). Each key is a value at a time (series|table|entity|variable|time), the largest value in a window
(series_max|table|variable|start|end|entity) or a sum over one (series_sum|...); the package fetches the table for
that entity, variable and window and computes the same. Remote: the live set for the tables it holds, local files for
the rest (a clone's, or ERW_DATA_DIR).

    ERW_REMOTE_TESTS=1 python -m pytest package/tests/test_page_figures.py -v -m remote

A figure whose time the backend no longer holds (the live set keeps 35 days of EIA-930) is skipped, and said so.
"""

import json
import math
import warnings
from pathlib import Path

import pandas as pd
import pytest

import erw

pytestmark = pytest.mark.remote
FIX = json.loads((Path(__file__).resolve().parent / "page_figures.json").read_text(encoding="utf-8"))


def compute(key, backend):
    p = key.split("|")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", erw.ERWLicenseWarning)
        if p[0] == "series":
            _, table, entity, variable, ts = p
            t = pd.Timestamp(ts)
            df = erw.fetch(table, entity=entity, variable=variable, start=t, end=t + pd.Timedelta(seconds=1), backend=backend)
            return None if df.empty else float(df["value"].iloc[0])
        _, table, variable, start, end, entity = p
        df = erw.fetch(table, entity=entity, variable=variable, start=start, end=end, backend=backend)
        if df.empty:
            return None
        return float(df["value"].max() if p[0] == "series_max" else df["value"].sum())


@pytest.mark.parametrize("fig", FIX["figures"], ids=[f["key"].split("|")[1] + ":" + f["key"].split("|")[0] for f in FIX["figures"]])
def test_the_package_reproduces_the_page(fig):
    got = compute(fig["key"], fig["backend"])
    if got is None:
        pytest.skip(f"{fig['backend']} no longer holds the time of {fig['key']}")
    want = float(fig["raw"])
    assert math.isclose(got, want, rel_tol=1e-9, abs_tol=1e-6), (fig["key"], got, want)
