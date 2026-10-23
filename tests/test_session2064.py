"""Session 2064: the NRC's renewed reactor licenses and approved power uprates.

Energy Research Warehouse (ERW). Tests warehouse/connectors/nrc_license_actions.py on pages built here in the NRC's form
(rows made up for the test, not the NRC's): a renewal with a footnote mark and its note, a withdrawn application, a
four-digit year; the uprates and the page's total kept apart; a mark with no note, a missing issue date with no
withdrawal note and a date that does not read stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2064 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import nrc_license_actions as N  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}


def renewal_page(rows, notes="* Fort Calhoun Station was permanently shut down on October 24, 2016. **** The application was withdrawn by the licensee."):
    body = "".join(f"<tr><td><a href='/x/{i}'>{p}</a></td><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for i, (p, a, b, c) in enumerate(rows))
    return (f"<html><body><table><tr><th>Plant Name and Unit(s)</th><th>Application Received</th><th>Renewed License Issued</th>"
            f"<th>Date Entering Extended Operation</th></tr>{body}</table><p>{notes}</p><p>Industry Activities</p></body></html>").encode()


UPRATES = ("<table><tr><th>NO.</th><th>PLANT</th><th>% UPRATE</th><th>MWt</th><th>DATE APPROVED</th><th>TYPE</th><th>ACCESSION #</th></tr>"
           "<tr><td>1</td><td>Calvert Cliffs 1</td><td>5.5</td><td>140</td><td>09/09/77</td><td>S</td><td>ML01</td></tr>"
           "<tr><td>2</td><td>Oconee 2</td><td>1.64</td><td>42</td><td>01/26/21</td><td>MU</td><td>ML20</td></tr>"
           "<tr><td></td><td>Total MWt</td><td></td><td>180</td><td></td><td></td><td></td></tr></table>").encode()


class Parse(unittest.TestCase):
    def test_renewals(self):
        rows = N.renewals(renewal_page([("Fort Calhoun*", "01/11/02", "11/04/03", "08/09/13"), ("Crystal River 3", "12/18/08", "****", ""),
                                        ("Diablo Canyon 1 &amp; 2", "11/24/09", "04/02/2026", "11/02/44 (Unit 1)")]), BASE)
        got = {r["x_plant"]: r for r in rows}
        f = got["Fort Calhoun"]
        self.assertEqual((f["event_date"], f["status"], f["x_application_received"], f["event_type"]), ("2003-11-04", "issued", "2002-01-11", "license_renewal"))
        self.assertIn("permanently shut down", f["x_note"])
        c = got["Crystal River 3"]
        self.assertEqual((c["status"], c["event_date"]), ("withdrawn", "2008-12-18"))
        self.assertEqual(got["Diablo Canyon 1 & 2"]["event_date"], "2026-04-02")

    def test_uprates(self):
        rows, s, printed = N.uprates(UPRATES, BASE)
        self.assertEqual((len(rows), s, printed), (2, 182.0, 180.0))
        self.assertEqual((rows[0]["event_id"], rows[0]["event_date"], rows[0]["x_uprate_mwt"], rows[0]["mw"]), ("nrc:uprate:1", "1977-09-09", 140.0, ""))

    def test_stops(self):
        for rows in ([("Kewaunee**", "08/14/08", "02/24/11", "")], [("Plant X", "08/14/08", "", "")], [("Plant Y", "13/40/08", "02/24/11", "")]):
            with self.assertRaises(RuntimeError):
                N.renewals(renewal_page(rows), BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(N.TABLE), "power;uranium")
        self.assertIn(N.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {N.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
