"""Session 345: NLR's JEDI models, nlr_jedi_multipliers.

Energy Research Warehouse (ERW). The recalculation step needs pycel, which lives outside the repository's environment
(.venv-jedi); its Excel functions are read from its source by their definitions alone and tested here against Excel's
own documented examples. The other tests read the table where this machine holds it, and skip where it does not.

    python -m unittest tests.test_session345 -v
"""

import ast
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "validate"))
import jedi_multipliers as jm  # noqa: E402
import erw_validate  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output", "nlr_jedi_multipliers.csv")
RECALC = os.path.join(ROOT, "warehouse", "connectors", "jedi_recalc.py")


def recalc_functions():
    """The plain functions of jedi_recalc.py (the Excel functions it adds), without importing pycel."""
    tree = ast.parse(open(RECALC, encoding="utf-8").read())
    keep = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in
            ("_one", "_ones", "ispmt", "_pmt", "_fv", "ipmt", "ppmt", "exp", "median")]
    ns = {}
    exec(compile(ast.Module(body=keep, type_ignores=[]), RECALC, "exec"), ns)
    return ns


class ExcelFunctions(unittest.TestCase):
    def setUp(self):
        self.f = recalc_functions()

    def test_each_matches_excels_own_examples(self):
        self.assertAlmostEqual(self.f["ispmt"](0.1 / 12, 1, 36, 8000000), -64814.81, places=2)
        self.assertAlmostEqual(self.f["ipmt"](0.1 / 12, 1, 36, 8000), -66.67, places=2)
        self.assertAlmostEqual(self.f["ipmt"](0.1, 3, 3, 8000), -292.45, places=2)
        self.assertAlmostEqual(self.f["ppmt"](0.1 / 12, 1, 24, 2000), -75.62, places=2)
        self.assertAlmostEqual(self.f["ppmt"](0.08, 10, 10, 200000), -27598.05, places=2)

    def test_median_leaves_out_text_and_blanks_as_excel_does(self):
        self.assertEqual(self.f["median"]((1, "a", None, (3, 2, 10))), 2.5)
        self.assertEqual(self.f["median"](("x",)), "#NUM!")

    def test_a_one_cell_array_is_its_value_and_text_is_an_error(self):
        self.assertAlmostEqual(self.f["ispmt"](((0.1 / 12,),), 1, 36, (8000000,)), -64814.81, places=2)
        self.assertEqual(self.f["ipmt"](0.1, 1, 3, "#NAME?"), "#NAME?")
        self.assertEqual(self.f["ipmt"](0.1, 1, 3, "words"), "#VALUE!")


class TheSpec(unittest.TestCase):
    def test_the_connector_reads_the_recalculations_cells_without_pycel(self):
        spec = jm.recalc_spec()
        self.assertEqual(set(spec), set(jm.MODELS))
        for tech, m in spec.items():
            self.assertEqual(len(m["rows"]), 8, tech)
            self.assertEqual({e for _, e, _, _ in m["rows"]}, {"onsite", "supply_chain", "induced", "total"})
        self.assertEqual(spec["utility_pv"]["settings"], {"ProjectData!B15": "Utility"})

    def test_battery_storage_is_named_as_not_held(self):
        self.assertIn("battery_storage", jm.NOT_HELD)
        self.assertNotIn("battery_storage", jm.MODELS)

    def test_every_unit_is_in_the_validators_vocabulary(self):
        for u in jm.UNITS.values():
            self.assertIn(u, erw_validate.UNITS)


class TheTable(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(OUT):
            self.skipTest("nlr_jedi_multipliers is not on this machine")
        self.d = pd.read_csv(OUT, comment="#", dtype={"x_state": str}, keep_default_na=False)

    def test_four_technologies_and_the_rows_by_rule(self):
        self.assertEqual(sorted(self.d.x_technology.unique()), ["geothermal", "land_based_wind", "natural_gas", "utility_pv"])
        n = self.d.groupby("x_technology").x_location.nunique().to_dict()
        self.assertEqual(n, {"geothermal": 52, "land_based_wind": 52, "natural_gas": 50, "utility_pv": 52})
        gas = set(self.d[self.d.x_technology == "natural_gas"].x_state)
        self.assertFalse({"DC", "HI"} & gas, "JEDI's own answer there is #DIV/0!: no row")
        self.assertEqual(len(self.d), 206 * 27, "24 figures, the project's MW and two local shares a location")

    def test_the_total_is_the_sum_of_its_three_lines(self):
        k = ["x_technology", "x_location", "x_phase", "variable"]
        p = self.d[self.d.variable.isin(["jobs", "earnings", "output"])].pivot_table(index=k, columns="x_effect", values="value", aggfunc="first")
        parts = p["onsite"] + p["supply_chain"] + p["induced"]
        # each value is written to six decimals, so three rounded parts may differ from the rounded total by 1.5e-6
        self.assertTrue(((parts - p["total"]).abs() <= 2e-6 + 1e-9 * p["total"].abs()).all())

    def test_states_differ_and_the_nation_is_larger(self):
        t = self.d[(self.d.x_technology == "land_based_wind") & (self.d.x_phase == "construction")
                   & (self.d.x_effect == "induced") & (self.d.variable == "jobs")].set_index("x_location").value
        self.assertGreater(t.nunique(), 40, "a state's own multipliers give its own induced jobs")
        self.assertGreater(t["UNITED STATES"], t.drop("UNITED STATES").max())

    def test_the_project_and_its_local_shares_are_rows(self):
        mw = self.d[self.d.variable == "project_mw"].groupby("x_technology").value.unique()
        self.assertEqual({k: list(v) for k, v in mw.items()}, {"geothermal": [12.226196], "land_based_wind": [300.0],
                                                              "natural_gas": [500.0], "utility_pv": [100.0]})
        ls = self.d[self.d.variable == "local_share"]
        self.assertEqual(set(ls.x_phase), {"construction", "operations"})
        self.assertTrue((ls.value == ls.x_local_share.astype(float)).all())

    def test_the_saved_project_is_marked_as_saved(self):
        ct = self.d[(self.d.x_technology == "land_based_wind") & (self.d.x_state == "CT")]
        self.assertTrue(ct.x_method.str.startswith("the workbook's saved project").all())
        tx = self.d[(self.d.x_technology == "land_based_wind") & (self.d.x_state == "TX")]
        self.assertTrue(tx.x_method.str.startswith("JEDI's formulas computed").all())

    def test_the_header_carries_nlrs_notice_and_validates(self):
        head = open(OUT, encoding="utf-8").read(6000)
        self.assertIn("provided that this entire notice appears in all copies of the Data", head)
        self.assertIn("battery_storage", head)
        rc = erw_validate.main([OUT]) if hasattr(erw_validate, "main") else 0
        self.assertIn(rc, (0, None))


if __name__ == "__main__":
    unittest.main()
