"""Session 2264: the Census Bureau's Quarterly Services Survey benchmark, utilities and hosting.

Energy Research Warehouse (ERW). Tests warehouse/connectors/census_qss.py on a dataset built here in the Census Bureau's
time series form (figures made up for the test, not the Census Bureau's): a revenue figure in millions written as
dollars with its coefficient of variation, an adjusted figure with _sa, a percent change not taken, a figure marked S
counted; a missing section, a period that does not read and a key given twice each stopping the run; the sector rule and
the holds. No network.

    python -m unittest tests.test_session2264 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import census_qss as Q  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

CATS = ["cat_idx,cat_code,cat_desc,cat_indent", '1,22T,"22: Utilities",0', '2,2211T,"2211: Electric Power",1', '3,22121T,"2212: Gas",1',
        '4,2213T,"2213: Water",1', '5,518T,"518: Data Processing, Hosting, and Related Services",1']
DTS = ["dt_idx,dt_code,dt_desc,dt_unit", '1,QREV,"Total Revenue",MLN$', '2,PQREV,"Total Revenue Percent Change",PCT']
ETS = ["et_idx,err_code,err_desc,err_unit", '1,E_QREV,"Coefficient Of Variation For Total Revenue",PCT']
PERS = ["per_idx,per_name", "1,Q1-2024", "2,Q2-2024"]


def dataset(data, pers=PERS, drop=None):
    secs = {"CATEGORIES": CATS, "DATA TYPES": DTS, "ERROR TYPES": ETS, "GEO LEVELS": ["geo_idx,geo_code,geo_desc", '1,US,"U.S. Total"'],
            "TIME PERIODS": pers, "DATA": ["per_idx,cat_idx,dt_idx,et_idx,geo_idx,is_adj,val"] + data}
    return "\n\n".join("\n".join([k] + v) for k, v in secs.items() if k != drop).encode("utf-8")


class Parse(unittest.TestCase):
    def test_rows(self):
        counts = {}
        out = Q.parse(dataset(["1,2,1,0,1,0,140000", "1,2,0,1,1,0,1.5", "1,2,1,0,1,1,141000", "1,2,2,0,1,0,3.0", "2,5,1,0,1,0,S"]), {}, counts)
        got = {(r["entity"], r["variable"], r["ts_utc"]): r for r in out}
        a = got[("census_qss:2211", "total_revenue", "2024-01-01T00:00:00Z")]
        self.assertEqual((a["value"], a["unit"], a["freq"], a["x_cv"]), (140000e6, "USD", "P3M", "1.5"))
        self.assertIn(("census_qss:2211", "total_revenue_sa", "2024-01-01T00:00:00Z"), got)
        self.assertEqual(len(out), 2)
        self.assertEqual(counts, {"marked S": 1})

    def test_stops(self):
        for content, words in [(dataset(["1,2,1,0,1,0,1"], drop="ERROR TYPES"), "sections not as read"),
                               (dataset(["1,2,1,0,1,0,1"], pers=["per_idx,per_name", "1,2024Q1"]), "does not read"),
                               (dataset(["1,2,1,0,1,0,1", "1,2,1,0,1,0,2"]), "given twice")]:
            with self.assertRaises(RuntimeError) as c:
                Q.parse(content, {}, {})
            self.assertIn(words, str(c.exception))


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(Q.TABLE), "power;gas;datacenters")
        self.assertIn(Q.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {Q.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
