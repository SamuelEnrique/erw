"""Session 724 (chain 062): the trader's path, fixed. The seven faults session 723's walk found inside the chain's files
(docs/reviews/siting-trader-path.md, "What broke"): a node chosen as A or B shows in the box's lists; the headline and
the A and B panel are drawn in the node view; the node panel's Close keeps the screen and its two links set the node as
A or B; the node list's status line keeps the hub's name as written; the basis spread is a sortable, keyed column
(allgrids|nodespread|<node>, the 90th percentile less the 10th of the panel); the sort line says the transmission sort
reads the profile's own charge; the shared line cites the column's table. The gaps file gains real time at the nodes.
No request, no model call, no database read."""
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
const F = await import('./scripts/siting-files.mjs');
const f = F.files(), dc = await F.dc();
const rows = S.nodeTable(dc, f, { profile: 'datacenter', lf: 0.9, strike: null });
const withSpread = rows.filter((r) => r.spread !== null);
const desc = S.sortNodes(rows, 'spread', 'desc');
const first = desc[0];
const n = f.nodes.nodes.find((k) => `ercot:${k.id}` === first.id);
const out = {
  sorts: S.NODE_SORTS, words: S.NODE_SORT_WORDS,
  n: rows.length, nSpread: withSpread.length,
  firstId: first.id, firstSpread: first.spread, firstPct: n.pct,
  descOk: desc.filter((r) => r.spread !== null).every((r, i, a) => i === 0 || a[i - 1].spread >= r.spread),
  nullLast: desc.slice(desc.length - (rows.length - withSpread.length)).every((r) => r.spread === null),
  stat: S.sitingStat(f, `allgrids|nodespread|${first.id}`, dc),
  statNone: S.sitingStat(f, 'allgrids|nodespread|ercot:HB_HUBAVG', dc),
  nodeAsRow: !!S.rowOf(f, first.id),
};
process.stdout.write(JSON.stringify(out));
"""


def run():
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", SCRIPT], cwd=SITE, capture_output=True, text=True, timeout=300, encoding="utf-8")
    if r.returncode and "TypeScript" in (r.stderr or "") and "strip" in (r.stderr or ""):
        raise unittest.SkipTest("this node does not read TypeScript files")
    if r.returncode:
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout)


class TheSpreadColumn(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = run()

    def test_the_spread_is_the_panels_percentiles(self):
        o = self.out
        self.assertEqual(list(o["sorts"]), ["node", "cls", "energy", "basis", "spread", "allin", "days"])
        self.assertEqual(o["words"]["basis"], "basis to HB_HUBAVG")
        self.assertEqual(o["words"]["spread"], "basis spread")
        self.assertGreater(o["nSpread"], 800)
        self.assertAlmostEqual(o["firstSpread"], o["firstPct"][2] - o["firstPct"][0], places=9)
        self.assertTrue(o["descOk"])
        self.assertTrue(o["nullLast"])

    def test_the_key_is_recomputed_and_a_hub_has_none(self):
        o = self.out
        self.assertAlmostEqual(o["stat"], o["firstSpread"], places=9)
        self.assertIsNone(o.get("statNone"))   # JSON drops an undefined value: the key is absent
        self.assertTrue(o["nodeAsRow"])


class TheViewsWords(unittest.TestCase):
    def test_the_node_list(self):
        n = src("site", "app", "cost-of-power", "AllGridsNodes.tsx")
        self.assertNotIn("toLowerCase()", n)
        self.assertIn("Sorted by {NODE_SORT_WORDS[by]}", n)
        self.assertIn("data-check={`allgrids|nodespread|${r.id}`}", n)
        self.assertIn('spread: "Basis spread"', n)
        # session 709's sort is kept in the address as before
        self.assertIn('q.set("nsort", by); q.set("ndir", d);', n)

    def test_the_view(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        # the headline and the panel in both views, not inside the hubs branch
        self.assertIn("<Headline x={x} /><AbPanel x={x} />", v)
        self.assertNotIn('{x.rows === "hubs" ? <><Headline x={x} /><AbPanel x={x} /></> : null}', v)
        # the panel keeps the screen on Close and sets A or B
        self.assertIn("<NodePanel id={q.node} q={q} />", v)
        self.assertIn('data-node-close="1"', v)
        self.assertIn('data-node-set="a"', v)
        self.assertIn('data-node-set="b"', v)
        self.assertNotIn('new URLSearchParams({ view: "allgrids", rows: "nodes" })', v)
        # the box's lists hold a node once chosen
        self.assertIn("rows={formRows(hubs, x)}", v)
        self.assertIn("(node)", v)
        # the transmission sort says what it reads; the shared line cites the column's table
        self.assertIn("The sort reads the profile's own charge, not the firm figure beside it.", v)
        self.assertNotIn("(lbnl_interconnection_queue)", v)
        self.assertIn("from Berkeley Lab's queue file: the column's figure", v)
        # session 716's rule: no database read
        self.assertNotIn("@/lib/supabase", v)

    def test_the_check_address_and_its_floor(self):
        a = "/cost-of-power?view=allgrids&rows=nodes&nsort=spread&ndir=desc&a=ercot%3ABBREEZE_1_2&b=ercot%3AELSAUZ_ALL"
        self.assertIn(f'"{a}"', src("site", "scripts", "check-values.mjs"))
        floors = json.loads(src("site", "scripts", "check-values-floor.json"))
        found = [v for d in (floors, *[x for x in floors.values() if isinstance(x, dict)]) for k, v in d.items() if k == a]
        self.assertEqual(found, [10])


class TheGaps(unittest.TestCase):
    def test_real_time_at_the_nodes_is_a_row(self):
        md = src("docs", "reviews", "siting-gaps.md")
        self.assertIn("| ERCOT nodes | Energy | a node's real-time price", md)
        g = json.loads(src("site", "data", "siting", "gaps.json"))
        self.assertTrue(any(r["Grid"] == "ERCOT nodes" and r["Column"] == "Energy" and "real-time" in r["What is not held"] for r in g["rows"]))

    def test_no_em_dash(self):
        for p in (("site", "app", "cost-of-power", "AllGridsView.tsx"), ("site", "app", "cost-of-power", "AllGridsNodes.tsx"), ("site", "lib", "siting.ts"),
                  ("docs", "reviews", "siting-gaps.md"), ("docs", "reviews", "siting-trader-path.md")):
            self.assertNotIn(chr(0x2014), src(*p), p)


if __name__ == "__main__":
    unittest.main()
