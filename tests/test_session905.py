"""Session 905: method notes for chain 049's tables, and the faults their checks found.

Energy Research Warehouse (ERW). Tests that an EIA-411 area's footnote mark is not part of its name (RFC[5] was a second
entity), that the pipeline projects' dates carry no time and their ids end in a slug, that the multifuel table's header
names session 896, and that every chain 049 table has its note linked from coverage. No network.

    python -m unittest tests.test_session905 -v
"""

import datetime as dt
import os
import re
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eia411 as E  # noqa: E402
import eia_gas_pipeline_projects as G  # noqa: E402
import eia860_schedules as S  # noqa: E402

N = float("nan")
NOTES = {
    "eia411_capacity_margins_annual": "eia411", "eia860_boilers": "eia860_environment", "eia860_cooling_systems": "eia860_environment",
    "eia860_emission_controls": "eia860_environment", "eia860_multifuel_generators": "eia860_schedules",
    "eia923_plant_fuel_monthly": "eia923_monthly", "eia923_fuel_receipts": "eia923_receipts",
    "eia_gas_pipeline_projects": "eia_gas_pipeline_projects", "ercot_node_places": "ercot_node_places",
    "eia_power_costs_annual": "eia_power_costs_annual", "eia_uranium_marketing_annual": "eia_uranium_marketing_annual",
}


class Fixes(unittest.TestCase):
    def test_a_footnote_mark_is_not_part_of_the_area(self):
        head = ["Interconnection", "NERC Regional Assesment Area"]
        f = pd.DataFrame([head + ["Net Internal Demand[1]", N], [N, N, "Actual", N], [N, N, "2005/ 2006", "2006/ 2007"],
                          ["Eastern Interconnection", "RFC[5]", 100, 110]])
        t = pd.DataFrame(E.sheet_rows(f, "winter", "u", "r"))
        self.assertEqual(set(t.entity), {"eia411:rfc"})

    def test_pipeline_dates_and_ids(self):
        head = ["Last Updated Date", "Project Name", "Pipeline Operator Name", "Status", "Completed Date", "Year In Service Date"]
        f = pd.DataFrame([["title"] + [N] * 5, head,
                          [dt.datetime(2009, 6, 26), "Old One", "Op", "Completed", dt.datetime(1996, 6, 1), 1996],
                          [dt.datetime(2026, 7, 6), "Phased One", "Op", "Approved", None, "2020-2027 (phased)"]])
        t = G.sheet_rows(f, "historical", "u", "r").set_index("x_project_name")
        self.assertEqual((t.loc["Old One", "x_completed_date"], t.loc["Old One", "x_last_updated"]), ("1996-06-01", "2009-06-26"))
        self.assertEqual(t.loc["Phased One", "event_id"], "eia_gas_pipeline:phased_one:2020_2027_phased")
        self.assertEqual((t.loc["Phased One", "event_date"], t.loc["Phased One", "x_date_basis"]), ("2026-07-06", "last_updated"))

    def test_each_schedule_names_its_session(self):
        self.assertEqual(S.TABLES["3_5_Multifuel"]["session"], 896)
        self.assertEqual({S.TABLES[k]["session"] for k in ("4___Owner", "3_4_Energy_Storage", "3_3_Solar", "3_2_Wind")}, {885})


class Notes(unittest.TestCase):
    def test_every_table_has_its_note_linked(self):
        with open(os.path.join(ROOT, "docs", "coverage.md"), encoding="utf-8") as f:
            rows = {ln.split("|")[1].strip().strip("`"): ln for ln in f if ln.startswith("| `")}
        for table, note in NOTES.items():
            with open(os.path.join(ROOT, "docs", "methods", note + ".md"), encoding="utf-8") as f:
                text = f.read()
            # the "Tables:" paragraph, which may wrap onto the lines below it
            line = text[text.index("Tables: "):].replace("\r\n", "\n").split("\n\n")[0]
            self.assertIn(f"`{table}`", line, table)
            self.assertEqual(text.count(chr(0x2014)) + text.count(chr(0x2013)), 0, note)
            cells = re.split(r"(?<!\\)\|", rows[table].rstrip())[1:-1]
            self.assertEqual(cells[-1].strip(), f"[{note}](methods/{note}.md)", table)


if __name__ == "__main__":
    unittest.main()
