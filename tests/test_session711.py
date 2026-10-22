"""Session 711: a node's panel on the All grids tab (docs/methods/siting.md). Its daily basis percentiles over the
node file's twelve whole months, recomputed here from the table where it is on this machine; each month's mean in the
shared chart; what is not held about its place said so. No request, no model call."""
import json
import os
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MAIN = os.path.join(os.path.dirname(ROOT), "erw")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Panel(unittest.TestCase):
    def test_the_percentiles_are_the_table_s(self):
        nodes = json.loads(src("site", "data", "siting", "nodes.json"))
        self.assertEqual((nodes["pct_from"], nodes["pct_to"]), ("2025-10", "2026-09"))
        p = None
        for d in (os.path.join(ROOT, "runs", "archive_restore"), os.path.join(MAIN, "runs", "archive_restore")):
            if os.path.exists(os.path.join(d, "node_basis_daily.csv")):
                p = os.path.join(d, "node_basis_daily.csv")
                break
        if not p:
            raise unittest.SkipTest("node_basis_daily is not on this machine")
        keep = []
        for ch in pd.read_csv(p, comment="#", usecols=["entity", "variable", "ts_utc", "value"], chunksize=500_000):
            keep.append(ch[(ch["variable"] == "dam_basis") & ch["entity"].isin(["ercot:7RNCHSLR_ALL", "ercot:A4_DGR1_RN"])])
        d = pd.concat(keep)
        d = d[(d["ts_utc"] >= "2025-10-01") & (d["ts_utc"] < "2026-10-01")]
        for n in nodes["nodes"]:
            if n["id"] in ("7RNCHSLR_ALL", "A4_DGR1_RN"):
                v = d.loc[d["entity"] == f"ercot:{n['id']}", "value"]
                self.assertEqual(n["pct"][3], len(v))
                for i, q in enumerate((0.1, 0.5, 0.9)):
                    self.assertAlmostEqual(n["pct"][i], round(float(v.quantile(q)), 4), places=4)

    def test_the_panel_draws_its_keys_and_says_what_is_not_held(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        for k in ("check={`allgrids|nodepct|${id}|10`}", "check={`allgrids|nodepct|${id}|90`}", "<InlineSpark values={months.map", "No table of the warehouse places an ERCOT settlement point in a county"):
            self.assertIn(k, v)
        self.assertIn('"/cost-of-power?view=allgrids&rows=nodes&node=ercot%3A7RNCHSLR_ALL"', src("site", "scripts", "check-values.mjs"))
        self.assertIn("data-node-open={r.id}", src("site", "app", "cost-of-power", "AllGridsNodes.tsx"))


if __name__ == "__main__":
    unittest.main()
