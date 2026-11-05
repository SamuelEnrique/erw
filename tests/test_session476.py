"""Session 476: consolidate.py check compared a consolidated table with the member copies the last build left in
warehouse/output/members/, even when a run had written the table since; on 21 October 2026 it read iso_rtm_hub_prices as
MISMATCH and printed only "failed", never why. A member copy older than the table is now not compared (and said so),
and the reasons are printed."""

import os
import sys
import tempfile
import time
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import consolidate as C  # noqa: E402

MEMBERS = [("caiso_rtm_hub_prices", {"market": "caiso_rtm"}), ("ercot_rtm_hub_prices", {"market": "ercot_rtm"})]


def write(path, markets, mtime):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("# a test table\nentity,market,value\n")
        for i, m in enumerate(markets):
            f.write(f"e{i},{m},1\n")
    os.utime(path, (mtime, mtime))


class Check(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = self.tmp.name
        self.stage = os.path.join(self.out, "members")
        os.makedirs(self.stage)
        self.lines = []
        for p in (mock.patch.object(C, "OUT", self.out), mock.patch.object(C, "STAGE", self.stage),
                  mock.patch.object(C, "log", self.lines.append)):
            p.start()
            self.addCleanup(p.stop)
        self.now = time.time()
        write(os.path.join(self.out, "iso_rtm_hub_prices.csv"), ["caiso_rtm"] * 2 + ["ercot_rtm"] * 3, self.now)

    def test_an_older_member_copy_is_not_compared(self):
        write(os.path.join(self.stage, "ercot_rtm_hub_prices.csv"), ["ercot_rtm"] * 2, self.now - 3600)  # the last build's
        write(os.path.join(self.stage, "caiso_rtm_hub_prices.csv"), ["caiso_rtm"] * 2, self.now + 1)
        self.assertEqual(C.check_family("iso_rtm_hub_prices", MEMBERS), [])
        self.assertIn("not compared, older than iso_rtm_hub_prices.csv: ercot_rtm_hub_prices", self.lines[-1])

    def test_a_newer_member_copy_that_differs_is_still_a_mismatch(self):
        write(os.path.join(self.stage, "ercot_rtm_hub_prices.csv"), ["ercot_rtm"] * 2, self.now + 1)
        msgs = C.check_family("iso_rtm_hub_prices", MEMBERS)
        self.assertEqual(msgs, ["iso_rtm_hub_prices: ercot_rtm_hub_prices has 3 rows here, 2 in "
                                + os.path.relpath(os.path.join(self.stage, "ercot_rtm_hub_prices.csv"), C.ROOT)])

    def test_main_prints_the_reasons(self):
        write(os.path.join(self.stage, "ercot_rtm_hub_prices.csv"), ["ercot_rtm"] * 2, self.now + 1)
        with mock.patch.object(C, "read_map", return_value={"iso_rtm_hub_prices": MEMBERS}):
            self.assertEqual(C.main(["check", "--family", "iso_rtm_hub_prices"]), 1)
        self.assertTrue(any("ercot_rtm_hub_prices has 3 rows here, 2 in" in line for line in self.lines))


if __name__ == "__main__":
    unittest.main()
