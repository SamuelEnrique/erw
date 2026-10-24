"""Session 2258: the Census Bureau's construction spending (C30).

Energy Research Warehouse (ERW). Tests warehouse/connectors/census_c30.py on workbooks built here in the Census Bureau's
form (figures made up for the test, not the Census Bureau's): a private column and public, state and federal columns
keyed by owner and type, millions written as dollars, a blank with no row, the p and r marks, the notes ending the
sheet; a workbook not the one read, a month given twice and a figure that does not read each stopping the run; the
sector rule and the holds. No network.

    python -m unittest tests.test_session2258 -v
"""

import io
import os
import sys
import unittest

import openpyxl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import census_c30 as C  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

PRIV = C.FILES[1]
PUB = C.FILES[3]


def book(title, head, rows, unit="(Millions of dollars. Details may not add to totals.)"):
    wb = openpyxl.Workbook()
    w = wb.active
    w.append([title])
    w.append([unit])
    w.append([])
    w.append(["Date"] + head)
    for r in rows:
        w.append(list(r))
    w.append([])
    w.append(["Source: U.S. Census Bureau, Construction Spending."])
    b = io.BytesIO()
    wb.save(b)
    return b.getvalue()


class Parse(unittest.TestCase):
    def test_private(self):
        counts = {}
        out = C.parse(book(PRIV[3], ["Total\n_x000D_Private Construction1", "Data center"], [("Aug-26p", 149209, 7535), ("Jan-93", 30000, None)]),
                      *PRIV[:3], PRIV[3], {}, counts)
        got = {(r["entity"], r["ts_utc"]): r for r in out}
        d = got[("census_c30:private:data_center", "2026-08-01T00:00:00Z")]
        self.assertEqual((d["value"], d["unit"], d["variable"], d["x_status"]), (7535e6, "USD", "value_put_in_place", "p"))
        self.assertIn(("census_c30:private:total_private_construction", "1993-01-01T00:00:00Z"), got)
        self.assertEqual(counts["privtime blank"], 1)

    def test_public_owners(self):
        out = C.parse(book(PUB[3], ["Total\n_x000D_Public Construction1", "Public\n_x000D_Power", "Total State and Local Construction2",
                                    "State\n_x000D_Power", "Total Federal Construction3", "Federal\n_x000D_Power"], [("Jul-26r", 1, 2, 3, 4, 5, 6)]),
                      *PUB[:3], PUB[3], {}, {})
        self.assertEqual(sorted(r["entity"] for r in out), sorted(["census_c30:public:total", "census_c30:public:power", "census_c30:state_local:total",
                                                                   "census_c30:state_local:power", "census_c30:federal:total", "census_c30:federal:power"]))

    def test_detail_before_2002(self):
        counts = {}
        out = C.parse(book(PUB[3], ["Total\n_x000D_Public Construction1", "Public\n_x000D_Power"], [("Dec-01", 5, 0), ("Jan-02", 6, 0)]),
                      *PUB[:3], PUB[3], {}, counts)
        got = {(r["entity"], r["ts_utc"]): r["value"] for r in out}
        self.assertNotIn(("census_c30:public:power", "2001-12-01T00:00:00Z"), got)
        self.assertEqual(got[("census_c30:public:power", "2002-01-01T00:00:00Z")], 0.0)
        self.assertEqual(counts["pubtime detail before 2002"], 1)

    def test_stops(self):
        for content, words in [(book("Another title", ["Data center"], [("Aug-26", 1)]), "not the workbook read"),
                               (book(PRIV[3], ["Data center"], [("Aug-26", 1), ("Aug-26", 2)]), "given twice"),
                               (book(PRIV[3], ["Data center"], [("Aug-26", "(S)")]), "does not read"),
                               (book(PRIV[3], ["Data center"], [("Aug-26", 1), ("Annual", 2), ("Jul-26", 3)]), "not a month among the months")]:
            with self.assertRaises(RuntimeError) as c:
                C.parse(content, *PRIV[:3], PRIV[3], {}, {})
            self.assertIn(words, str(c.exception))


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(C.TABLE), "power;datacenters")
        self.assertIn(C.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {C.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
