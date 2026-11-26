"""Audit of the interconnection queue, finding 2 (session 10213, docs/reviews/queues-model-audit-2026-11-26.md): the
builder marks the United States' solar-with-storage shares as counting ERCOT's 66 past requests, none of them withdrawn
by the file's labels (queue_summary.not_comparable, session 7052), and the method note says the site's copy carries the
mark. The page drew only ERCOT's mark (noneWithdrawn), so the default view's technology table printed the United States'
62.62 percent withdrawn unmarked. Without ERCOT's 66 it would be 66.08 percent; no figure moves here.

1. The page's file carries the mark for the United States' pair, and the figure is 62.62. Passes on main.
2. The fix on this branch, words only: the share withdrawn draws the file's mark as its hover wherever a view has one
   and is not already marked by noneWithdrawn. Fails on main."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheUnitedStatesMarkIsDrawn(unittest.TestCase):
    def test_the_file_carries_the_mark_and_the_figure(self):
        q = json.loads(src("site", "data", "queues.json"))
        self.assertIn("us|solar_battery", q["not_comparable"])
        self.assertIn("ERCOT's 66 past requests", q["not_comparable"]["us|solar_battery"])
        self.assertEqual(q["views"]["us|solar_battery"]["whole"]["past_withdrawn_share_pct"], 62.62)
        self.assertEqual(q["views"]["us|solar_battery"]["whole"]["past_requests"], 1260)

    def test_the_page_draws_the_files_mark(self):
        page = src("site", "app", "queues", "page.tsx")
        self.assertIn("const mark = file.not_comparable?.[`${grid.slug}|${tech.slug}`];", page)
        self.assertIn("data-not-comparable={`${grid.slug}|${tech.slug}`}", page)
        self.assertIn('The method note, "ERCOT\'s solar with storage is not comparable", says why.', page)
        self.assertIn("not_comparable?: Record<string, string>;", src("site", "lib", "queues.ts"))
        note = src("docs", "methods", "interconnection_queue_summary.md")
        self.assertIn("would be 66.08 percent (1,194 past requests), not 62.62 (1,260)", note)
        for t in (page, note):
            self.assertNotIn(chr(0x2014), t)


if __name__ == "__main__":
    unittest.main()
