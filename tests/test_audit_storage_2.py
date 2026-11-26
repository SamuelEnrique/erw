"""Session 10212 (storage audit, finding 2): "latest complete local day" on /storage is the newest settled day.

The daily cycle's header read "Balancing authority, latest complete local day". Since session 7050 the builder writes an
EIA-930 day only when it ended at least 48 hours before the area's newest hour (warehouse/derived/storage_daily_cycle.py,
SETTLE_HOURS), because EIA posts its newest hours early and fills them in later; CAISO's rows have no such wait.
Measured on the main copy's tables as of 2026-11-05 12:00 UTC (docs/reviews/storage-model-audit-2026-11-26/measures.json,
"newest_days"): every EIA-930 row showed 1 November while 2 and 3 November were complete, and CAISO's row showed
4 November. The two hourly charts draw the hours the cycle waits for, as EIA first posted them.

Words only (site/app/storage/page.tsx, SETTLE_WORDS and NEWEST_WORDS, and the header): no figure moves.
"""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class SettledDay(unittest.TestCase):
    def test_the_builder_waits_for_eia_and_not_for_caiso(self):
        b = read("warehouse", "derived", "storage_daily_cycle.py")
        self.assertIn("SETTLE_HOURS = 48", b)
        self.assertIn("if not settled(day, tz, newest):", b)
        caiso = b[b.index("def caiso_rows("):b.index("def main(")]
        self.assertNotIn("settled(", caiso)

    def test_the_page_says_so(self):
        p = read("site", "app", "storage", "page.tsx")
        self.assertNotIn("latest complete local day", p)
        self.assertIn('data-day-head="1">Balancing authority, newest local day shown</th>', p)
        self.assertIn('const SETTLE_WORDS = "The EIA-930 rows show a day only once it ended at least 48 hours before EIA\'s newest hour', p)
        self.assertIn('data-settle-note="1">{SETTLE_WORDS}</p>', p)
        self.assertIn("for every hour of its day` : \"\"}.{NEWEST_WORDS} The CAISO line", p)
        self.assertRegex(p, re.compile(r'const NEWEST_WORDS = " These are EIA\'s newest hours, which it may still revise'))
        self.assertNotIn(chr(0x2014), p)


if __name__ == "__main__":
    unittest.main()
