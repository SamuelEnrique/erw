"""Session 724 (chain 062): the trader's walk, fixed. The node list gains the basis's spread (the panel's 90th percentile
less its 10th), sortable and keyed; the months node_basis_daily lacks are named from the node file; a node can be set
as A or B from its panel, and the box's lists keep it; the list filters by name (nq in the address) and downloads the
rows shown as a CSV made in the browser. No request, no model call."""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


SCRIPT = """
const S = await import('./lib/siting.ts');
import fs from 'node:fs';
const nodes = JSON.parse(fs.readFileSync('data/siting/nodes.json', 'utf8'));
const n = nodes.nodes.find((k) => k.pct);
const short = S.nodeShortMonths(nodes);
const fixture = { pct_from: '2026-01', pct_to: '2026-03', nodes: [{ dam_basis: { '2026-01': [1, 31], '2026-02': [1, 20] } }, { dam_basis: { '2026-02': [1, 27] } }] };
const rows = [{ node: 'A', spread: 3 }, { node: 'B', spread: 9 }, { node: 'C', spread: null }];
process.stdout.write(JSON.stringify({ sorts: S.NODE_SORTS, short, words: S.shortMonthsWords(short), fixture: S.nodeShortMonths(fixture),
  none: S.shortMonthsWords([]), id: n.id, pct: n.pct, sorted: S.sortNodes(rows, 'spread', 'desc').map((r) => r.node) }));
"""


def run():
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", SCRIPT], cwd=SITE, capture_output=True, text=True, timeout=300, encoding="utf-8")
    if r.returncode != 0 and "Unknown file extension" in r.stderr:
        raise unittest.SkipTest("this node does not read TypeScript files")
    if r.returncode != 0:
        raise AssertionError(r.stderr)
    return json.loads(r.stdout)


class Trader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.o = run()

    def test_the_spread_sorts_and_a_node_without_one_goes_last(self):
        self.assertIn("spread", self.o["sorts"])
        self.assertEqual(self.o["sorted"], ["B", "A", "C"])

    def test_the_short_months_are_the_file_s(self):
        # the fixture: January whole, February at most 27 of 28 days, March none
        self.assertEqual(self.o["fixture"], [{"month": "2026-02", "held": 27, "of": 28}, {"month": "2026-03", "held": 0, "of": 31}])
        # the real file: node_basis_daily lacks 21 August to 19 September 2026 (session 723's walk)
        months = {v["month"]: (v["held"], v["of"]) for v in self.o["short"]}
        self.assertEqual(set(months), {"2026-08", "2026-09"})
        self.assertEqual(months["2026-08"][1], 31)
        self.assertIn("for every node", self.o["words"])
        self.assertIn("holds every day", self.o["none"])

    def test_the_page_draws_each_fix(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        n = src("site", "app", "cost-of-power", "AllGridsNodes.tsx")
        self.assertIn('data-node-set="a"', v)
        self.assertIn('data-node-set="b"', v)
        self.assertIn("(node)", v)                                          # the box's lists keep a node set as A or B
        self.assertIn("data-check={`allgrids|nodespread|${r.id}`}", n)
        self.assertIn('data-node-find="1"', n)
        self.assertIn('data-node-download="1"', n)
        self.assertIn('q.set("nq"', n)
        self.assertIn('"/cost-of-power?view=allgrids&rows=nodes&nsort=spread&ndir=desc"', src("site", "scripts", "check-values.mjs"))
        self.assertIn("nodespread", src("site", "lib", "siting.ts").split("export function sitingStat")[1])


if __name__ == "__main__":
    unittest.main()
