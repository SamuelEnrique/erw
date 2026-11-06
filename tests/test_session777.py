"""Session 777 (chain 064): the node list's rows handed to the browser column by column (lib/siting.ts, nodeColumns and
nodeRowsOf): the same rows come back, every field equal, so no figure or word moves; the field names and the id are no
longer repeated on each of 873 rows. No request, no model call."""
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
const rows = S.nodeTable(d, f, S.sitingInputs({ view: 'allgrids', profile: 'flexible' }));
const back = S.nodeRowsOf(S.nodeColumns(rows));
process.stdout.write(JSON.stringify({ n: rows.length, same: JSON.stringify(back) === JSON.stringify(rows), rows: JSON.stringify(rows).length, cols: JSON.stringify(S.nodeColumns(rows)).length }));
"""


class Columns(unittest.TestCase):
    def test_the_rows_come_back_whole_and_lighter(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        r = subprocess.run([exe, "--input-type=module", "-e", SCRIPT], cwd=SITE, capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0:
            raise AssertionError(r.stderr)
        o = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertGreater(o["n"], 800)
        self.assertTrue(o["same"])
        self.assertLess(o["cols"], 0.7 * o["rows"])

    def test_the_view_hands_columns(self):
        with open(os.path.join(SITE, "app", "cost-of-power", "AllGridsView.tsx"), encoding="utf-8") as f:
            self.assertIn("columns={nodeColumns(nodeTable(", f.read())


if __name__ == "__main__":
    unittest.main()
