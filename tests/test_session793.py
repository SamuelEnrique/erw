"""Session 793 (chain 065): the hub table's download. The rows shown, in the page's own figures; a cell the page draws in
words (lib/siting.ts, columnWords: "license needed", "not held", "no capacity market") is written as those words, never a
number. No request, no model call."""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")

SCRIPT = """
const F = await import('./scripts/siting-files.mjs');
const S = await import('./lib/siting.ts');
const f = F.files(), d = await F.dc();
const x = S.sitingInputs({ view: 'allgrids' });
const w = (id, col) => S.columnWords(d, f, S.rowOf(f, id), x, col);
process.stdout.write(JSON.stringify({ ercotCap: w('ercot:HB_HUBAVG', 'capacity'), pjmCap: w('pjm:grid', 'capacity'), ercotEnergy: w('ercot:HB_HUBAVG', 'energy'),
  caisoTx: w('caiso:TH_SP15_GEN-APND', 'transmission'), caisoAllin: w('caiso:TH_SP15_GEN-APND', 'allin') }));
"""


class Download(unittest.TestCase):
    def test_words_where_the_page_draws_words(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        r = subprocess.run([exe, "--input-type=module", "-e", SCRIPT], cwd=SITE, capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0:
            raise AssertionError(r.stderr)
        o = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertEqual(o["ercotCap"], "no capacity market")
        self.assertEqual(o["pjmCap"], "license needed")
        self.assertIsNone(o["ercotEnergy"])                 # a figure: the CSV writes the number
        self.assertEqual(o["caisoTx"], "not held")
        self.assertEqual(o["caisoAllin"], "not held")

    def test_the_view_draws_the_button(self):
        with open(os.path.join(SITE, "app", "cost-of-power", "AllGridsView.tsx"), encoding="utf-8") as f:
            v = f.read()
        self.assertIn("<AllGridsDownload", v)
        self.assertIn("columnWords(SITING_DC, SITING_FILES, r, x, c.id) ?? columnValue(", v)
        with open(os.path.join(SITE, "app", "cost-of-power", "AllGridsDownload.tsx"), encoding="utf-8") as f:
            self.assertIn('data-hub-download="1"', f.read())


if __name__ == "__main__":
    unittest.main()
