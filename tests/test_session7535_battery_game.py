"""Session 7535 (chain 304, part A): the home battery game (/play/battery) taken to the done line.

Held here: the pieces this session changed, drawn to HTML with the site's own code (site/scripts/test-battery-game-render.mjs:
the decisions block, the outage banner of faults row 5, no move that moves nothing on any day and mode, rows 3 and 4,
the cap's date, row 6); the page's figures as committed (site/scripts/battery-game-figures.mjs --check); the replication
from the note's rules (every figure inside half the page's last shown digit); the do-file's expected values against the
replication's; the method note, the cross-check and the faults file; the wording of rows 1 and 2; and that no committed
file of the replication holds a license-held row (the game's days are ERCOT's and CAISO's; neither is a held grid).
"""
import json
import os
import re
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
REP = os.path.join(ROOT, "replication", "battery_game")
NODE = shutil.which("node")
DASHES = (chr(0x2014), chr(0x2013))
HELD_PREFIXES = ("isone:", "miso:", "nyiso:", "iso:isone", "iso:miso", "iso:nyiso")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(script, *args):
    r = subprocess.run([NODE, "--import", "./scripts/tsx-register.mjs", f"scripts/{script}", *args], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=900)
    return r.returncode, r.stdout, r.stderr


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class ThePiecesDrawn(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code, cls.out, cls.err = node("test-battery-game-render.mjs")

    def test_every_check_passes(self):
        self.assertEqual(self.code, 0, self.out[-3000:] + self.err[-1500:])
        self.assertNotIn("FAIL", self.out)
        m = re.search(r"(\d+) of (\d+) checks pass", self.out)
        self.assertTrue(m and m.group(1) == m.group(2) and int(m.group(2)) >= 80, self.out[-500:])

    def test_rows_3_and_4_on_every_day(self):
        self.assertGreaterEqual(len(re.findall(r"(?m)^ok   \S+ \S+: the perfect plan keeps 0 moves that move nothing", self.out)), 28)

    def test_the_figures_are_as_committed(self):
        code, out, err = node("battery-game-figures.mjs", "--check")
        self.assertEqual(code, 0, out[-2000:] + err[-1000:])
        self.assertIn("as committed", out)


class TheReplication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = subprocess.run([sys.executable, os.path.join(REP, "replicate.py"), "--tables", os.path.join(REP, "no-tables-here")], capture_output=True, text=True, encoding="utf-8", timeout=900)
        cls.code, cls.out = r.returncode, r.stdout + r.stderr

    def test_n_of_n(self):
        self.assertEqual(self.code, 0, self.out[-3000:])
        m = re.search(r"(\d+) of (\d+) figures inside half", self.out)
        self.assertTrue(m and m.group(1) == m.group(2) and int(m.group(2)) >= 3295, self.out[-800:])
        self.assertNotIn("\nDIFF", self.out)
        self.assertNotIn("\nMISSING", self.out)

    def test_the_do_files_expected_values_are_the_replications(self):
        do = src("replication", "battery_game", "replicate.do")
        for line, want in (("perfect battery's score", "60.9710"), ("plain rule's score", "43.8903"), ("fleet of 10,000 homes", "609710.12"), ("the rise", "408.90")):
            self.assertRegex(self.out, re.escape(want), line)
        for want in ("60.97 (60.9710)", "43.89 (43.8903)", "609,710.12", "408.90", "511.93 (511.9258)", "3,842.89", "24.90"):
            self.assertIn(want, do)

    def test_the_figures_file_counts_itself(self):
        body = json.loads(src("replication", "battery_game", "page_figures.json"))
        self.assertEqual(body["n"], len(body["figures"]))
        self.assertGreaterEqual(body["n"], 3290)
        cases = json.loads(src("replication", "battery_game", "cases.json"))["cases"]
        self.assertEqual(len(cases), 105)


class NoHeldRow(unittest.TestCase):
    def test_the_committed_files_hold_only_ercot_and_caiso(self):
        levels = json.loads(src("site", "data", "battery_levels.json"))["levels"]
        self.assertEqual({l["entity"].split(":")[0] for l in levels}, {"ercot", "caiso"})
        for name in ("page_figures.json", "cases.json", "stata_input.csv", "replicate.py", "replicate.do"):
            text = src("replication", "battery_game", name).lower()
            for p in HELD_PREFIXES:
                self.assertNotIn(p, text, f"{name} names {p}")


class TheWords(unittest.TestCase):
    def test_row_1_the_wear_is_per_kwh_drawn_out(self):
        game = src("site", "app", "play", "battery", "Game.tsx")
        self.assertIn("wear on every kWh drawn out of the battery", game)
        self.assertIn("of wear on each kWh it draws out of the battery", game)
        self.assertNotIn("wear on every kWh sold", game)

    def test_row_2_the_source_line_names_seven_days(self):
        page = src("site", "app", "play", "battery", "page.tsx")
        self.assertIn("the seven famous days (five ERCOT, two CAISO)", page)
        self.assertIn('"iso_hub_prices_history"]', page)

    def test_row_6_the_cap_date(self):
        for parts in (("site", "app", "play", "battery", "page.tsx"), ("site", "lib", "battery.ts")):
            self.assertNotIn("cap since 2023", src(*parts))
        self.assertIn("since 1 January 2022", src("docs", "methods", "battery_game.md"))


class TheDocuments(unittest.TestCase):
    def test_the_note_lists_the_blocks_keys(self):
        note, dec = src("docs", "methods", "battery_game.md"), src("site", "app", "play", "battery", "Decisions.tsx")
        keys = re.findall(r'\{ key: "([a-z]+)"', dec)
        self.assertEqual(len(keys), 15)
        sec = note.split("### The decisions block", 1)[1].split("###", 1)[0]
        self.assertEqual(re.findall(r"(?m)^\| `([a-z]+)` \|", sec), keys)

    def test_the_faults_file_counts(self):
        f = src("docs", "reviews", "battery-game-faults-2026-11-16.md")
        kinds = re.findall(r"(?m)^\| \d+ \| .*? \| (site|data machine|ruling) \| ", f)
        self.assertEqual(len(kinds), 10)
        self.assertEqual((kinds.count("site"), kinds.count("data machine"), kinds.count("ruling")), (6, 1, 3))
        self.assertIn("Counts: 10 faults: 6 site (all fixed), 1 data machine, 3 rulings.", f)

    def test_no_dashes_in_what_this_session_wrote(self):
        for parts in (("docs", "methods", "battery_game.md"), ("docs", "reviews", "battery-game-faults-2026-11-16.md"),
                      ("docs", "reviews", "battery-game-crosscheck-2026-11-16.md"), ("site", "app", "play", "battery", "Decisions.tsx"),
                      ("site", "scripts", "test-battery-game-render.mjs"), ("site", "scripts", "battery-game-figures.mjs"),
                      ("replication", "battery_game", "replicate.py"), ("replication", "battery_game", "replicate.do")):
            text = src(*parts)
            for d in DASHES:
                self.assertNotIn(d, text, "/".join(parts))


if __name__ == "__main__":
    unittest.main()
