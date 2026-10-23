"""The three backends give the same rows where they hold the same window (session 1001, chain 070).

Energy Research Warehouse (ERW), docs/methods/packages.md. Five public tables, each kept whole in the live set and in
the Stanford dataset's draft (one entities, one events, three series), fetched through fetch(..., backend=) from local
files, the live set (its REST address, anon key) and Redivis (`datapages.erw:b9wm`, the draft, version="next": the
latest release, v1.0, holds only the starter table until the ERW's first full release is clicked). For each pair of
backends: the rows each holds, the rows both hold by the table's key, and the rows among those whose values differ:
in the newest 92 days of the table's own time (a publisher revises its recent months, and each backend is as new as its
last load), counted; before them, none. A number is compared as a number (a CSV's "1200.0" is "1200" elsewhere).
The counts are written to package/tests/three_backends.json, so a session can report them.

    ERW_REMOTE_TESTS=1 python -m pytest package/tests/test_backends_three.py -v -m remote

The machine's own tables are read from ERW_DATA_DIR (or the clone's warehouse/output); each backend's copy is as new as
its last load, so a row one holds and another does not is counted, not failed.
"""

import json
from pathlib import Path

import pandas as pd
import pytest

import erw

pytestmark = pytest.mark.remote

FIVE = {
    "eia860m_retired_generators": ({}, ["entity_id"]),
    "caiso_grid_emergencies": ({}, ["event_id"]),
    "carbon_intensity_monthly": ({}, ["entity", "variable", "ts_utc"]),
    "ercot_peak_premium_annual": ({}, ["entity", "variable", "ts_utc"]),
    "eia_fuel_spot_prices": ({"entity": "eia:henry_hub", "start": "2025-01-01", "end": "2026-01-01"},
                             ["entity", "variable", "ts_utc"]),
}
OUT = Path(__file__).resolve().parent / "three_backends.json"


@pytest.fixture(scope="module")
def backends():
    erw.requests(reset=True)
    made = {}
    try:
        made["local"] = erw.LocalBackend()
        made["live"] = erw.LiveBackend()
        made["redivis"] = erw.RedivisBackend(version="next")
    except Exception as exc:
        pytest.skip(f"a backend is not readable here: {type(exc).__name__}: {str(exc)[:200]}")
    yield made
    erw.set_backend()


def _frame(b, name, kw):
    erw.set_backend(b)
    df = erw.fetch(name, **kw)
    return df


def _cell(v: str) -> str:
    """A number as a number ("1200.0" in a CSV is "1200" in the live set and Redivis), anything else as written."""
    try:
        return repr(float(v))
    except ValueError:
        return v


RECENT = pd.Timedelta(days=92)


def _compare(a: pd.DataFrame, b: pd.DataFrame, key):
    """Rows each holds, rows both hold by the key, and among those the rows whose values differ: in the newest 92 days
    of the table's own time (a publisher revises its recent months, and each backend is as new as its last load), and
    before them (a fault, which must be none)."""
    cols = [c for c in a.columns if c in b.columns and c not in ("retrieved_at", "vintage", "source_url")]
    x = a[cols].astype(str).map(_cell).set_index(key)
    y = b[cols].astype(str).map(_cell).set_index(key)
    common = x.index.intersection(y.index)
    xs, ys = x.loc[common].sort_index(), y.loc[common].sort_index()
    bad = (xs != ys).any(axis=1) if len(common) else pd.Series(dtype=bool)
    recent = 0
    if "ts_utc" in key and len(common):
        t = pd.to_datetime(xs.index.get_level_values("ts_utc"), utc=True)
        newest = max(a["ts_utc"].max(), b["ts_utc"].max())
        is_recent = pd.Series(t >= newest - RECENT, index=xs.index)
        recent = int((bad & is_recent).sum())
    return {"left": len(x), "right": len(y), "both": len(common), "differ_recent": recent,
            "differ_before": int(bad.sum()) - recent}


def test_the_three_backends_agree(backends):
    record = {}
    for name, (kw, key) in FIVE.items():
        frames = {k: _frame(b, name, kw) for k, b in backends.items()}
        record[name] = {"rows": {k: len(f) for k, f in frames.items()},
                        "version_lines": {k: f.attrs["erw"]["version_line"] for k, f in frames.items()}}
        for left, right in (("local", "live"), ("local", "redivis"), ("live", "redivis")):
            record[name][f"{left}|{right}"] = _compare(frames[left], frames[right], key)
    record["_requests"] = erw.requests()
    OUT.write_text(json.dumps(record, indent=2, default=str), encoding="utf-8")
    for name in FIVE:
        for pair in ("local|live", "local|redivis", "live|redivis"):
            c = record[name][pair]
            assert c["both"] > 0, (name, pair, c)
            assert c["differ_before"] == 0, (name, pair, c)
