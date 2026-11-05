"""Session 2343: the Swiss Federal Office of Energy's monthly electricity balance (ENSTAT, opendata.swiss).

Energy Research Warehouse (ERW). Tests warehouse/connectors/bfe_switzerland_electricity.py on a file built here in the
CSV's form (made up for the test, not SFOE's): each cell a row in MWh on the month's first day, the German column kept
as node and the final flag as x_final, a NULL cell not written; a header of another form, a month out of range, a final
flag other than 0 or 1, a value that is not a number and a month given twice stopping the run; the sector rule and the
holds. No network.

    python -m unittest tests.test_session2343 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import bfe_switzerland_electricity as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
HEAD = ",".join(S.HEADER)
VALS = ["1656", "1303", "1810", "NULL", "307", "10", "1461", "6547", "690", "5857", "2015", "2945", "4927", "366", "4561"]


def csvtext(*lines):
    return (HEAD + "\n" + "\n".join(lines) + "\n").encode("utf-8")


class Parse(unittest.TestCase):
    def test_rows(self):
        t = S.parse(csvtext("2026,7,0," + ",".join(VALS)), BASE).set_index("variable")
        self.assertEqual(len(t), 14)
        self.assertNotIn("other_generation", t.index)
        r = t.loc["national_consumption"]
        self.assertEqual((r.ts_utc, r.value, r.unit, r.geo, r.node, r.x_final), ("2026-07-01T00:00:00Z", 4927000.0, "MWh", "CH", "Landesverbrauch_GWh", "0"))
        self.assertEqual(t.loc["solar_generation"].value, 1461000.0)

    def test_stops(self):
        line = "2026,7,0," + ",".join(VALS)
        bad = [("Year,Month," + HEAD.split(",", 2)[2] + "\n" + line + "\n").encode(),
               csvtext("2026,13,0," + ",".join(VALS)),
               csvtext("2026,7,2," + ",".join(VALS)),
               csvtext("2026,7,0,about," + ",".join(VALS[1:])),
               csvtext(line, line)]
        for content in bad:
            with self.assertRaises((RuntimeError, ValueError)):
                S.parse(content, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
