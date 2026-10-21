"""Sessions 548 and 549: EIA's nuclear outages by reactor, a day, from session 516's connector by plant. Held on a
real record's form: one entity a reactor under its plant, MW kept, the percent as a ratio; the run reads until a short page
and stops when a day is missing; the table is held from /data and Redivis v1 until uploaded.
"""

import json
import os
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_nuclear_outages_generator as N  # noqa: E402
import release_v1 as R  # noqa: E402

UNITS = {"capacity-units": "megawatts", "outage-units": "megawatts", "percentOutage-units": "percent"}


def rec(day, gen="1"):
    return dict(period=day, facility="46", facilityName="Browns Ferry", generator=gen, capacity="1254.7", outage="0", percentOutage="0", **UNITS)


class TheRows(unittest.TestCase):
    def test_a_reactor_an_entity(self):
        t = N.rows([rec("2026-10-21", "1"), rec("2026-10-21", "2")], "u", "r")
        self.assertEqual(sorted(t["entity"].unique()), ["eia_nuclear_outages_gen:46:1", "eia_nuclear_outages_gen:46:2"])
        r = t[(t["entity"] == "eia_nuclear_outages_gen:46:1") & (t["variable"] == "capacity")].iloc[0]
        self.assertEqual((r["value"], r["unit"], r["node"]), (1254.7, "MW", "Browns Ferry, reactor 1"))

    def run_pages(self, pages):
        answers = iter(pages)
        with mock.patch.object(N.ip, "load_key", return_value="k"), \
             mock.patch.object(N.ip, "raw_cached", side_effect=lambda c, u: (json.dumps({"response": {"total": "1", "data": [rec(d) for d in next(answers)]}}).encode(), {})), \
             mock.patch.object(N.ip, "write_snapshot") as ws:
            rc = N.main(["--from", "2026-10-19", "--out-dir", tempfile.mkdtemp()])
        return rc, ws

    def test_reads_until_a_short_page(self):
        rc, ws = self.run_pages([["2026-10-19", "2026-10-20", "2026-10-21"]])
        self.assertEqual(rc, 0)
        self.assertEqual(len(ws.call_args[0][0]), 9)

    def test_a_missing_day_stops(self):
        rc, ws = self.run_pages([["2026-10-19", "2026-10-21"]])
        self.assertEqual(rc, 1)
        ws.assert_not_called()

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_nuclear_outages_generator_daily\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_nuclear_outages_generator_daily", R.STORAGE_HELD["eia_nuclear_outages_generator_daily"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_nuclear_outages_generator.py", "tests/test_session548.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()
