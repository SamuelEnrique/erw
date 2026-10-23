"""Session 981: the other minerals of energy in usgs_mcs_critical_minerals.

Energy Research Warehouse (ERW). Tests warehouse/connectors/usgs_mcs.py's additions on rows built here in the data
release's form (figures made up for the test, not USGS's): the ten new chapters taken, kilograms as metric tons, troy
ounces as kilograms, a price per metric ton unit written per ton of content, a figure printed in two sections with one
value kept once and with two values stopping the run. No network.

    python -m unittest tests.test_session981 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import usgs_mcs as U  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
SALIENT = "Salient Statistics" + chr(0x2014) + "United States"
WORLD = "World Mine Production and Reserves"


def row(chapter, section, country, stat, detail, unit, year, value):
    return [chapter, section, chapter.title(), country, stat, detail, unit, year, value, "", "Yes", ""]


def frame(extra=()):
    rows = [row(c, SALIENT, "United States", "Production", "Production", "metric tons", "2024", "1") for c in U.CHAPTERS]
    rows += list(extra)
    return pd.DataFrame(rows, columns=U.HEAD, dtype=str)


class Additions(unittest.TestCase):
    def test_chapters(self):
        self.assertEqual(len(U.CHAPTERS), 16)
        self.assertTrue({"MANGANESE", "PLATINUM-GROUP METALS", "SILICON", "VANADIUM"} <= set(U.CHAPTERS))

    def test_units(self):
        t, _ = U.build(frame([
            row("PLATINUM-GROUP METALS", SALIENT, "United States", "Production", "Mine production: Platinum", "kilograms", "2025", "1,800"),
            row("PLATINUM-GROUP METALS", SALIENT, "United States", "Price", "Price, dollars per troy ounce: Platinum", "dollars per troy ounce", "2025", "1,000"),
            row("MANGANESE", SALIENT, "United States", "Price", "Price, average, manganese content, dollars per metric ton unit", "dollars per metric ton", "2025", "4.5")]), BASE)
        t = t.set_index("entity")
        pt = t.loc["usgs_mcs:platinum_group_metals:united_states:mine_production_platinum"]
        self.assertEqual((pt.value, pt.unit), (1.8, "t"))
        price = t.loc["usgs_mcs:platinum_group_metals:united_states:price_dollars_per_troy_ounce_platinum"]
        self.assertEqual(price.unit, "USD/kg")
        self.assertAlmostEqual(price.value, 32150.7466, places=3)
        mn = t.loc["usgs_mcs:manganese:united_states:price_average_manganese_content_dollars_per_metric_ton_unit"]
        self.assertEqual((mn.value, mn.unit), (450.0, "USD/t"))

    def test_two_sections(self):
        a = row("PLATINUM-GROUP METALS", SALIENT, "United States", "Production", "Mine production: Palladium", "kilograms", "2024", "10,200")
        b = row("PLATINUM-GROUP METALS", WORLD, "United States", "Production", "Mine production: Palladium", "kilograms", "2024", "10,200")
        t, marks = U.build(frame([a, b]), BASE)
        self.assertEqual(marks["repeated in two sections, kept once"], 1)
        self.assertEqual((t.entity == "usgs_mcs:platinum_group_metals:united_states:mine_production_palladium").sum(), 1)
        c = row("PLATINUM-GROUP METALS", WORLD, "United States", "Production", "Mine production: Palladium", "kilograms", "2024", "9,000")
        with self.assertRaises(RuntimeError):
            U.build(frame([a, c]), BASE)


if __name__ == "__main__":
    unittest.main()
