"""Session 978: EIA's International Energy Outlook 2023.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_ieo.py on API rows built here in EIA's form (figures
made up for the test, not EIA's): units scaled, the region in the entity and the node, a value EIA leaves empty left
out; a unit not in the map and a table not asked for stopping the run; every facet in the page's sort; the sector rule
and the holds. No network.

    python -m unittest tests.test_session978 -v
"""

import os
import sys
import unittest
from urllib.parse import parse_qsl, urlparse

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_ieo as I  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": ""}


def row(table="20", unit="bill kWh", value="124.9", region="6-2", rname="United States", sid="pgdis_nu_tot_bkwh", name="Net generation : Nuclear"):
    return {"period": "2030", "history": "PROJECTION", "scenario": "Reference", "tableId": table, "tableName": "t", "seriesId": sid,
            "seriesName": name, "regionId": region, "regionName": rname, "value": value, "unit": unit}


class Rows(unittest.TestCase):
    def test_shape(self):
        out = pd.DataFrame(I.rows([row(), row(table="1", unit="quad Btu", value="97.5", region="0-0", rname="No Regional Tables",
                                               sid="cnsm_pe_afm_qbtu", name="Energy use : Africa and Middle East"), row(value=None)], BASE))
        self.assertEqual(len(out), 2)
        g = out[out.variable == "generation"].iloc[0]
        self.assertEqual((g.entity, g.value, g.unit, g.node), ("eia_ieo2023:20:6-2:pgdis_nu_tot_bkwh", 124900000.0, "MWh", "Net generation : Nuclear : United States"))
        c = out[out.variable == "consumption"].iloc[0]
        self.assertEqual((c.value, c.unit, c.node), (97500.0, "TBtu", "Energy use : Africa and Middle East"))

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            I.rows([row(unit="TWh")], BASE)
        with self.assertRaises(RuntimeError):
            I.rows([row(table="63")], BASE)

    def test_sort_holds_every_facet(self):
        q = dict(parse_qsl(urlparse(I.url_of("k", 0)).query))
        self.assertEqual([q[f"sort[{i}][column]"] for i in range(4)], ["tableId", "regionId", "seriesId", "period"])


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(I.NAME), "power;carbon")
        self.assertIn(I.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {I.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
