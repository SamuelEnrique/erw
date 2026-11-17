"""Session 7550 (chain 304, part B): Should your family get an EV? (/play/ev) read as the reader it is for.

Energy Research Warehouse (ERW). No network, no model, no warehouse table written.

- TheReadDrawn   site/scripts/test-ev-game-read.mjs: the read's four site rows held fixed on the game and its decisions
                 fold drawn to HTML, and site/scripts/ev-game-figures.mjs --check (the committed figures are the page's).
- TheReadFile    docs/reviews/ev-game-read-2026-11-16.md: the reader and five cases first, numbered rows with a kind and a
                 state, the counts adding up, the shared figures table, no em dash and no figure of a held table.

    python -m unittest tests.test_session7550_ev_game_read -v
"""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
READ = os.path.join(ROOT, "docs", "reviews", "ev-game-read-2026-11-16.md")
EM_DASH = chr(0x2014)
KINDS = {"site", "data machine", "browser", "ruling"}


def src(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class TheReadDrawn(unittest.TestCase):
    def run_node(self, *args):
        return subprocess.run([NODE, "--import", "./scripts/tsx-register.mjs", *args], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=600)

    def test_read_rows_held(self):
        r = self.run_node("scripts/test-ev-game-read.mjs")
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-2000:])
        self.assertIn("every check passed", r.stdout)

    def test_figures_as_committed(self):
        r = self.run_node("scripts/ev-game-figures.mjs", "--check")
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-2000:])
        self.assertIn("as committed", r.stdout)


class TheReadFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t = src(READ)
        cls.rows = re.findall(r"^\| (\d+) \| ([\d, ]+) \| (.+?) \| (.+?) \| (site|data machine|browser|ruling) \| (.+?) \|$", cls.t, re.M)

    def test_reader_and_cases_first(self):
        head = self.t.split("## ")[0]
        self.assertIn("**The reader:**", head)
        self.assertIn("**The five cases:**", head)
        for place in ("Phoenix", "Minneapolis", "Fresno", "student"):
            self.assertIn(place, head)

    def test_rows_numbered_with_kind_and_state(self):
        nums = [int(r[0]) for r in self.rows]
        self.assertGreaterEqual(len(nums), 10)
        self.assertEqual(nums, list(range(1, len(nums) + 1)))
        for r in self.rows:
            self.assertIn(r[4], KINDS)
            self.assertTrue(r[5].strip())

    def test_counts_add_up(self):
        m = re.search(r"\*\*Counts\.\*\* Site, fixed: (\d+).*?Data machine: (\d+).*?Browser: (\d+).*?Ruling: (\d+)", self.t)
        self.assertIsNotNone(m)
        kinds = [r[4] for r in self.rows]
        self.assertEqual([int(x) for x in m.groups()], [kinds.count("site"), kinds.count("data machine"), kinds.count("browser"), kinds.count("ruling")])

    def test_shared_figures_and_cited_rows(self):
        self.assertIn("## The figures this page shares with other pages", self.t)
        self.assertIn("/learn/bill", self.t)
        self.assertIn("/board", self.t)
        self.assertIn("session 7547", self.t)

    def test_no_em_dash_no_held_table(self):
        self.assertNotIn(EM_DASH, self.t)
        with open(os.path.join(SITE, "data", "license_status.json"), encoding="utf-8") as f:
            held = set(json.load(f)["tables"])
        named = set(re.findall(r"`([a-z0-9_]+)`", self.t))
        self.assertEqual(sorted(named & held), [], "the read names a license-held table")


if __name__ == "__main__":
    unittest.main()
