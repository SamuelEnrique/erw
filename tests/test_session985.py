"""Session 985: EPA's eGRID subregions.

Energy Research Warehouse (ERW). Tests warehouse/connectors/egrid_subregions.py on a sheet built here in eGRID's form
(figures made up for the test, not EPA's): short tons and lb/MWh converted by their exact factors, the resource mix as a
ratio, eGRID's "--" left out; a field missing and a subregion given twice stopping the run; the sector rule and the
holds. No network.

    python -m unittest tests.test_session985 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import egrid_subregions as G  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}


def frame(rows):
    cols = ["YEAR", "SUBRGN", "SRNAME"] + list(G.FIELDS)
    out = []
    for r in rows:
        d = {c: 0.1 for c in cols}
        d.update(r)
        out.append(d)
    return pd.DataFrame(out, columns=cols)


ROW = {"YEAR": 2023, "SUBRGN": "ERCT", "SRNAME": "ERCOT All", "SRCO2AN": 1000.0, "SRCO2RTA": 800.0, "SRGSPR": 0.45, "SRNBCO2": "--"}


class Build(unittest.TestCase):
    def test_rows(self):
        s = G.build(frame([ROW]), BASE).set_index("variable")
        self.assertAlmostEqual(s.loc["co2_emissions"].value, 907.18474)
        self.assertAlmostEqual(s.loc["co2_rate"].value, 362.873896)
        self.assertEqual((s.loc["share_gas"].value, s.loc["share_gas"].unit), (0.45, "ratio"))
        self.assertNotIn("co2_rate_nonbaseload", s.index)
        self.assertEqual(s.loc["co2_rate"].entity, "egrid:ERCT")

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            G.build(frame([ROW]).drop(columns=["SRNGENAN"]), BASE)
        with self.assertRaises(RuntimeError):
            G.build(frame([ROW, ROW]), BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(G.NAME), "power;carbon")
        self.assertIn(G.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {G.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
