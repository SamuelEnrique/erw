"""Session 2177: BSEE's offshore incidents.

Energy Research Warehouse (ERW). Tests warehouse/connectors/bsee_incidents.py on workbooks built here in BSEE's two
forms (rows made up for the test, not BSEE's): the 2020 on form with serial numbers and a totals line, checked; the
2018 form with bracketed column names, one fatalities column, no serial (a hash id) and a note in the date column
ending the sheet; a total that differs, a serial given twice and a flag that is neither Y nor N each stopping the run;
the years found on the page; the sector rule and the holds. No network.

    python -m unittest tests.test_session2177 -v
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
import bsee_incidents as B2  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASIC = ["Date", "Time", "Operator Name", "OCS Region", "District Name", "Area Name", "Block", "Lease", "Water Depth (feet)",
         "Structure Name", "Structure Type", "Rig Name"]
NEW_FLAGS = ["Explosion", "Fire", "Loss of Well Control Underground", "Loss of Well Control Surface", "Loss of Well Control Diverter",
             "Loss of Well Control Equipment Failure", "Major Collision", "Minor Collision", "Crane", "Other Lifting Device",
             "Reportable H2S Release", "Shut Down Gas Release"]
OLD_FLAGS = ["Explosion", "Fire", "Loss of Well Control (Underground)", "Loss of Well Control (Surface)", "Loss of Well Control (Diverter)",
             "Loss of Well Control (Equipment failure/improper procedure)", "Major Collision (Property damage >$25k)",
             "Minor Collision (Property damage  <= $25k)", "Crane", "Other Lifting Device", "Reportable H2S Release", "Shut Down Gas Release"]


def book(new=True, rows=None, total_fire=None, flag="Y"):
    wb = openpyxl.Workbook()
    w = wb.active
    w.title = "CY2024 Incidents" if new else "Incidents"
    w.append(["Bureau of Safety and Environmental Enforcement"])
    if new:
        head = ["SN_EV_MASTERS"] + BASIC + ["Incident Summary", "Operator Fatalities", "Contractor Fatalities", "Operator Number of Other Injuries"] + NEW_FLAGS
    else:
        head = BASIC + ["Incident Summary", "Number of Fatalities", "Number of Injuries No lost Time"] + OLD_FLAGS
    w.append(head)
    rows = rows if rows is not None else [("-1", dt.datetime(2024, 1, 2), "G01673", 0, 1, flag), ("-2", dt.datetime(2024, 1, 3), "", 1, 0, "N")]
    fires = 0
    for sn, d, lease, fat, inj, fire in rows:
        flags = ["N"] * len(NEW_FLAGS)
        flags[1] = fire
        fires += fire == "Y"
        base = [d, "1800", "Op LLC", "Gulf of America", "New Orleans District", "Main Pass Area", "296", lease, 220, "C", "FIXED", ""]
        if new:
            w.append([sn] + base + ["A worker was hurt.", fat, 0, inj] + flags)
        else:
            w.append(base + ["A worker was hurt.", fat, inj] + flags)
    w.append([])
    if new:
        tot = [""] * len(head)
        tot[head.index("Fire")] = fires if total_fire is None else total_fire
        w.append(tot)
    else:
        w.append(["General:\nBSEE Incident Reporting Requirements ..."])
    wb.create_sheet("Metadata")
    b = io.BytesIO()
    wb.save(b)
    return b.getvalue()


class Parse(unittest.TestCase):
    def test_new_form(self):
        rows, checked = B2.parse(book(), 2024, "u")
        self.assertTrue(checked)
        r = rows[0]
        self.assertEqual((r["event_id"], r["event_date"], r["entity_ids"], r["x_fire"], r["x_injuries"], r["x_loss_of_well_control"]),
                         ("bsee_incident:-1", "2024-01-02", "lease:G01673", "Y", 1, "N"))
        self.assertEqual(rows[1]["x_fatalities"], 1)

    def test_old_form(self):
        rows, checked = B2.parse(book(new=False), 2018, "u")
        self.assertFalse(checked)
        self.assertEqual(len(rows), 2)
        self.assertTrue(rows[0]["event_id"].startswith("bsee_incident:h"))
        self.assertEqual(B2.parse(book(new=False), 2018, "u")[0][0]["event_id"], rows[0]["event_id"])  # stable

    def test_stops(self):
        for content, words in [(book(total_fire=5), "BSEE's total is"),
                               (book(rows=[("-1", dt.datetime(2024, 1, 2), "", 0, 0, "N")] * 2), "given twice"),
                               (book(flag="maybe"), "neither Y nor N")]:
            with self.assertRaises(RuntimeError) as c:
                B2.parse(content, 2024, "u")
            self.assertIn(words, str(c.exception))

    def test_year_links(self):
        page = ('<a href="/sites/bsee.gov/files/2026-04/cy-2024-excel-spreadsheet.xlsx">a</a>'
                '<a href="https://www.bsee.gov/sites/bsee.gov/files/cy2018-public-release-01-17-2020.xlsx">b</a>'
                '<a href="https://www.bsee.gov/sites/bsee.gov/files/incident-statistics/fy2014_public_release.xlsx">c</a>')
        self.assertEqual(sorted(B2.year_links(page)), [2018, 2024])


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(B2.TABLE), "oil;gas")
        self.assertIn(B2.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {B2.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
