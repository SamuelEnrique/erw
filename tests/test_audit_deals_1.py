"""Audit of the energy deal tracker, finding 1 (session 10215, docs/reviews/deals-model-audit-2026-11-26.md): the window.
The first tab says "Energy deals reported in the news since 2025-10-01", but the table's rows run from January 2025 (42
of the 583 rows of 12 November 2026 are dated January to April 2025). The tracker's chart note says the stories of "June
to September 2025" were not scored; of the 1,885 stories of May to September 2025 held, 13 were scored (all of May), so
May is empty for the same reason. And it says "The ERW has scored the news daily since 23 September 2026", but no story
was scored after 12 November 2026 (as of 26 November 2026; warehouse/deals/checked.csv's last check is that evening), so
the month's cells for November count four dated days and the page says nothing of how far they reach.

1. Through the page's library (site/lib/dealsview.ts, run by Node): the month's cells count the deals dated in the month,
   whatever day the newest is, and the month before only when the month holds none. Passes on main.
2. The record of the stories sent to the extractor is in git. Passes on main.
3. The fix on this branch, words only: the lead says "since January 2025" and that the stories scored are uneven; the
   month's note names the newest deal held and says no story was scored after 12 November 2026; the chart's note names
   May to September 2025 and the stop; the method notes say the same. Fails on main."""
import csv
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "dealsview.ts").replace("\\", "/")
JS = """
const V = await import(%s);
const row = (id, date) => V.rowOf({ event_id: id, event_date: date, status: null, mw: 100, price: null, source: "s", source_url: "u", extra: { ai_power: "true" } });
const a = V.monthBlock([row("a", "2026-11-04T08:00:00Z"), row("b", "2026-11-12T21:25:21Z"), row("c", "2026-10-30T10:00:00Z")], "2026-11");
const b = V.monthBlock([row("c", "2026-10-30T10:00:00Z")], "2026-11");
console.log(JSON.stringify([a.month, a.deals, a.mw, a.empty, b.month, b.deals, b.empty]));
""" % json.dumps(LIB)


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


class TheWindowAndItsAsOfDate(unittest.TestCase):
    def test_the_month_counts_what_is_dated_in_it_up_to_the_newest(self):
        out = subprocess.run(["node", "--input-type=module"], input=JS, capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(json.loads(out.stdout.strip().splitlines()[-1]), ["2026-11", 2, 200, False, "2026-10", 1, True])

    def test_the_record_of_the_stories_sent_is_in_git(self):
        with open(os.path.join(ROOT, "warehouse", "deals", "checked.csv"), encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertGreater(len(rows), 1000)
        self.assertTrue(all(r["checked_at"][:4] == "2026" for r in rows))

    def test_the_first_tab_says_the_window_and_how_far_it_reaches(self):
        page = flat(src("site", "app", "deals", "page.tsx"))
        self.assertNotIn("since 2025-10-01", page)
        self.assertIn("Energy deals reported in the news since January 2025, from the stories the ERW scores, each with its sources. The stories "
                      "scored are not even over that span: the tracker&apos;s chart of deals by month says which months are thin or empty, and why.", page)
        self.assertIn("The newest deal held is dated {newest}: the cells count the deals dated in the month up to that day, and not every story "
                      "of a month was scored (none after 12 November 2026, as of 26 November 2026).", page)

    def test_the_chart_names_the_months_not_scored_and_the_stop(self):
        v2 = flat(src("site", "app", "deals", "v2", "view.tsx"))
        self.assertNotIn("June to September 2025 are held but not scored", v2)
        self.assertIn("of the stories of May to September 2025 held, almost none was scored (13 of 1,885)", v2)
        self.assertIn("scored none after 12 November 2026 (as of 26 November 2026); the newest deal held is dated {all[0].date}.", v2)

    def test_the_method_notes_say_the_same(self):
        self.assertNotIn("since 1 October 2025", src("docs", "methods", "energy_deals.md"))
        note = flat(src("docs", "methods", "deal_tracker.md"))
        self.assertIn("of the 1,885 stories of those months held, 13 were scored (all of May)", note)
        self.assertIn("no story was scored after 12 November 2026", note)


if __name__ == "__main__":
    unittest.main()
