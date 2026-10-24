"""Session 2451: Uzbekistan's electricity production and consumption by region, a year (SIAT, the statistics committee's
open data).

Energy Research Warehouse (ERW). Tests warehouse/connectors/siat_uzbekistan.py's reader on an indicator file built here
in SIAT's JSON form (made up for the test, not its figures): the republic and two regions, a zero kept, a key that is not
a year ("2022.1") left out, the republic's excess over its regions allowed as unallocated; a code, unit or region not as
read, a value that is not a number and regions adding to more than the republic stopping the run; the sector rule and
the holds (public). No network.

    python -m unittest tests.test_session2451 -v
"""

import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import siat_uzbekistan as S  # noqa: E402
import build_coverage as B  # noqa: E402


def item(code="1.02.02.0004", unit="Million kWt hour", region="Andijan region", rep=100.0, a=40.0, b=50.0, bad=None):
    meta = [{"name_en": "Indicator identification number (code)", "value_en": code},
            {"name_en": "Unit of measurement", "value_en": unit},
            {"name_en": "Note", "value_en": "2010-2022 final, 2023 preliminary"}]
    rows = [{"Code": "1700", "Klassifikator_en": "Republic of Uzbekistan", "2022": rep, "2022.1": 0.0, "2023": 0.0},
            {"Code": "1703", "Klassifikator_en": region, "2022": a if bad is None else bad, "2023": 0.0},
            {"Code": "1726", "Klassifikator_en": "Tashkent city", "2022": b, "2023": 0.0}]
    return json.dumps([{"metadata": meta, "data": rows}]).encode()


class Reader(unittest.TestCase):
    def test_values(self):
        var, vals, note, unalloc = S.indicator(item(), 440)
        self.assertEqual(var, "generation")
        self.assertEqual(vals[("Republic of Uzbekistan", "1700", 2022)], 100.0)
        self.assertEqual(vals[("Tashkent city", "1726", 2023)], 0.0)
        self.assertNotIn(2022.1, {y for (_, _, y) in vals})
        self.assertEqual(unalloc, 10.0)
        self.assertIn("preliminary", note)

    def test_stops(self):
        for bad in (item(code="1.02.02.0005"), item(unit="GWh"), item(region="Atlantis"), item(bad="12a"), item(a=60.0)):
            with self.assertRaises(RuntimeError):
                S.indicator(bad, 440)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))
        with open(os.path.join(ROOT, "warehouse", "redivis", "release_v1.py"), encoding="utf-8") as f:
            self.assertIn(f'"{S.NAME}"', f.read())


if __name__ == "__main__":
    unittest.main()
