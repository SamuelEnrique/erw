"""Session 2567: BCRPData's monthly series of Peru's crude oil, natural gas liquids and natural gas production (INEI's and
MINEM's figures).

Energy Research Warehouse (ERW). Tests warehouse/connectors/bcrp_peru_hydrocarbons.py on a response built here (made up for
the test, not BCRP's): the three series with their units (kbbl, kbbl, MMcf) as given, an "n.d." cell not written, the series
code kept; a series not asked, a series in another unit, a month missing and a cell that is not a figure stopping the run;
the sector rule and the registration. No network.

    python -m unittest tests.test_session2567 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import bcrp_peru_hydrocarbons as H  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": ""}
TO = "2000-3"
LIST = "Producci" + chr(0xF3) + "n minera e hidrocarburos (miles de unidades recuperables) - "


def doc(ends=None, months=("Jan.2000", "Feb.2000", "Mar.2000"), cell=None):
    ends = ends or [s[1] for s in H.SERIES]
    periods = [{"name": m, "values": [cell(j, m) if cell else str(100 * (j + 1)) for j in range(3)]} for m in months]
    return {"config": {"title": "t", "series": [{"name": LIST + e} for e in ends]}, "periods": periods}


class Parse(unittest.TestCase):
    def test_rows(self):
        t = H.parse(doc(cell=lambda j, m: "n.d." if (j, m) == (1, "Feb.2000") else f"{100 * (j + 1)}.5"), BASE, TO)
        r = {(e, ts[:7]): (v, u) for e, ts, v, u in zip(t.entity, t.ts_utc, t.value, t.unit)}
        self.assertEqual(r[("bcrp_pe:crude_oil", "2000-01")], (100.5, "kbbl"))
        self.assertEqual(r[("bcrp_pe:natural_gas", "2000-03")], (300.5, "MMcf"))
        self.assertNotIn(("bcrp_pe:natural_gas_liquids", "2000-02"), r)
        self.assertEqual(len(t), 8)
        self.assertEqual(set(t.x_series_code), {"PN01882AM", "PN01883AM", "PN01884AM"})

    def test_stops(self):
        e = [s[1] for s in H.SERIES]
        bad = [doc(ends=e[:2] + ["Miner" + chr(0xED) + "a Met" + chr(0xE1) + "lica - Cobre (miles de toneladas)"]),
               doc(ends=e[:2] + ["Hidrocarburos - Gas Natural (miles de metros c" + chr(0xFA) + "bicos)"]),
               doc(months=("Jan.2000", "Mar.2000")),
               doc(cell=lambda j, m: "-5" if j == 0 else "1")]
        for d in bad:
            with self.assertRaises(RuntimeError):
                H.parse(d, BASE, TO)


class Registered(unittest.TestCase):
    def test_sector_and_registration(self):
        self.assertEqual(B.sector_of(H.NAME), "oil;gas")
        self.assertIn(H.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {H.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
