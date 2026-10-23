"""Session 2036: AFDC's light-duty vehicle registration counts by state and fuel type.

Energy Research Warehouse (ERW). Tests warehouse/connectors/afdc_registrations.py on a page built here in AFDC's form
(made up for the test, not AFDC's): the year's table read into rows, the United States row kept as the page's own; a
table for another year, a column not as expected, a place not known, a count not a whole number and a table without all
52 places stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2036 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import afdc_registrations as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
COLS = list(A.COLUMNS)


def page(year, places=None, head=None, cell="1,200"):
    places = places or list(A.PLACES)
    head = head or ["State"] + COLS
    rows = "".join("<tr><td>" + p + "</td>" + "".join(f"<td>{cell}</td>" for _ in COLS) + "</tr>" for p in places)
    return (f"<h2>{year} Light-Duty Vehicle Registration Counts by State and Fuel Type</h2><table><thead><tr>"
            + "".join(f"<th>{h}</th>" for h in head) + f"</tr></thead><tbody>{rows}</tbody></table>")


class Parse(unittest.TestCase):
    def test_rows(self):
        c = A.parse(page(2024), 2024)
        self.assertEqual(len(c), 52 * 12)
        self.assertEqual(c[("CA", "Electric (EV)")], 1200)
        s = A.build([(2024, c)], lambda y: BASE).set_index(["entity", "variable"])
        a = s.loc[("afdc_reg:US", "registrations_ev")]
        self.assertEqual((a.geo, a.unit, a.freq, a.ts_utc, a.node), ("US", "count", "P1Y", "2024-01-01T00:00:00Z", "Electric (EV)"))
        self.assertEqual(s.loc[("afdc_reg:TX", "registrations_unknown_fuel")].geo, "US-TX")

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            A.parse(page(2023), 2024)
        with self.assertRaises(RuntimeError):
            A.parse(page(2024, head=["State"] + COLS[:-1] + ["Other"]), 2024)
        with self.assertRaises(RuntimeError):
            A.parse(page(2024, places=list(A.PLACES) + ["Guam"]), 2024)
        with self.assertRaises(RuntimeError):
            A.parse(page(2024, cell="about 1,200"), 2024)
        with self.assertRaises(RuntimeError):
            A.parse(page(2024, places=list(A.PLACES)[:-2]), 2024)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.TABLE), "power;products")
        self.assertIn(A.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
