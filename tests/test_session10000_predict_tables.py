"""Session 10000 (chain 701, data requests 2 and 5 of docs/state/data_requests_predict.md): the ERW forecast's ledgers as
the tables predict_demand_forecasts and predict_price_forecasts. Made-up ledgers; no table is read."""
import ast
import importlib.util
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load():
    sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
    spec = importlib.util.spec_from_file_location("predict_tables_t", os.path.join(ROOT, "warehouse", "predict", "predict_tables.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def constant(path, name):
    tree = ast.parse(open(os.path.join(ROOT, path), encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise KeyError(name)


def ledger(series, rows):
    cols = ["series", "place", "target_day", "ts_utc", "local_hour", "made_utc", "inputs_through_utc", "horizon_days",
            "method", "erw", "lo", "hi"]
    return pd.DataFrame([dict(zip(cols, [series] + r)) for r in rows], columns=cols)


class TheLedgerAsATable(unittest.TestCase):
    def setUp(self):
        self.m = load()
        self.d = ledger("demand", [
            ["region-tex", "2026-11-27", "2026-11-27T06:00:00Z", "0", "2026-11-26T11:00:00Z", "2026-11-25T05:00:00Z", "3", "regression", "45000.5", "43000", "47000"],
            ["ba-erco", "2026-11-27", "2026-11-27T06:00:00Z", "0", "2026-11-26T11:00:00Z", "2026-11-25T05:00:00Z", "3", "regression", "44000.0", "42000", "46000"],
            ["ba-erco", "2026-11-27", "2026-11-27T06:00:00Z", "0", "2026-11-26T20:00:00Z", "2026-11-25T05:00:00Z", "2", "regression", "44100.0", "", ""],
        ])

    def test_each_place_its_own_entity_and_every_making_kept(self):
        t = self.m.table(self.d, "demand", "2026-11-26T23:00:00Z")
        self.assertEqual(sorted(t["entity"].unique()), ["eia930:ERCO", "eia930:TEX"])
        self.assertEqual(len(t), 3)   # a second making of an hour is a second row, never a replacement
        self.assertEqual(sorted(t[t["entity"] == "eia930:ERCO"]["vintage"]), ["2026-11-26T11:00:00Z", "2026-11-26T20:00:00Z"])
        self.assertEqual(set(t["variable"]), {"demand_forecast_mw"})
        self.assertEqual(list(t.columns), self.m.COLS)

    def test_a_row_without_a_figure_is_left_out_and_counted(self):
        # 27 November 2026: run.py wrote 24 rows with no figure for ba-spa; the table had been refused whole
        d = pd.concat([self.d, ledger("demand", [
            ["ba-spa", "2026-11-28", "2026-11-28T06:00:00Z", "0", "2026-11-27T19:00:00Z", "2026-11-27T05:00:00Z", "2", "regression", "", "", ""]])],
            ignore_index=True)
        t = self.m.table(d, "demand", "2026-11-27T23:00:00Z")
        self.assertEqual(len(t), 3)
        self.assertNotIn("eia930:SPA", set(t["entity"]))
        words = self.m.figureless(d, "demand")
        self.assertEqual(words, "1 (ba-spa made 2026-11-27T19:00:00Z: 1)")
        self.assertTrue(any("left out: 1 (ba-spa" in h for h in self.m.header("demand", t, "20261127T230000Z", words)))
        self.assertEqual(self.m.figureless(self.d, "demand"), "none")

    def test_a_row_without_its_hour_is_still_refused(self):
        d = self.d.copy()
        d.loc[0, "made_utc"] = ""
        with self.assertRaises(ValueError):
            self.m.table(d, "demand", "2026-11-27T23:00:00Z")

    def test_the_header_says_revisions_are_kept(self):
        # the validator keys a table by vintage only when its header says so (erw_validate.REVISIONS_KEPT)
        t = self.m.table(self.d, "demand", "2026-11-26T23:00:00Z")
        kept = constant("warehouse/validate/erw_validate.py", "REVISIONS_KEPT")
        self.assertTrue(any(h.startswith(kept) for h in self.m.header("demand", t, "20261126T230000Z")))

    def test_the_price_names_its_hub(self):
        p = ledger("price", [["region-cal", "2026-11-27", "2026-11-27T08:00:00Z", "0", "2026-11-26T11:00:00Z", "2026-11-26T07:00:00Z", "2", "regression", "38.84", "28.63", "50.55"]])
        t = self.m.table(p, "price", "2026-11-26T23:00:00Z")
        self.assertEqual((t["entity"][0], t["market"][0], t["node"][0], t["unit"][0]), ("eia930:CAL", "caiso", "TH_SP15_GEN-APND", "USD/MWh"))

    def test_a_place_with_no_grid_is_refused(self):
        p = ledger("price", [["region-midw", "2026-11-27", "2026-11-27T06:00:00Z", "0", "2026-11-26T11:00:00Z", "", "2", "regression", "30", "", ""]])
        with self.assertRaises(ValueError):
            self.m.table(p, "price", "2026-11-26T23:00:00Z")

    def test_a_row_twice_is_refused(self):
        with self.assertRaises(ValueError):
            self.m.table(pd.concat([self.d, self.d.iloc[[0]]]), "demand", "2026-11-26T23:00:00Z")

    def test_an_empty_ledger_is_refused(self):
        with self.assertRaises(ValueError):
            self.m.table(self.d.iloc[0:0], "demand", "2026-11-26T23:00:00Z")

    def test_the_grids_and_hubs_are_run_pys(self):
        self.assertEqual(self.m.PRICE_GRID, constant("warehouse/predict/run.py", "PRICE_GRID"))
        self.assertEqual(self.m.HUBS, constant("warehouse/predict/predict_data.py", "HUBS"))

    def test_the_daily_step_follows_the_forecast(self):
        with open(os.path.join(ROOT, "warehouse", "run_data_machine.sh"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn("soft_step dm_predict_tables", s)
        self.assertLess(s.index("soft_step dm_predict "), s.index("soft_step dm_predict_tables"))


if __name__ == "__main__":
    unittest.main()
