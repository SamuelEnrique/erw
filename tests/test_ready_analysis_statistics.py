"""wip/ready-analysis-statistics (session 11406, chain 770, part C): the other choice of the Automated Analysis audit
of 26 November, finding 6 (docs/reviews/analysis-model-audit-2026-11-26.md), readied for Samuel's ruling, not requested.

On main the deep hunt's drafts (all forty of the shortlist) carry none of session 361's statistics block: no trend p,
no Benjamini-Hochberg q over the round, no step-or-trend shape, no count of the claims tested. On this branch the
deep builder computes the block over each family's run, puts it on the card and says it in the footnote, as the
weekly hunt does; the page's FindingCard already prints "A step, not a trend" from it. The audit counted 12 of the
forty's 37 yearly claims a step by the engine's own rule (draft 33, cooling degree days in Texas, breaks at 2022);
they gain the flag when the drafts are next built on the data machine. The audit's own test is carried, turned round."""
import json
import os
import sys
import tempfile
import unittest
from unittest import mock
import csv

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIND = os.path.join(ROOT, "warehouse", "analysis", "findings")
DEEP = os.path.join(FIND, "deep")
sys.path.insert(0, FIND)
sys.path.insert(0, DEEP)
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import builder  # noqa: E402
import hunt  # noqa: E402
import hunt_measures as hm  # noqa: E402


def synthetic(region_specs, years=range(2015, 2026)):
    def fn(in_dir):
        rows, tables = [], {}
        for region, slope in region_specs:
            for i, y in enumerate(years):
                step = 3.0 if (slope == "step" and y >= 2021) else 0.0
                v = 50 + step + (0 if slope == "step" else slope * i) + (0.3 if i % 2 else -0.3)
                rows.append(hm._row(region, f"Place {region}", y, v, 8760))
            tables[region] = ["test_table"]
        return {"rows": rows, "tables": tables}
    return fn


def full_years(slug):
    with open(os.path.join(ROOT, "docs", "findings", slug + ".csv"), encoding="utf-8") as f:
        lines = [ln for ln in f if not ln.startswith("#")]
    rows = [r for r in csv.DictReader(lines) if str(r.get("full_year")) == "1"]
    return [int(float(r["year"])) for r in rows], [float(r["value"]) for r in rows]


class DeepDraftsCarryTheBlock(unittest.TestCase):
    def run_family(self, specs):
        P = builder.candidate("test_measure", "testfam", synthetic(specs), "USD per MWh", 2, 8000, 1.0, "A TEST MEASURE", "a test measure",
                              lambda w: f"the test measure at {w}", "A test's limits.",
                              lambda region: {"py": '"""a script"""\nprint(1)\n', "do": "* a do-file\n\nclear all\n"}, consequence=2)
        with tempfile.TemporaryDirectory() as d, mock.patch.object(builder, "DOCS", os.path.join(d, "docs")), \
                mock.patch.object(hunt, "blocked_grids", lambda meta_dir=None: set()):
            s = builder.run("testfam", [P], d, dry_run=False, log=lambda m: None, out_root=os.path.join(d, "runs"),
                            load=lambda built, log: [x["id"] for x in built])
            day = os.listdir(os.path.join(d, "runs"))[0]
            return [json.load(open(os.path.join(d, "runs", day, "testfam", did + ".json"), encoding="utf-8")) for did in s["drafts"]]

    def test_a_steady_rise_carries_the_round_and_its_trend(self):
        rows = self.run_family([("ercot_A", 3.0), ("ercot_B", -0.05)])   # B changes by less than a typical yearly move and fails
        self.assertEqual(len(rows), 1)
        st = rows[0]["card"]["statistics"]
        self.assertEqual(st["session"], 361)
        self.assertEqual((st["round"]["claims_tested"], st["round"]["claims_passing"]), (2, 1))
        self.assertIsNotNone(st["round"]["q_bh"])
        self.assertFalse(st["shape"]["step_better"])
        self.assertIn("This hunt tested 2 claims and 1 passed its tests; this claim's q-value over the round is", rows[0]["card"]["footnote"])

    def test_a_step_is_said_to_be_one(self):
        rows = self.run_family([("ercot_S", "step")])
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["card"]["statistics"]["shape"]["step_better"])
        self.assertIn(" Its shape: ", rows[0]["card"]["footnote"])

    def test_draft_33_is_a_step_by_the_engines_own_rule(self):
        import findings_common as common
        ys, vs = full_years("weather/cdd-wd-tex")
        sh = common.step_or_trend(ys, vs)
        self.assertTrue(sh["step_better"])
        self.assertEqual(int(sh["break_year"]), 2022)
        with open(os.path.join(DEEP, "builder.py"), encoding="utf-8") as f:
            t = f.read()
        for name in ("common.bh_q", '"statistics"', 'c.get("shape")'):
            self.assertIn(name, t)


if __name__ == "__main__":
    unittest.main()
