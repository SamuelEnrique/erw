"""wip/ready-digest-news-hold (session 11406, chain 770, part C): the first part of the other choice of the Digest
audit of 26 November, finding 6 (docs/reviews/digest-model-audit-2026-11-26.md), readied for Samuel's ruling, not
requested.

On main the news index's hold (news_index, "license needed" since 21 October) holds the Digest's story sections only:
the opening number, when it is a story's figure, and the numbers block's story rows are drawn (the Digest of 12
November: "USD 74 billion: SpaceX plans ..., as Bloomberg.com reported" and two rows, pv magazine USA's 580 MW and JPT's
USD 2.1 billion). On this branch site/lib/digest.ts holds them too, each line replaced in place by "license needed":
on that issue 3 lines held (before 0). The Roundup's story sections (What mattered, Weekend, The five stories: 8 items
and 6 links in W45) are not changed here. Run through the site's own library by Node, no build."""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
JS = """
import fs from "node:fs";
const D = await import(process.argv[1]);
const md = fs.readFileSync(process.argv[2], "utf-8");
const r = D.digestMarkdown(md, "2026-11-12", null, new Date("2026-11-28T12:00:00Z"));
const lines = r.md.split("\\n");
const held = lines.filter((l) => l.includes("this figure is a story's, from the news index")).length;
const leaks = ["Bloomberg.com reported", "580 MW (Sunrun", "USD 2.1 billion (Strathcona"].filter((w) => r.md.includes(w));
const kept = r.md.includes("Henry Hub natural gas") && r.md.includes("US48 demand peaked");
console.log(JSON.stringify({ held, leaks, kept }));
"""


class TheHoldReachesTheOpeningAndTheRows(unittest.TestCase):
    def test_the_issue_of_12_november(self):
        if not shutil.which("node") or not os.path.isdir(os.path.join(SITE, "node_modules")):
            self.skipTest("node or the site's packages are not here")
        url = "file:///" + os.path.join(SITE, "lib", "digest.ts").replace("\\", "/")
        out = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "--input-type=module", "-e", JS, url,
                              os.path.join(ROOT, "docs", "digest", "2026-11-12.md")], cwd=SITE, capture_output=True, text=True, timeout=300)
        self.assertEqual(out.returncode, 0, out.stderr[-2000:])
        r = json.loads(out.stdout.strip().splitlines()[-1])
        print(json.dumps(r))
        self.assertEqual(r["held"], 3)
        self.assertEqual(r["leaks"], [])
        self.assertTrue(r["kept"])                      # the market and physical rows stay

    def test_the_roundup_of_w45(self):
        if not shutil.which("node") or not os.path.isdir(os.path.join(SITE, "node_modules")):
            self.skipTest("node or the site's packages are not here")
        js = """
import fs from "node:fs";
const D = await import(process.argv[1]);
const md = fs.readFileSync(process.argv[2], "utf-8");
const r = D.holdRoundupStories(md, new Date("2026-11-28T12:00:00Z"));
const g = (s) => (s.match(/news\\.google\\.com/g) || []).length;
console.log(JSON.stringify({ google_before: g(md), google_after: g(r), held: (r.match(/come from the news index/g) || []).length,
  deals: r.includes("### Deals of the week"), numbers: r.includes("## The week in five numbers") }));
"""
        url = "file:///" + os.path.join(SITE, "lib", "digest.ts").replace("\\", "/")
        out = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "--input-type=module", "-e", js, url,
                              os.path.join(ROOT, "docs", "roundup", "2026-W45.md")], cwd=SITE, capture_output=True, text=True, timeout=300)
        self.assertEqual(out.returncode, 0, out.stderr[-2000:])
        r = json.loads(out.stdout.strip().splitlines()[-1])
        print(json.dumps(r))
        self.assertEqual(r["held"], 3)                  # What mattered, Weekend, The five stories of the week
        self.assertLess(r["google_after"], r["google_before"])
        self.assertTrue(r["deals"] and r["numbers"])
        self.assertIn("holdRoundupStories(holdRoundupGrids(md))", open(os.path.join(SITE, "lib", "markdown.ts"), encoding="utf-8").read())

    def test_the_code(self):
        with open(os.path.join(SITE, "lib", "digest.ts"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn('if (s.title === "The opening number") {', s)
        self.assertIn("out[i] = `- ${heldLine}`;", s)


if __name__ == "__main__":
    unittest.main()
