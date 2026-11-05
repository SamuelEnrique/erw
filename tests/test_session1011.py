"""Session 1011 (chain 070): llms.txt and the AI reader. package/llms.txt opens with the specification's section 0 (the
six calls in three languages, the backends, the types, held tables, the citation, the ten tables readers want first);
the chat's briefing is regenerated from it (site/lib/chat/spec.json); the site serves the same text at /llms.txt
(copied at build into content/llms.json), to the internal view only while the site is in review. No request."""
import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


LLMS = src("package", "llms.txt")
SPEC = src("docs", "methods", "packages.md")


class Briefing(unittest.TestCase):
    def test_section_0_is_the_specification_s(self):
        self.assertIn("## 0. Read it in Python, Stata or R (docs/methods/packages.md, session 1011)", LLMS)
        lead = ("A researcher who works in Python, Stata or R reads any public table of the Energy Research Warehouse (ERW) "
                "with the same six calls, gets the same rows in the same column types, and cites the same line.")
        self.assertIn(lead, SPEC)
        self.assertIn(lead, " ".join(LLMS.split()))
        for call in ("erw.tables()", "erw tables, clear", "erw_tables()", "erw.standard(t)", "erw_standard(t)"):
            self.assertIn(call, LLMS)
        self.assertIn("Redivis dataset `datapages.erw`, version <tag>", " ".join(LLMS.split()))
        self.assertNotIn(chr(0x2014), LLMS)

    def test_the_ten_tables_are_public(self):
        import csv
        with open(os.path.join(ROOT, "package", "src", "erw", "data", "tables.csv"), encoding="utf-8") as f:
            verdict = {r["table"]: r["verdict"] for r in csv.DictReader(f)}
        block = LLMS.split("The ten tables most readers want first", 1)[1].split("## 1.", 1)[0]
        names = [ln.split("`")[1] for ln in block.splitlines() if ln.startswith("- `")]
        self.assertEqual(len(names), 10)
        self.assertTrue(all(verdict.get(n) == "public" for n in names), names)

    def test_the_chat_s_briefing_is_current(self):
        out = subprocess.run([sys.executable, os.path.join(ROOT, "warehouse", "chat", "check_spec.py")], capture_output=True,
                             text=True, cwd=ROOT, timeout=300)
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)


class Route(unittest.TestCase):
    def test_the_site_serves_the_same_text_to_the_internal_view(self):
        build = src("site", "scripts", "build-content.mjs")
        self.assertIn('JSON.stringify({ text: read(path.join(repo, "package", "llms.txt")) })', build)
        route = src("site", "app", "llms.txt", "route.ts")
        self.assertIn('import llms from "@/content/llms.json";', route)
        self.assertIn("if (!(await cookieOpens(cookie, process.env.INTERNAL_COSTS_TOKEN))) {", route)
        self.assertIn("return new Response((llms as { text: string }).text,", route)
        self.assertIn("/content/llms.json", src("site", ".gitignore"))

    def test_the_copy_is_byte_for_byte(self):
        # build-content's own read: the file as it is, its line ends LF (as the repository stores it)
        out = os.path.join(ROOT, "site", "content", "llms.json")
        if not os.path.exists(out):
            self.skipTest("site/content/llms.json is written by a build (npm run content)")
        self.assertEqual(json.load(open(out, encoding="utf-8"))["text"], LLMS)


if __name__ == "__main__":
    unittest.main()
