"""Ruling alternative 3 of /explore/interconnection (session 7710, 17 November 2026, branch wip/alt-interconnection-3; not a
default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-interconnection-2026-11-17.md, line 3): the
withdrawn share by MW in the MW view, not by count? On this branch the builder writes mw_withdrawal_rate (withdrawn MW over
MW entered; warehouse/derived/queue_statistics.py stats) and the MW view draws it in its third headline, its chart and a
column. Pinned with the builder's own function on the local CAISO and SPP queue tables where they are on the machine
(warehouse/output, or the folder ERW_TABLES_DIR names): CAISO 2021 0.71 by count, 0.67 by MW; 2017 0.74 to 0.61; 2018 0.70
to 0.76; 2003 0.36 to 0.63 (+27 points, the largest); SPP 2001 0.76 to 0.91; ERCOT has no withdrawn positions, so no share.

    python -m unittest tests.test_alt_interconnection_3 -v
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


def read(name):
    path = os.path.join(TABLES, f"{name}.csv")
    n = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            n += 1
    d = pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False)
    d["year"] = d["queue_date"].str.slice(0, 4)
    return {y: g for y, g in d.groupby("year") if y}


class TheRule(unittest.TestCase):
    def test_the_share_by_mw(self):
        d = pd.DataFrame([dict(status=s, capacity_mw=mw, queue_date="2021-01-01", actual_in_service_date="") for s, mw in
                          (("withdrawn", "300"), ("withdrawn", "100"), ("active", "600"), ("completed", "0"))])
        o = qs.stats(d, "caiso")
        self.assertEqual((o["withdrawal_rate"][0], o["mw_withdrawal_rate"][0]), (0.5, 0.4))

    def test_no_share_where_no_withdrawn_is_held(self):
        d = pd.DataFrame([dict(status="completed", capacity_mw="10", queue_date="2021-01-01", actual_in_service_date="2023-01-01")])
        self.assertNotIn("mw_withdrawal_rate", qs.stats(d, "ercot"))


@unittest.skipUnless(all(os.path.exists(os.path.join(TABLES, f"{t}_interconnection_queue.csv")) for t in ("caiso", "spp")), "the queue tables are not on this machine")
class OnTheLocalTables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.caiso, cls.spp = read("caiso_interconnection_queue"), read("spp_interconnection_queue")

    def pair(self, by, iso, y):
        o = qs.stats(by[y], iso)
        return round(o["withdrawal_rate"][0], 2), round(o["mw_withdrawal_rate"][0], 2)

    def test_caiso(self):
        self.assertEqual({y: self.pair(self.caiso, "caiso", y) for y in ("2021", "2017", "2018", "2003")},
                         {"2021": (0.71, 0.67), "2017": (0.74, 0.61), "2018": (0.70, 0.76), "2003": (0.36, 0.63)})

    def test_spp(self):
        self.assertEqual(self.pair(self.spp, "spp", "2001"), (0.76, 0.91))


if __name__ == "__main__":
    unittest.main()
