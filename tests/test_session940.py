"""Session 940: Berkeley Lab's PV+battery hybrid PPA prices.

Energy Research Warehouse (ERW). Tests warehouse/connectors/lbnl_hybrid_ppa_prices.py on a sheet built here in LBNL's form
(figures made up for the test, not LBNL's): a greenfield PPA dated by its execution, a retrofit by the retrofit's, two EIA
ids made two entity ids, the combined price; headings not as read and a priced row without a date stopping the run; the
sector rule and the holds. No network.

    python -m unittest tests.test_session940 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import lbnl_hybrid_ppa_prices as H  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def row(**kw):
    r = [None] * len(H.HEAD)
    for k, v in kw.items():
        r[int(k[1:])] = v
    return r


def sheet(rows):
    return pd.DataFrame([[None] * len(H.HEAD), [h or None for h in H.HEAD]] + rows)


class Sheet(unittest.TestCase):
    def test_kinds_ids_and_prices(self):
        t = H.events(sheet([row(c2="2017-04-14 00:00:00", c7="AZ", c8="Pinal_Central", c10="61678", c11="20", c13="10", c28="81.15"),
                            row(c4="2021-10-18 00:00:00", c7="CA", c8="Desert_Sunlight", c10="58542/65857", c11="250", c28="206.4")]), "u", "r").set_index("event_id")
        a = t.loc["lbnl_hybrid:61678:greenfield"]
        self.assertEqual((a.event_date, a.mw, a.price, a.x_bess_mw, a.x_plant, a.entity_ids), ("2017-04-14", 20, 81.15, 10, "Pinal Central", "lbnl_solar:61678"))
        b = t.loc["lbnl_hybrid:58542_65857:retrofit"]
        self.assertEqual((b.event_date, b.entity_ids, b.x_kind), ("2021-10-18", "lbnl_solar:58542;lbnl_solar:65857", "retrofit"))

    def test_stops(self):
        bad = sheet([row(c8="X", c28="1")])
        with self.assertRaises(RuntimeError):
            H.events(bad, "u", "r")
        head = sheet([])
        head.iloc[1, 11] = "PV MW-DC"
        with self.assertRaises(RuntimeError):
            H.events(head, "u", "r")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        name = "lbnl_hybrid_ppa_prices"
        self.assertEqual(B.sector_of(name), "power")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
