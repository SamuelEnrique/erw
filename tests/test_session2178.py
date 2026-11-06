"""Session 2178: the NRC's Reactor Oversight Process findings and violations.

Energy Research Warehouse (ERW). Tests warehouse/connectors/nrc_rop_findings.py on a workbook built here with the NRC's
23 columns (rows made up for the test, not the NRC's): a finding read with its docket, type, color and x_ columns; an
issue date held as an Excel serial number read as one and counted; a key given twice, a date that does not read and a
changed column each stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2178 -v
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
import nrc_rop_findings as N  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def row(date, title="Failure to maintain a procedure", typ="NCV", color="Green"):
    v = dict.fromkeys(N.COLUMNS, "")
    v.update({"Procedure": "IP 71111.12", "Issue Date": date, "Report Number": "2024-001", "Type": typ, "CornerstoneCode": "MS",
              "Cornerstone": "Mitigating Systems", "Title": title, "Docket Number": "05000220", "Site Name": "Nine Mile Point",
              "Site Code": "NMP", "Region": "1", "Year": 2024, "Quarter": 1, "Significance": color, "Link": "https://www.nrc.gov/docs/ML24/x.pdf"})
    return [v[c] for c in N.COLUMNS]


def book(rows, columns=None):
    wb = openpyxl.Workbook()
    w = wb.active
    w.append(columns or N.COLUMNS)
    for r in rows:
        w.append(r)
    b = io.BytesIO()
    wb.save(b)
    return b.getvalue()


class Parse(unittest.TestCase):
    def test_rows(self):
        serials = []
        rows = N.parse(book([row(dt.datetime(2024, 2, 5)), row(45337, title="Another", typ="FIN", color="White")]), {}, serials)
        a, b = rows
        self.assertEqual((a["event_date"], a["event_type"], a["status"], a["entity_ids"], a["parties"], a["x_cornerstone"]),
                         ("2024-02-05", "ncv", "green", "nrc_reactor:05000220", "Nine Mile Point", "Mitigating Systems"))
        self.assertEqual((b["event_date"], b["event_type"], b["status"]), ("2024-02-15", "fin", "white"))
        self.assertEqual(len(serials), 1)
        self.assertTrue(a["event_id"].startswith("nrc_rop:"))
        self.assertEqual(N.parse(book([row(dt.datetime(2024, 2, 5))]), {}, [])[0]["event_id"], a["event_id"])  # stable

    def test_stops(self):
        cols = list(N.COLUMNS)
        cols[0] = "Inspection Procedure"
        for content, words in [(book([row(dt.datetime(2024, 2, 5))] * 2), "given twice"),
                               (book([row("soon")]), "does not read"),
                               (book([row(dt.datetime(2024, 2, 5))], cols), "data dictionary")]:
            with self.assertRaises(RuntimeError) as c:
                N.parse(content, {}, [])
            self.assertIn(words, str(c.exception))


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(N.TABLE), "power;uranium")
        self.assertIn(N.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {N.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
