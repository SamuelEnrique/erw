"""Session 38: the home battery game.

Energy Research Warehouse (ERW). No network, no model.
1. The perfect-foresight optimum (site/lib/battery.ts, dynamic programming) equals brute force over all 3^12 action
   sequences on 12-interval toy days: site/scripts/test-battery.mjs, run with Node (23.6 or later runs the TypeScript
   file as it is).
2. Each famous level in site/data/battery_levels.json is real rows: its timestamps and prices equal the ERCOT HB_HUBAVG
   real-time rows of the warehouse table it names, and it holds every interval of its operating day.

    python -m unittest tests.test_session38 -v
"""

import json
import os
import shutil
import subprocess
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
LEVELS = os.path.join(SITE, "data", "battery_levels.json")
OUT = os.path.join(ROOT, "warehouse", "output")


class Optimum(unittest.TestCase):
    def test_dp_equals_brute_force(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node is not installed")
        r = subprocess.run([node, os.path.join("scripts", "test-battery.mjs")], cwd=SITE, capture_output=True, text=True,
                           timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("equals brute force", r.stdout)


def rows_of(table, ts):
    """The ERCOT HB_HUBAVG real-time rows of `table` at the timestamps `ts`, streamed."""
    path = os.path.join(OUT, table + ".csv")
    want = set(ts)
    parts = []
    for ch in pd.read_csv(path, comment="#", usecols=["ts_utc", "value", "market", "node"], chunksize=500_000):
        ch = ch[(ch["node"] == "HB_HUBAVG") & (ch["market"] == "ercot_rtm") & ch["ts_utc"].isin(want)]
        parts.append(ch)
    return pd.concat(parts).sort_values("ts_utc")


class RealRows(unittest.TestCase):
    def setUp(self):
        self.levels = json.load(open(LEVELS, encoding="utf-8"))["levels"]

    def test_five_days_whole(self):
        self.assertEqual(len(self.levels), 5)
        for lv in self.levels:
            a = pd.Timestamp(lv["date"]).tz_localize("America/Chicago")
            need = int(((a + pd.DateOffset(days=1)).normalize() - a).total_seconds() // 900)
            self.assertEqual(len(lv["price"]), need, lv["date"])
            self.assertEqual(len(lv["ts_utc"]), need, lv["date"])
            local = pd.to_datetime(lv["ts_utc"], utc=True).tz_convert("America/Chicago").strftime("%Y-%m-%d")
            self.assertTrue((local == lv["date"]).all(), lv["date"])

    def test_prices_are_the_tables_rows(self):
        by_table = {}
        for lv in self.levels:
            by_table.setdefault(lv["table"], []).append(lv)
        for table, lvs in by_table.items():
            if not os.path.exists(os.path.join(OUT, table + ".csv")):
                self.skipTest(f"{table}.csv is not on this machine")
            got = rows_of(table, [t for lv in lvs for t in lv["ts_utc"]]).set_index("ts_utc")["value"]
            for lv in lvs:
                if table == "iso_rtm_hub_prices" and not set(lv["ts_utc"]) <= set(got.index):
                    continue  # the rolling table has dropped the day since the file was written
                self.assertEqual([float(got[t]) for t in lv["ts_utc"]], lv["price"], lv["date"])


if __name__ == "__main__":
    unittest.main()
