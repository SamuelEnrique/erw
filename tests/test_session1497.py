"""Sessions 1497 to 1499 (chain 158): the three users' paths walked on a build, each step with its screenshot, and the
walk's script. No network, no browser, no model. Nothing here sets the environment at import.
"""
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ThePaths(unittest.TestCase):
    def test_every_step_has_its_screenshot(self):
        shots = set(os.listdir(os.path.join(ROOT, "docs", "brand", "review-1497")))
        for name, prefix in (("trader-1497.json", "trader"), ("onenergy-1497.json", "onenergy"), ("lab-1497.json", "lab")):
            with open(os.path.join(ROOT, "docs", "reviews", "paths", name), encoding="utf-8") as f:
                steps = json.load(f)["steps"]
            for s in steps:
                self.assertIn(f"{prefix}-{s['id']}-1280.png", shots, (name, s["id"]))
            self.assertIn(f"{prefix}-{steps[0]['id']}-390.png", shots)

    def test_the_documents_name_their_walk(self):
        for doc, words in (("trader-path.md", "## Walked again on a build, 6 November 2026 (session 1497, chain 158)"),
                           ("onenergy-walkthrough.md", "# The On.Energy walkthrough, click by click"),
                           ("lab-path.md", "# The lab's path, click by click")):
            with open(os.path.join(ROOT, "docs", "reviews", doc), encoding="utf-8") as f:
                t = f.read()
            self.assertIn(words, t)
            self.assertIn("walk-paths-1497.mjs", t)
            self.assertNotIn(chr(0x2014), t)

    def test_the_script_reads_only(self):
        with open(os.path.join(ROOT, "site", "scripts", "walk-paths-1497.mjs"), encoding="utf-8") as f:
            js = f.read()
        self.assertIn('import { withBrowser } from "./browser.mjs";', js)
        self.assertIn("It reads only.", js)
        self.assertNotIn("method: \"POST\"", js)


if __name__ == "__main__":
    unittest.main()
