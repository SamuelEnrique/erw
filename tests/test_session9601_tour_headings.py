"""Session 9601 (chain 620, 20 November 2026): no stop of the tour quotes words its page no longer shows.

Energy Research Warehouse (ERW). `node scripts/check-tour.mjs https://erw-flame.vercel.app` passed 89 of 96 on 20
November (row 429 of `docs/state/browser_reads_wanted.md`). Seven quoted headings were not among their pages' headings:
- "Your battery" on /cost-of-power/battery: the box is "Assumptions" since the owner's ruling of 15 October (session
  296). The stop now says "Assumptions".
- "Right now: demand" and "Who runs this grid" on /grid: they are on ERCOT's page, and /grid alone opens on the Lower
  48 since session 299. The stop, written "ERCOT first", opens /grid?grid=ercot.
- "Who trades with whom" on /supply: the heading carries its year ("Who trades with whom, 2025"). The check reads a
  heading with and without a year at its end.
- "How the map is drawn" on /map?tab=resources: a heading inside the fold "Method note", closed until opened. The
  stop's words say to open the fold, and the check reads the fold's headings.
- "Top of the industry" and "ERW's Numbers Today" on /digest: the page shows no Digest on a day none is written (the
  Digest is paused). Left as it is, for the owner's ruling: no Digest work is done here.

Held here, on the source (the proof in a browser is check-tour on a build): the three stops' words and addresses; each
quoted phrase of a stop is one the check reads; the check's two new readings; the page sources still hold the words.
Nothing here sets the environment, reads a table or makes a request.
"""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(NODE, "node is not installed")
class TheStops(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = subprocess.run([NODE, "--input-type=module", "-e", "import { STOPS } from './lib/tour.ts'; console.log(JSON.stringify(STOPS));"],
                           cwd=SITE, capture_output=True, text=True, timeout=60, encoding="utf-8")
        assert r.returncode == 0, r.stderr
        cls.stops = json.loads(r.stdout.strip().splitlines()[-1])
        cls.by = {s["title"]: s for s in cls.stops}

    def test_the_battery_stop_names_the_box_as_the_page_does(self):
        s = self.by["What a battery earns"]
        self.assertIn("Assumptions", s["headings"])
        self.assertNotIn("Your battery", json.dumps(s))
        page = "".join(src(folder, f) for folder, _, files in os.walk(os.path.join(SITE, "app", "cost-of-power", "battery")) for f in files if f.endswith(".tsx"))
        self.assertIn("Assumptions", page)
        self.assertNotRegex(page, r'<h2[^>]*>\s*Your battery|title="Your battery"', "no heading of the page reads Your battery")

    def test_the_grid_stop_opens_ercot_where_its_words_are(self):
        s = self.by["The grid"]
        self.assertEqual(s["href"], "/grid?grid=ercot")
        self.assertIn("ERCOT first", s["line"])
        grid = src("site", "components", "grid", "YourGrid.tsx")
        for h in ("Right now: demand", "Who runs this grid"):
            self.assertIn(h, s["headings"])
            self.assertIn(f'title="{h}"', grid)
        self.assertEqual(self.by["Every region of the grid"]["href"], "/grid", "the stop of the thirteen regions still opens the tool as it opens")

    def test_the_resource_stop_sends_the_reader_into_the_fold(self):
        s = self.by["What is under the ground and in the wind"]
        self.assertEqual(s["inFold"], {"fold": "Method note", "headings": ["How the map is drawn"]})
        self.assertNotIn("How the map is drawn", s["headings"])
        self.assertIn('open "Method note" under the map and read "How the map is drawn"', s["look"])

    def test_every_quoted_phrase_is_one_the_check_reads(self):
        for s in self.stops:
            read = s["headings"] + ([s["inFold"]["fold"]] + s["inFold"]["headings"] if s.get("inFold") else [])
            for q in re.findall(r'"([^"]+)"', s["look"]):
                self.assertIn(q, read, s["href"])


class TheCheck(unittest.TestCase):
    def setUp(self):
        self.c = src("site", "scripts", "check-tour.mjs")

    def test_a_heading_with_its_year_is_also_read_without_it(self):
        self.assertIn("(/, \\\\d{4}$/.test(h) ? [h, h.replace(/, \\\\d{4}$/, '')] : [h])", self.c)
        self.assertIn("for (const q of s.headings) check(hs.includes(q)", self.c)

    def test_a_folds_headings_are_read_by_the_folds_name(self):
        self.assertIn("const FOLDED = (fold) =>", self.c)
        self.assertIn("if (s.inFold) {", self.c)
        self.assertIn('the heading "${q}" is inside the fold "${s.inFold.fold}"', self.c)

    def test_no_em_dash(self):
        for parts in (("site", "lib", "tour.ts"), ("site", "scripts", "check-tour.mjs"), ("tests", "test_session9601_tour_headings.py")):
            self.assertNotIn(EM, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
