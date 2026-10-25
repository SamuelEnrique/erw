"""Session 2134: NIFC's WFIGS wildfires.

Energy Research Warehouse (ERW). Tests warehouse/connectors/wfigs_wildfires.py on pages built here in the feature
service's form (made up for the test, not NIFC's): each record an event keyed on its IRWIN id, its discovery day in UTC,
its status from the containment and fire-out times, the sizes as published; a page with an error, a page without
features, a record without a field, a record without an IRWIN id and a discovery time not a time stopping the run; the
query's threshold; the sector rule and the holds. No network.

    python -m unittest tests.test_session2134 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import wfigs_wildfires as W  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}


def rec(**kw):
    a = dict(OBJECTID=1, UniqueFireIdentifier="2020-CAXXX-000001", IrwinID="{AB12CD34-0000-4000-8000-000000000001}",
             IncidentName="Test", POOState="US-CA", POOCounty="Nowhere", InitialLatitude=38.5, InitialLongitude=-121.25,
             FinalAcres=None, IncidentSize=1500, FireCauseGeneral="Lightning", FireCause="Natural",
             FireDiscoveryDateTime=1597536000000, ContainmentDateTime=None, FireOutDateTime=None)
    a.update(kw)
    return {"attributes": a}


class Parse(unittest.TestCase):
    def test_rows(self):
        page = {"features": [rec(), rec(IrwinID="{AB12CD34-0000-4000-8000-000000000002}", FinalAcres=2000.5,
                                        ContainmentDateTime=1598000000000),
                             rec(IrwinID="{AB12CD34-0000-4000-8000-000000000003}", ContainmentDateTime=1598000000000,
                                 FireOutDateTime=1599000000000)], "exceededTransferLimit": True}
        rows, more = W.rows_of(page, BASE)
        self.assertTrue(more)
        self.assertEqual(rows[0]["event_id"], "wfigs:ab12cd34-0000-4000-8000-000000000001")
        self.assertEqual(rows[0]["event_date"], "2020-08-16")
        self.assertEqual(rows[0]["x_discovered_utc"], "2020-08-16T00:00:00Z")
        self.assertEqual(rows[0]["status"], "")
        self.assertEqual(rows[0]["x_final_acres"], "")
        self.assertEqual(rows[0]["x_incident_size_acres"], "1500")
        self.assertEqual(rows[0]["x_unique_fire_id"], "2020-CAXXX-000001")
        self.assertEqual(rows[1]["status"], "contained")
        self.assertEqual(rows[1]["x_final_acres"], "2000.5")
        self.assertEqual(rows[2]["status"], "out")
        self.assertFalse(W.rows_of({"features": [rec()]}, BASE)[1])

    def test_stops(self):
        bad = rec()
        del bad["attributes"]["FireCause"]
        for page in ({"error": {"code": 400}}, {"count": 3}, {"features": [bad]}, {"features": [rec(IrwinID=None)]},
                     {"features": [rec(FireDiscoveryDateTime=None)]}, {"features": [rec(FireDiscoveryDateTime="soon")]}):
            with self.assertRaises(RuntimeError):
                W.rows_of(page, BASE)

    def test_query(self):
        self.assertIn("COALESCE(FinalAcres,IncidentSize) >= 1000", W.where(1000))
        self.assertIn("IncidentTypeCategory = 'WF'", W.where(1000))
        self.assertIn("resultOffset=2000", W.page_url(1000, 2000))


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(W.TABLE), "power")
        self.assertIn(W.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {W.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
