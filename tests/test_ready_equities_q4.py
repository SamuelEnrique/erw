"""Ready branch for /equities (session 11408, chain 770 part C; weekend page 2026-11-28, part 3.5, "work out a fourth
quarter as the year less nine months": the other choice, yes). Not the default: it waits for Samuel's ruling.

site/lib/equities.ts fourthQuarters: a sum whose quarter is filed only inside a year's total is the year less its first
nine months, where both are filed for one fiscal year and the quarter is not; drawn in the chart beside the quarters
filed, never in the headline or the tables, never for debt or shares. On the page files now on main: 1,507 fourth
quarters of revenue worked out; companies with a fourth-quarter point 146 to 218 of 234.

1. scripts/test-ready-equities-q4.mjs (a fixture, and the counts on the real series files), run by Node.
2. The page and the note say it."""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
REACT = os.path.isdir(os.path.join(SITE, "node_modules", "react"))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class AFourthQuarterWorkedOut(unittest.TestCase):
    @unittest.skipUnless(NODE and REACT, "node or the site's packages are not installed")
    def test_the_rule_and_the_counts(self):
        r = subprocess.run([NODE, "--import", "./scripts/events-page-register.mjs", "scripts/test-ready-equities-q4.mjs"],
                           cwd=SITE, capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        counts = json.loads([ln for ln in r.stdout.splitlines() if ln.startswith("{")][-1])
        self.assertGreater(counts["fourth_quarters_worked"], 0)
        self.assertGreater(counts["after"], counts["companies_with_a_fourth_quarter_before"])

    def test_the_words(self):
        view = src("site", "app", "equities", "view.tsx")
        self.assertIn('worked: q.per === "3" ? fourthQuarters(fs, q.fig) : []', view)
        self.assertIn("fourth quarters filed only inside a year are worked out as the year less its first nine months", view)
        self.assertIn("data-eq-worked={x.worked.length}", view)
        self.assertIn("export function fourthQuarters(fs: Filing[], col: FigureKey): WorkedPoint[]", src("site", "lib", "equities.ts"))
        self.assertIn("**A fourth quarter worked out (session 11408", src("docs", "methods", "equities.md"))


if __name__ == "__main__":
    unittest.main()
