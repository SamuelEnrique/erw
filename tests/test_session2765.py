"""Session 2765: INE's 2021 census table of Spain's dwellings by their electricity consumption.

Energy Research Warehouse (ERW). Tests warehouse/connectors/ine_es_dwellings_electricity.py on a CSV built here (made up for the
test, not INE's): the areas read from their "<code> <name>" cells at four levels, the thousands points read, the median stated
in MWh, the items made variables; each total checked against its classes, occasional use against its bands, and each parent
area's counts against its parts; a broken class sum, a broken area sum, an item not expected and a value not a number stopping
the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2765 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import ine_es_dwellings_electricity as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def counts(total):
    """Counts for an area of `total` dwellings: 10 per cent empty, the rest in classes that add to it."""
    v = {k: 0.0 for k in A.ITEMS.values()}
    v.update(dwellings_empty=total * 0.1, dwellings_low_consumption=total * 0.1, dwellings_occasional_251_500_kwh=total * 0.1,
             dwellings_occasional_501_750_kwh=total * 0.1, dwellings_1001_2000_kwh=total * 0.6, median_annual_consumption=2196)
    v["dwellings_occasional_use"] = v["dwellings_occasional_251_500_kwh"] + v["dwellings_occasional_501_750_kwh"]
    v["dwellings_total"] = total
    return v


def fmt(x):
    return f"{int(x):,}".replace(",", ".")


def csv(nat_total=2000, item=None, value=None, classes_ok=True):
    inv = {v: k for k, v in A.ITEMS.items()}
    lines = [";".join(A.HEADER)]
    areas = [("Total Nacional", "", "", "", counts(nat_total)), ("Total Nacional", "01 Andalucía", "", "", counts(2000)),
             ("Total Nacional", "01 Andalucía", "04 Almería", "", counts(2000)),
             ("Total Nacional", "01 Andalucía", "04 Almería", "04001 Abla", counts(1000)),
             ("Total Nacional", "01 Andalucía", "04 Almería", "04002 Abrucena", counts(1000))]
    if not classes_ok:
        areas[4][4]["dwellings_total"] = 1010
    for a in areas:
        for v, x in a[4].items():
            s = value if (value is not None and a[3] == "04001 Abla" and v == "dwellings_empty") else fmt(x)
            lines.append(";".join(list(a[:4]) + [inv[v], s]))
    if item:
        lines.append(";".join(["Total Nacional", "", "", "", item, "1"]))
    return ("﻿" + "\n".join(lines) + "\n").encode("utf-8")


class Parse(unittest.TestCase):
    def test_rows(self):
        vals, names, areas = A.parse(csv())
        self.assertEqual(len(areas), 5)
        self.assertEqual(vals[(("municipality", "04001"), "dwellings_total")], 1000.0)   # "1.000" read as a thousand
        t = A.frame(vals, names, areas, dict(source="s", source_url="u", retrieved_at="r", vintage="v"))
        self.assertEqual(len(t), 5 * 18)
        m = t[(t.entity == "ine_viv:es") & (t.variable == "median_annual_consumption")]
        self.assertEqual((m.value.iloc[0], m.unit.iloc[0]), (2.196, "MWh"))
        self.assertEqual(set(t.x_level), {"nation", "ccaa", "province", "municipality"})
        self.assertIn("ine_viv:mun_04002", set(t.entity))
        self.assertEqual(t[t.entity == "ine_viv:prov_04"].node.iloc[0].split(":")[0], "04 Almería")

    def test_stops(self):
        for content in (csv(nat_total=2100),                                 # the nation is not its community
                        csv(classes_ok=False),                               # a municipality's total is not its classes
                        csv(item="Viviendas con jardín"),
                        csv(value="n.d.")):
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
