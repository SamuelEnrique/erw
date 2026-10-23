"""Session 852: ERCOT's Transmission Project and Information Tracking report (TPIT), as ercot_transmission_projects.

Energy Research Warehouse (ERW). Tests warehouse/connectors/ercot_tpit.py on a project sheet built here in the TPIT's
layout (projects and figures made up for the test, not ERCOT's): the headings found by their names, the contact column
never read, ERCOT's 9999-01-01 taken as no date, the actual date before the projected one, the workbook found on the page
by its title, the sector rule and the holds. No network.

    python -m unittest tests.test_session852 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import ercot_tpit as C  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

N = float("nan")
HEAD = ["ERCOT Project Number", "Project Title (text)", "Project Description (text)", "Comments/Reasons for Delays (text)",
        'Terminal "from" Location', 'Terminal "to" Location', "Transmission Status (text)", "Associated Projects",
        "Transmission Owner (text)", "TSP/Company Contact", "Transmission Owner Project Number (Optional)",
        "Projected In-Service Date (Month/Yr)", "Actual In-Service Date (Month/Yr)", "Service Level kV", "Trans Circuit Miles New",
        "Trans Circuit Miles Rebuilt, Reconductored or Upgraded", "Autotransformer Capacity (MVA)", "Reactive Capability Added (Mvar)",
        "County Location for Substation or Starting Point for a Line", "County Location for Ending Point for a Line",
        "Planning Charter Tier", "RPG Number", "Phase Number", "MOD Project Number", "RTP Project Number"]


def row(num, phase, projected, actual, contact="A Person_x000D_\nperson@example.com"):
    v = {h: N for h in HEAD}
    v.update({"ERCOT Project Number": num, "Project Title (text)": "A Test_x000D_\nLine", "Transmission Owner (text)": "TOWN",
              "TSP/Company Contact": contact, "Projected In-Service Date (Month/Yr)": projected,
              "Actual In-Service Date (Month/Yr)": actual, "Service Level kV": 345.0, "Trans Circuit Miles New": 4.5,
              "County Location for Substation or Starting Point for a Line": "Ector", "Phase Number": phase})
    return [v[h] for h in HEAD]


def sheet(rows):
    return pd.DataFrame([["JULY BASE ... TPIT FUTURE PROJECTS AS OF 7/13/2026"] + [N] * (len(HEAD) - 1), HEAD] + rows)


class TheSheet(unittest.TestCase):
    def test_rows_dates_and_no_contact(self):
        t = C.sheet_rows(sheet([row(81590, 81591, pd.Timestamp("2027-01-01"), N),
                                row(73359, 73360, pd.Timestamp("2026-06-11"), pd.Timestamp("9999-01-01")),
                                row(62643, 62664, pd.Timestamp("2025-05-15"), pd.Timestamp("2025-06-01"))]), "Completed", "u")
        self.assertEqual(t.event_id.tolist(), ["ercot_tpit:81590:81591", "ercot_tpit:73359:73360", "ercot_tpit:62643:62664"])
        self.assertEqual(t.event_date.tolist(), ["2027-01-01", "2026-06-11", "2025-06-01"])
        self.assertEqual(t.x_date_kind.tolist(), ["projected", "projected", "actual"])
        self.assertEqual(t.x_actual_in_service.tolist()[1], "9999-01-01")        # ERCOT's cell kept
        self.assertEqual((t.status.iloc[0], t.parties.iloc[0], t.x_kv.iloc[0], t.x_title.iloc[0]), ("completed", "TOWN", "345", "A Test Line"))
        self.assertFalse(any("example.com" in str(v) for v in t.to_numpy().ravel()))

    def test_a_missing_heading_stops(self):
        f = sheet([row(1, 2, pd.Timestamp("2027-01-01"), N)])
        f.iloc[1, HEAD.index("Service Level kV")] = "Voltage"
        with self.assertRaises(RuntimeError):
            C.sheet_rows(f, "Future", "u")

    def test_the_workbook_on_the_page(self):
        html = ('<a download href="https://www.ercot.com/files/docs/2022/03/02/X.xlsx" title="Transmission Project and Information Tracking" class="d">'
                '<a download href="https://www.ercot.com/files/docs/2021/10/22/A.zip" title="Archived Transmission Project and Information Tracking">')
        self.assertEqual(C.workbook_url(html), "https://www.ercot.com/files/docs/2022/03/02/X.xlsx")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of("ercot_transmission_projects"), "power")
        self.assertIn("ercot_transmission_projects", R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn("  - ercot_transmission_projects", f.read())


if __name__ == "__main__":
    unittest.main()
