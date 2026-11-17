"""Session 7622: the other choice of the ruling on CAISO's large-load steps (branch wip/alt-cost-of-power-4, not landed).
The draft final proposal of 24 September 2026 states no duration for the PTOs' large load interconnection study in
large_load_connection_rules; under the other choice the straw proposal's figure of 11 August 2026 (90 days) is carried
into that step, marked as carried, in the hover of the rows' filed steps on the All grids tab.

What is held to:
  carriedSteps (lib/siting.ts, run by node over site/data/siting/conn_rules.json, built 14 November 2026) carries one
    step in all the grids held: CAISO's draft final proposal's study step, 90 days, from the straw proposal;
  a step with its own duration is never changed, and a carried figure comes only from an earlier document of the same
    grid stating the same step;
  the hover names the earlier document and says the later one states none.

No request, no model call. Skips when node is absent."""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TheStrawsFigureCarried(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        js = """
import fs from "node:fs";
const S = await import("./lib/siting.ts");
const f = { connRules: JSON.parse(fs.readFileSync("data/siting/conn_rules.json", "utf-8")) };
const carried = [], changed = [];
for (const [g, steps] of Object.entries(f.connRules.grids)) {
  const out = S.carriedSteps(steps);
  out.forEach((x, i) => { if (x.carried) carried.push([g, x.date, x.duration, x.unit, x.carried.slice(0, 40)]); if (steps[i].duration && (x.duration !== steps[i].duration || x.carried)) changed.push([g, i]); });
}
const tip = S.filedSteps(f, { id: "caiso:x", grid: "caiso", region: "SP15", label: "SP15", kind: "hub" });
console.log(JSON.stringify({ carried, changed, tip }));
"""
        r = subprocess.run([exe, "--input-type=module", "-e", js], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            raise AssertionError(r.stderr[-1500:])
        cls.got = json.loads(r.stdout)

    def test_one_step_is_carried_caisos_study(self):
        self.assertEqual(self.got["carried"], [["caiso", "2026-09-24", "90", "days", "CAISO, Large Loads Considerations, Straw"]])

    def test_no_stated_duration_changes(self):
        self.assertEqual(self.got["changed"], [])

    def test_the_hover_says_it_is_carried(self):
        self.assertIn("90 days, carried from CAISO, Large Loads Considerations, Straw Proposal, 11 August 2026", self.got["tip"])
        self.assertIn("this document states none (CAISO, Large Load Enhancements, Draft Final Proposal, 24 September 2026", self.got["tip"])
        self.assertNotIn(chr(0x2014), self.got["tip"])


if __name__ == "__main__":
    unittest.main()
