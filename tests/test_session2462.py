"""Session 2462: the National Statistical Committee of the Kyrgyz Republic's generation by kind of station and electricity
balance.

Energy Research Warehouse (ERW). Tests warehouse/connectors/nsc_kyrgyzstan.py's reader on sheets built here in the
committee's form (figures made up for the test, not the committee's): the old classification's years before 2011 and
GKED-3's from 2011, the overlap checked, a footnote mark in a cell read, "-" with no row, the whole-number years' rounding
allowed, a failed balance kept and named; a line not in the map, sheets that disagree and a value that is not a number
stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2462 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import nsc_kyrgyzstan as K  # noqa: E402
import build_coverage as B  # noqa: E402


def frame(years, lines):
    rows = [["t", "t", "title"], [None] * 3, [None] * 3, [None] * 3, ["k", "r", "Items"] + years, [None] * 3]
    rows += [["k", "r", label] + vals for label, vals in lines]
    width = max(len(r) for r in rows)
    return pd.DataFrame([r + [None] * (width - len(r)) for r in rows])


def gen_book(total_2011="10.0"):
    old = frame([2010, 2011], [("The electric power are produced", [9, 10]), ("Hydroelectric power stations", [8, 9]),
                               ("Thermoelectric power stations", [1, 1])])
    new = frame([2011, 2012], [("The electric power are produced", [float(total_2011), 12.5]), ("Hydroelectric power stations", [9.0, 11.0]),
                               ("Thermoelectric power stations", [1.0, 1.4]), ("Otherelectric power stations", ["-", 0.1])])
    return {"1.05.01.03": old, "1.05.01.03 (GKED-3)": new}


def bal_book(manuf_2010="5,5 2", exports_2012=2.0, label="Other activities"):
    old = frame([2010, 2011], [("Electricity produced", [9.0, 10.0]), ("Electricity imported", [1.0, "-"]),
                               ("Electricity consumed in:", [8.0, 9.0]), ("Manufacturing", [manuf_2010, 6.0]),
                               ("Social services", [1.5, 2.0]), ("Transmission losses", [1.0, 1.0]), ("Electricity exported", [2.0, 1.0])])
    new = frame([2011, 2012], [("Electricity produced", [10.0, 12.5]), ("Electricity imported", ["-", 1.0]),
                               ("Electricity consumed in:", [9.0, 11.5]), ("Manufacturing", [6.0, 7.0]),
                               (label, [2.0, 3.0]), ("Transmission losses", [1.0, 1.5]), ("Electricity exported", [1.0, exports_2012])])
    return {"1.05.01.02": old, "1.05.01.02 (GKED-3)": new}


class Rows(unittest.TestCase):
    def test_rows(self):
        rows, gaps = K.parse(gen_book(), bal_book())
        self.assertEqual(rows[("consumption_manufacturing", 2010)], (5.5, "1248"))
        self.assertEqual(rows[("generation_hydro", 2012)], (11.0, "344"))
        self.assertEqual(rows[("consumption_other_activities", 2012)], (3.0, "1248"))
        self.assertEqual(rows[("consumption_social_services", 2010)], (1.5, "1248"))
        self.assertNotIn(("consumption_social_services", 2011), rows)  # the GKED-3 sheet gives 2011 on
        self.assertNotIn(("imports", 2011), rows)
        self.assertNotIn(("generation_other", 2011), rows)
        self.assertEqual(gaps, [])
        t = K.finish(rows, {}, {})
        self.assertEqual(t[(t.variable == "produced") & (t.ts_utc == "2012-01-01T00:00:00Z")].value.item(), 12500.0)

    def test_kept_and_named(self):
        rows, gaps = K.parse(gen_book(), bal_book(exports_2012=1.5))
        self.assertEqual(rows[("exports", 2012)], (1.5, "1248"))
        self.assertEqual([g[0] for g in gaps], [2012])

    def test_stops(self):
        for g, b in ((gen_book(total_2011="11.0"), bal_book()), (gen_book(), bal_book(manuf_2010="x")),
                     (gen_book(), bal_book(label="Mining"))):
            with self.assertRaises(RuntimeError):
                K.parse(g, b)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(K.NAME), "power")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {K.NAME}\n", f.read().replace("\r\n", "\n"))
        with open(os.path.join(ROOT, "warehouse", "redivis", "release_v1.py"), encoding="utf-8") as f:
            self.assertIn(f'"{K.NAME}",', f.read())


if __name__ == "__main__":
    unittest.main()
