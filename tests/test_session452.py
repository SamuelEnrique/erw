"""Session 452: ercot_peak_premium reads the ERCOT real-time history and the rolling table. Since the daily append step
writes the live days into the year's history too, every interval of the rolling table is in both, and the builder failed
("62208 rows repeat a (hub, interval) across the input tables"). The same interval at the same price is now one row;
the same interval at two prices is still refused."""

import os
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import iso_prices as ip  # noqa: E402
import ercot_peak_premium as pp  # noqa: E402


def write(folder, name, rows):
    with open(os.path.join(folder, name + ".csv"), "w", encoding="utf-8", newline="") as f:
        f.write("# a test table\n" + ",".join(ip.SERIES_COLS) + "\n")
        for ts, value in rows:
            cells = dict(entity="ercot:HB_HUBAVG", variable="spp_rtm", ts_utc=ts, value=str(value), unit=pp.USD,
                         freq="PT15M", node="HB_HUBAVG", source="ercot:NP6-905-CD")
            f.write(",".join(cells.get(c, "") for c in ip.SERIES_COLS) + "\n")


class Inputs(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        patcher = mock.patch.object(ip, "OUT_DIR", self.tmp.name)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.lines = []

    def test_an_interval_in_both_at_the_same_price_is_read_once(self):
        write(self.tmp.name, "ercot_rtm_hub_prices_2026", [("2026-10-19T05:00:00Z", 30.5), ("2026-10-19T05:15:00Z", 31.0)])
        write(self.tmp.name, "ercot_rtm_hub_prices", [("2026-10-19T05:15:00Z", 31.0), ("2026-10-19T05:30:00Z", 29.0)])
        d, names = pp.load(self.lines.append)
        self.assertEqual(names, ["ercot_rtm_hub_prices_2026", "ercot_rtm_hub_prices"])
        self.assertEqual(sorted(d["ts_utc"]), ["2026-10-19T05:00:00Z", "2026-10-19T05:15:00Z", "2026-10-19T05:30:00Z"])
        kept = d[d["ts_utc"] == "2026-10-19T05:15:00Z"]
        self.assertEqual(list(kept["table"]), ["ercot_rtm_hub_prices_2026"])  # the history's row, read first
        self.assertTrue(any("1 intervals in both" in line for line in self.lines))

    def test_an_interval_in_both_at_two_prices_is_still_refused(self):
        write(self.tmp.name, "ercot_rtm_hub_prices_2026", [("2026-10-19T05:15:00Z", 31.0)])
        write(self.tmp.name, "ercot_rtm_hub_prices", [("2026-10-19T05:15:00Z", 35.0)])
        with self.assertRaisesRegex(RuntimeError, "2 rows repeat a \\(hub, interval\\)"):
            pp.load(self.lines.append)

    def test_no_overlap_reads_every_row(self):
        write(self.tmp.name, "ercot_rtm_hub_prices_2025", [("2025-12-31T05:45:00Z", 20.0)])
        write(self.tmp.name, "ercot_rtm_hub_prices", [("2026-10-19T05:00:00Z", 30.5)])
        d, _ = pp.load(self.lines.append)
        self.assertEqual(len(d), 2)
        self.assertFalse(any("intervals in both" in line for line in self.lines))


if __name__ == "__main__":
    unittest.main()
