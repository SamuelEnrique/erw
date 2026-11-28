"""Session 11405 (chain 770, part C): ruling 65 readied, wip/ready-severance-btu-1034 (origin/main with
wip/alt-severance-3 merged; part 3.2 of the weekend page of 28 November keeps it apart from the S1 switches of
wip/switch-severance, with which it conflicts in site/app/severance/Calculator.tsx). Not requested: it lands on the
owner's word.

The severance calculator takes an Mcf of gas as 1.034 MMBtu (EIA's 1,034 Btu a cubic foot, site/data/forecast/gas.json),
the rule /impact uses; origin/main takes it as 1.000. Measured with the page's own function and rules file
(site/scripts/test-alt-severance-3.mjs): one well's 46,500 Mcf of Texas gas at USD 2.99, USD 10,427.63 on origin/main,
10,782.16 here (+3.40 percent); New Mexico's gas taxes the same 3.40 percent (11,039.38 to 11,414.72); Louisiana's
per-Mcf tax 7,040.10 under both; oil unchanged. The Lease tab and the lease finder still price an Mcf as one MMBtu.
"""
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheSource(unittest.TestCase):
    def test_the_calculator_hands_the_factor_to_compute(self):
        calc = src("site", "app", "severance", "Calculator.tsx")
        self.assertIn("mmbtuPerMcf: MMBTU_PER_MCF", calc)
        self.assertIn("mmbtuPerMcf", src("site", "lib", "severance.ts"))


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class TheFigures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = subprocess.run([NODE, "--import", "./scripts/tsx-register.mjs", "scripts/test-alt-severance-3.mjs"], cwd=SITE,
                           capture_output=True, text=True, encoding="utf-8", timeout=300)
        cls.code, cls.out = r.returncode, r.stdout + r.stderr

    def test_every_check_passes(self):
        self.assertEqual(self.code, 0, self.out[-2000:])
        m = re.search(r"(\d+) of (\d+) passed", self.out)
        self.assertTrue(m and m.group(1) == m.group(2) and int(m.group(2)) >= 7, self.out[-800:])

    def test_the_measured_figures(self):
        self.assertIn("Texas gas, 46,500 Mcf at $2.99: main 10427.63, the other choice 10782.16", self.out)
        self.assertIn("New Mexico gas, 46,500 Mcf at $2.99: main 11039.38, the other choice 11414.72", self.out)


if __name__ == "__main__":
    unittest.main()
