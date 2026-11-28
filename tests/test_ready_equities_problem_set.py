"""Ready branch for the equities problem set (session 11408, chain 770 part C; weekend page 2026-11-28, part 3.5, "the
equities problem set: list it, or keep it waiting": the other choice, list it). Not the default: it waits for Samuel's
ruling. The question beside it (may it call Expand Energy "a producer of mostly natural gas") is his, and unchanged here.

site/lib/problems.ts: the module moves from WAITING_MODULES to SETS and COUNTRY, its guide with the others; its three
choices join PROBLEM_DECISIONS (site/app/learn/problems/Decisions.tsx) and the note's table. Listed sets 10 to 11 on
the index; waiting sets 2 to 1. The next dated edition (scripts/build-problem-edition.mjs) holds it.

1. The lists in the code.
2. scripts/test-problem-sets-render.mjs (every set's decisions block, the note's keys equal), run by Node."""
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
REACT = os.path.isdir(os.path.join(SITE, "node_modules", "react"))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheProducerSetIsListed(unittest.TestCase):
    def test_the_lists(self):
        text = src("site", "lib", "problems.ts")
        self.assertIn("const WAITING_MODULES = [REPORT];", text)
        self.assertIn("...[TRADE, STORM, GROUND, WHERE, AUTH, PRODUCER].map((m) => m.META),", text)
        self.assertRegex(text, r"Object\.fromEntries\(\[TRADE, STORM, GROUND, WHERE, AUTH, PRODUCER\]\.map")
        self.assertIn("...PRODUCER_DECISIONS,", src("site", "app", "learn", "problems", "Decisions.tsx"))
        note = src("docs", "methods", "problem_sets.md")
        for k in ("producer-company", "producer-days", "producer-filed-twice"):
            self.assertRegex(note, r"(?m)^\| `" + re.escape(k) + "` \\|")
        self.assertIn("listed since session 11408", note)

    @unittest.skipUnless(NODE and REACT, "node or the site's packages are not installed")
    def test_the_decisions_render(self):
        r = subprocess.run([NODE, "--import", "./scripts/problem-sets-register.mjs", "scripts/test-problem-sets-render.mjs"],
                           cwd=SITE, capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])
        self.assertIn("ok: 11 sets", r.stdout)


if __name__ == "__main__":
    unittest.main()
