"""Session 332 (the chain of 20 October 2026, night): /policy and /events (the index and the nine event pages) finished
to the five tools' standard, lighter. Every action's significance is a checked number and /policy is in check-values'
list; the policy and event tables are offered to download (session 328's shared line); the notes say what the pages
draw today. Energy Research Warehouse (ERW)."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DASH = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class ThePolicyNumbers(unittest.TestCase):
    def test_the_score_is_checked_and_the_page_is_in_the_list(self):
        t = src("site", "app", "policy", "PolicyTable.tsx")
        self.assertIn('<Num check={`event|policy_actions|${r.event_id}|significance`} raw={Number(r.significance)}>{r.significance}</Num>', t)
        cv = src("site", "scripts", "check-values.mjs")
        self.assertIn('  "/policy",', cv[cv.index("const PAGES"):cv.index("const PAGES") + 2000])
        floor = json.loads(src("site", "scripts", "check-values-floor.json"))["floor"]
        self.assertEqual((floor["/policy"], floor["/deals?tab=companies"]), (10, 10))
        self.assertIn('"significance"', src("site", "lib", "data.ts")[src("site", "lib", "data.ts").index("export async function policyActions"):][:400])


class TheDownloads(unittest.TestCase):
    def test_both_policy_views_and_every_event_page_offer_their_tables(self):
        self.assertEqual(src("site", "app", "policy", "page.tsx").count('<TableDownloads tables={["policy_actions", "policy_reads"]} />'), 2)
        es = src("site", "components", "EventStudy.tsx")
        self.assertIn('<TableDownloads tables={[T, "event_study_estimates"]} />', es)
        self.assertIn('<TableDownloads tables={[T, "event_study_estimates"]} />', src("site", "app", "events", "page.tsx"))
        pages = sorted(d for d in os.listdir(os.path.join(ROOT, "site", "app", "events")) if os.path.isfile(os.path.join(ROOT, "site", "app", "events", d, "page.tsx")))
        self.assertEqual(len(pages), 9)
        for d in pages:
            self.assertIn("<EventStudy ", src("site", "app", "events", d, "page.tsx"), d)   # each page ends with the block that carries the line


class TheNotes(unittest.TestCase):
    def test_the_notes_say_what_the_pages_draw_today(self):
        self.assertIn("## 10. The page as it stands (session 332, 20 October 2026)", src("docs", "methods", "policy_monitor.md"))
        self.assertIn("## The pages as they stand (session 332, 20 October 2026)", src("docs", "methods", "events.md"))


class NoEmDash(unittest.TestCase):
    def test_none_in_what_the_session_wrote(self):
        for parts in (("site", "app", "policy", "PolicyTable.tsx"), ("site", "app", "policy", "page.tsx"), ("site", "components", "EventStudy.tsx"),
                      ("site", "app", "events", "page.tsx"), ("site", "scripts", "check-values.mjs"), ("docs", "methods", "policy_monitor.md"),
                      ("docs", "methods", "events.md"), ("tests", "test_session332.py")):
            self.assertNotIn(DASH, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
