"""Session 425: the ledger of /internal/waits reads sessions 351 to the newest report present (site/scripts/build-waits.mjs).

Energy Research Warehouse (ERW). Session 414 fixed the run at 351 to 413, so the reports that landed after it never
joined. What is held to:

  LEDGER's end is "newest", resolved by resolveRun to the highest session number among the reports the build read;
  the ledger resolves it itself, and so does the build's fault path, so the page always names a number;
  session 414's test and docs/machines.md say the same;
  on the repository's own reports, the run reaches past 413, every report of 401 to 415 present is read, and no
    asked line sits in two items (the node test, run here, holds the rest).

No request, no model call; the environment is read, never set. The tests that need node skip when it is absent.

    python -m unittest tests.test_session425 -v
"""

import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SCRIPT = os.path.join("site", "scripts", "build-waits.mjs")
REPORTS = os.path.join(ROOT, "archive", "sessions")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node_json(code):
    node = shutil.which("node")
    r = subprocess.run([node, "--input-type=module", "-e", code], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True,
                       encoding="utf-8", timeout=300)
    if r.returncode != 0:
        raise AssertionError((r.stdout + r.stderr)[-3000:])
    return json.loads(r.stdout)


class TheRun(unittest.TestCase):
    def test_the_end_is_the_newest_report_and_is_resolved_everywhere(self):
        s = src(*SCRIPT.split(os.sep))
        self.assertIn('export const LEDGER = { from: 351, to: "newest" };', s)
        self.assertIn("export function resolveRun(reports, run = LEDGER) {", s)
        body = s.split("export function ledger(", 1)[1]
        self.assertTrue(body.split("\n", 2)[1].strip() == "run = resolveRun(reports, run);", "the ledger resolves the run first")
        self.assertIn("led = { ...resolveRun(all), error:", s, "the fault path names a number too")
        self.assertNotIn("...LEDGER, error", s)
        self.assertNotIn(chr(0x2014), s)

    def test_the_check_reads_an_item_with_punctuation_after_inline_code(self):
        s = src("site", "scripts", "check-internal-waits.mjs")
        self.assertIn('.replace(/ ([,.;:)])/g, "$1").includes(words.replace(/ ([,.;:)])/g, "$1"))', s)

    def test_414s_test_and_the_machines_note_follow(self):
        self.assertIn('export const LEDGER = { from: 351, to: "newest" };', src("tests", "test_session414.py"))
        self.assertIn("351 to the newest report present at the build since session 425", src("docs", "machines.md"))


@unittest.skipUnless(shutil.which("node"), "no node on this machine")
class OnTheRepository(unittest.TestCase):
    def test_resolve_run(self):
        out = node_json(
            'import { resolveRun } from "./scripts/build-waits.mjs";'
            'console.log(JSON.stringify([resolveRun([{ n: 351 }, { n: 475 }]), resolveRun([{ n: 300 }]), resolveRun([{ n: 475 }], { from: 900, to: 902 })]));'
        )
        self.assertEqual(out, [{"from": 351, "to": 475}, {"from": 351, "to": 351}, {"from": 900, "to": 902}])

    def test_the_ledger_reaches_the_newest_report_and_reads_401_to_415(self):
        out = node_json(
            'import { build } from "./scripts/build-waits.mjs";'
            'const w = build(".."); const L = w.ledger;'
            'const lines = L.groups.flatMap((g) => g.asked.map((x) => x.session + ":" + x.line));'
            'console.log(JSON.stringify({ error: L.error, from: L.from, to: L.to, held: L.held, lines, marker: w.marker.order }));'
        )
        self.assertIsNone(out["error"])
        self.assertEqual(out["from"], 351)
        present = []
        for f in os.listdir(REPORTS):
            m = re.match(r"^SESSION_(\d+)([A-Za-z]?)_REPORT\.md$", f)
            if m and int(m.group(1)) >= 351 and (out["marker"] is None or int(m.group(1)) * 100 > out["marker"]):
                present.append(int(m.group(1)))
        self.assertEqual(out["to"], max(present), "the run ends at the newest report present")
        self.assertGreater(out["to"], 413)
        held = {int(re.match(r"\d+", h).group(0)) for h in out["held"]}
        for n in range(401, 416):
            if n in present:
                self.assertIn(n, held, f"session {n}'s report is read")
        self.assertEqual(len(out["lines"]), len(set(out["lines"])), "no asked line in two items")

    def test_the_node_cases_hold(self):
        r = subprocess.run([shutil.which("node"), os.path.join("site", "scripts", "test-waits-ledger.mjs")], cwd=ROOT, capture_output=True,
                           text=True, encoding="utf-8", timeout=300)
        self.assertEqual(r.returncode, 0, (r.stdout + r.stderr)[-3000:])


if __name__ == "__main__":
    unittest.main()
