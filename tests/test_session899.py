"""Session 899: EIA's natural gas pipeline projects.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_gas_pipeline_projects.py on a sheet built here in the
tracker's form (figures made up for the test, not EIA's): the newest workbook the page links, the event date by the
completed date, else the year in service, else EIA's last update (x_date_basis saying which), a cost range kept as EIA
writes it, a heading not in the map stopping the run, the sector rule and the holds. No network.

    python -m unittest tests.test_session899 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_gas_pipeline_projects as G  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = ["Last Updated Date", "Project Name", "Pipeline Operator Name", "Project Type", "Status", "Completed Date",
        "Year In Service Date", "State(s)", "Cost (millions)", "Miles", "Additional Capacity (MMcf/d)", "Docket/Permit  Number"]


def sheet(rows):
    return pd.DataFrame([["Natural Gas Pipeline Projects"] + [None] * (len(HEAD) - 1), HEAD] + rows)


class Projects(unittest.TestCase):
    def test_newest_workbook(self):
        page = ('<a href="/naturalgas/pipelines/EIA-NaturalGasPipelineProjects_Apr2025.xlsx">'
                '<a href="/naturalgas/pipelines/EIA-NaturalGasPipelineProjectsAug2026.xlsx">'
                '<a href="/naturalgas/pipelines/EIA-NaturalGasPipelineProjects_Apr2026.xlsx">')
        self.assertEqual(G.newest(page), ("https://www.eia.gov/naturalgas/pipelines/EIA-NaturalGasPipelineProjectsAug2026.xlsx", "Aug 2026"))

    def test_dates_and_fields(self):
        rows = [[pd.Timestamp("2026-07-05"), "Alaska LNG pipe", "8 Star", "New Pipeline", "Approved ", None, 2029, "AK", "13000-17000", 807, 3300, "CP17-178"],
                [pd.Timestamp("2025-01-02"), "Old Lateral", "Op", "Lateral", "Completed", pd.Timestamp("2024-11-01"), 2024, "TX", 10, 5, 50, None],
                [pd.Timestamp("2026-03-01"), "Undated Idea", "Op", "Expansion", "Announced", None, None, "LA", None, None, 100, None]]
        t = G.sheet_rows(sheet(rows), "current", "u", "r").set_index("x_project_name")
        a = t.loc["Alaska LNG pipe"]
        self.assertEqual((a.event_id, a.event_date, a.x_date_basis, a.status), ("eia_gas_pipeline:alaska_lng_pipe:2029", "2029-01-01", "year_in_service", "approved"))
        self.assertEqual((a.x_cost_million_usd, a.x_capacity_mmcfd, a.x_docket, a.parties), ("13000-17000", "3300", "CP17-178", "8 Star"))
        self.assertEqual((t.loc["Old Lateral"].event_date, t.loc["Old Lateral"].x_date_basis), ("2024-11-01", "completed"))
        self.assertEqual((t.loc["Undated Idea"].event_date, t.loc["Undated Idea"].x_date_basis), ("2026-03-01", "last_updated"))

    def test_a_heading_not_in_the_map_stops(self):
        s = sheet([[None] * len(HEAD)])
        s.iloc[1, 3] = "Something New"
        with self.assertRaises(RuntimeError):
            G.sheet_rows(s, "current", "u", "r")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        name = "eia_gas_pipeline_projects"
        self.assertEqual(B.sector_of(name), "gas")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
