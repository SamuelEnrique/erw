"""Session 9000, chain 601 (parts E to G): grid alerts in one table, CAISO's tie transfers, outages, and the page
/conditions with its files."""
import glob
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "conditions")
OPS = ["caiso", "ercot", "spp", "miso", "pjm", "nyiso", "isone"]
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheConnectors(unittest.TestCase):
    def test_caiso_outage_hours_weight_the_part_of_the_hour(self):
        import pandas as pd
        import grid_outages as go
        x = pd.DataFrame({"OUTAGE MRID": ["1", "2", "2"], "RESOURCE ID": ["A", "B", "B"], "OUTAGE TYPE": ["PLANNED", "FORCED", "FORCED"],
                          "CURTAILMENT START DATE TIME": ["2026-11-18 00:30:00", "2026-11-18 00:00:00", "2026-11-18 00:00:00"],
                          "CURTAILMENT END DATE TIME": ["2026-11-18 01:00:00", None, None],
                          "CURTAILMENT MW": [100.0, 50.0, 50.0], "RESOURCE PMAX MW": [200.0, 60.0, 60.0]})
        orig = go.caiso_frame
        go.caiso_frame = lambda raw, day: x
        try:
            rows, other = go.caiso_rows(pd.Timestamp("2026-11-18"), b"", {"url": "u", "retrieved_at": "t"})
        finally:
            go.caiso_frame = orig
        h0 = rows[rows["ts"] == rows["ts"].min()].set_index("variable")["value"]
        self.assertAlmostEqual(h0["outage_mw_planned"], 50.0)  # half the hour
        self.assertAlmostEqual(h0["outage_mw_forced"], 50.0)   # the same curtailment printed twice counts once
        self.assertEqual(len(rows), 3 * 24)
        self.assertEqual(other, [])

    def test_caiso_outage_addresses_follow_the_report_names(self):
        import grid_outages as go
        self.assertTrue(go.caiso_url("2026-11-18").endswith("report-20261118.xlsx"))
        self.assertTrue(go.caiso_url("2024-08-01").endswith("report-aug-01-2024.xlsx"))
        self.assertIn("curtailed-and-non-operational", go.caiso_url("2024-06-01"))
        self.assertTrue(go.caiso_url("2024-05-31").endswith("report-2024-05-31.xlsx"))

    def test_tie_pairs_take_one_side(self):
        import pandas as pd
        import caiso_tie_flows as tf
        ts = pd.date_range("2026-11-18 08:00", periods=288, freq="5min", tz="UTC").strftime("%Y-%m-%dT%H:%M:%S-00:00")
        x = pd.concat([
            pd.DataFrame({"INTERVAL_START_GMT": ts, "FROM_BAA": "PACE", "TO_BAA": "AZPS", "DIRECTION": "E", "VALUE": "10"}),
            pd.DataFrame({"INTERVAL_START_GMT": ts, "FROM_BAA": "AZPS", "TO_BAA": "PACE", "DIRECTION": "I", "VALUE": "10"}),
        ], ignore_index=True)
        gaps = []
        rows = tf.rows_of(pd.Timestamp("2026-11-18"), x, {"url": "u", "retrieved_at": "t"}, gaps)
        self.assertEqual(set(rows["entity"]), {"caiso:AZPS-PACE"})
        self.assertEqual(set(rows["value"]), {-10.0})  # PACE sends to AZPS: negative from AZPS's side
        self.assertEqual(len(rows), 288)


@unittest.skipUnless(os.path.exists(os.path.join(DIR, "index.json")), "the conditions files are not on this machine")
class TheFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = {}
        for op in OPS:
            with open(os.path.join(DIR, f"{op}.json"), encoding="utf-8") as fh:
                cls.f[op] = json.load(fh)
        with open(os.path.join(DIR, "index.json"), encoding="utf-8") as fh:
            cls.index = json.load(fh)

    def test_held_grids_draw_no_held_strip(self):
        for op in ("pjm", "nyiso", "isone", "miso", "ercot"):
            f = self.f[op]
            for s in ("out", "constraints"):
                self.assertNotEqual(f["strips"][s]["status"], "shown", f"{op} {s}")
            i = f["daily_columns"].index("out_mean")
            self.assertTrue(all(r[i] is None for r in f["daily"]), op)
        self.assertEqual(self.f["pjm"]["strips"]["out"]["status"], "license needed")
        self.assertEqual(self.f["miso"]["strips"]["out"]["status"], "paused")

    def test_demand_is_drawn_for_every_grid(self):
        for op in OPS:
            self.assertEqual(self.f[op]["strips"]["demand"]["status"], "shown")
            i = self.f[op]["daily_columns"].index("demand_peak")
            self.assertTrue(any(r[i] for r in self.f[op]["daily"]), op)

    def test_the_nine_events_are_windows(self):
        ev = sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(ROOT, "site", "data", "regions", "events", "*.json")))
        self.assertEqual(sorted(e["id"] for e in self.index["events"]), ev)
        for op in OPS:
            self.assertEqual({w["id"] for w in self.f[op]["windows"]}, set(ev) | {"recent"})

    def test_rows_are_as_wide_as_their_columns(self):
        for op in OPS:
            f = self.f[op]
            for r in f["daily"][:50]:
                self.assertEqual(len(r), len(f["daily_columns"]))
            for rows in f["hourly"].values():
                for r in rows[:50]:
                    self.assertEqual(len(r), len(f["hourly_columns"]))


class ThePage(unittest.TestCase):
    def test_page_reads_its_files_and_is_in_no_menu(self):
        s = src("site", "lib", "conditions.ts")
        for op in OPS:
            self.assertIn(f"@/data/conditions/{op}.json", s)
        self.assertIn("index: false", src("site", "app", "conditions", "page.tsx"))
        self.assertIn('"/conditions": "review"', src("site", "lib", "release.ts"))   # session 11405 (decision 4 of the weekend page of 28 November 2026, readied): in the menu, its own line, in review
        self.assertIn('"/conditions"', src("site", "scripts", "check-routes.mjs"))


if __name__ == "__main__":
    unittest.main()
