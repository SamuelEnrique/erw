"""Ruling alternative 6 of /shoulder (session 7703, 17 November 2026, branch wip/alt-shoulder-6; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-shoulder-2026-11-17.md, line 6): add a figure for
batteries of 2, 4 or 8 hours? On this branch warehouse/derived/shoulder_hours.py duration_metrics writes, for each month
with a fleet, d<D>_batteries_mw (the shoulder's MWh above the mean over D), d<D>_fleet_share (that over the fleet's MW) and
d<D>_hours_covered (the smaller of D and the shoulder's length), and the page draws them in a table under the headline
numbers. No figure that stands moves.

Pinned with the builder's function on the table's months, where shoulder_hours_monthly is on the machine (warehouse/output,
or the folder ERW_TABLES_DIR names), and with the page drawn on the table with those rows added
(site/scripts/alt-shoulder-draw.mjs): ERCOT, August 2026 (66,630 MWh over 5 hours, fleet 18,204 MW): 33,315 MW of 2-hour
batteries (1.83 times the fleet's MW, 2 of 5 hours), 16,657 MW of 4-hour (0.92, 4 of 5), 8,329 MW of 8-hour (0.46, 5 of 5);
California by EIA-930, November 2025 (36,217 MWh over 8 hours, 15,221 MW): 18,109, 9,054 and 4,527 MW (1.19, 0.59, 0.30).

    python -m unittest tests.test_alt_shoulder_6 -v
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import shoulder_hours as sh  # noqa: E402

TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
CSV = os.path.join(TABLES, "shoulder_hours_monthly.csv")


class TheRule(unittest.TestCase):
    def test_the_figures_of_a_month(self):
        got = sh.duration_metrics(5.0, 1000.0, 400.0)
        self.assertEqual((got["d2_batteries_mw"], got["d4_batteries_mw"], got["d8_batteries_mw"]), (500.0, 250.0, 125.0))
        self.assertEqual((got["d2_hours_covered"], got["d4_hours_covered"], got["d8_hours_covered"]), (2.0, 4.0, 5.0))
        self.assertEqual(got["d2_fleet_share"], 1.25)
        self.assertNotIn("d2_fleet_share", sh.duration_metrics(5.0, 1000.0, None))
        self.assertEqual(sh.duration_metrics(0, 0.0, 400.0), {})
        self.assertEqual((sh.unit_of("d4_batteries_mw"), sh.unit_of("d4_hours_covered"), sh.unit_of("d4_fleet_share")), ("MW", "hour", "ratio"))


def table():
    n = 0
    with open(CSV, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            n += 1
    return pd.read_csv(CSV, skiprows=n, dtype=str, keep_default_na=False)


@unittest.skipUnless(os.path.exists(CSV), "shoulder_hours_monthly is not on this machine")
class OnTheTable(unittest.TestCase):
    CASES = (("iso:ercot", "ercot", "2026-08"), ("iso:caiso", "caiso", "2025-11"))

    @classmethod
    def setUpClass(cls):
        t = table()
        cls.t = t
        cls.new = {}
        for entity, _, m in cls.CASES:
            val = lambda v: float(t[(t["entity"] == entity) & (t["variable"] == v) & (t["ts_utc"] == f"{m}-01T00:00:00Z")]["value"].iloc[0])
            cls.new[(entity, m)] = sh.duration_metrics(val("shoulder_hours"), val("shoulder_mwh_above_mean"), val("fleet_mw"))

    def test_the_builder_figures(self):
        e, c = self.new[("iso:ercot", "2026-08")], self.new[("iso:caiso", "2025-11")]
        self.assertEqual([round(e[f"d{d}_batteries_mw"]) for d in (2, 4, 8)], [33315, 16657, 8329])
        self.assertEqual([round(e[f"d{d}_fleet_share"], 2) for d in (2, 4, 8)], [1.83, 0.92, 0.46])
        self.assertEqual([e[f"d{d}_hours_covered"] for d in (2, 4, 8)], [2.0, 4.0, 5.0])
        self.assertEqual([round(c[f"d{d}_batteries_mw"]) for d in (2, 4, 8)], [18109, 9054, 4527])
        self.assertEqual([round(c[f"d{d}_fleet_share"], 2) for d in (2, 4, 8)], [1.19, 0.59, 0.30])
        self.assertEqual([c[f"d{d}_hours_covered"] for d in (2, 4, 8)], [2.0, 4.0, 8.0])

    def test_the_page_drawn_with_the_rows_added(self):
        t = self.t
        add = []
        for (entity, m), f in self.new.items():
            base = t[(t["entity"] == entity) & (t["ts_utc"] == f"{m}-01T00:00:00Z")].iloc[0].to_dict()
            add += [dict(base, variable=k, value=str(round(v, 4))) for k, v in f.items()]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "shoulder_hours_monthly.csv")
            pd.concat([t, pd.DataFrame(add)], ignore_index=True).to_csv(path, index=False)
            p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-shoulder-draw.mjs", path,
                                json.dumps([{"grid": g, "month": m} for _, g, m in self.CASES] + [{"grid": "ercot", "month": "2026-07"}])], cwd=SITE, capture_output=True, text=True, timeout=600)
        self.assertEqual(p.returncode, 0, p.stderr[-2000:])
        e, c, other = json.loads(p.stdout)
        self.assertIn("by-duration=2026-08", e["marks"])
        self.assertIn("2 hours 33,314.94 MW 1.83 times 2 of 5 4 hours 16,657.47 MW 0.92 times 4 of 5 8 hours 8,328.74 MW 0.46 times 5 of 5", e["text"])
        self.assertIn("by-duration=2025-11", c["marks"])
        self.assertIn("8 hours 4,527.16 MW 0.30 times 8 of 8", c["text"])
        self.assertFalse(any(x.startswith("by-duration") for x in other["marks"]))                      # a month without the rows draws no table
        self.assertIn("they would need 3.66 hours on the average day", e["summary"])                    # no figure that stands moves


if __name__ == "__main__":
    unittest.main()
