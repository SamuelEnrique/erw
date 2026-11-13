"""A held table's row count is held too (session 4005, chain 228, the landing desk).

The desktop's third window (chain 229, sessions 4100 to 4150) held policy_actions and policy_reads: the PUCT's news
releases need written permission. Its gate on 13 November 2026 found /policy?view=week printing "0" for the actions read
where the live set holds 151: the week view's count carries the key event_count|policy_actions|since|<day>, and Num's
heldBy read a table from event| and entity| keys but not from event_count|, so the count was drawn from the empty held
rows as a number. heldBy (site/components/Num.tsx) and check-holds.mjs's judgeKey now read event_count|<table>| as
event|<table>| is read, so the count says "license needed". /policy joins land_check.py's HELD_FLOOR_PAGES (its floor a
pass only when the page shows "license needed"), a default for Samuel's ruling."""

import json
import os
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import land_check as LC  # noqa: E402


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheCountOfAHeldTable(unittest.TestCase):
    def test_num_reads_the_table_of_a_count_key(self):
        s = src("site", "components", "Num.tsx")
        self.assertIn('else if (head === "event_count") table = p[1] ?? "";', s)
        # read before KEY_TABLE, beside event| and entity|
        self.assertLess(s.index('head === "event_count"'), s.index("else if (head in KEY_TABLE)"))

    def test_check_holds_judges_a_count_key_by_its_table(self):
        if shutil.which("node") is None:
            self.skipTest("node is not on this machine")
        mod = os.path.join(ROOT, "site", "scripts", "check-holds.mjs").replace("\\", "/")
        js = ("import('file:///" + mod.lstrip("/") + "').then((m) => { const held = new Map([['policy_actions', {byGrid: false, grids: new Set()}]]);"
              "console.log(JSON.stringify([m.judgeKey('event_count|policy_actions|since|2026-10-14', held, new Set()),"
              "m.judgeKey('event_count|policy_actions|all', held, new Set()), m.judgeKey('event_count|energy_deals|all', held, new Set())])) })")
        out = subprocess.run(["node", "-e", js], capture_output=True, text=True, timeout=60, cwd=os.path.join(ROOT, "site"))
        if out.returncode != 0 and "Cannot find" in out.stderr:
            self.skipTest("check-holds.mjs needs the site's modules: " + out.stderr.strip().splitlines()[-1][:120])
        self.assertEqual(out.returncode, 0, out.stderr)
        got = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertEqual(got[0]["table"], "policy_actions")
        self.assertEqual(got[1]["table"], "policy_actions")
        self.assertIsNone(got[2])

    def test_the_policy_page_floor_is_a_held_floor(self):
        self.assertIn("/policy", LC.HELD_FLOOR_PAGES)
        log = 'note | /x | y\nFAIL | /policy | the floor | the page carries 0 checked numbers and 2 held by a license; its floor is 10\n'
        self.assertEqual(LC.held_floor_failures(log), ["/policy"])


if __name__ == "__main__":
    unittest.main()
