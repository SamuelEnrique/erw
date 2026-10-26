"""Session 2770: Statbel's beSTAT export, Belgium's gross electricity production by product, 2018 to 2025.

Energy Research Warehouse (ERW). Tests warehouse/connectors/statbel_electricity_production.py on a CSV built here (made up for
the test, not Statbel's): the total and the products read, GWh stated as MWh, the products checked against the total; a broken
sum, a missing year, a product given twice, a value not a number and an indicator not expected stopping the run; the sector rule
and the holds. No network.

    python -m unittest tests.test_session2770 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import statbel_electricity_production as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def csv(total=30.0, drop=None, twice=False, value=None, indicator="Gross electricity production"):
    lines = [",".join(f'"{h}"' for h in A.HEADER)]
    for grp, prod, v in (("Nuclear energy", "Nuclear energy", 20.0), ("Renewables and biofuels", "Wind", 10.0), ("", "", total)):
        for y in A.YEARS:
            if drop == (prod, y):
                continue
            x = value if (value is not None and prod == "Wind" and y == "2025") else v
            lines.append(f'"All products","{grp}","{prod}","{indicator}","{y}",{x}')
    if twice:
        lines.append(lines[1])
    return ("\n".join(lines) + "\n").encode("utf-8")


class Parse(unittest.TestCase):
    def test_rows(self):
        vals, keys = A.parse(csv())
        t = A.frame(vals, keys, dict(source="s", source_url="u", retrieved_at="r", vintage="v"))
        self.assertEqual(len(t), 3 * 8)
        w = t[(t.entity == "statbel_gep:be:renewables_and_biofuels:wind") & (t.ts_utc == "2025-01-01T00:00:00Z")]
        self.assertEqual(w.value.iloc[0], 10000.0)                              # 10 GWh stated as MWh
        self.assertEqual(w.node.iloc[0], "Renewables and biofuels: Wind")
        self.assertIn("statbel_gep:be:total", set(t.entity))

    def test_stops(self):
        for content in (csv(total=31.0), csv(drop=("Wind", "2019")), csv(twice=True), csv(value='"n.a."'),
                        csv(indicator="Net electricity production")):
            with self.assertRaises(RuntimeError):
                A.parse(content)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
