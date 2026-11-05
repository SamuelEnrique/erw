"""Session 2230: SMARD's Germany generation by source and grid load.

Energy Research Warehouse (ERW). Tests warehouse/connectors/smard_germany.py on a zip built here in SMARD's form (made up
for the test, not SMARD's): each source a generation_ variable, the grid load its own, MWh on the month's first day,
thousands separators read, "-" not written; the query's start at 1 January 2015 in German time; a zip without its two
files, a column of another form, a Start date not the first of a month and a value not a number stopping the run; the
sector rule and the holds. No network.

    python -m unittest tests.test_session2230 -v
"""

import io
import os
import sys
import unittest
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import smard_germany as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": ""}
GEN = ("Start date;End date;Biomass [MWh] Calculated resolutions;Fossil gas [MWh] Calculated resolutions\n"
       "Jan 1, 2015;Feb 1, 2015;3,153,613.46;1,615,352.60\nOct 1, 2026;Nov 1, 2026;-;-\n")
CON = "Start date;End date;grid load [MWh] Calculated resolutions\nJan 1, 2015;Feb 1, 2015;42,390,489.77\n"


def zipped(gen=GEN, con=CON, names=("Actual_generation_x_Month_1.csv", "Actual_consumption_x_Month_2.csv")):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr(names[0], gen)
        z.writestr(names[1], con)
    return b.getvalue()


class Parse(unittest.TestCase):
    def test_rows(self):
        t = S.parse(zipped(), BASE).set_index(["variable", "ts_utc"])
        self.assertEqual(t.loc[("generation_biomass", "2015-01-01T00:00:00Z")].value, 3153613.46)
        self.assertEqual(t.loc[("generation_fossil_gas", "2015-01-01T00:00:00Z")].node, "Fossil gas")
        self.assertEqual(t.loc[("grid_load", "2015-01-01T00:00:00Z")].value, 42390489.77)
        self.assertEqual(len(t), 3)
        self.assertEqual(set(t.unit), {"MWh"})

    def test_query(self):
        f = S.body(0)["request_form"][0]
        self.assertEqual((f["region"], f["resolution"], f["timestamp_from"]), ("DE", "month", 1420066800000))

    def test_stops(self):
        for z in (zipped(names=("a.csv", "b.csv")), zipped(gen=GEN.replace("Biomass [MWh] Calculated resolutions", "Biomass (MWh)")),
                  zipped(gen=GEN.replace("Jan 1, 2015;Feb", "Jan 2, 2015;Feb")), zipped(con=CON.replace("42,390,489.77", "many"))):
            with self.assertRaises(RuntimeError):
                S.parse(z, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
