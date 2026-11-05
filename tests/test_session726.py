"""Session 726 (chain 062): the utility planner's walk, fixed. The Utility column's revenue per MWh is of three kinds
(bundled, delivery only, energy only, from EIA-861's service type); each cell names its kind, the sort's line says so,
and the A and B panel subtracts only like from like. No figure changes. No request, no model call."""
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
const f = F.files();
const row = (id) => S.rowOf(f, id);
process.stdout.write(JSON.stringify({ pjm: S.utilityKind(f, row('pjm:grid')), nyc: S.utilityKind(f, row('nyiso:N.Y.C.')),
  sp15: S.utilityKind(f, row('caiso:TH_SP15_GEN-APND')), words: S.SERVICE_WORDS }));
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
    return json.loads(r.stdout.strip().splitlines()[-1])


class Kinds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.o = run()

    def test_each_row_s_kind_is_its_seller_s_service(self):
        self.assertEqual(self.o["pjm"], "Delivery")       # FirstEnergy Pennsylvania: the wires
        self.assertEqual(self.o["nyc"], "Delivery")       # Consolidated Edison: the wires
        self.assertEqual(self.o["sp15"], "Bundled")       # Southern California Edison
        self.assertEqual(self.o["words"], {"Bundled": "", "Delivery": "delivery only", "Energy": "energy only"})

    def test_the_page_names_the_kind_and_subtracts_like_from_like(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        self.assertEqual(v.count("data-util-kind={u.service}"), 2)            # the state's seller and the county's
        self.assertIn('<Words words="not alike"', v)
        self.assertIn('x.sort === "utility" ? <> {UTILITY_KINDS_LINE}</>', v)
        self.assertIn("delivery only or energy only", src("site", "lib", "siting.ts"))


if __name__ == "__main__":
    unittest.main()
