"""Session 1157 (chain 077, 23 October 2026): Ask your grid, on stored answers. The Ask panel of /grid shows, under the
live box, up to five stored example answers for the grid on screen (site/components/grid/AskExamples.tsx,
site/lib/gridask.ts), copied from the recorded evaluations in warehouse/chat/eval/ into site/data/grid_ask_examples.json
by site/scripts/build-grid-ask-examples.mjs: answers graded right, each figure traced to a tool result, held tables
refused in the live Ask's words. No model call. Energy Research Warehouse (ERW)."""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
LOADER = ["--import", "./scripts/alias-register.mjs"]
DASHES = (chr(0x2014), chr(0x2013))
NEW = [("site", "components", "grid", "AskExamples.tsx"), ("site", "lib", "gridask.ts"), ("site", "scripts", "build-grid-ask-examples.mjs"),
       ("site", "scripts", "test-grid-ask.mjs"), ("site", "data", "grid_ask_examples.json"), ("tests", "test_session1157.py")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheFiles(unittest.TestCase):
    def test_no_dash(self):
        for p in NEW:
            text = src(*p)
            for d in DASHES:
                self.assertNotIn(d, text, "/".join(p))

    def test_the_panel_follows_the_live_box(self):
        page = src("site", "app", "grid", "page.tsx")
        self.assertIn("<AskExamples grid={grid} />", page)
        self.assertLess(page.index("<AskView grid={grid}"), page.index("<AskExamples grid={grid} />"))

    def test_the_panel_is_named_and_folded(self):
        comp = src("site", "components", "grid", "AskExamples.tsx")
        self.assertIn("data-grid-panel={`grid_ask_${grid.slug}`}", comp)
        code = re.sub(r"//.*", "", comp)
        self.assertIn("<details", code)
        self.assertNotIn(" open", code.split("<details", 1)[1].split(">", 1)[0])
        self.assertNotIn("data-check", code)

    def test_every_example_names_its_source(self):
        data = json.loads(src("site", "data", "grid_ask_examples.json"))
        self.assertEqual(data["max_examples"], 5)
        for slug, g in data["grids"].items():
            self.assertLessEqual(len(g["examples"]), 5, slug)
            for e in g["examples"]:
                self.assertTrue(e["file"].startswith("warehouse/chat/eval/"), e["id"])
                self.assertTrue(os.path.isfile(os.path.join(ROOT, e["file"])), e["id"])
                self.assertEqual(e["verdict"], "right", e["id"])
                self.assertTrue(e["question_id"] and e["run"] and e["asked_at_utc"], e["id"])
                for s in e["sources"]:
                    self.assertTrue(s["tables"] and s["figures"], e["id"])
        # session 1187: chains 075 and 076's runs of 23 October are read, each with its grades file
        graded = {f["file"]: f for f in data["files"] if f.get("grades")}
        for name in ("eval_s1113_run.json", "eval_s1114_run.json", "eval_s1133_s320_run.json", "eval_s1133_s1114_run.json"):
            f = graded.get("warehouse/chat/eval/" + name)
            self.assertIsNotNone(f, name)
            self.assertTrue(os.path.isfile(os.path.join(ROOT, f["grades"])), name)
            self.assertGreater(f["kept"], 0, name)


class TheNodeTest(unittest.TestCase):
    @unittest.skipUnless(NODE and os.path.isdir(os.path.join(SITE, "node_modules")), "node or the site's packages are not on this machine")
    def test_the_node_test_passes(self):
        r = subprocess.run([NODE, *LOADER, "scripts/test-grid-ask.mjs"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1500:])
        self.assertRegex(r.stdout, r"(\d+) of \1 passed")

    @unittest.skipUnless(NODE, "node is not on this machine")
    def test_the_data_file_is_current(self):
        r = subprocess.run([NODE, "scripts/build-grid-ask-examples.mjs", "--check"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
