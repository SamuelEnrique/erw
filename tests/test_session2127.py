"""Session 2127: EPA's Landfill Methane Outreach Program (LMOP) database.

Energy Research Warehouse (ERW). Tests warehouse/connectors/epa_lmop.py on a workbook built here in the composite data
file's form (made up for the test, not EPA's): one row a landfill and project, EPA's statuses mapped and kept, a project
fed by two landfills on two rows, the dates and the other columns kept in snake case, EPA's summary counts checked; a
missing column, a status not EPA's, a landfill and project given twice and a summary that disagrees with the rows stopping
the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2127 -v
"""

import datetime as dt
import io
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import epa_lmop as L  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

COLS = ["GHGRP ID", "Landfill ID", "Landfill Name", "State", "Latitude", "Longitude", "Current Project Status", "Project ID",
        "Project Name", "Project Start Date", "Project Shutdown Date", "Project Type Category", "Rated MW Capacity",
        "Project Owner(s)", "Waste in Place (tons)"]


def row(landfill, project, status, name="LF", mw=None, project_name=None, start=None):
    return ["1004173", landfill, name, "NJ", 40.5, -74.3, status, project, project_name, start, None,
            "Electricity" if mw else "Unknown", mw, "Owner Co" if mw else None, 216100]


def workbook(rows, landfills, operational, drop=None):
    t = pd.DataFrame(rows, columns=COLS)
    if drop:
        t = t.drop(columns=[drop])
    s = pd.DataFrame([["Count of Unique Landfills in this File", "Count of Unique Operational Projects in this File"],
                      [landfills, operational]])
    b = io.BytesIO()
    with pd.ExcelWriter(b, engine="openpyxl") as w:
        s.to_excel(w, sheet_name="Summary", header=False, index=False)
        t.to_excel(w, sheet_name="LMOP Database", index=False)
    return b.getvalue()


ROWS = [row(958, "1016-0", "Operational", "ILR LF", 22.5, "Project #1", dt.datetime(2012, 7, 31)),
        row(946, "1016-0", "Operational", "Edison LF", 22.5, "Project #1", dt.datetime(2012, 7, 31)),
        row(946, "1016-1", "Operational", "Edison LF", 1.4, "Expansion #1"),
        row(1000, "1072-0", "Candidate", "Port Washington LF")]


class Build(unittest.TestCase):
    def test_rows(self):
        t, landfills, operational = L.build(workbook(ROWS, 3, 1), "u", "r", "")
        self.assertEqual((len(t), landfills, operational), (4, 3, 1))
        a = t[t.entity_id == "lmop:958:1016-0"].iloc[0]
        self.assertEqual((a.entity_type, a["name"], a.status, a.lmop_status, a.capacity_mw, a.geo, a.operator),
                         ("project", "ILR LF: Project #1", "operating", "Operational", "22.5", "US-NJ", "Owner Co"))
        self.assertEqual((a.project_start_date, a.ghgrp_id, a.waste_in_place_tons), ("2012-07-31", "1004173", "216100"))
        c = t[t.entity_id == "lmop:1000:1072-0"].iloc[0]
        self.assertEqual((c.status, c.lmop_status, c["name"], c.capacity_mw), ("", "Candidate", "Port Washington LF", ""))

    def test_stops(self):
        for bad in (workbook(ROWS, 3, 1, drop="Rated MW Capacity"), workbook(ROWS + [row(1, "9-0", "Maybe")], 4, 1),
                    workbook(ROWS + [ROWS[0]], 3, 1), workbook(ROWS, 3, 2), workbook(ROWS, 4, 1)):
            with self.assertRaises(RuntimeError):
                L.build(bad, "u", "r", "")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(L.NAME), "power;gas")
        self.assertIn(L.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {L.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
