"""Ruling alternative 1 of /explore/interconnection (session 7710, 17 November 2026, branch wip/alt-interconnection-1; not a
default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-interconnection-2026-11-17.md, line 1): ERCOT's
"Reached operation" is an agreement signed, not a plant running; keep the fix in words on the page, or read operation from
an in-service day? The queue connector on main reads it from the day of approval to synchronize (actual_in_service_date)
from its pull after session 7022; the statistics of the pulls held still count the agreements. On this branch the
builder (warehouse/derived/queue_statistics.py stats, OPERATION_BY_DAY) applies the same reading to every pull: a
completed ERCOT position without that day is waiting; and the page takes the common words again ("Reached operation").
Pinned with the builder's own function on made-up rows and on the local queue table where it is on the machine
(warehouse/output, or the folder ERW_TABLES_DIR names; the pull of 19 October 2026): positions operating by entry year
2018 32 to 21 (6,514 to 4,474 MW), 2020 48 to 12, 2021 73 to 15, 2022 116 to 15 (24,127 to 2,407 MW), 2023 117 to 7,
2024 89 to 9, 2025 44 to 0, as the impact file counts the queue file.

    python -m unittest tests.test_alt_interconnection_1 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import queue_statistics as qs  # noqa: E402

TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
CSV = os.path.join(TABLES, "ercot_interconnection_queue.csv")


class TheRule(unittest.TestCase):
    def frame(self):
        rows = [("completed", "2024-05-01", 100), ("completed", "", 200), ("active", "", 50), ("completed", " ", 25)]
        return pd.DataFrame([dict(status=s, actual_in_service_date=d, capacity_mw=str(mw), queue_date="2022-01-15", proposed_in_service_date="") for s, d, mw in rows])

    def test_ercot_is_operating_only_with_a_day(self):
        o = qs.stats(self.frame(), "ercot")
        self.assertEqual((o["positions_operating"][0], o["mw_operating"][0], o["positions_waiting"][0], o["mw_waiting"][0]), (1.0, 100.0, 3.0, 275.0))

    def test_another_queue_reads_its_status_as_before(self):
        o = qs.stats(self.frame(), "caiso")
        self.assertEqual((o["positions_operating"][0], o["positions_waiting"][0]), (3.0, 1.0))


@unittest.skipUnless(os.path.exists(CSV), "the ERCOT queue table is not on this machine")
class OnTheLocalTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        n = 0
        with open(CSV, encoding="utf-8") as f:
            for line in f:
                if not line.startswith("#"):
                    break
                n += 1
        d = pd.read_csv(CSV, skiprows=n, dtype=str, keep_default_na=False)
        d["year"] = d["queue_date"].str.slice(0, 4)
        cls.by = {y: g for y, g in d.groupby("year") if y}

    def test_positions_operating_by_entry_year(self):
        got = {y: int(qs.stats(self.by[y], "ercot")["positions_operating"][0]) for y in ("2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025")}
        self.assertEqual(got, {"2018": 21, "2019": 7, "2020": 12, "2021": 15, "2022": 15, "2023": 7, "2024": 9, "2025": 0})

    def test_the_mw(self):
        self.assertEqual(round(qs.stats(self.by["2022"], "ercot")["mw_operating"][0]), 2407)
        self.assertEqual(round(qs.stats(self.by["2018"], "ercot")["mw_operating"][0]), 4474)

    def test_main_reading_of_the_same_pull(self):
        completed = {y: int((g["status"] == "completed").sum()) for y, g in self.by.items()}
        self.assertEqual((completed["2018"], completed["2022"], completed["2025"]), (32, 116, 44))


if __name__ == "__main__":
    unittest.main()
