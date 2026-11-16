"""Session 7022 (chain 301, the data machine, 16 November 2026): done-line request 40.

gridstatus 0.36.0 writes "Completed" for an ERCOT position whose "IA Signed" day is filled (a signed interconnection
agreement), and copies "Approved for Synchronization" into "Actual Completion Date". The queue connector counted every
such position as in operation. It now reads ERCOT's own milestones: completed only with a day of approval to
synchronize; a signed agreement alone is active, its iso_status "IA Signed". The frame below has the columns the
library returns, with values of the kinds the report holds.
"""

import importlib.util
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def connector():
    sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
    spec = importlib.util.spec_from_file_location("iso_queues_7022", os.path.join(ROOT, "warehouse", "connectors", "iso_queues.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def frame():
    return pd.DataFrame({
        "Queue ID": ["21INR0001", "21INR0002", "23INR0003", "25INR0004"],
        "Project Name": ["A Solar", "B Storage", "C Wind", "D Gas"],
        "Interconnecting Entity": ["A LLC", "B LLC", "C LLC", "D LLC"],
        "County": ["Pecos", "Harris", "Nolan", "Ector"], "State": ["Texas"] * 4,
        "Interconnection Location": ["X 345kV"] * 4,
        "Generation Type": ["Solar - Photovoltaic Solar", "Other - Battery Energy Storage", "Wind - Wind Turbine", "Gas - Combined-Cycle"],
        "Capacity (MW)": [200.0, 100.0, 150.0, 300.0],
        "Queue Date": ["2021-01-05", "2021-03-01", "2023-06-01", "2025-02-01"],
        "Proposed Completion Date": ["2023-06-01", "2024-01-01", "2026-12-01", "2027-06-01"],
        # the library's Status: Completed where IA Signed is filled
        "Status": ["Completed", "Completed", "Active", "Completed"],
        "IA Signed": ["2022-01-10", "2022-05-01", None, "2025-09-01"],
        "Approved for Synchronization": ["2023-05-20", None, None, None],
        "Actual Completion Date": ["2023-05-20", None, None, None],
    })


class ERCOTsMilestones(unittest.TestCase):
    def setUp(self):
        self.m = connector()

    def test_only_a_day_of_approval_to_synchronize_is_in_operation(self):
        out = self.m.build("ercot", frame(), "https://example.invalid/queue", "2026-11-16T19:00:00Z", lambda s: None)
        by = dict(zip(out["queue_id"], zip(out["status"], out["iso_status"], out["status_date"])))
        self.assertEqual(by["21INR0001"][:2], ("completed", "Approved for Synchronization"))
        self.assertTrue(by["21INR0001"][2].startswith("2023-05-20"))
        self.assertEqual(by["21INR0002"], ("active", "IA Signed", ""))       # signed, not synchronized: still in the queue
        self.assertEqual(by["21INR0002"][1], "IA Signed")
        self.assertEqual(by["23INR0003"][:2], ("active", "Active"))
        self.assertEqual(by["25INR0004"][:2], ("active", "IA Signed"))

    def test_the_librarys_completed_is_no_longer_an_ercot_status(self):
        self.assertNotIn("Completed", self.m.STATUS_MAP["ercot"])
        self.assertEqual(self.m.STATUS_MAP["ercot"]["Approved for Synchronization"], "completed")
        # NYISO's (its In Service sheet) and ISO-NE's (status C, Commercial) stay as they were
        self.assertEqual((self.m.STATUS_MAP["nyiso"]["Completed"], self.m.STATUS_MAP["isone"]["Completed"]), ("completed", "completed"))


if __name__ == "__main__":
    unittest.main()
