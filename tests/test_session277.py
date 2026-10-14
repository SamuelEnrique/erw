"""Session 277: stale and empty, round two.

Energy Research Warehouse (ERW). Two fixes at their cause: ERCOT's zone load, whose files ERCOT posts once a month,
failed when its window asked for hours ERCOT had not posted (now "stale at source", a skip by the CARB rule of session
271); and the zone price history's CAISO part, which only the GitHub runner was asked to refresh, where the table is
not held (now a weekly step of the data machine). Held here, with no request: both, and that a run that read no file
at all still fails.
"""

import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import ercot_zone_load as ezl  # noqa: E402
import iso_prices as ip  # noqa: E402
import zone_load as zl  # noqa: E402

EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheZoneLoadLag(unittest.TestCase):
    def run_with(self, pull):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(ip, "RAW") as raw, \
                mock.patch.object(ip, "write_status"), mock.patch.dict(os.environ, {"ERW_SKIP_EXIT": "75"}), \
                redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()) as err:
            raw.open = lambda *a: None
            rc = zl.run(ezl.SPEC, pull, ["--out-dir", d])
        return rc, out.getvalue() + err.getvalue()

    def test_files_read_with_no_hour_in_the_window_is_stale_at_source(self):
        rc, said = self.run_with(lambda log, first, counter: ([], ["Native_Load_2026.zip: 6,551 hours, to 2026-09-30 23:00 Central"]))
        self.assertEqual(rc, 75)
        self.assertIn("SKIPPED: stale at source: the operator's files hold no hour on or after", said)

    def test_no_file_read_at_all_still_fails(self):
        rc, said = self.run_with(lambda log, first, counter: ([], []))
        self.assertEqual(rc, 1)
        self.assertIn("the operator answered no hour", said)


class TheZoneHistoryStep(unittest.TestCase):
    def test_a_weekly_step_asks_caiso_only(self):
        text = src("warehouse", "run_data_machine_tables.sh")
        steps = [tuple(line.strip().strip('"').split("|")) for line in text.split("TABLE_STEPS=(", 1)[1].split("\n)", 1)[0].strip().splitlines()]
        self.assertEqual([s[:3] for s in steps[18:]], [("dm_zone_history_pull", "-", "weekly"), ("dm_zone_history_write", "iso_zone_prices_history", "weekly")])
        for s in steps[18:]:
            self.assertIn("--iso caiso --recent 9", s[3])
            for word in ("nyiso", "isone", "spp", "miso"):
                self.assertNotIn(word, s[3])
        self.assertIn("WEEKLY_LIVE='^(iso_zone_prices_history|", text)
        self.assertNotIn(EM, text)


if __name__ == "__main__":
    unittest.main()
