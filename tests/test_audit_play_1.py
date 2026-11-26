"""Audit of the games under /play, finding 1 (session 10227, docs/reviews/play-model-audit-2026-11-26.md): the battery
game's "What is stored" said a play's research record had "nothing that joins it to a leaderboard row", and that a
posted score stored the level, nickname, score, perfect score and time, "nothing else".

The two routes write the same level, the same score (four places), the same preset and a database time to both tables
(site/app/api/play/finish/route.ts into game_plays, site/app/api/play/score/route.ts into game_scores; migration 013
stamps ts with now() on both), so a posted play's two rows can be matched; the public row also stores the preset and the
difficulty. The page now says so, and names the usage counts and the hourly limit's daily code. Words only: no route,
table or figure changes. Fails on main, passes on the branch.

No table, no request, no model call; the environment is read, never set."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return re.sub(r"\s+", " ", s)


class WhatIsStored(unittest.TestCase):
    def test_the_routes_write_what_could_join_the_rows(self):
        finish, score = read("site/app/api/play/finish/route.ts"), read("site/app/api/play/score/route.ts")
        self.assertIn('insertRow("game_plays"', finish)
        self.assertIn('insertRow("game_scores"', score)
        for field in ("level_date: s.level.date", "score: s.score", "preset: s.preset"):
            self.assertIn(field, flat(finish), field)
            self.assertIn(field, flat(score), field)
        mig = read("warehouse/supabase/migrations/013_game.sql")
        self.assertEqual(mig.count("ts timestamptz not null default now()"), 2)

    def test_the_page_says_so(self):
        page = flat(read("site/app/play/battery/page.tsx"))
        self.assertNotIn("nothing that joins it to a leaderboard row", page)
        self.assertIn("the mode and battery settings it was played under", page)
        self.assertIn("so they could be matched to each other; no column joins them", page)
        self.assertIn("the page view and the fact that a setting was changed (never its value) are counted", page)
        self.assertIn("never the address itself", page)

    def test_the_page_makes_no_promise_the_usage_counter_reads(self):
        # site/lib/usage.ts PROMISE: a page saying nothing is sent stops the "input changed" counts; this page has them
        page = read("site/app/play/battery/page.tsx")
        self.assertIsNone(re.search(r"sent or stored|never sent|nothing is uploaded", page, re.I))

    def test_the_note_says_so(self):
        note = read("docs/methods/battery_game.md")
        self.assertIn("What could join the two (session 10227", note)

    def test_no_em_dash(self):
        for p in ("site/app/play/battery/page.tsx", "docs/methods/battery_game.md", "tests/test_audit_play_1.py"):
            self.assertNotIn(chr(0x2014), read(p))


if __name__ == "__main__":
    unittest.main()
