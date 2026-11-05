"""Session 982: the National Inventory of Dams.

Energy Research Warehouse (ERW). Tests warehouse/connectors/usace_nid.py on rows built here in the inventory's form
(made up for the test, not USACE's): the Federal ID as the id, the state's code, a dam with one coordinate left without a
pair; a Federal ID given twice and a state not in the map stopping the run; the entity type dam in the validator; the
sector rule and the holds. No network.

    python -m unittest tests.test_session982 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
sys.path.append(os.path.join(ROOT, "warehouse", "validate"))
import usace_nid as N  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402
import erw_validate as V  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "2026-10-22"}


def frame(rows):
    cols = N.NAMED + list(N.FIELDS)
    out = []
    for r in rows:
        d = {c: "" for c in cols}
        d.update(r)
        out.append(d)
    return pd.DataFrame(out, columns=cols)


ROWS = [{"Dam Name": "Hoover Dam", "Federal ID": "NV10122", "NID ID": "NV10122", "State": "Nevada", "Latitude": "36.0", "Longitude": "-114.7",
         "Purposes": "Hydroelectric, Irrigation", "Owner Names": "Bureau of Reclamation"},
        {"Dam Name": "Half Placed", "Federal ID": "TX00001", "NID ID": "TX00001", "State": "Texas", "Latitude": "30.1"}]


class Dams(unittest.TestCase):
    def test_rows(self):
        t = N.dams(frame(ROWS), BASE).set_index("entity_id")
        h = t.loc["usace_nid:NV10122"]
        self.assertEqual((h.entity_type, h.geo, h.operator, h.purposes), ("dam", "US-NV", "Bureau of Reclamation", "Hydroelectric, Irrigation"))
        x = t.loc["usace_nid:TX00001"]
        self.assertEqual((x.lat, x.lon, x.coordinate_given), ("", "", "lat 30.1; lon "))

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            N.dams(frame([ROWS[0], ROWS[0]]), BASE)
        with self.assertRaises(RuntimeError):
            N.dams(frame([dict(ROWS[0], State="Ontario")]), BASE)

    def test_vocabulary(self):
        self.assertIn("dam", V.ENTITY_TYPES)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(N.NAME), "power")
        self.assertIn(N.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {N.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
