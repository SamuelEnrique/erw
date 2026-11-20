"""Sessions 8005 and 8006 (chain 501, steps D3 and D1): the printed-words check of warehouse/connectors/ai_energy_published.py,
its rows file, and the helpers of warehouse/derived/resource_tables.py; the coal fields' web file where the data machine
has written it.

Energy Research Warehouse (ERW). docs/methods/ai_energy_published.md, docs/methods/resource_layers_table.md.

    python -m unittest tests.test_session8005_ai_energy_and_resources -v
"""

import base64
import csv
import json
import math
import os
import sys
import unittest

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import ai_energy_published as aep  # noqa: E402
import resource_tables as rt  # noqa: E402

ROWS = os.path.join(ROOT, "warehouse", "sources", "ai_energy_published", "rows.csv")
COAL = os.path.join(ROOT, "site", "data", "resources", "coal_fields.json")


class PrintedWords(unittest.TestCase):
    def test_spaces_and_hyphenated_breaks_do_not_matter(self):
        text = "...wefindthemedianGeminiApps\ntextpromptconsumes0.24Whofenergy...the active AI Acceler-\nator power (0.14 Wh"
        self.assertTrue(aep.check("we find the median Gemini Apps text prompt consumes 0.24 Wh of energy", text))
        self.assertTrue(aep.check("the active AI Accelerator power (0.14 Wh", text))
        self.assertFalse(aep.check("consumes 0.42 Wh of energy", text))

    def test_a_cut_needs_both_pieces(self):
        text = "Training Meena used\n9 footnote\n232 MWh and emissions"
        self.assertTrue(aep.check("Training Meena used [...] 232 MWh", text))
        self.assertFalse(aep.check("Training Meena used [...] 233 MWh", text))

    def test_the_value_is_a_number_of_the_words(self):
        self.assertTrue(aep.number_in("its energy consumption is 1287 MWh", 1287))
        self.assertTrue(aep.number_in("Total energy used 433,196 kWh", 433196))
        self.assertFalse(aep.number_in("its energy consumption is 1287 MWh", 1278))


class RowsFile(unittest.TestCase):
    def test_every_row_says_what_it_measures_and_where(self):
        rows = list(csv.DictReader(open(ROWS, encoding="utf-8")))
        self.assertGreaterEqual(len(rows), 21)
        ids = [r["id"] for r in rows]
        self.assertEqual(len(ids), len(set(ids)))
        for r in rows:
            for k in ("publisher", "publisher_kind", "date", "url", "page", "printed", "value", "unit", "measures", "subject"):
                self.assertTrue(r[k].strip(), (r["id"], k))
            self.assertIn(r["unit"], ("Wh", "kWh", "MWh", "TWh"), r["id"])
            self.assertNotIn(chr(0x2014), r["printed"])

    def test_no_figure_of_the_erws_own(self):
        # each value is a number printed in its own row's words: nothing summed or averaged across publishers
        for r in csv.DictReader(open(ROWS, encoding="utf-8")):
            self.assertTrue(aep.number_in(r["printed"], float(r["value"])), r["id"])


class Resources(unittest.TestCase):
    def test_a_grid_decodes_with_its_empty_cells(self):
        raw = np.array([[1000, 65535], [2500, 0]], dtype="<u2")
        obj = {"values": base64.b64encode(raw.tobytes()).decode(), "nrows": 2, "ncols": 2, "scale": 0.001, "offset": 0.0, "nodata": 65535}
        v = rt.decode_grid(obj)
        self.assertAlmostEqual(v[0, 0], 1.0)
        self.assertTrue(math.isnan(v[0, 1]))
        self.assertAlmostEqual(v[1, 0], 2.5)

    def test_area_on_a_sphere(self):
        want = rt.R_KM ** 2 * math.radians(1) * math.sin(math.radians(1))
        self.assertAlmostEqual(rt.ring_area_km2([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]), want, delta=want * 1e-9)

    def test_the_offshore_rights_are_not_resources(self):
        self.assertNotIn("offshore_wind_leases", rt.TAKEN)
        self.assertNotIn("offshore_wind_planning_areas", rt.TAKEN)


@unittest.skipUnless(os.path.exists(COAL), "the coal fields' file is written on the data machine")
class CoalFile(unittest.TestCase):
    def test_contract(self):
        self.assertLess(os.path.getsize(COAL), 2 * 1024 ** 2)
        d = json.load(open(COAL, encoding="utf-8"))
        self.assertEqual(d["tables"], ["resource_layer_features"])
        self.assertEqual(len(d["features"]), 602)
        self.assertEqual(set(d["features"][0]["properties"]), {"province", "name", "age", "rank", "area_km2"})


if __name__ == "__main__":
    unittest.main()
