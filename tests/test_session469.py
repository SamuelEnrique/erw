"""Session 469 (the chain of 21 to 22 October 2026, night, run on portable-laptop): /policy's impact reads against the
tables they cite. Each read shows its figures and their source (the action's own text) or "no figure"; the review counts
every read with the page's own function; the method note says what the score and a read are today; the Tag filter has
one more choice, large loads, interconnection or tariffs, not chosen by default. Energy Research Warehouse (ERW)."""
import csv
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
REVIEW = os.path.join(ROOT, "docs", "reviews", "policy-impact-reads-2026-10-21.md")
ROWS = os.path.join(ROOT, "docs", "reviews", "policy-impact-reads-2026-10-21.csv")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class ThePureFunctions(unittest.TestCase):
    @unittest.skipUnless(NODE and os.path.isdir(os.path.join(SITE, "node_modules")), "node or the site's packages are not on this machine")
    def test_the_node_test_passes(self):
        r = subprocess.run([NODE, *LOADER, "scripts/test-policy-reads.mjs"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1500:])
        self.assertRegex(r.stdout, r"(\d+) of \1 passed")


class TheReview(unittest.TestCase):
    def setUp(self):
        self.doc = src("docs", "reviews", "policy-impact-reads-2026-10-21.md")
        with open(ROWS, encoding="utf-8") as f:
            self.rows = list(csv.DictReader(f))

    def test_no_dash(self):
        for p in (REVIEW, ROWS, os.path.join(ROOT, "docs", "methods", "policy_monitor.md"), os.path.join(SITE, "lib", "policyreads.ts")):
            with open(p, encoding="utf-8") as f:
                t = f.read()
            for d in DASHES:
                self.assertNotIn(d, t, p)

    def test_every_row_is_one_of_three_and_its_figures_agree(self):
        self.assertEqual(len({r["read_event_id"] for r in self.rows}), len(self.rows))
        for r in self.rows:
            self.assertIn(r["cites"], ("text", "none", "table"), r["read_event_id"])
            self.assertEqual(r["cites"] == "none", r["figures"] == "" and r["tables_named"] == "", r["read_event_id"])
            self.assertEqual(r["cites"] == "table", r["tables_named"] != "", r["read_event_id"])

    def test_the_counts_stated_are_the_rows(self):
        n = {k: sum(r["cites"] == k for r in self.rows) for k in ("text", "none", "table")}
        figures = sum(len([x for x in r["figures"].split(";") if x.strip()]) for r in self.rows)
        self.assertIn(f"**{len(self.rows)} reads; {n['table']} cite an ERW table; {n['text']} state figures, every one from the action's own text; {n['none']} state no figure.**", self.doc)
        self.assertIn(f"state {figures} figures between them", self.doc)
        self.assertIn(f"| **All** | **{len(self.rows)}** | **{n['text']}** | **{n['none']}** | **{n['table']}** |", self.doc)
        for agency in sorted({r["agency"] for r in self.rows}):
            mine = [r for r in self.rows if r["agency"] == agency]
            row = f"| {agency} | {len(mine)} | {sum(r['cites'] == 'text' for r in mine)} | {sum(r['cites'] == 'none' for r in mine)} | {sum(r['cites'] == 'table' for r in mine)} |"
            self.assertIn(row, self.doc, agency)


class ThePage(unittest.TestCase):
    def test_each_read_says_what_it_cites(self):
        page = src("site", "app", "policy", "page.tsx")
        self.assertIn('import { citeOf } from "@/lib/policyreads";', page)
        self.assertIn("cite: read ? citeOf(read, TABLES) : null", page)
        t = src("site", "app", "policy", "PolicyTable.tsx")
        self.assertIn("data-read-cites={r.cite.kind}", t)
        self.assertIn("CITE_WORDS.none", t)
        self.assertIn("Source: <a href={r.source_url}>the action</a>", t)

    def test_the_filter_is_one_more_choice_and_not_chosen_by_default(self):
        w = src("site", "lib", "policyweek.ts")
        self.assertIn('export const LOAD_GROUP = "loads_interconnection_tariffs";', w)
        self.assertIn('export const LOAD_GROUP_TAGS = ["large_load", "interconnection", "transmission_cost"] as const;', w)
        t = src("site", "app", "policy", "PolicyTable.tsx")
        self.assertIn("[LOAD_GROUP, LOAD_GROUP_LABEL]", t)
        self.assertIn('const [tag, setTagOnly] = useState(tagAtOpen);', t)     # the address chooses; nothing else does
        self.assertIn('const [minSig, setMinSig] = useState(tagAtOpen ? "" : "5");', t)
        self.assertIn('setTag(""); setMinSig("5");', t)                        # Reset: no tag, as before

    def test_the_browser_check_reads_both(self):
        t = src("site", "scripts", "check-policy-reads.mjs")
        self.assertIn("tagHref(LOAD_GROUP)", t)
        self.assertIn("data-read-cites-of", t)
        self.assertIn('back.tag === "" && back.sig === "5" && back.shown === plain.shown', t)

    def test_release_is_not_touched(self):
        r = subprocess.run(["git", "diff", "--quiet", "origin/main", "--", "site/lib/release.ts"], cwd=ROOT, capture_output=True)
        if r.returncode not in (0, 1):
            self.skipTest("git or origin/main is not available")
        self.assertEqual(r.returncode, 0, "site/lib/release.ts differs from origin/main")


class TheMethodNote(unittest.TestCase):
    def test_section_eleven(self):
        t = src("docs", "methods", "policy_monitor.md")
        s = t[t.index("## 11. What a read cites"):]
        self.assertIn("`event|policy_actions|<id>|significance`", s)
        self.assertIn("`/policy?tag=loads_interconnection_tariffs`", s)
        self.assertIn("`site/lib/policyreads.ts`", s)
        self.assertIn("docs/reviews/policy-impact-reads-2026-10-21.md", s)
        self.assertTrue(re.search(r"1,926 actions, every one scored: 377 at 5 or\s+more", s))


if __name__ == "__main__":
    unittest.main()
