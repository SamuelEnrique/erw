"""Session 2617: NAWEC's Annual Activity Report 2022, Table 3, the Gambia's electricity a month in 2022 by source.

Energy Research Warehouse (ERW). Tests warehouse/connectors/nawec_gambia_electricity.py on page lines built here (made up for
the test, not the report's): the table found by its title, the column line read with its stray spaces, each month's five
figures taken (thousands separators removed) with its variable; a title found twice, a month missing, sources that miss the
month's total and a column that misses the Total line stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2617 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import nawec_gambia_electricity as N  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}


def lines(march_total="5,000.00", total_omvg="11010.5", drop=None, twice=False):
    out = ["text", N.TITLE, "Month N AWEC S E NELEC OMVG Karpower Total"]
    for m in N.MONTHS:
        if m == drop:
            continue
        if m == "March":
            out.append(f"March 1,000.00 500.00 1000.5 2,499.50 {march_total}")
        else:
            out.append(f"{m} 1,000.00 500.00 910 2,590.00 5,000.00")
    out += [f"Total 12,000.00 6,000.00 {total_omvg} 30,989.50 60,000.00", "Percentage 20% 10% 18% 52% 100.00%"]
    return out + (["x", N.TITLE] if twice else [])


class Parse(unittest.TestCase):
    def test_rows(self):
        t = N.parse_lines(lines(), BASE)
        r = {(e.split(":")[-1], ts[:7]): (var, v) for e, var, ts, v in zip(t.entity, t.variable, t.ts_utc, t.value)}
        self.assertEqual(r[("nawec", "2022-01")], ("generation", 1000.0))
        self.assertEqual(r[("omvg", "2022-03")], ("imports", 1000.5))
        self.assertEqual(r[("karpower", "2022-03")], ("generation", 2499.5))
        self.assertEqual(r[("total", "2022-12")], ("supply", 5000.0))
        self.assertEqual(len(t), 60)
        self.assertEqual(set(t.unit), {"MWh"})

    def test_stops(self):
        for bad in (lines(twice=True), lines(drop="June"), lines(march_total="5,100.00"), lines(total_omvg="11110.5")):
            with self.assertRaises(RuntimeError):
                N.parse_lines(bad, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(N.NAME), "power")
        self.assertIn(N.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {N.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
