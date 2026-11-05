"""Session 2562: NBS's Statistical Yearbook 2026, tables 12.2 and 12.1 (the Maldives' production by island a month, Male's use
by sector a year).

Energy Research Warehouse (ERW). Tests warehouse/connectors/nbs_maldives_electricity.py on sheet rows built here (made up for
the test, not NBS's): a region's heading passed over, kWh to MWh for 12.2 and '000 kWh as MWh for 12.1, the Total column not
written, the shares not taken; an island twice, months that miss their total, a sector missing, sectors that miss their
total, a cell that is not a number, a header row missing and a 12.2 already in thousands (its unit check) stopping the run;
the sector rule and the holds. No network.

    python -m unittest tests.test_session2562 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import nbs_maldives_electricity as N  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"prod": {"retrieved_at": "r", "vintage": "v"}, "use": {"retrieved_at": "r", "vintage": "v"}}
MO = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def island(name, per_month):
    return [name, per_month * 12] + [per_month] * 12


def prod(islands=None, title="Table  12.2 :  MONTHLY ELECTRICITY PRODUCTION BY PUBLIC SECTOR, 2025"):
    islands = islands if islands is not None else [island("K.Male'", 1_000_000), island("K.Vilimale'", 100_000),
                                                   island("K.Hulhumale", 900_000), island("AA.Ukulhas", 5_000)]
    return ([["2025 , dhivehi", None], [title, None], ["(In ' 000 kWh) ", None], ["Locality"] + ["x"] * 13,
             [None, "Total"] + MO, ["Greater Male' Region"] + [None] * 13] + islands + [["Source: State Electric Company Limited"] + [None] * 13])


def use(total=(15_000.0, 16_000.0), rows=None):
    rows = rows if rows is not None else [["Residential ", 8_000.0, 9_000.0], ["Manufacturing and  Commercial", 5_000.0, 5_000.0],
                                          ["Government Buildings", 1_500.0, 1_500.0], ["Public Places and  Schools1_/", 500.0, 500.0]]
    return ([["2025 - 2010 , dhivehi", None, None], ["Table 12.1 :   ELECTRICITY UTILIZATION IN MALE', 2010 - 2025", None, None],
             ["Load Distribution", 2024, 2025, "dhivehi"], ["Total (In ' 000 kWh)", *total, "dhivehi"]] + rows +
            [["%  share", 100, 100], ["Residential ", 53.3, 56.25]])


class Parse(unittest.TestCase):
    def test_rows(self):
        t = N.parse(prod(), use(), BASE)
        r = {(e, v, ts[:7]): x for e, v, ts, x in zip(t.entity, t.variable, t.ts_utc, t.value)}
        self.assertEqual(r[("nbs_mv:k_male", "production", "2025-01")], 1000.0)
        self.assertEqual(r[("nbs_mv:aa_ukulhas", "production", "2025-12")], 5.0)
        self.assertEqual(r[("nbs_mv:male:total", "utilization", "2025-01")], 16000.0)
        self.assertEqual(r[("nbs_mv:male:public_places_schools", "utilization", "2024-01")], 500.0)
        self.assertEqual(len(t), 4 * 12 + 5 * 2)
        self.assertEqual(set(t.freq), {"P1M", "P1Y"})
        self.assertEqual(set(t.unit), {"MWh"})

    def test_stops(self):
        bad = [(prod(islands=[island("K.Male'", 1_000_000), island("K.Male'", 1), island("K.Vilimale'", 1), island("K.Hulhumale", 900_000)]), use()),
               (prod(islands=[["K.Male'", 12_000_000] + [1_000_000] * 11 + [2_000_000], island("K.Vilimale'", 100_000), island("K.Hulhumale", 900_000)]), use()),
               (prod(), use(rows=use()[4:7])),
               (prod(), use(total=(15_000.0, 16_500.0))),
               (prod(islands=[["K.Male'", "n/a"] + [1] * 12, island("K.Vilimale'", 1), island("K.Hulhumale", 1)]), use()),
               (prod()[:4] + prod()[5:], use()),
               (prod(islands=[island("K.Male'", 1_000), island("K.Vilimale'", 100), island("K.Hulhumale", 900)]), use()),
               (prod(title="Table 12.2 : MONTHLY ELECTRICITY CONSUMPTION, 2025"), use())]
        for p, u in bad:
            with self.assertRaises(RuntimeError):
                N.parse(p, u, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(N.NAME), "power")
        self.assertIn(N.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {N.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
