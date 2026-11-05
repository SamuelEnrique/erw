"""Session 516: EIA's nuclear outages by plant, a day.

Energy Research Warehouse (ERW). Held on real records of EIA's API (21 October 2026): one entity a plant with its name,
MW kept, the percent as a ratio; the run reads until a short page (EIA's total counts the plants with blank figures, which
the data leave out) and stops when the pages leave day order or a day has no row. The table is held from /data and
Redivis v1 until uploaded.
"""

import os
import sys
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_nuclear_outages_facility as F  # noqa: E402
import release_v1 as R  # noqa: E402

UNITS = {"capacity-units": "megawatts", "outage-units": "megawatts", "percentOutage-units": "percent"}
REAL = [dict(period="2026-10-21", facility="46", facilityName="Browns Ferry", capacity="3755.8", outage="0", percentOutage="0", **UNITS),
        dict(period="2026-10-21", facility="204", facilityName="Clinton Power Station", capacity="1107.1", outage="0", percentOutage="0", **UNITS),
        dict(period="2026-10-21", facility="210", facilityName="Wolf Creek Generating Station", capacity="1255", outage="0", percentOutage="0", **UNITS)]


class TheRows(unittest.TestCase):
    def test_a_plant_an_entity(self):
        t = F.rows(REAL, "u", "r")
        self.assertEqual(sorted(t["entity"].unique()), ["eia_nuclear_outages:204", "eia_nuclear_outages:210", "eia_nuclear_outages:46"])
        b = t[t["entity"] == "eia_nuclear_outages:46"].set_index("variable")
        self.assertEqual((b.loc["capacity", "value"], b.loc["capacity", "unit"], b.loc["capacity", "node"]), (3755.8, "MW", "Browns Ferry"))
        self.assertEqual((b.loc["outage_share", "value"], b.loc["outage_share", "unit"]), (0.0, "ratio"))

    def test_a_plant_twice_in_a_day_stops(self):
        with self.assertRaises(RuntimeError):
            F.rows([REAL[0], REAL[0]], "u", "r")


def run_with(pages, tmp):
    """main() on pages given in order, offline of the network: each get returns the next page."""
    answers = iter(pages)
    with mock.patch.object(F.ip, "load_key", return_value="k"), \
         mock.patch.object(F.ip, "raw_cached", side_effect=lambda c, u: (__import__("json").dumps({"response": next(answers)}).encode(), {})), \
         mock.patch.object(F.ip, "write_snapshot") as ws:
        rc = F.main(["--from", "2026-10-19", "--out-dir", tmp])
    return rc, ws


class TheReading(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp = tempfile.mkdtemp()

    def page(self, days, total=999):
        return {"total": str(total), "data": [dict(REAL[0], period=d) for d in days]}

    def test_reads_until_a_short_page_whatever_the_total_says(self):
        rc, ws = run_with([self.page(["2026-10-19", "2026-10-20", "2026-10-21"])], self.tmp)
        self.assertEqual(rc, 0)
        self.assertEqual(len(ws.call_args[0][0]), 9)

    def test_a_missing_day_stops(self):
        rc, ws = run_with([self.page(["2026-10-19", "2026-10-21"])], self.tmp)
        self.assertEqual(rc, 1)
        ws.assert_not_called()

    def test_pages_out_of_day_order_stop(self):
        rc, ws = run_with([self.page(["2026-10-21", "2026-10-19"])], self.tmp)
        self.assertEqual(rc, 1)
        ws.assert_not_called()


class TheHold(unittest.TestCase):
    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_nuclear_outages_facility_daily\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_nuclear_outages_facility_daily", R.STORAGE_HELD["eia_nuclear_outages_facility_daily"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_nuclear_outages_facility.py", "tests/test_session516.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()
