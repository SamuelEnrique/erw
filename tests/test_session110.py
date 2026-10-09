"""Session 110: the home page and menu by audience, a draft (/home/v2, in review).

Three ways in; each tool's status read from the release gate, the live ones first; one sentence saying what the ERW
is; the draft menu drawn inside the page and nowhere else; the live home page and the site's menu untouched.
"""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", js], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        if "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr or "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


class TheThreeWaysIn(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = node("const a = await import('./lib/audience.ts'); const r = await import('./lib/release.ts');"
                       "console.log(JSON.stringify({ sentence: a.ONE_SENTENCE, counts: a.counts(), live: Object.entries(r.RELEASE).filter(([, s]) => s === 'live').map(([p]) => p),"
                       " audiences: a.AUDIENCES.map((x) => ({ id: x.id, label: x.label, written: x.tools.map((t) => t.href), listed: a.listed(x).map((t) => [t.href, t.status, r.statusOf(t.href)]), questions: x.tools.map((t) => t.question) })) }));")

    def test_three_audiences_as_asked(self):
        self.assertEqual([a["label"] for a in self.out["audiences"]], ["Investors and lenders", "Operators and developers", "Students and teachers"])

    def test_a_tools_status_is_the_release_gates_and_the_live_ones_come_first(self):
        for a in self.out["audiences"]:
            statuses = [s for _, s, _ in a["listed"]]
            self.assertTrue(all(s == gate for _, s, gate in a["listed"]), a["id"])          # never a status of the page's own
            self.assertEqual(statuses, sorted(statuses, key=lambda s: s != "live"), a["id"])   # live first, then review
            self.assertEqual(sorted(h for h, _, _ in a["listed"]), sorted(a["written"]))      # no tool lost, none added
        # session 126: this asked that every way in open on something a visitor can use. Since the owner's lock of
        # 5 October 2026 three pages were open, and the students' list held none of them; the draft is in review itself.
        # Session 166 (the owner's instruction of 8 October 2026): no page is live, so no way in opens on an open page;
        # what still must hold: every listed status is the gate's, and the gate holds no live page.
        self.assertEqual(self.out["live"], [])
        self.assertTrue(all(s == "review" for a in self.out["audiences"] for _, s, _ in a["listed"]))

    def test_every_tool_has_a_page_and_a_question(self):
        for a in self.out["audiences"]:
            self.assertEqual(len(a["written"]), len(set(a["written"])), a["id"])
            for href, q in zip(a["written"], a["questions"]):
                path = href.split("?")[0].strip("/")
                self.assertTrue(os.path.exists(os.path.join(ROOT, "site", "app", *path.split("/"), "page.tsx")), href)
                self.assertGreater(len(q), 20, href)

    def test_every_live_tool_of_the_site_is_listed_under_some_audience(self):
        listed = {h for a in self.out["audiences"] for h in a["written"]}
        for path in self.out["live"]:
            if path in ("/", "/terms") or path.startswith("/data/methods/"):
                continue                                                                       # the home page itself, the terms and the methods notes are not tools
            self.assertIn(path, listed, path)

    def test_one_sentence_and_the_counts(self):
        s = self.out["sentence"]
        self.assertEqual(s.count("."), 1)                                                      # one sentence
        self.assertTrue(s.startswith("The Energy Research Warehouse is "))
        c = self.out["counts"]
        hrefs = {h for a in self.out["audiences"] for h in a["written"]}
        self.assertEqual(c["tools"], len(hrefs))
        self.assertEqual(c["live"] + c["review"], c["tools"])


class ThePage(unittest.TestCase):
    def test_in_review_with_the_draft_menu_inside_it(self):
        page = src("site", "app", "home", "v2", "page.tsx")
        self.assertRegex(src("site", "lib", "release.ts"), r'"/home/v2":\s*"review"')
        self.assertIn('data-draft-menu="1"', page)
        self.assertIn("Draft menu, shown on this page only", page)
        self.assertIn("data-one-sentence", page)
        self.assertIn('data-tool="review" className="text-muted"', page)                       # the tools in review are greyed
        self.assertIn("listed(a)", page)

    def test_the_live_home_page_and_the_menu_do_not_read_the_draft(self):
        for rel in (("site", "app", "page.tsx"), ("site", "components", "Nav.tsx"), ("site", "app", "layout.tsx"), ("site", "lib", "pages.ts")):
            self.assertNotIn("lib/audience", src(*rel), "/".join(rel))                           # none imports the draft
        r = subprocess.run(["git", "log", "--format=%s", "-1", "--", "site/app/page.tsx", "site/components/Nav.tsx", "site/lib/pages.ts", "site/app/layout.tsx"],
                           cwd=ROOT, capture_output=True, text=True)
        self.assertNotIn("Session 110", r.stdout)

    def test_no_em_dash(self):
        for rel in ("site/lib/audience.ts", "site/app/home/v2/page.tsx", "tests/test_session110.py"):
            self.assertNotIn(chr(0x2014), src(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()
