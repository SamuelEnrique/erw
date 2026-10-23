"""Session 854: generation with a signed interconnection agreement, derived from Berkeley Lab's Queued Up file.

Energy Research Warehouse (ERW). Tests warehouse/derived/interconnection_agreements.py on a queue built here (requests
made up for the test): a request counts when it is still in the queue and is marked signed by its phase or its date,
not when it gives an operation date; the grid, fuel and year sums; the sector rule, the tier and the holds. No network.

    python -m unittest tests.test_session854 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import interconnection_agreements as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def req(i, status, region, mw, phase="", ia="", on="", fuel="Solar"):
    return dict(entity_id=f"lbnl:x:{i}", name=f"r{i}", geo="US-TX", lat="", lon="", capacity_mw=str(mw), status=status, operator="",
                source="lbnl:queued_up", source_url="u", retrieved_at="r", vintage="2025-12-31", q_id=str(i), region=region,
                state="TX", county="Ector", utility="", lbnl_entity="E", type_clean=fuel, ia_date=ia, ia_phase=phase,
                q_date="2020-01-01", prop_date="", on_date=on)


Q = pd.DataFrame([
    req(1, "active", "ERCOT", 100, phase="IA Executed"),
    req(2, "active", "ERCOT", 50, ia="2024-05-01", fuel="Battery"),
    req(3, "suspended", "PJM", 20, phase="IA Executed", ia="2023-02-01"),
    req(4, "active", "PJM", 300, phase="Facility Study"),
    req(5, "active", "ERCOT", 70, phase="IA Executed", on="2025-06-01"),
    req(6, "operating", "ERCOT", 900, phase="IA Executed", ia="2019-01-01"),
    req(7, "withdrawn", "PJM", 40, phase="IA Executed"),
])


class Signed(unittest.TestCase):
    def test_which_requests_count(self):
        t, counts, still = A.signed(Q)
        self.assertEqual(t.queue_id.tolist(), ["1", "2", "3"])
        self.assertEqual(t.signed_by.tolist(), ["phase", "date", "phase+date"])
        self.assertEqual(counts, {"in the queue": 5, "phase and date": 1, "phase only": 2, "date only": 1,
                                  "with an operation date, left out": 1})

    def test_the_sums(self):
        t, _, still = A.signed(Q)
        s = A.summary(t, still).set_index(["entity", "variable", "ts_utc"])["value"]
        snap = A.SNAPSHOT_TS
        self.assertEqual(s[("interconnection_agreements:ercot", "mw_signed", snap)], 150.0)
        self.assertEqual(s[("interconnection_agreements:ercot", "active_mw", snap)], 220.0)
        self.assertEqual(s[("interconnection_agreements:us", "projects_signed", snap)], 3.0)
        self.assertEqual(s[("interconnection_agreements:ercot:battery", "mw_signed", snap)], 50.0)
        self.assertEqual(s[("interconnection_agreements:pjm", "mw_signed_in_year", "2023-01-01T00:00:00Z")], 20.0)
        self.assertAlmostEqual(s[("interconnection_agreements:pjm", "signed_share_pct", snap)], 100 * 20 / 320, places=2)


class Registered(unittest.TestCase):
    def test_sector_tier_holds(self):
        for t in ("interconnection_agreements_signed", "interconnection_agreements_by_grid"):
            self.assertEqual(B.sector_of(t), "power")
            self.assertIn(t, R.STORAGE_HELD)
            with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
                self.assertIn(f"  - {t}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
