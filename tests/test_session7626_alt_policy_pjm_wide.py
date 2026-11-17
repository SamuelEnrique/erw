"""Session 7626: the other choice of the ruling on PJM-wide records in the policy monitor (branch wip/alt-policy-1, not
landed). Filtering the monitor by Virginia showed 7 records and not the PJM-wide actions that bind Virginia; under the
other choice a record that names PJM and no state is kept under each PJM state's filter.

What is held to (the page's own filter, lib/policymonitor.ts run by node, on site/data/policy/monitor.json built
16 November 2026, the view as it opens: significance 5 or more):
  Virginia 7 to 14 (+7, +100 percent); every PJM state gains the same 7: DC, Delaware and New Jersey 7, Indiana and
    Maryland 9, Michigan, North Carolina and West Virginia 10, Ohio 11, Illinois 13, Pennsylvania and Tennessee 14,
    Kentucky 15; with the floor lifted Virginia 27 to 35;
  a state outside PJM is unchanged (Texas 45), and the filter keeps a record by its own states as before.

No request, no model call. Skips when node is absent."""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class PjmWideRecordsUnderEachState(unittest.TestCase):
    def test_the_counts(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        js = """
import fs from "node:fs";
const P = await import("./lib/policymonitor.ts");
const d = JSON.parse(fs.readFileSync("data/policy/monitor.json", "utf-8"));
const out = {};
for (const s of P.PJM_STATES) out[s] = P.filterRows(d.rows, { ...P.OPEN_FILTERS, states: [s] }).length;
out.VA_all = P.filterRows(d.rows, { ...P.NO_FILTERS, states: ["VA"] }).length;
out.TX = P.filterRows(d.rows, { ...P.OPEN_FILTERS, states: ["TX"] }).length;
out.wide = d.rows.filter((r) => P.pjmWide(r) && (r.significance ?? -1) >= 5).length;
console.log(JSON.stringify(out));
"""
        r = subprocess.run([exe, "--input-type=module", "-e", js], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr[-1500:])
        got = json.loads(r.stdout)
        self.assertEqual(got, {"DE": 7, "DC": 7, "IL": 13, "IN": 9, "KY": 15, "MD": 9, "MI": 10, "NJ": 7, "NC": 10, "OH": 11, "PA": 14,
                               "TN": 14, "VA": 14, "WV": 10, "VA_all": 35, "TX": 45, "wide": 7})

    def test_the_rule(self):
        with open(os.path.join(ROOT, "site", "lib", "policymonitor.ts"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn('export const pjmWide = (r: Pick<MonitorRow, "grids" | "states">) => (r.grids ?? []).includes("pjm") && !(r.states ?? []).length;', s)
        self.assertIn("stateHolds(f.states, r) && one(f.statuses, r.status)", s)
        self.assertNotIn(chr(0x2014), s)


if __name__ == "__main__":
    unittest.main()
