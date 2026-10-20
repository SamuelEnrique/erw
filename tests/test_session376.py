"""Session 376: the real-time node prices kept before ERCOT's seven-day list loses them. node_basis.py --daily (a
rebuild only when the saved files hold a whole real-time day node_basis_daily does not, a skip otherwise), the step
dm_node_rt of the data machine's run after the node prices' own pull, and table_stores.py --no-redivis for
node_basis_daily (Redivis's storage is full: no session uploads it)."""

import datetime as dt
import os
import re
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import node_basis as nb  # noqa: E402
import table_stores as ts  # noqa: E402


def zips_for(d, days, drop=()):
    """Empty files named as ERCOT names the 15-minute real-time files, for whole Central days."""
    for day in days:
        start = dt.datetime.strptime(day, "%Y-%m-%d")
        for k in range(1, 4 * nb.hours_in(day) + 1):
            end = start + dt.timedelta(minutes=15 * k)
            if end in drop:
                continue
            name = f"cdr.00012301.0000000000000000.{end:%Y%m%d}.000202403.SPPHLZNP6905_{end:%Y%m%d}_{end:%H%M}_csv.zip"
            open(os.path.join(d, name), "wb").close()


class Days(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_a_day_is_whole_with_all_its_intervals(self):
        zips_for(self.d, ["2026-10-18", "2026-10-19"])
        self.assertEqual(nb.rt_days_saved(self.d), ["2026-10-18", "2026-10-19"])

    def test_the_day_closed_by_midnight(self):
        # the file stamped 00:00 of the 20th closes the 19th; without it the 19th is not whole
        zips_for(self.d, ["2026-10-19"], drop={dt.datetime(2026, 10, 20, 0, 0)})
        self.assertEqual(nb.rt_days_saved(self.d), [])

    def test_a_file_posted_twice_counts_once(self):
        zips_for(self.d, ["2026-10-18"], drop={dt.datetime(2026, 10, 18, 12, 0)})
        open(os.path.join(self.d, "cdr.00012301.0000000000000000.20261018.114702248.SPPHLZNP6905_20261018_1145_csv.zip"), "wb").close()
        self.assertEqual(nb.rt_days_saved(self.d), [])

    def test_gained(self):
        self.assertEqual(nb.gained(["2026-10-18", "2026-10-19"], ["2026-10-17", "2026-10-18"]), ["2026-10-19"])
        self.assertEqual(nb.gained(["2026-10-18"], ["2026-10-18"]), [])

    def test_nothing_gained_is_a_skip(self):
        with mock.patch.object(nb, "rt_days_saved", lambda: ["2026-10-18"]), \
             mock.patch.object(nb, "rt_days_held", lambda path=None: ["2026-10-18"]), \
             mock.patch.object(nb, "build", side_effect=AssertionError("no build when nothing is gained")), \
             mock.patch.dict(os.environ, {"ERW_SKIP_EXIT": "75"}):
            self.assertEqual(nb.main(["--daily", "--out-dir", self.d]), 75)


class Stores(unittest.TestCase):
    def test_no_redivis_leaves_out_the_draft(self):
        self.assertEqual([s for s, _, _ in ts.commands("node_basis_daily")], ["validate", "coverage", "archive", "redivis"])
        self.assertEqual([s for s, _, _ in ts.commands("node_basis_daily", redivis=False)], ["validate", "coverage", "archive"])
        ran = []

        class R:
            returncode = 0

        def run(cmd, **k):
            ran.append(os.path.basename(cmd[1]))
            return R()
        d = tempfile.mkdtemp()
        try:
            self.assertTrue(ts.stores("node_basis_daily", run=run, log=lambda *a: None, runs=d, redivis=False))
        finally:
            shutil.rmtree(d, ignore_errors=True)
        self.assertNotIn("upload.py", ran)


class Step(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "warehouse", "run_data_machine.sh"), encoding="utf-8") as f:
            self.sh = f.read()

    def test_after_the_node_prices_pull(self):
        self.assertLess(self.sh.index('table_stores dm_node_stores "$NODES" "$was"'), self.sh.index("soft_step dm_node_rt "))
        self.assertLess(self.sh.index("soft_step dm_node_rt "), self.sh.index("soft_step dm_carb_auction"))
        self.assertIn('soft_step dm_node_rt "$PYTHON" warehouse/derived/node_basis.py --daily', self.sh)

    def test_node_basis_daily_never_goes_to_redivis(self):
        line = [ln for ln in self.sh.splitlines() if "dm_node_rt_stores_daily" in ln and "soft_step" in ln]
        self.assertEqual(len(line), 1)
        self.assertIn("--no-redivis", line[0])
        self.assertNotRegex(self.sh, r'table_stores \S+ "\$NODE_DAILY"')


if __name__ == "__main__":
    unittest.main()
