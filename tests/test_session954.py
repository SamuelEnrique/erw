"""Session 954: the USGS's Mineral Commodity Summaries for the minerals of batteries and grids.

Energy Research Warehouse (ERW). Tests warehouse/connectors/usgs_mcs.py on rows built here in the data release's form
(figures made up for the test, not USGS's): the six chapters kept, others left out, units scaled (thousand metric tons,
cents per pound), USGS's marks counted and not written, the em dash of a section written as a colon, the import sources'
four-year period; a unit not in the map stopping the run; the two new units in the validator; the sector rule and the
holds. No network.

    python -m unittest tests.test_session954 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
sys.path.append(os.path.join(ROOT, "warehouse", "validate"))
import usgs_mcs as U  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402
import erw_validate as V  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
SALIENT = "Salient Statistics" + chr(0x2014) + "United States"


def row(chapter, section, country, stat, detail, unit, year, value):
    return [chapter, section, chapter.title(), country, stat, detail, unit, year, value, "", "Yes", ""]


def frame(extra=()):
    rows = [row(c, SALIENT, "United States", "Production", "Production", "metric tons", "2024", "1") for c in U.CHAPTERS]
    rows += [row("COPPER", SALIENT, "United States", "Price", "Price, cents per pound", "cents per pound", "2024", "415"),
             row("NICKEL", "World Mine Production and Reserves", "Indonesia", "Production", "Mine production", "thousand metric tons", "2025", "2,600"),
             row("LITHIUM", SALIENT, "United States", "Consumption", "Consumption, apparent", "metric tons", "2025", "W"),
             row("COBALT", SALIENT, "United States", "Export", "Exports", "metric tons", "2025", chr(0x2014)),
             row("LITHIUM", "Import Sources", "Chile", "Import sources 2021-2024", "All", "percent", "2021" + chr(0x2013) + "24", "54"),
             row("ZINC", SALIENT, "United States", "Production", "Production", "metric tons", "2024", "9")]
    rows += list(extra)
    return pd.DataFrame(rows, columns=U.HEAD, dtype=str)


class Build(unittest.TestCase):
    def test_rows(self):
        t, marks = U.build(frame(), BASE)
        t = t.set_index("entity")
        self.assertEqual(len(t), len(U.CHAPTERS) + 3)  # one production row a chapter, and three of the rows below (session 981: 16 chapters)
        self.assertFalse(any(e.startswith("usgs_mcs:zinc") for e in t.index))
        self.assertAlmostEqual(t.loc["usgs_mcs:copper:united_states:price_cents_per_pound"].value, 4.15)
        self.assertEqual(t.loc["usgs_mcs:copper:united_states:price_cents_per_pound"].unit, "USD/lb")
        ni = t.loc["usgs_mcs:nickel:indonesia:mine_production"]
        self.assertEqual((ni.value, ni.unit, ni.geo), (2600000.0, "t", ""))
        li = t.loc["usgs_mcs:lithium:chile:all"]
        self.assertEqual((li.ts_utc, li.freq, li.variable), ("2021-01-01T00:00:00Z", "P4Y", "import_share"))
        self.assertEqual(t.loc["usgs_mcs:cobalt:united_states:production"].x_section, "Salient Statistics: United States")
        self.assertEqual(marks, {"W": 1, "dash": 1})

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            U.build(frame([row("COPPER", SALIENT, "United States", "Production", "Production", "long tons", "2024", "1")]), BASE)

    def test_units_in_the_vocabulary(self):
        self.assertTrue({"t", "USD/kg"} <= V.UNITS)
        self.assertTrue({u for u, _ in U.UNITS.values()} <= V.UNITS)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        name = U.NAME
        self.assertEqual(B.sector_of(name), "metals")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
