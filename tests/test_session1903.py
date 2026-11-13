"""Session 1903: the gate of 13 November (runs/land_check/0c285324...) stopped at check-values on nine cells of the
datacenter tracker's grids view that session 1898 drew for the first time (they had been held with the facilities):
"FAIL | /datacenters?view=grids | dcgrid|capacity_mw|ERCOT | page shows "164,685" | page read 164685.4 | Supabase 164685.4"
and "dcgrid|reserve_margin|ERCOT | page shows "11.4" | page read 11.428383". The page's value was the live set's; the
checker expected two decimals for a figure that is not whole, while app/datacenters/FacilitiesVsGrid.tsx writes MW whole
and the reserve margin and the share of peak to one decimal. The checker now reads them as the page writes them.

The two rules are taken from site/scripts/check-values.mjs and run in node on the gate's own cells."""

import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CV = os.path.join(ROOT, "site", "scripts", "check-values.mjs")
PAGE = os.path.join(ROOT, "site", "app", "datacenters", "FacilitiesVsGrid.tsx")

# (check key, the page's text, the raw value, passes)
CASES = [
    ["dcgrid|capacity_mw|ERCOT", "164,685", "164685.4", True],
    ["dcgrid|reserve_margin|ERCOT", "11.4", "11.428383", True],
    ["dcgrid|capacity_mw|MISO", "195,473", "195472.7", True],
    ["dcgrid|capacity_mw|NYISO", "42,787", "42786.6", True],
    ["dcgrid|peak_mw|ERCOT", "83,597", "83597", True],
    ["dcgrid|share_of_peak|ERCOT", "12.3", "12.345", True],
    # a wrong figure still fails
    ["dcgrid|capacity_mw|ERCOT", "164,686", "164685.4", False],
    ["dcgrid|reserve_margin|ERCOT", "11.5", "11.428383", False],
    # another key is not read by these rules
    ["projects|mw|x", "164,685", "164685.4", False],
]


def rule_lines():
    with open(CV, encoding="utf-8") as f:
        src = f.read()
    return [ln.strip() for ln in src.splitlines() if re.match(r"\s*const dc(Whole|One) = ", ln)]


class TheRule(unittest.TestCase):
    def test_both_rules_are_in_the_checker_and_join_the_text_test(self):
        self.assertEqual(len(rule_lines()), 2)
        with open(CV, encoding="utf-8") as f:
            # session 4219 (chain 239): the forecast's own text rule joins after them
            self.assertRegex(f.read(), r"\|\| chartOk \|\| dcWhole \|\| dcOne( \|\| forecastOk)?;")

    def test_the_page_writes_as_the_rules_read(self):
        with open(PAGE, encoding="utf-8") as f:
            src = f.read()
        self.assertIn('const whole = (v: number) => Math.round(v).toLocaleString("en-US");', src)
        self.assertIn("{rm.peak.pct.toFixed(1)}", src)
        self.assertIn("{share.toFixed(1)}", src)

    @unittest.skipUnless(shutil.which("node"), "node is not on this machine")
    def test_the_gate_s_cells(self):
        js = "const cases = " + json.dumps(CASES) + ";\nconst out = cases.map(([check, text, raw]) => {\n" + \
             "\n".join(rule_lines()) + "\nreturn dcWhole || dcOne; });\nconsole.log(JSON.stringify(out));"
        r = subprocess.run(["node", "-e", js], capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout), [c[3] for c in CASES])


if __name__ == "__main__":
    unittest.main()
