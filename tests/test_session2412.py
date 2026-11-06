"""Session 2412: EIA's U.S. net imports of crude oil and petroleum products by country, a month (petroleum/move/neti).

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_net_imports.py's row reader and its sum on records built
here in the form EIA's API v2 gives them (made up for the test, not EIA's figures): the partner's code, a group's area
code, a record without a value, a negative net import; a product, unit or period not understood and a key twice stopping
the run; crude oil plus products against the total; the sector rule, the live-set hold and the release hold (public). No
network.

    python -m unittest tests.test_session2412 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import eia_net_imports as N  # noqa: E402
import build_coverage as B  # noqa: E402


def rec(product, value, area="NUS-NCA", name="CAN", period="2025-05", series=None, units="MBBL/D"):
    return {"period": period, "duoarea": area, "area-name": name, "product": product, "process": "IMN", "series": series or f"S_{product}_{area}",
            "series-description": f"U.S. Net Imports from {name} of {product} (Thousand Barrels per Day)", "value": value, "units": units}


class Rows(unittest.TestCase):
    def test_rows(self):
        t = N.rows([rec("EPC0", "3800"), rec("EPP0", "-700"), rec("EP00", "3100"), rec("EP00", "778", area="NUS-ME0", name="NA"),
                    rec("EPC0", None, area="NUS-NMX", name="MEX")], "u", "2026-10-24T10:43:00Z")
        self.assertEqual(len(t), 4)
        self.assertEqual(set(t.unit), {"kbbl/d"})
        self.assertEqual(t[t.variable == "net_imports_products"].value.iloc[0], -700.0)
        self.assertEqual(sorted(t.x_partner.unique()), ["CAN", "NUS-ME0"])
        self.assertEqual(t.ts_utc.iloc[0], "2025-05-01T00:00:00Z")

    def test_stops(self):
        for bad in ([rec("EPJK", "1")], [rec("EPC0", "1", units="MBBL")], [rec("EPC0", "1", period="2025")],
                    [rec("EPC0", "1"), rec("EPC0", "2")]):
            with self.assertRaises(RuntimeError):
                N.rows(bad, "u", "r")

    def test_sum(self):
        t = N.rows([rec("EPC0", "100"), rec("EPP0", "50"), rec("EP00", "150"),
                    rec("EPC0", "10", area="NUS-NBR", name="BRA"), rec("EPP0", "5", area="NUS-NBR", name="BRA"), rec("EP00", "20", area="NUS-NBR", name="BRA"),
                    rec("EPP0", "7", area="NUS-NMX", name="MEX"), rec("EP00", "99", area="NUS-NMX", name="MEX")], "u", "r")
        checked, bad = N.check_sum(t)
        self.assertEqual(checked, 2)                 # Mexico has no crude oil record, so it is not summed
        self.assertEqual(list(bad.index), [("NUS-NBR", "2025-05-01T00:00:00Z")])
        self.assertEqual(bad.iloc[0], 5.0)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(N.NAME), "oil;products")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {N.NAME}\n", f.read().replace("\r\n", "\n"))
        with open(os.path.join(ROOT, "warehouse", "redivis", "release_v1.py"), encoding="utf-8") as f:
            self.assertIn(f'"{N.NAME}"', f.read())


if __name__ == "__main__":
    unittest.main()
