"""Audit of the datacenter power tracker, finding 2 (session 10211, docs/reviews/tracker-model-audit-2026-11-26.md): the
page reads "the news since 2025-01-01", but the stories scored are not even over that span. By month of publication
(news_stories and warehouse/datacenters/checked.csv, 26 November 2026): May to September 2025, 1,885 stories, 13 scored,
none sent to the extractor; October to December 2025, 790 of 1,935 scored; June to August 2026, 863 of 1,819; since
September 2026 the daily feed, up to 11,914 stories a month against at most 656 before. 136 of the 193 facilities with a
first story were first reported in September to November 2026, so the chart of planned MW by the quarter first reported
shows what was read as much as what was announced.

1. Through the page's library (site/lib/dcrollups.ts, run by Node): the chart's quarter is the first story's, and a
   facility with no first story is not on it. Passes on main.
2. The fix on this branch, words only: the scope words say the stories read are uneven over the span; the chart's note
   says its quarters show what was read. Fails on main."""
import csv
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "dcrollups.ts").replace("\\", "/")
JS = """
const R = await import(process.argv[1]);
const row = (id, first, mw) => ({ entity_id: id, capacity_mw: mw, status: "planned", operator: "", extra: { state: "TX", ...(first ? { first_story_at: first } : {}) } });
const q = R.plannedByQuarter([row("a", "2025-03-04T08:00:00Z", 100), row("b", "2026-10-29T15:05:24Z", 200), row("c", "", 300)]);
console.log(JSON.stringify(q.map((x) => [x.quarter, x.parts.reduce((s, p) => s + p.mw, 0)])));
"""


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


class TheNewsWindowIsUneven(unittest.TestCase):
    def test_the_chart_dates_a_facility_by_its_first_story(self):
        out = subprocess.run(["node", "--input-type=module", "-e", JS, LIB], capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(json.loads(out.stdout.strip().splitlines()[-1]), [["2025-Q1", 100], ["2026-Q4", 200]])

    def test_the_record_of_the_stories_sent_is_in_git(self):
        # warehouse/datacenters/checked.csv (in git): every story the extractor was sent, with when it was sent
        with open(os.path.join(ROOT, "warehouse", "datacenters", "checked.csv"), encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertGreater(len(rows), 1000)

    def test_the_page_says_the_window_is_uneven(self):
        page = flat(src("site", "app", "datacenters", "page.tsx"))
        self.assertIn("The stories read are not even over that span (as of 26 November 2026): none published from May to September 2025 was scored, "
                      "two in five of October to December 2025 and about half of June to August 2026, and since September 2026 the daily feed holds up "
                      "to eighteen times the stories of an earlier month, so most facilities with a date were first reported in the last three months.", page)
        charts = flat(src("site", "app", "datacenters", "DcCharts.tsx"))
        self.assertIn("A quarter shows which stories were read as much as when a facility was announced: the news read is not even over time "
                      "(the scope, above the list).", charts)


if __name__ == "__main__":
    unittest.main()
