"""Audit of the datacenter power tracker, finding 4 (session 10211, docs/reviews/tracker-model-audit-2026-11-26.md): the
note of the chart "The operators with the most MW stated" read "The operator, else the developer", but the chart's
function (site/lib/dcrollups.ts, operatorMw) reads rollups(rows, "operator"), the operator alone, as decision 9 says the
views by operator do. On the table of 25 November 2026 the fallback would make the largest bar 10,400 MW, not 1,000.

1. Through the page's library (run by Node): a facility with a developer and no operator is not on the chart. Passes on
   main.
2. The fix on this branch, words only: the note says the chart reads the operator a source names. Fails on main."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "dcrollups.ts").replace("\\", "/")
JS = """
const R = await import(process.argv[1]);
const row = (id, op, dev, mw) => ({ entity_id: id, capacity_mw: mw, status: "planned", operator: op, extra: { state: "OH", developer: dev } });
console.log(JSON.stringify(R.operatorMw([row("a", "", "A developer", 10400), row("b", "An operator", "", 1000)]).map((o) => [o.operator, o.mw])));
"""


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheOperatorChartSaysItsRule(unittest.TestCase):
    def test_a_developer_alone_is_not_on_the_chart(self):
        out = subprocess.run(["node", "--input-type=module", "-e", JS, LIB], capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(json.loads(out.stdout.strip().splitlines()[-1]), [["An operator", 1000]])

    def test_the_note_names_the_rule_the_code_uses(self):
        charts = src("site", "app", "datacenters", "DcCharts.tsx")
        self.assertNotIn("The operator, else the developer", charts)
        self.assertIn("The operator a source names, as every view by operator reads it; a facility whose sources name only a developer is not here "
                      "(decision 9); the MW its counted facilities state.", charts)


if __name__ == "__main__":
    unittest.main()
