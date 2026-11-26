"""Audit of the interconnection queue, finding 3 (session 10213, docs/reviews/queues-model-audit-2026-11-26.md): the
page said "Recent years are mostly still open" and that 2000 to 2020 is "old enough ... for most outcomes to be known";
decision 6 and the method note said "still mostly open". In the default view (the United States, every technology)
28.6 to 49.3 percent of each year 2021 to 2024 is still open (most of the rest withdrawn); only 2025 is mostly open. Of
the 2000 to 2020 requests, 58.67 percent of ERCOT's standalone batteries and 60.00 percent of SPP's solar with storage
are still open. No figure moves.

1. From the page's file: in the default view no year 2021 to 2024 is mostly open and 2025 is; in two views most past
   requests are still open. Passes on main.
2. The fix on this branch, words only: the chart's note, decision 6 and the method note say it as the file has it.
   Fails on main."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def open_share(r):
    n = r["requests_operating"] + r["requests_withdrawn"] + r["requests_active"] + r["requests_suspended"]
    return (r["requests_active"] + r["requests_suspended"]) / n


class RecentYearsAreNotMostlyOpen(unittest.TestCase):
    def test_the_file(self):
        q = json.loads(src("site", "data", "queues.json"))
        us = q["views"]["us|all"]["years"]
        self.assertEqual([round(100 * open_share(us[str(y)]), 1) for y in range(2021, 2026)], [28.6, 44.1, 36.8, 49.3, 79.0])
        self.assertEqual(q["views"]["us|all"]["whole"]["past_open_share_pct"], 10.33)
        self.assertEqual(q["views"]["ercot|battery"]["whole"]["past_open_share_pct"], 58.67)
        self.assertEqual(q["views"]["spp|solar_battery"]["whole"]["past_open_share_pct"], 60.0)

    def test_the_words(self):
        page = src("site", "app", "queues", "page.tsx")
        self.assertNotIn("Recent years are mostly still open", page)
        self.assertNotIn("old enough (five years or more) for most outcomes to be known.", page)
        self.assertIn("five years old or more, so in most views most of their outcomes are known (the headline&apos;s &quot;still active or "
                      "suspended&quot; says how many are not). Recent years still hold many requests whose outcome is not known (in most views "
                      "fewer than half of each year 2021 to 2024, and most of 2025), which is why they are not in the shares above.", page)
        dec, note = src("site", "lib", "decisions.ts"), src("docs", "methods", "interconnection_queue_summary.md")
        for t in (dec, note):
            self.assertNotIn("still mostly open", t)
            self.assertIn("so recent years, many of whose requests are still open, do not read as a low completion rate.", t)
        self.assertNotIn("Recent years are mostly still", note)
        self.assertIn("only 2025 is mostly open (79.0 percent)", note)
        for t in (page, dec, note):
            self.assertNotIn(chr(0x2014), t)


if __name__ == "__main__":
    unittest.main()
