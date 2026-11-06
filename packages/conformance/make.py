#!/usr/bin/env python3
"""Session 1006 (chain 070): the conformance file of the three packages, made once from the Python package.

Energy Research Warehouse (ERW), docs/methods/packages.md. Twenty calls with the answers the Python package gave on
the live set (anon key): ten fetches (rows, first and last time), four citations (the words before the clause that
says where the rows came from), three licenses (verdict and words), one refusal of a held table (its exact words), one
standard (shape and key) and the table list of the record (one table's row; at least 299 tables). Each package's runner (run_python.py,
run_stata.do, run_r.R) makes the same calls and compares. The live set's address and key come from the environment
and are not written.

    python packages/conformance/make.py          writes packages/conformance/conformance.json
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "package" / "src"))

import erw  # noqa: E402

FETCH = [
    {"table": "eia_fuel_spot_prices", "entity": ["eia:henry_hub"], "start": "2025-01-01", "end": "2026-01-01"},
    {"table": "eia_fuel_spot_prices", "entity": ["eia:wti_cushing", "eia:brent"], "start": "2026-09-01", "end": "2026-10-01"},
    {"table": "carbon_intensity_monthly", "entity": ["eia930:CISO"], "variable": ["intensity_demand"]},
    {"table": "ercot_peak_premium_annual", "entity": ["HB_HUBAVG"], "end": "2026-01-01"},
    {"table": "caiso_grid_emergencies", "start": "2022-09-01", "end": "2022-09-15"},
    {"table": "eia860m_retired_generators", "variable": ["generator"]},
    # session 1055 (chain 072): call 7 was eia930_all_demand on 18 October, which leaves the live set's 35 days about 22
    # November; the hourly intensity of the same hours is kept 430 days (live_set.yaml), so the file holds until 2027
    {"table": "carbon_intensity_hourly", "entity": ["eia930:ERCO"], "variable": ["intensity_demand"], "start": "2026-10-18", "end": "2026-10-19"},
    {"table": "state_generation_mix_monthly", "entity": ["eia:TX"], "start": "2025-01-01", "end": "2026-01-01"},
    {"table": "iso_curtailment_monthly", "start": "2025-01-01", "end": "2026-01-01"},
    {"table": "carbon_intensity_daily", "entity": ["eia930:ERCO"], "start": "2026-10-01", "end": "2026-10-08"},
]
CITE = ["eia_fuel_spot_prices", "carbon_intensity_monthly", "eia860m_retired_generators", "caiso_grid_emergencies"]
LICENSE = ["eia_fuel_spot_prices", "iso_rtm_hub_prices", "pjm_rpm_capacity_prices"]
HELD = "iso_rtm_hub_prices"
VIA = " Via the Energy Research Warehouse (ERW), table "


def stamp(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    erw.requests(reset=True)
    erw.set_backend(erw.LiveBackend())
    calls = []
    for i, c in enumerate(FETCH, 1):
        kw = {k: v for k, v in c.items() if k != "table"}
        df = erw.fetch(c["table"], **kw)
        t = df["event_date"] if "event_date" in df else (df["ts_utc"] if "ts_utc" in df else df["status_date"])
        calls.append({"n": i, "call": "fetch", "args": c,
                      "expect": {"rows": len(df), "first": stamp(t.min()) if len(df) else "",
                                 "last": stamp(t.max()) if len(df) else ""}})
    for t in CITE:
        c = erw.cite(t)
        calls.append({"n": len(calls) + 1, "call": "cite", "args": {"table": t},
                      "expect": {"before_clause": c.split(", the live set, fetched")[0] + ","}})
    for t in LICENSE:
        lic = erw.license(t)
        calls.append({"n": len(calls) + 1, "call": "license", "args": {"table": t},
                      "expect": {"verdict": lic["verdict"], "words": lic["words"]}})
    try:
        erw.fetch(HELD, start="2026-10-20")
        refused = ""
    except erw.ERWLicenseHeld as e:
        refused = str(e)
    calls.append({"n": len(calls) + 1, "call": "refusal", "args": {"table": HELD, "backend": "live"},
                  "expect": {"message": refused}})
    s = erw.standard("eia860m_retired_generators")
    calls.append({"n": len(calls) + 1, "call": "standard", "args": {"table": "eia860m_retired_generators"},
                  "expect": {"shape": s["shape"], "key": s["key"]}})
    # the record (coverage.csv), as the Stata and R packages read it: one table's row, and a floor for the count (the
    # record grows; a count would fail at each new table)
    t = erw.tables(backend="local").set_index("table").loc["eia_fuel_spot_prices"]
    calls.append({"n": len(calls) + 1, "call": "tables", "args": {"backend": "local", "table": "eia_fuel_spot_prices"},
                  "expect": {"shape": t["shape"], "verdict": t["verdict"], "in_live": t["in_live"], "at_least": 299}})
    out = {"made_by": "session 1003's fixtures' calls and session 1006 (chain 070), the Python package on the live set; version 2, session 1055 (chain 072): call 7 on a table the live set keeps 430 days",
           "made_at": stamp(__import__("pandas").Timestamp.now(tz="UTC")), "via": VIA.strip(),
           "calls": calls, "requests": erw.requests()}
    # session 1055 (chain 072): the errors block (session 1013's sentences, which the runners read) is carried over from
    # the file as it stands; this script does not make it, and a remake that dropped it lost them once
    old = HERE / "conformance.json"
    if old.exists() and "errors" in json.loads(old.read_text(encoding="utf-8")):
        out["errors"] = json.loads(old.read_text(encoding="utf-8"))["errors"]
    (HERE / "conformance.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(calls)} calls written; requests {erw.requests()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
