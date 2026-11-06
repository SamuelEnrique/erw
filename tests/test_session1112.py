"""Session 1112 (chain 075): the held grids, said right.

Held here: the saved rows of session 320's four held-grid questions (tests/fixtures/session1112/held_reads.json,
written by warehouse/chat/eval/fixture_s1112.py) hold every hub of the month, the held grids' included, and each
question's public figures are the public hubs' rows; site/scripts/test-ask-1112.mjs holds that the site's query tool,
asked for a held grid's rows, names the grid, says "license needed", states none of its figures and gives the same
query's figure for every public grid, also in a chat scoped to the held grid; the hold's list of grids is the status
file's (site/data/license_status.json), unchanged by this session.
No network, no warehouse table, no model. Nothing here sets the environment at import.
"""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
FIX = os.path.join(ROOT, "tests", "fixtures", "session1112", "held_reads.json")


def fixture():
    with open(FIX, encoding="utf-8") as f:
        return json.load(f)


class TheRows(unittest.TestCase):
    def test_the_four_and_their_public_hubs(self):
        fx = fixture()
        self.assertEqual(sorted(fx["questions"]), ["d05", "d07", "g07", "g08"])
        for qid, q in fx["questions"].items():
            self.assertTrue(q["entity"].startswith(("isone:", "nyiso:")), qid)
            rows = [r for r in fx["rows"] if r["table_name"] == q["table"] and r["variable"] == q["variable"]
                    and r["ts_utc"].startswith(q["start"])]
            self.assertIn(q["entity"], {r["entity"] for r in rows}, qid)
            public = {r["entity"]: r["value"] for r in rows if not r["entity"].startswith(("isone:", "nyiso:", "miso:"))}
            self.assertEqual(public, q["public"], qid)
            self.assertEqual({e.split(":")[0] for e in public}, {"caiso", "ercot", "spp"}, qid)

    def test_the_hold_is_the_status_files(self):
        with open(os.path.join(SITE, "data", "license_status.json"), encoding="utf-8") as f:
            st = json.load(f)["tables"]
        for t in ("merchant_revenue_monthly", "cost_of_power_monthly"):
            self.assertEqual(st[t]["status"], "license needed")
            self.assertEqual(sorted(st[t]["publishers"]), ["ISO-NE", "MISO", "NYISO"])


class TheSiteTool(unittest.TestCase):
    def test_the_site_tool_on_the_same_rows(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        if not os.path.isdir(os.path.join(SITE, "node_modules")):
            raise unittest.SkipTest("the site's packages are not installed in this copy")
        r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "scripts/test-ask-1112.mjs"], cwd=SITE,
                           capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("5 of 5 passed", r.stdout)


if __name__ == "__main__":
    unittest.main()
