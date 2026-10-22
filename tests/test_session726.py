"""Session 726 (chain 062): the utility planner's path, fixed. The three faults session 725's walk found inside the
chain's files (docs/reviews/siting-utility-path.md, "What broke"): each utility figure says its basis under it (bundled,
energy only or delivery only; the county's seller or the state's stand-in) and the sort line says what the utility sort
compares; the rule's document is a link beside the rule's words; the A and B panel's utility row says each side's basis
in its tip. No figure moves. No request, no model call, no database read."""
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
const f = F.files();
const row = (id) => S.rowOf(f, id);
const words = (id) => S.utilityBasisWords(S.utilityCell(f, row(id)));
const out = {
  houston: words('ercot:HB_HOUSTON'), north: words('ercot:LZ_NORTH'), nyc: words('nyiso:N.Y.C.'), semass: words('isone:.Z.SEMASS'),
  pjm: words(S.hubRows(f.index).find((r) => r.grid === 'pjm').id), node: words('ercot:7RNCHSLR_ALL'),
  service: S.SERVICE_WORDS,
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


class TheBasisWords(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = run()

    def test_each_kind_of_seller(self):
        o = self.out
        self.assertEqual(o["service"], {"Bundled": "bundled", "Energy": "energy only", "Delivery": "delivery only"})
        # Houston's row is placed in Harris County; its seller is bundled
        self.assertEqual(o["houston"], "bundled; Harris County, TX")
        # the North load zone is not a place: the state's stand-in (TXU, which EIA-861 lists as bundled)
        self.assertEqual(o["north"], "bundled; the state's stand-in (TX)")
        # New York City's county seller bills delivery only
        self.assertEqual(o["nyc"], "delivery only; New York County, NY")
        self.assertEqual(o["semass"], "energy only; the state's stand-in (MA)")
        # PJM's row is placed in a county by session 718's hub counties: the words take the same form
        self.assertRegex(o["pjm"], r"^(bundled|energy only|delivery only); [A-Za-z .'-]+ County, [A-Z]{2}$")
        # a node has no utility: no words
        self.assertIsNone(o.get("node"))


class TheViewsWords(unittest.TestCase):
    def test_the_cells_and_the_sort_line(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        self.assertEqual(v.count("<UtilBasis c={c} />"), 2)
        self.assertIn('data-util-basis="1"', v)
        self.assertIn("The figure is a seller's industrial revenue over its sales: bundled, energy only or delivery only", v)
        self.assertIn("utilityBasisWords", v)

    def test_the_rules_document_is_a_link(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        self.assertIn('data-rule-doc="1"', v)
        self.assertIn('<a href={c.rule.url} className="underline" target="_blank" rel="noreferrer" data-rule-doc="1"', v)

    def test_the_panels_utility_row(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        self.assertIn('"ab-utility-basis": "1"', v)
        self.assertIn("What each side's figure is (session 726)", v)
        # session 716's rule: no database read
        self.assertNotIn("@/lib/supabase", v)

    def test_no_em_dash(self):
        for p in (("site", "app", "cost-of-power", "AllGridsView.tsx"), ("site", "lib", "siting.ts"), ("docs", "reviews", "siting-utility-path.md")):
            self.assertNotIn(chr(0x2014), src(*p), p)


if __name__ == "__main__":
    unittest.main()
