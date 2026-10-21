"""Session 523: EIA's nuclear outages by plant, read in two windows, 2007 to 2014 and 2015 on.

Energy Research Warehouse (ERW). The windows run in order and meet; a run with no --from reads both, the first with
EIA's end parameter and the second open-ended (the address session 516's saved pages answer); a page past its window's
end, or a day missing where the windows meet, stops the run.
"""

import datetime as dt
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eia_nuclear_outages_facility as F  # noqa: E402

UNITS = {"capacity-units": "megawatts", "outage-units": "megawatts", "percentOutage-units": "percent"}


def rec(day):
    return dict(period=day, facility="46", facilityName="Browns Ferry", capacity="3755.8", outage="0", percentOutage="0", **UNITS)


class TheWindows(unittest.TestCase):
    def test_they_meet_in_order(self):
        w = F.WINDOWS
        self.assertEqual(w[0][0], "2007-01-01")
        self.assertIsNone(w[-1][1])
        for (a, b), (c, _) in zip(w, w[1:]):
            self.assertEqual(dt.date.fromisoformat(b) + dt.timedelta(days=1), dt.date.fromisoformat(c))

    def run_pages(self, pages):
        asked, answers = [], iter(pages)

        def cached(c, url):
            asked.append(url)
            return json.dumps({"response": {"total": "1", "data": [rec(d) for d in next(answers)]}}).encode(), {}
        with mock.patch.object(F, "WINDOWS", [("2014-12-30", "2014-12-31"), ("2015-01-01", None)]), \
             mock.patch.object(F.ip, "load_key", return_value="k"), \
             mock.patch.object(F.ip, "raw_cached", side_effect=cached), \
             mock.patch.object(F.ip, "write_snapshot") as ws:
            rc = F.main(["--out-dir", tempfile.mkdtemp()])
        return rc, ws, asked

    def test_both_windows_are_read_and_written_together(self):
        rc, ws, asked = self.run_pages([["2014-12-30", "2014-12-31"], ["2015-01-01", "2015-01-02"]])
        self.assertEqual(rc, 0)
        self.assertIn("end=2014-12-31", asked[0])
        self.assertNotIn("end=", asked[1])
        self.assertEqual(len(ws.call_args[0][0]), 4 * 3)

    def test_a_page_past_its_window_stops(self):
        rc, ws, _ = self.run_pages([["2014-12-30", "2015-01-01"], ["2015-01-01"]])
        self.assertEqual(rc, 1)
        ws.assert_not_called()

    def test_a_day_missing_where_they_meet_stops(self):
        rc, ws, _ = self.run_pages([["2014-12-30"], ["2015-01-01"]])
        self.assertEqual(rc, 1)
        ws.assert_not_called()


if __name__ == "__main__":
    unittest.main()
