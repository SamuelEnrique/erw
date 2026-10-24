"""Session 2492: the Fiji Bureau of Statistics' table 3.7[A] and Electricity 2024's Appendix III (EFL's production and sales).

Energy Research Warehouse (ERW). Tests warehouse/connectors/fbos_fiji_electricity.py on texts built here (made up for the
test, not FBoS's): kWh to MWh, the appendix's figures read as GWh once its totals equal 3.7[A]'s units sold, a cell n/a
with no row and counted, the totals and the sales' value not written; a total that differs, a missing table, years not
consecutive and a figure of another form stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2492 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import fbos_fiji_electricity as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
NL = chr(10)


def key(rows=("2011 837,180,802 740,873,951 288,778", "2012 822,803,910 731,631,798 290,451")):
    return NL.join(["Key Statistics", "3.7[A] Production and Sales of Electricity by Energy Fiji Ltd",
                    "Years Units Produced (kwh) Units Sold (kwh) Sales [$000]"] + list(rows) + ["Source: Energy Fiji Limited"])


def report(rows=("2011 193.0 329.4 218.5 n/a 740.9", "2012 191.7 326.2 201.2 12.5 731.6")):
    return NL.join(["APPENDIX III: SALES OF ELECTRICITY 2011 - 2024", "Sales of Electricity by Type of Consumers",
                    "Industrial Commercial Domestic", "Years Others Total", "Units Sold - kwh (000's)"] + list(rows)
                   + ["Sales Value ($000)", "2011 71,399 137,733 72,340 7,306 288,778"])


class Parse(unittest.TestCase):
    def test_rows(self):
        counts = {}
        t = S.parse(key(), report(), BASE, BASE, counts)
        r = {(a, b, c[:4]): v for a, b, c, v in zip(t.entity, t.variable, t.ts_utc, t.value)}
        self.assertEqual(r[("fbos:fj:efl", "generation", "2011")], 837180.802)
        self.assertEqual(r[("fbos:fj:efl", "sales", "2012")], 731631.798)
        self.assertEqual(r[("fbos:fj:commercial", "sales", "2011")], 329400.0)
        self.assertEqual(r[("fbos:fj:others", "sales", "2012")], 12500.0)
        self.assertNotIn(("fbos:fj:others", "sales", "2011"), r)
        self.assertNotIn("fbos:fj:total", set(t.entity))
        self.assertEqual(len(t), 2 * 2 + 4 * 2 - 1)
        self.assertEqual(counts, {"cells n/a": 1})
        self.assertEqual(set(t.unit), {"MWh"})

    def test_stops(self):
        bad = [(key(), report(("2011 193.0 329.4 218.5 n/a 750.9", "2012 191.7 326.2 201.2 12.5 731.6"))),
               (key(), "nothing"), ("nothing", report()),
               (key(("2011 837,180,802 740,873,951 288,778", "2013 822,803,910 731,631,798 290,451")), report()),
               (key(("2011 837,180,802 740,873,951 288,778", "2012 822803910 731,631,798 290,451")), report())]
        for k, rp in bad:
            with self.assertRaises(RuntimeError):
                S.parse(k, rp, BASE, BASE, {})


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
