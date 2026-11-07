"""Session 2246 (chain 156): the datacenter tracker's charts, every figure keyed and traced
(site/lib/dcrollups.ts dcFigures, site/app/datacenters/DcCharts.tsx, scripts/check_datacenters.py).

check_datacenters.py recomputes each figure with its own Python and compares it with the page's functions run by node:
here on a small table, and on datacenter_facilities where this checkout holds it.
"""

import os
import shutil
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import check_datacenters as cd  # noqa: E402

COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator", "source",
        "source_url", "retrieved_at", "vintage", "state", "grid", "first_story_at", "power_kind"]


def table(rows):
    d = tempfile.mkdtemp(prefix="erw_s2246_")
    pd.DataFrame([{c: r.get(c, "") for c in COLS} for r in rows], columns=COLS).to_csv(os.path.join(d, "datacenter_facilities.csv"), index=False)
    return d


ROWS = [
    {"entity_id": "datacenter:1", "capacity_mw": "1200", "status": "planned", "operator": "Crusoe", "state": "TX", "first_story_at": "2026-02-01", "power_kind": "behind_the_meter_gas"},
    {"entity_id": "datacenter:2", "capacity_mw": "222", "status": "under_construction", "operator": "Fermi", "state": "TX", "grid": "ERCOT", "first_story_at": "2026-05-01"},
    {"entity_id": "datacenter:3", "capacity_mw": "", "status": "planned", "operator": "Meta", "state": "LA", "first_story_at": "2026-05-02"},
    {"entity_id": "datacenter:4", "capacity_mw": "2000", "status": "planned", "operator": "Meta", "state": "LA", "first_story_at": "2026-05-03", "power_kind": "gas"},
    {"entity_id": "datacenter:5", "capacity_mw": "900", "status": "withdrawn", "operator": "OpenAI", "state": "TX", "first_story_at": "2026-06-01"},
    {"entity_id": "datacenter:6", "capacity_mw": "50", "status": "operating", "operator": "Nebius", "state": "", "first_story_at": "2026-06-01"},
]


class TheTrace(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("node"):
            raise unittest.SkipTest("node is not on this machine")
        d = table(ROWS)
        t = pd.read_csv(os.path.join(d, "datacenter_facilities.csv"), dtype=str, keep_default_na=False)
        cls.page, cls.mine = cd.page_figures(t), cd.recompute(t)

    def test_every_figure_agrees(self):
        lines, bad = cd.compare(self.page, self.mine)
        self.assertEqual(bad, 0, "\n".join(x for x in lines if not x.startswith("ok")))

    def test_the_figures(self):
        m = self.mine
        self.assertEqual(m["dcchart|planned|2026-Q1|ERCOT"], 1200)
        self.assertEqual(m["dcchart|planned|2026-Q2|MISO"], 2000)
        self.assertEqual(m["dcchart|planned|2026-Q2|without"], 1)
        self.assertEqual(m["dcchart|operator|Meta|mw"], 2000)
        self.assertNotIn("dcchart|operator|OpenAI|mw", m)          # withdrawn: not counted
        self.assertNotIn("dcchart|operator|Nebius|mw", m)          # no US state: not counted
        self.assertEqual(m["dcchart|power|none|facilities"], 2)
        self.assertEqual(m["dcchart|power|gas|pct"], 25.0)


class TheWarehouse(unittest.TestCase):
    def test_the_stored_facilities_trace(self):
        if not os.path.exists(os.path.join(ROOT, "warehouse", "output", "datacenter_facilities.csv")) or not shutil.which("node"):
            raise unittest.SkipTest("datacenter_facilities or node is not on this machine")
        self.assertEqual(cd.main(["--quiet"]), 0)


class TheView(unittest.TestCase):
    def test_hovers_keys_and_colors(self):
        with open(os.path.join(ROOT, "site", "app", "datacenters", "DcCharts.tsx"), encoding="utf-8") as f:
            s = f.read()
        for k in ("dcchart|planned|", "dcchart|operator|", "dcchart|power|"):
            self.assertIn(k, s)
        self.assertGreaterEqual(s.count("<title>"), 2)
        self.assertIn('stroke="#FFFFFF" strokeWidth="1"', s)
        self.assertNotIn("—", s)


if __name__ == "__main__":
    unittest.main()
