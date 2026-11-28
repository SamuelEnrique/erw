"""Session 8012, chain 505 (part B2): the page "Energy per AI query, as published" (/ai-energy)."""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheFile(unittest.TestCase):
    def setUp(self):
        self.d = json.loads(src("site", "data", "ai_energy.json"))

    def test_every_row_has_its_words_and_source(self):
        self.assertTrue(self.d["rows"])
        for r in self.d["rows"]:
            for k in ("x_printed", "x_unit", "x_measures", "source_url", "event_date", "parties", "x_sha256"):
                self.assertTrue(str(r[k]).strip(), (r["event_id"], k))
        self.assertEqual(self.d["table"], "ai_energy_published")
        self.assertNotIn(chr(0x2014), src("site", "data", "ai_energy.json"))


class ThePage(unittest.TestCase):
    def setUp(self):
        self.page = src("site", "app", "ai-energy", "page.tsx")
        self.lib = src("site", "lib", "aienergy.ts")

    def test_nothing_computed_from_the_figures(self):
        for word in ("reduce(", "Math."):
            self.assertNotIn(word, self.page + self.lib.split("export function figure")[0])

    def test_no_order_by_size(self):
        self.assertNotIn("x_value -", self.lib)
        self.assertNotIn("- a.x_value", self.lib)

    def test_in_no_menu(self):
        self.assertIn('{ href: "/ai-energy", label: "Energy per AI query, as published"', src("site", "lib", "pages.ts"))   # session 11405 (decision 4 of the weekend page of 28 November 2026, readied): in the menu under its own name
        self.assertIn('"/ai-energy": "review"', src("site", "lib", "release.ts"))   # session 11405 (decision 4, readied): its own line in the release gate, in review

    def test_the_fold_and_the_note_are_one_list(self):
        keys = re.findall(r'\{ key: "([a-z0-9-]+)", session: "', src("site", "app", "ai-energy", "Decisions.tsx"))
        note = src("docs", "methods", "ai_energy_published.md").split("### Decisions (session 8012)")[1]
        self.assertEqual(re.findall(r"^\| `([a-z0-9-]+)` \|", note, re.M), keys)


@unittest.skipUnless(NODE, "node is not on this machine")
class TheOrders(unittest.TestCase):
    def test_orders_keep_every_row(self):
        code = ("import fs from 'node:fs'; import * as A from './lib/aienergy.ts';"
                "const f = A.readAiFile(JSON.parse(fs.readFileSync('./data/ai_energy.json', 'utf8')));"
                "console.log(JSON.stringify({ n: f.rows.length, o: ['publisher','measures','newest','oldest'].map((k) => A.ordered(f.rows, k).length),"
                " first: A.ordered(f.rows, 'publisher')[0].parties, fig: A.figure(18061781), small: A.figure(0.0001) }));")
        r = subprocess.run([NODE, "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)
        d = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertEqual(d["o"], [d["n"]] * 4)
        self.assertEqual(d["first"], "Google")
        self.assertEqual(d["fig"], "18,061,781")
        self.assertEqual(d["small"], "0.0001")


if __name__ == "__main__":
    unittest.main()
