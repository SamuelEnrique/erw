"""wip/ready-home-digest (session 11406, chain 770, part C): the other choice of the home page audit of 26 November,
finding 1 (docs/reviews/home-model-audit-2026-11-26.md), readied for Samuel's ruling, not requested.

On main the home page's Digest block reads only "## Top of the industry" (site/lib/markdown.ts, topItems); the newest
issues ("ERW Daily Digest", from 12 November 2026) hold their stories under "## What moved", so the block draws "no
data". On this branch topItems reads "What moved" when the old section is not there: 5 stories drawn instead of "no
data" (before 0, after 5, on docs/digest/latest.md as it stands). The audit's test (tests/test_audit_home_15.py on
wip/audit-home-15) is carried: the library itself is run by Node on the newest issue."""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
JS = """
import fs from "node:fs";
const M = await import(process.argv[1]);
const md = fs.readFileSync(process.argv[2], "utf-8");
const old = "# Energy Digest, 2026-11-06\\n\\n## Top of the industry\\n\\n1. A\\n2. B\\n\\n## What moved\\n\\n1. C\\n";
console.log(JSON.stringify({ n: (M.topItems(md, 5) || []).length, first: (M.topItems(md, 5) || [""])[0].slice(0, 60),
  old: M.topItems(old, 5), none: M.topItems("# x\\n\\n## Other\\n\\n1. A\\n", 5) }));
"""


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheNewFormsStories(unittest.TestCase):
    def test_the_library_reads_what_moved(self):
        md = src("site", "lib", "markdown.ts")
        self.assertIn('const start = old >= 0 ? old : md.indexOf("\\n## What moved");', md)
        self.assertIn("or 'What moved' section", src("site", "app", "page.tsx"))

    def test_the_newest_issue_draws_five(self):
        if not shutil.which("node") or not os.path.isdir(os.path.join(SITE, "node_modules")):
            self.skipTest("node or the site's packages are not here")
        url = "file:///" + os.path.join(SITE, "lib", "markdown.ts").replace("\\", "/")
        out = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "--input-type=module", "-e", JS, url,
                              os.path.join(ROOT, "docs", "digest", "latest.md")], cwd=SITE, capture_output=True, text=True, timeout=300)
        self.assertEqual(out.returncode, 0, out.stderr[-2000:])
        r = json.loads(out.stdout.strip().splitlines()[-1])
        print(json.dumps(r))
        latest = src("docs", "digest", "latest.md")
        if "\n## Top of the industry" not in latest:
            sect = latest[latest.index("\n## What moved"):]
            sect = sect[:sect.index("\n## ", 3)]
            self.assertEqual(r["n"], min(5, len(re.findall(r"^\d+\.\s", sect, re.M))))
            self.assertEqual(r["n"], 5)
        self.assertEqual(r["old"], ["A", "B"])          # the old form is read as before
        self.assertIsNone(r["none"])


if __name__ == "__main__":
    unittest.main()
