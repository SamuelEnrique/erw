"""Session 955: BLM California's renewable energy rights-of-way.

Energy Research Warehouse (ERW). Tests warehouse/connectors/blm_renewable.py on answers built here in the feature
service's form (made up for the test, not BLM's): the serial number as the id, BLM's dates as days, the disposition in
its own column and status left empty; a field not as read, a truncated answer and a record without a serial number
stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session955 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import blm_renewable as M  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": ""}


def body(serial="CACA   052537", fields=None, more=False):
    a = {f: None for f in M.FIELDS}
    a.update(ProjectName="Alta East X, LLC", SerialNumber=serial, Disposition="Authorized", CaseType="ROW-WIND DEV FAC",
             CaseTypeCode=283003, EffectiveDate=1338361200000, ApplicationDate=1273647600000, BLMAcres=2082, ProjectType="turbines")
    out = {"fields": [{"name": f} for f in (fields or M.FIELDS)], "features": [{"attributes": a}]}
    if more:
        out["exceededTransferLimit"] = True
    return out


class Rows(unittest.TestCase):
    def test_shape(self):
        r = M.rows(0, body(), BASE)[0]
        self.assertEqual((r["entity_id"], r["status"], r["x_disposition"], r["status_date"], r["x_application_date"], r["x_layer"], r["geo"]),
                         ("blm_row:CACA052537", "", "Authorized", "2012-05-30", "2010-05-12", "verified", "US-CA"))

    def test_plss_fields_allowed(self):
        self.assertEqual(len(M.rows(1, body(fields=M.PLSS + M.FIELDS), BASE)), 1)

    def test_stops(self):
        for b in (body(fields=M.FIELDS[:-1]), body(more=True), body(serial="")):
            with self.assertRaises(RuntimeError):
                M.rows(0, b, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(M.NAME), "power")
        self.assertIn(M.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {M.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
