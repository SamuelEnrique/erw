"""Session 2112: the Treasury's Section 1603 awards.

Energy Research Warehouse (ERW). Tests warehouse/connectors/treasury_1603.py on a list built here in the Treasury's form
(rows made up for the test, not the Treasury's): the title's date, an award date written as an Excel serial number, the
event's fields and its stable id; a total that differs, an award given twice, a funded amount with cents and a state
that is not two letters each stopping the run; the list's address found on the page; the sector rule and the holds.
No network.

    python -m unittest tests.test_session2112 -v
"""

import datetime as dt
import io
import os
import sys
import unittest

import openpyxl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import treasury_1603 as T  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u"}


def book(rows=None, total=None):
    rows = rows if rows is not None else [("Sun Farm LLC", "NJ", "Solar Electricity", 1000, dt.datetime(2012, 3, 1)),
                                          ("Wind Co", "TX", "Wind", 5000, 40940)]
    wb = openpyxl.Workbook()
    w = wb.active
    w.append(["Section 1603 - Payments for Specified Renewable Energy Property in Lieu of Tax Credits      Awardees as of March 1, 2018"])
    w.append(T.HEAD)
    for r in rows:
        w.append(list(r))
    w.append([])
    w.append(["Total", "", "", total if total is not None else sum(r[3] for r in rows)])
    b = io.BytesIO()
    wb.save(b)
    return b.getvalue()


class Parse(unittest.TestCase):
    def test_list(self):
        rows, when, serials, total = T.parse(book(), BASE)
        self.assertEqual((when, total, len(rows), len(serials)), ("2018-03-01", 6000, 2, 1))
        w = rows[1]
        self.assertEqual((w["event_date"], w["entity_ids"], w["x_technology"], w["x_funded_usd"], w["event_type"], w["price"]),
                         ("2012-02-01", "US-TX", "Wind", 5000, "grant_award", ""))
        self.assertTrue(w["event_id"].startswith("treasury_1603:"))
        self.assertEqual(T.parse(book(), BASE)[0][1]["event_id"], w["event_id"])  # stable

    def test_stops(self):
        one = ("Sun Farm LLC", "NJ", "Solar Electricity", 1000, dt.datetime(2012, 3, 1))
        for kw, words in [(dict(total=999), "sum to"), (dict(rows=[one, one]), "given twice"),
                          (dict(rows=[("A", "NJ", "Wind", 10.5, dt.datetime(2012, 3, 1))]), "whole number"),
                          (dict(rows=[("A", "New Jersey", "Wind", 10, dt.datetime(2012, 3, 1))]), "two letters"),
                          (dict(rows=[("A", "NJ", "Wind", 10, "soon")]), "does not read")]:
            with self.assertRaises(RuntimeError) as c:
                T.parse(book(**kw), BASE)
            self.assertIn(words, str(c.exception), kw)

    def test_list_url(self):
        page = '<a href=/system/files/216/GUIDANCE.pdf>g</a><a href=/system/files/216/Website-Awarded-as-of-3.1.18.xlsx>list</a>'
        self.assertEqual(T.list_url(page), "https://home.treasury.gov/system/files/216/Website-Awarded-as-of-3.1.18.xlsx")
        with self.assertRaises(RuntimeError):
            T.list_url("<a href=/x.pdf>x</a>")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(T.TABLE), "power;deals")
        self.assertIn(T.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {T.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
