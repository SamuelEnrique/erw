"""Audit of "What a datacenter pays", finding 8 (session 10203, docs/reviews/datacenter-model-audit-2026-11-26.md): in
California the page prices a load at a generator trading hub (TH_SP15_GEN-APND by default, TH_ZP26 and TH_NP15 beside
it). A load in CAISO settles at its utility's default load aggregation point (DLAP), not at a generator trading hub, and
no DLAP price is held in the page's files or in the warehouse. Decision 2 states that a hub or load zone stands for the
site; the gap between the hub and the price a California load pays is not measured.

This branch makes no fix: it needs a table (a data request in the audit's hand-back) and a fix would move figures. The
test shows that every CAISO region of the page's index is a generator trading hub and none is a load aggregation point."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class CaliforniaAtGeneratorHubs(unittest.TestCase):
    def test_every_caiso_region_is_a_generator_hub(self):
        with open(os.path.join(ROOT, "site", "data", "datacenter", "index.json"), encoding="utf-8") as f:
            idx = json.load(f)
        ids = [r["id"] for r in idx["grids"]["caiso"]["regions"]]
        self.assertTrue(ids)
        self.assertEqual(idx["grids"]["caiso"]["main"], "TH_SP15_GEN-APND")
        for i in ids:
            self.assertTrue(i.startswith("TH_") and i.endswith("_GEN-APND"), i)
            self.assertNotIn("DLAP", i)


if __name__ == "__main__":
    unittest.main()
