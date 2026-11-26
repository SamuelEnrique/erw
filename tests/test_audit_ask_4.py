"""Session 10234 (chain 710, part D): the About page says what the chat's number check does, and when it was last asked.

docs/reviews/ask-model-audit-2026-11-26.md, finding 4. The About page said the tool "states no number a query of the
warehouse did not return: every figure of an answer is checked against what its tools read, in its unit", and called
23 October 2026 the evaluation's last asking. The check also counts the question's numbers and the model's own tool
arguments (warehouse/chat/ask.py unverified), judges a unit only for a figure written with a money word, percent or MW
(unit_mismatches), and never asks whose figure a number is; the evaluation was asked again through 14 November 2026
(docs/methods/ask.md, "The evaluations"). Words only, no figure moved. Fails on main, passes on the branch.

The page is drawn to HTML with the site's own code (site/scripts/tsx-register.mjs and font-stub-loader.mjs, no build,
no network) when node and the site's packages are here; skipped otherwise.
"""
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
PAGE = os.path.join(SITE, "app", "about", "page.tsx")
NEW = ("states no number it cannot trace", "a number its queries returned or the question or its own queries named",
       "it does not prove that the figure is the right row, grid or day", "Its evaluation of 23 October 2026 (later askings, to",
       "14 November 2026, are in its method)")
OLD = ("states no number a query of the warehouse did not return", "last asked on 23 October 2026")


def src():
    with open(PAGE, encoding="utf-8") as f:
        return " ".join(f.read().split())


class TheAboutPagesWords(unittest.TestCase):
    def test_the_new_words_are_in_the_source(self):
        s = src()
        for w in NEW:
            self.assertIn(" ".join(w.split()), s)
        for w in OLD:
            self.assertNotIn(w, s)

    def test_no_score_moved(self):
        s = src()
        for w in ("19 of 30 hard questions on the economics pages right", "(17 of 30 on 20 October)", "24 of 30 of a second set"):
            self.assertIn(w, s)

    def test_the_page_drawn_says_them(self):
        node = shutil.which("node")
        if not node or not os.path.isdir(os.path.join(SITE, "node_modules")):
            raise unittest.SkipTest("node or the site's packages are not here")
        tmp = tempfile.mkdtemp(prefix="audit_ask_4_")
        script = os.path.join(tmp, "draw.mjs")
        out = os.path.join(tmp, "about.txt")
        with open(script, "w", encoding="utf-8") as f:
            f.write(DRAW)
        r = subprocess.run([node, "--import", "./scripts/tsx-register.mjs", script, out], cwd=SITE, capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        with open(out, encoding="utf-8") as f:
            text = f.read()
        self.assertIn("states no number it cannot trace", text)
        self.assertIn("it does not prove that the figure is the right row, grid or day", text)
        self.assertIn("later askings, to 14 November 2026, are in its method", text)
        self.assertNotIn("last asked on 23 October 2026", text)


DRAW = r"""
import fs from "node:fs";
import path from "node:path";
import { createRequire, register } from "node:module";
import { pathToFileURL } from "node:url";
register(pathToFileURL(path.join(process.cwd(), "scripts", "font-stub-loader.mjs")).href, import.meta.url);
const [outFile] = process.argv.slice(2);
const req = createRequire(path.join(process.cwd(), "package.json"));
const { renderToStaticMarkup } = req("react-dom/server");
globalThis.fetch = async () => new Response("not held", { status: 404 });
const Page = (await import(pathToFileURL(path.join(process.cwd(), "app", "about", "page.tsx")).href)).default;
const html = renderToStaticMarkup(await Page());
const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&");
fs.writeFileSync(outFile, ent(html.replace(/<[^>]+>/g, " ")).replace(/\s+/g, " "));
process.exitCode = 0;
"""


if __name__ == "__main__":
    unittest.main()
