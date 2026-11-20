"""Chain 507 (session 8900): a state's share of US crude counts the state once.

Energy Research Warehouse (ERW). eia_crude_production_state_monthly holds Alaska's total (MCRFPAK) and its North Slope
(MANFPAK, within Alaska) under one code, SAK; the findings hunt summed both, and the draft state-crude-share-crude-ak
said 6.1 percent of US crude in 2025 where Alaska counted once is 3.1 (withdrawn by the audit). The measure, its Python
mirror and its Stata mirror now read the state's total only. Small files written here; no warehouse file, no network.
"""

import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings", "deep"))
import oil  # noqa: E402

ROWS = [("eia_crude_production:NUS:MCRFPUS", 1000.0), ("eia_crude_production:SAK:MCRFPAK", 40.0),
        ("eia_crude_production:SAK:MANFPAK", 38.0), ("eia_crude_production:STX:MCRFPTX", 420.0)]


def table(d):
    p = os.path.join(d, oil.CRUDE + ".csv")
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write("# a test table\nentity,variable,ts_utc,value\n")
        for y in (2024, 2025):
            for m in range(1, 13):
                for e, v in ROWS:
                    f.write(f"{e},field_production_per_day,{y}-{m:02d}-01T00:00:00Z,{v}\n")
    return p


class CrudeShare(unittest.TestCase):
    def test_the_measure_counts_alaska_once(self):
        with tempfile.TemporaryDirectory() as d:
            table(d)
            rows = oil.state_crude_share(d)["rows"]
        ak = {r["year"]: r for r in rows if r["region"] == "crude_AK"}
        tx = {r["year"]: r for r in rows if r["region"] == "crude_TX"}
        self.assertAlmostEqual(ak[2025]["value"], 4.0)
        self.assertEqual(ak[2025]["n"], 12)
        self.assertAlmostEqual(tx[2025]["value"], 42.0)

    def test_the_python_mirror_counts_alaska_once(self):
        with tempfile.TemporaryDirectory() as d:
            p = table(d)
            script = os.path.join(d, "r.py")
            with open(script, "w", encoding="utf-8") as f:
                f.write(oil.reproduce_py("state_crude_share", "crude_AK"))
            out = subprocess.run([sys.executable, "-I", script, p], capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        got = {ln.split()[0]: ln.split()[1:] for ln in out.stdout.splitlines() if ln.strip()}
        self.assertEqual(got["2025"], ["4.0", "12"])

    def test_the_stata_mirror_drops_the_area_within(self):
        do = oil.reproduce_do("state_crude_share", "crude_AK")
        self.assertIn('drop if word(subinstr(entity, ":", " ", .), 3) == "MANFPAK"', do)
        self.assertLess(do.index("MANFPAK"), do.index('keep if code == "NUS" | code == "SAK"'))


if __name__ == "__main__":
    unittest.main()
