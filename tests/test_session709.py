"""Session 709: the ERCOT node set of the All grids tab (docs/methods/siting.md). Every node a row with only its own
figures (energy, basis, all-in, days held), each the same as the hub table's arithmetic; what every node shares drawn
once above the table; the sort by any column, a node with no figure last; the list virtual, the first rows on the server.
No request, no model call."""
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
const F = await import('./scripts/siting-files.mjs');
const S = await import('./lib/siting.ts');
const d = await F.dc(); const f = F.files();
const x = { profile: 'datacenter', lf: 0.9, strike: null };
const rows = S.nodeTable(d, f, x);
const byE = S.sortNodes(rows, 'energy', 'desc'), byB = S.sortNodes(rows, 'basis', 'asc');
const r = rows.find((k) => k.per !== null) ?? null;
const out = { n: rows.length, held: rows.filter((k) => k.per !== null).length, first: r, whys: rows.filter((k) => k.per === null).map((k) => k.why),
  key: r && S.sitingStat(f, 'allgrids|energy|' + r.id + '|da', d), basis: r && S.sitingStat(f, 'allgrids|basis|' + r.id, d), allin: r && S.sitingStat(f, 'allgrids|allin|' + r.id + '|' + S.profileKey(x), d),
  energyDesc: byE.slice(0, 3).map((k) => k.per), lastE: byE.at(-1).per, basisAsc: byB.slice(0, 3).map((k) => k.basis),
  flex: r && S.nodeTable(d, f, { profile: 'flexible', lf: 0.9, strike: 1000 }).find((k) => k.id === r.id) };
process.stdout.write(JSON.stringify(out));
"""


def run():
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", SCRIPT], cwd=SITE, capture_output=True, text=True, timeout=900, encoding="utf-8")
    if r.returncode != 0 and "Unknown file extension" in r.stderr:
        raise unittest.SkipTest("this node does not read TypeScript files")
    if r.returncode != 0:
        raise AssertionError(r.stderr)
    return json.loads(r.stdout)


class Nodes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.o = run()

    # Session 2863: from 31 October 2026 no node has a twelve-month figure (node_basis_daily's day-ahead days stopped at
    # 20 October, under 90 percent of the hub's November 2025 to October 2026), and the script failed on the first drawn
    # node, which did not exist. With none drawn, every row says why; with one drawn, its figures are checked as before.
    # Which nodes are drawn is test_session701's count, from nodes.json and the rule.
    def test_every_node_a_row_and_its_figures_the_hub_table_s(self):
        self.assertEqual(self.o["n"], 873)
        r = self.o["first"]
        if r is None:
            self.assertEqual(self.o["held"], 0)
            self.assertEqual(len(self.o["whys"]), 873)
            self.assertTrue(all("fewer than 90 percent" in w or "are not held" in w for w in self.o["whys"]), self.o["whys"][:3])
            return
        self.assertEqual(r["per"], self.o["key"])
        self.assertEqual(r["basis"], self.o["basis"])
        self.assertEqual(r["allin"], self.o["allin"])
        self.assertGreaterEqual(r["days"], 0.9 * r["due"])

    def test_the_profile_moves_the_energy_not_the_basis(self):
        r, fl = self.o["first"], self.o["flex"]
        if r is None:
            self.assertIsNone(fl)
            return
        self.assertEqual(fl["basis"], r["basis"])
        self.assertLessEqual(fl["per"], r["per"])

    def test_the_sort_and_a_node_with_no_figure_last(self):
        e = [v for v in self.o["energyDesc"] if v is not None]
        self.assertEqual(e, sorted(e, reverse=True))
        self.assertEqual(self.o["energyDesc"][:len(e)], e)                 # the figures first, a node with none after
        self.assertIsNone(self.o["lastE"])
        b = [v for v in self.o["basisAsc"] if v is not None]
        self.assertEqual(b, sorted(b))
        self.assertEqual(self.o["basisAsc"][:len(b)], b)

    def test_the_list_is_virtual_and_shared_figures_are_drawn_once(self):
        n = src("site", "app", "cost-of-power", "AllGridsNodes.tsx")
        self.assertIn("sorted.slice(start, end)", n)
        self.assertIn("const ROW = 34, VIEW = 18, PAD = 12, FIRST = 40;", n)
        self.assertIn('q.set("nsort", by); q.set("ndir", d);', n)
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        self.assertIn("<NodeShared x={x} />", v)
        self.assertEqual(v.count("<SharedLine hub={hub} x={x} />"), 1)   # session 717: one sentence, each figure once


if __name__ == "__main__":
    unittest.main()
