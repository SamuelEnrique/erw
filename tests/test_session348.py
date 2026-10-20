"""Session 348: interconnection queue statistics by ISO and entry year, iso_queue_statistics.

Energy Research Warehouse (ERW). The rules are tested on fixtures (rows made here, not data); the table is read where
this machine holds it.

    python -m unittest tests.test_session348 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import queue_statistics as qs  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output", "iso_queue_statistics.csv")


def rows(*r):
    return pd.DataFrame([dict(status=s, capacity_mw=m, queue_date=q, actual_in_service_date=a) for s, m, q, a in r])


class TheRules(unittest.TestCase):
    def test_the_four_groups_and_the_rate(self):
        q = rows(("withdrawn", "100", "2015-01-01", None), ("completed", "50", "2015-03-01", "2018-03-01"),
                 ("active", "20", "2015-06-01", None), ("suspended", None, "2015-07-01", None), ("", "5", "2015-08-01", None))
        s = qs.stats(q, "caiso")
        self.assertEqual(s["positions_entered"][0], 5)
        self.assertEqual((s["positions_withdrawn"][0], s["positions_operating"][0], s["positions_waiting"][0], s["positions_status_not_stated"][0]), (1, 1, 2, 1))
        self.assertEqual(s["mw_waiting"][0], 20, "a position with no MW is counted, not summed")
        self.assertAlmostEqual(s["withdrawal_rate"][0], 0.2)
        self.assertAlmostEqual(s["wait_years_median"][0], (pd.Timestamp("2018-03-01") - pd.Timestamp("2015-03-01")).days / 365.25)

    def test_ercot_has_no_withdrawn_count_and_miso_no_wait(self):
        q = rows(("completed", "50", "2015-03-01", "2018-03-01"), ("active", "20", "2015-06-01", None))
        self.assertNotIn("withdrawal_rate", qs.stats(q, "ercot"))
        self.assertNotIn("positions_withdrawn", qs.stats(q, "ercot"))
        self.assertNotIn("wait_years_median", qs.stats(q, "miso"))
        self.assertNotIn("wait_positions", qs.stats(q, "isone"))

    def test_an_in_service_date_before_the_queue_date_is_not_a_wait(self):
        q = rows(("completed", "50", "2018-03-01", "2015-03-01"))
        s = qs.stats(q, "nyiso")
        self.assertEqual(s["wait_positions"][0], 0)
        self.assertNotIn("wait_years_median", s)

    def test_spp_says_its_date_may_be_requested(self):
        self.assertIn("requested", qs.rule_words("spp", "wait_years_median"))
        self.assertNotIn("requested", qs.rule_words("caiso", "wait_years_median"))


class TheTable(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(OUT):
            self.skipTest("iso_queue_statistics is not on this machine")
        self.d = pd.read_csv(OUT, comment="#")

    def test_six_isos_and_entities_led_by_the_grid(self):
        self.assertEqual(sorted(self.d.x_iso.unique()), ["CAISO", "ERCOT", "ISO-NE", "MISO", "NYISO", "SPP"])
        self.assertTrue(self.d.entity.str.match(r"^(ercot|caiso|nyiso|miso|spp|isone):queue_\d{4}$").all())

    def test_the_parts_add_up(self):
        w = self.d.pivot_table(index="entity", columns="variable", values="value", aggfunc="first").fillna(0)
        parts = w["positions_operating"] + w["positions_waiting"] + w["positions_status_not_stated"] + w.get("positions_withdrawn", 0)
        self.assertTrue((parts == w["positions_entered"]).all())
        self.assertNotIn("withdrawal_rate", set(self.d[self.d.x_iso == "ERCOT"].variable))

    def test_no_hash_in_a_row(self):
        with open(OUT, encoding="utf-8") as f:
            self.assertFalse(any("#" in line for line in f if not line.startswith("#")), "a reader that skips comments would cut the row")


if __name__ == "__main__":
    unittest.main()
