"""Ruling alternative 1 of Ask, the chat (session 7707, 17 November 2026, branch wip/alt-site-ask-1; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-site-ask-2026-11-17.md, line 1): may the chat
give Berkeley Lab's queue figures for a held grid's region (ISO-NE, NYISO, MISO), named as Berkeley Lab's, though the
grid's own table is "license needed"? On main it may. On this branch the held grids' regions are left out of that table:
rows in ISO-NE and NYISO are held (their own queues are license needed), rows in MISO are MISO's own (the pause), in both
loops (site/lib/chat/heldrows.ts REGION_HOLD and keepRows, lib/chat/tools.ts selects the region; warehouse/chat
license_hold.py region_held and tools.py). Pinned on rows made up here through the Python tool, through the site's
keepRows run by node, and on the local copy of the table where it is on the machine (warehouse/output, or the folder
ERW_TABLES_DIR names): the figures a reader is no longer given there (the impact file's, read on the live set, are ISO-NE
active 72 positions and 14,623.2 MW; NYISO active 190 and 27,119.2 MW; MISO active 1,646 and 350,124.6 MW).

    python -m unittest tests.test_alt_site_ask_1 -v
"""

import csv
import importlib.util
import json
import os
import subprocess
import unittest
from collections import defaultdict
from unittest import mock

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
TABLE = "lbnl_interconnection_queue"


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T = module("test_session1300_for_alt_site_ask_1", os.path.join(ROOT, "tests", "test_session1300.py"))
tools = T.tools
hold = tools.hold


def lbnl():
    """Berkeley Lab's queue as the tools hold it: made-up rows, one region each, no real row."""
    rows = [("ISO-NE", "active", 100.0), ("NYISO", "active", 200.0), ("MISO", "active", 300.0), ("PJM", "active", 400.0), ("ERCOT", "withdrawn", 50.0), ("PJM", "operational", 25.0)]
    return pd.DataFrame([{"entity_id": f"lbnl_queue:{i}", "entity_type": "generator", "name": "a request", "capacity_mw": mw, "status": s, "q_status": s,
                          "region": r, "status_date": pd.Timestamp("2024-01-01")} for i, (r, s, mw) in enumerate(rows)])


class Fixture:
    def __enter__(self):
        self.frames = T.Frames()
        self.frames.__enter__()
        self.frames.load()
        cov = tools._frames["_coverage"]
        tools._frames["_coverage"] = pd.concat([cov, pd.DataFrame([{**{c: None for c in cov.columns}, "table": TABLE, "source_report": "lbnl:queued_up", "license": "public",
                                                                    "tier": "raw", "sector": "power", "iso": "none", "interval": "snapshot", "n_rows": 6, "derived": "no"}])], ignore_index=True)
        tools._frames[TABLE] = lbnl()
        tools._frames.pop(("_held", TABLE), None)
        return self

    def __exit__(self, *exc):
        tools._frames.pop(("_held", TABLE), None)
        return self.frames.__exit__(*exc)


class TheRule(unittest.TestCase):
    def test_which_regions_are_held(self):
        self.assertEqual([hold.region_held(TABLE, r) for r in ("ISO-NE", "NYISO", "MISO", "PJM", "ERCOT", "", None)], ["held", "held", "paused", "", "", "", ""])
        self.assertEqual(hold.region_held("energy_projects", "ISO-NE"), "")

    def test_the_python_tool_leaves_the_regions_out(self):
        with Fixture(), mock.patch.dict(os.environ, {"ASK_HOLD": "on"}):
            got = tools.query(TABLE, "sum", where={"q_status": "active"})
            self.assertEqual(json.loads(json.dumps(got, default=str))["result"][0]["value"], 400.0)
            with self.assertRaises(tools.ToolError) as e:
                tools.query(TABLE, "sum", where={"region": "ISO-NE"})
            self.assertIn("license needed", str(e.exception))
            with self.assertRaises(tools.ToolError) as e:
                tools.query(TABLE, "sum", where={"region": "MISO"})
            self.assertIn("MISO is paused", str(e.exception))

    def test_the_python_tool_without_the_hold_gives_every_row(self):
        with Fixture(), mock.patch.dict(os.environ, {"ASK_HOLD": "off"}):
            got = tools.query(TABLE, "sum", where={"q_status": "active"})
            self.assertEqual(json.loads(json.dumps(got, default=str))["result"][0]["value"], 1000.0)

    def test_the_sites_keep_rows(self):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-site-ask-figures.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        self.assertEqual(json.loads(p.stdout), {"kept": ["PJM", "ERCOT"], "held": 2, "paused": 1, "fromExtra": {"kept": 0, "held": 1}})


@unittest.skipUnless(os.path.exists(os.path.join(TABLES, f"{TABLE}.csv")), "Berkeley Lab's table is not on this machine")
class OnTheTable(unittest.TestCase):
    def test_the_figures_no_longer_given(self):
        n, mw = defaultdict(int), defaultdict(float)
        with open(os.path.join(TABLES, f"{TABLE}.csv"), encoding="utf-8") as f:
            for r in csv.DictReader(line for line in f if not line.startswith("#")):
                if hold.region_held(TABLE, r["region"]):
                    n[(r["region"], r["q_status"])] += 1
                    mw[(r["region"], r["q_status"])] += float(r["capacity_mw"] or 0)
        got = {k: (n[k], round(mw[k], 1)) for k in (("ISO-NE", "active"), ("NYISO", "active"), ("MISO", "active"))}
        self.assertEqual(got, {("ISO-NE", "active"): (72, 14623.2), ("NYISO", "active"): (190, 27119.2), ("MISO", "active"): (1646, 350124.6)})


if __name__ == "__main__":
    unittest.main()
