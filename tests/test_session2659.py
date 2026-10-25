"""Session 2659: the Agency on Statistics of Tajikistan's table of electricity output, trade and consumption, 1991 to 2025.

Energy Research Warehouse (ERW). Tests warehouse/connectors/stat_tj_tajikistan_electricity.py on rows built here (made up for
the test, not the Agency's): each row given its item and variable and stated in MWh, a dash not written, the "of which" lines
skipped; a missing title or unit line, years not a run from 1991, a row not in the map, a row missing, a negative output and
hydro and thermal power far from the output stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2659 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import stat_tj_tajikistan_electricity as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": ""}
LABELS = ["Output", "  of which:", "  Hydropower", "  Thermal power", "Imports", "Exports", "Total internal consumption (by sector)",
          "  Industry", "  Construction", "  Agriculture", "  Transport", "  Other sectors", "  Households", "  Losses", "  Discrepancy"]


def sheet(years=(1991, 1992), output=(10.0, 11.0), thermal=(1.0, " -"), extra=None, drop=None, title=None, unit=None):
    rows = [(title or "Electricity output, trade and consumption, 1991" + chr(0x2013) + "2025", None, None),
            (unit or "in billions of kilowatt hours", None, None), (None,) + tuple(years)]
    vals = {"Output": output, "  Hydropower": (9.0, 11.0), "  Thermal power": thermal, "  of which:": (" ", " ")}
    for lab in LABELS:
        if lab == drop:
            continue
        rows.append((lab,) + tuple(vals.get(lab, (0.5, -0.1 if "Discrepancy" in lab else 0.4))))
    if extra:
        rows.append(extra)
    return rows


class Parse(unittest.TestCase):
    def test_rows(self):
        t = A.frame(A.parse_rows(sheet()), BASE)
        r = {(e, s[:4]): (v, x) for e, s, v, x in zip(t.entity, t.ts_utc, t.variable, t.value)}
        self.assertEqual(r[("tajstat:tj:output", "1992")], ("generation", 11000000.0))
        self.assertEqual(r[("tajstat:tj:hydro", "1991")], ("generation", 9000000.0))
        self.assertEqual(r[("tajstat:tj:losses", "1991")], ("distribution_losses", 500000.0))
        self.assertEqual(r[("tajstat:tj:discrepancy", "1992")], ("statistical_difference", -100000.0))
        self.assertNotIn(("tajstat:tj:thermal", "1992"), r)
        self.assertEqual(len(t), 14 * 2 - 1)
        self.assertEqual(set(t.node[t.entity == "tajstat:tj:hydro"]), {"Hydropower"})

    def test_stops(self):
        for rows in (sheet(title="Something else"), sheet(unit="in millions of kilowatt hours"), sheet(years=(1990, 1991)),
                     sheet(extra=("Nuclear", 1.0, 1.0)), sheet(drop="Exports"), sheet(output=(-1.0, 11.0)),
                     sheet(output=(12.5, 11.0))):
            with self.assertRaises(RuntimeError):
                A.parse_rows(rows)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
