"""Ruling alternative 4 of /events (session 7712, 17 November 2026, branch wip/alt-events-4; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-events-2026-11-17.md, line 4): on the Uri page,
one sentence on ERCOT's offer cap of February 2021? The cap itself is in a document the warehouse does not hold, so this
branch adds the figure the rows hold, and no cap: HB_HUBAVG stood at or above USD 8,900 per MWh in 345 fifteen-minute
intervals (86 hours) of 15 to 19 February 2021 (UTC days 15, 80, 94, 96 and 60), from ercot_all_hub_prices_history, which
the site's database does not hold, so the count stands in lib/eventstudy.ts URI_NEAR_CAP and this test counts it again in
the table where it is on the machine (warehouse/output, or the folder ERW_TABLES_DIR names). The page draws the sentence
with a hover (site/app/events/uri-2021/page.tsx). No figure that stands moves.

    python -m unittest tests.test_alt_events_4 -v
"""

import collections
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
CSV = os.path.join(TABLES, "ercot_all_hub_prices_history.csv")


def constant():
    with open(os.path.join(ROOT, "site", "lib", "eventstudy.ts"), encoding="utf-8") as f:
        s = f.read()
    m = re.search(r"export const URI_NEAR_CAP = \{ threshold: (\d+), intervals: (\d+), hours: ([\d.]+), byDay: \{ (.*?) \}", s)
    by = {d: int(n) for d, n in re.findall(r'"(\d{4}-\d{2}-\d{2})": (\d+)', m.group(4))}
    return int(m.group(1)), int(m.group(2)), float(m.group(3)), by


class TheSentence(unittest.TestCase):
    def test_the_constant_adds_up(self):
        thr, n, hours, by = constant()
        self.assertEqual((thr, n, hours, sum(by.values())), (8900, 345, 86.25, 345))

    def test_the_page_draws_it_and_states_no_cap(self):
        with open(os.path.join(ROOT, "site", "app", "events", "uri-2021", "page.tsx"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn("data-uri-near-cap={URI_NEAR_CAP.intervals}", s)
        self.assertNotIn("9,000", s)


@unittest.skipUnless(os.path.exists(CSV), "ercot_all_hub_prices_history is not on this machine")
class OnTheTable(unittest.TestCase):
    def test_the_count_is_the_tables(self):
        thr, n, _, by = constant()
        days = collections.Counter()
        with open(CSV, encoding="utf-8") as f:
            for line in f:
                if not line.startswith("ercot:HB_HUBAVG,spp_rtm,2021-02-"):
                    continue
                p = line.split(",")
                if float(p[3]) >= thr:
                    days[p[2][:10]] += 1
        self.assertEqual((sum(days.values()), dict(days)), (n, by))


if __name__ == "__main__":
    unittest.main()
