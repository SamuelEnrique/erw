"""Session 2953 (chain 157): iso_queue_snapshot_summary, the ISO queues summarized from their own snapshots. The
builder runs on a small queue written here: the snapshot's status sums, the years, the in-service rule (a completed
request, on or before the snapshot) and the median's floor of five. No request, no model call."""
import importlib.util
import os
import tempfile
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load():
    spec = importlib.util.spec_from_file_location("qs_2953", os.path.join(ROOT, "warehouse", "derived", "iso_queue_snapshot_summary.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def queue(rows):
    cols = ["capacity_mw", "fuel_technology", "status", "queue_date", "actual_in_service_date", "withdrawn_date", "retrieved_at"]
    return pd.DataFrame(rows, columns=cols)


ROWS = [(100, "Solar", "completed", f"2018-01-{i + 1:02d}", "2021-01-01", "", "2026-10-26T14:52:14Z") for i in range(5)]
ROWS += [(50, "Battery/Storage", "active", "2024-03-01", "2028-01-01", "", "2026-10-26T14:52:14Z"),       # a requested date
         (70, "Wind", "withdrawn", "2019-05-01", "2022-01-01", "2020-06-01", "2026-10-26T14:52:14Z"),       # withdrawn, dated
         (30, "Hybrid - Solar/Storage", "", "2023-01-01", "", "", "2026-10-26T14:52:14Z")]


class TheSummary(unittest.TestCase):
    def setUp(self):
        self.m = load()
        self.d = tempfile.TemporaryDirectory()
        q = queue(ROWS)
        with open(os.path.join(self.d.name, "spp_interconnection_queue.csv"), "w", encoding="utf-8", newline="") as f:
            f.write("# a test queue\n")
            q.to_csv(f, index=False)

    def tearDown(self):
        self.d.cleanup()

    def rows(self):
        out, snap = self.m.build_grid(self.m.read(self.d.name, "spp"), "spp")
        return pd.DataFrame(out), snap

    def test_the_snapshot(self):
        t, snap = self.rows()
        self.assertEqual(snap, "2026-10-26")
        get = lambda e, v: t[(t["entity"] == e) & (t["variable"] == v)]["value"].iloc[0]
        self.assertEqual(get("iso_queue:spp:solar", "completed_mw"), 500.0)
        self.assertEqual(get("iso_queue:spp:storage", "active_count"), 1)
        self.assertEqual(get("iso_queue:spp:solar_storage", "unknown_mw"), 30.0)

    def test_only_a_completed_request_is_in_service(self):
        t, _ = self.rows()
        done = t[(t["entity"] == "iso_queue:spp") & (t["variable"] == "completed_count")]
        self.assertEqual(list(zip(done["ts_utc"], done["value"])), [("2021-01-01T00:00:00Z", 5)])
        med = t[t["variable"] == "median_months_to_in_service"]
        self.assertEqual(list(zip(med["ts_utc"], med["value"])), [("2018-01-01T00:00:00Z", 35.9)])

    def test_the_median_needs_five(self):
        self.m.MIN_DATED = 6
        try:
            t, _ = self.rows()
            self.assertTrue(t[t["variable"] == "median_months_to_in_service"].empty)
            self.assertEqual(t[t["variable"] == "in_service_dated"]["value"].sum(), 5)
        finally:
            self.m.MIN_DATED = 5

    def test_the_fuel_groups(self):
        g = self.m.fuel_group
        self.assertEqual([g("Photovoltaic + Storage"), g("Other - Battery Energy Storage"), g("SUN"), g("WND"), g("Gas - Combustion (gas) Turbine"), g(""), g("Geothermal")],
                         ["solar_storage", "storage", "solar", "wind", "gas", "unknown", "other"])


if __name__ == "__main__":
    unittest.main()
