"""wip/ready-grid-screen (session 11406, chain 770, part C): the other choice of the Grid tool audit of 26 November,
finding 6 (docs/reviews/grid-model-audit-2026-11-26.md), readied for Samuel's ruling, not requested.

On main the network snapshot (warehouse/derived/grid_network.py, daily; network_hourly.py, hourly) takes every
interchange report as filed. On this branch a report above 20,000 MW (SCREEN_MW), which no single tie carries, is set
aside before the pair rule, so the hour is read from the other BA's report. In the table's seven weeks the audit read
(13 September to 3 November 2026) two reports exceed it, SPP's of its MISO tie on 4 and 6 October; the pair rule
reads MISO's report of that tie, so no figure on the page moves (before and after the same). The audit's own test
(tests/test_audit_grid_6.py on wip/audit-grid-6) is carried, turned round."""
import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DERIVED = os.path.join(ROOT, "warehouse", "derived")
sys.path.insert(0, DERIVED)
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))


class TheScreen(unittest.TestCase):
    def test_both_builders_screen(self):
        for name in ("grid_network.py", "network_hourly.py"):
            with open(os.path.join(DERIVED, name), encoding="utf-8") as f:
                t = f.read()
            self.assertIn("SCREEN_MW = 20000", t, name)
        with open(os.path.join(DERIVED, "grid_network.py"), encoding="utf-8") as f:
            self.assertIn('x = x[x["value"].abs() <= SCREEN_MW]', f.read())

    def test_an_impossible_report_gives_way_to_the_other_side(self):
        try:
            import network_hourly as nh
        except Exception as exc:  # the builder imports the connectors' library
            self.skipTest(f"network_hourly does not import here: {exc}")
        rows = [{"period": "2026-10-04T12", "fromba": "MISO", "toba": "SWPP", "value": 1200},
                {"period": "2026-10-04T12", "fromba": "SWPP", "toba": "MISO", "value": 45000},    # SPP files an impossible figure
                {"period": "2026-10-04T13", "fromba": "SWPP", "toba": "MISO", "value": -30000}]   # and is the only report of the hour
        flows, _ = nh.pair_flows(rows, {"MISO", "SWPP"})
        self.assertEqual(flows[("MISO", "SWPP")], {"2026-10-04T11:00:00Z": 1200.0})           # MISO's report; the second hour not held
        rows[0]["value"] = None
        flows, _ = nh.pair_flows(rows, {"MISO", "SWPP"})
        self.assertNotIn(("MISO", "SWPP"), flows)

    def test_the_note_says_it(self):
        with open(os.path.join(ROOT, "docs", "methods", "grid_network.md"), encoding="utf-8") as f:
            self.assertIn("a report above 20,000 MW, which no single tie carries, is set aside first", f.read())


if __name__ == "__main__":
    unittest.main()
