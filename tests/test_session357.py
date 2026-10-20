"""Session 357: the price years, each economics page's figure under every window of years held.

Energy Research Warehouse (ERW). warehouse/derived/price_years.py hands the battery's rows to
site/scripts/price-years.mjs, which runs the pages' own modules (lib/batterystack.ts, lib/merchant.ts with
lib/seller2.ts, lib/datacenter.ts). These tests run that script on the committed files alone (SPP: the battery's
review snapshot, the generator's snapshot and the datacenter's year files), so no live set and no key is needed, and
hold:

  1. every window the note names is there, and the last twelve months equal the page's own figure (the proofs);
  2. a calendar year held in part says so, and the averages are written only over full years;
  3. the driver's frame: the variable, ts_utc, freq and x_ columns of docs/methods/price_years.md, no duplicate key;
  4. the note's shape section, the live-set rule and the coverage rule.

    python -m unittest tests.test_session357 -v
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import price_years as P  # noqa: E402

NODE = shutil.which("node")


def spp_battery():
    with open(os.path.join(SITE, "data", "battery_stack_review.json"), encoding="utf-8") as f:
        g = json.load(f)["grids"]["spp"]
    return dict(entity=g["entity"], node="SPPNORTH_HUB", rows=[dict(variable=v, ts_utc=t, value=x) for v, t, x in g["rows"]], stress=[])


@unittest.skipUnless(NODE and os.path.isdir(os.path.join(SITE, "node_modules")), "node and the site's packages are needed")
class TestPagesCode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="erw357_")
        src, dst = os.path.join(cls.tmp, "in.json"), os.path.join(cls.tmp, "out.json")
        with open(src, "w", encoding="utf-8") as f:
            json.dump(dict(grids=["spp"], battery=dict(spp=spp_battery()), events={}), f)
        r = subprocess.run([NODE, "--import", "./scripts/alias-register.mjs", "scripts/price-years.mjs", src, dst], cwd=SITE,
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
        if r.returncode != 0:
            raise AssertionError(r.stderr[-800:])
        with open(dst, encoding="utf-8") as f:
            cls.res = json.load(f)
        cls.s = P.frame(cls.res, "2026-10-20T00:00:00Z")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_proofs_equal_the_pages(self):
        lines = P.prove(self.s, self.res, log=lambda *_: None)
        self.assertTrue(lines)
        tools = {p["tool"] for p in self.res["proofs"]}
        self.assertEqual(tools, {"battery", "generator", "datacenter"})

    def test_the_windows(self):
        b = self.s[(self.s.x_tool == "battery") & (self.s.x_config == "foresight_4h")]
        self.assertEqual(set(b.x_window_kind), {"year", "last_12", "all"})  # SPP held from September 2024: no full three years
        y24 = b[b.x_window == "year_2024"].iloc[0]
        self.assertEqual((y24.x_complete, y24.x_months, y24.x_from), ("false", 4, "2024-09"))
        d = self.s[(self.s.x_tool == "datacenter") & (self.s.node == "SPPSOUTH_HUB") & (self.s.x_config == "flat_da")]
        self.assertIn("avg_7y", set(d.x_window))  # SPP South's day-ahead prices from 2019: seven full years
        rt = self.s[(self.s.x_tool == "datacenter") & (self.s.node == "SPPNORTH_HUB") & (self.s.x_config == "flat_rt")]
        self.assertNotIn("avg_3y", set(rt.x_window))  # real time from September 2024: no three full years, no row
        a7 = d[d.x_window == "avg_7y"].iloc[0]
        self.assertEqual((a7.x_from, a7.x_to, a7.x_months, a7.freq), ("2019-01", "2025-12", 84, "P84M"))
        g = self.s[(self.s.x_tool == "generator") & (self.s.x_config == "solar")]
        self.assertTrue({"last_12", "all"} <= set(g.x_window))
        self.assertFalse(any(g.x_window_kind == "all_less"))  # the snapshot holds daily figures for ERCOT's events only

    def test_the_frame(self):
        s = self.s
        self.assertEqual(list(s.columns), P.COLS)
        self.assertFalse(s.duplicated(["entity", "variable", "ts_utc"]).any())
        r = s[(s.x_tool == "battery") & (s.x_window == "last_12") & (s.x_config == "dayahead_2h")].iloc[0]
        self.assertEqual(r.variable, "battery_dayahead_2h_last_12")
        self.assertEqual(r.ts_utc, f"{r.x_from}-01T00:00:00Z")
        self.assertEqual((r.unit, r.freq, r.x_left_out, r.market), ("USD/kW-year", "P12M", "none", "spp"))
        self.assertEqual(set(s[s.x_tool == "datacenter"].unit), {"USD/MWh"})


class TestShapeAndRules(unittest.TestCase):
    def test_note_and_rules(self):
        with open(os.path.join(ROOT, "docs", "methods", "price_years.md"), encoding="utf-8") as f:
            note = f.read()
        self.assertIn("## The table's shape (written before the table, for the code machine)", note)
        for c in P.X_COLS:
            self.assertIn(f"`{c}`", note)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            live = f.read()
        self.assertIn("'^price_years_by_window$'", live)
        with open(os.path.join(ROOT, "warehouse", "metadata", "build_coverage.py"), encoding="utf-8") as f:
            self.assertIn("price_years_by_window", f.read())
        self.assertNotIn("—", note)

    def test_public_grids_only(self):
        self.assertEqual(P.GRIDS, ["ercot", "caiso", "spp"])


if __name__ == "__main__":
    unittest.main()
