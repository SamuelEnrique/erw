"""Session 106: the datacenter tracker, version 2: ERCOT's large-load status as far as it is stated in words.

The connector's reading of a report on text made for the test (no document of ERCOT's is in the repository); the
site's copy against the table; the page's sentence and counts; the page in review. No network.
"""
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import unittest

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import ercot_large_load_status as c  # noqa: E402
import iso_prices as ip  # noqa: E402
import large_load_snapshot as snap  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")
FIRST = "Large Load Interconnection Status Update Large Load Integration Team March 13, 2026"
BODY = ("Loads Approved to Energize - Observations 1 Of the 9042 MW that have received Approval to Energize, ERCOT has observed a non-simultaneous monthly peak consumption of "
        "3883 MW in March 2025 which is a slight decrease since February 2025. This is calculated as the sum of the maximum value for each individual load per month")
BODY2 = "ERCOT has observed a simultaneous monthly peak consumption of 3,801 MW in March 2025 which is a slight decrease since February 2025."
NEW = "ERCOT has recently received 137 new LLI submissions. Preliminary review indicates these total approximately 140,000 MW of new Large Load by 2036."


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", js], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        if "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr or "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


class TheReading(unittest.TestCase):
    def test_the_figures_a_report_states_in_words(self):
        got = c.figures([FIRST, "a chart", BODY, BODY2, NEW])
        self.assertEqual(got, [("approved_to_energize_mw", "MW", 9042.0, ""), ("observed_nonsimultaneous_peak_mw", "MW", 3883.0, "March 2025"),
                               ("observed_simultaneous_peak_mw", "MW", 3801.0, "March 2025"), ("new_submissions_count", "count", 137.0, ""),
                               ("new_submissions_mw", "MW", 140000.0, "")])
        # the simultaneous sentence is not taken for the non-simultaneous one, nor the other way round
        self.assertEqual([v for v, *_ in c.figures([BODY2])], ["observed_simultaneous_peak_mw"])
        self.assertEqual([v for v, *_ in c.figures([BODY])], ["approved_to_energize_mw", "observed_nonsimultaneous_peak_mw"])

    def test_a_report_without_a_sentence_gives_no_row_for_it_and_nothing_is_filled(self):
        self.assertEqual(c.figures([FIRST, "Large Load Queue - Past 12 Months", "Questions?"]), [])
        rows, notes = c.rows_of([("https://www.ercot.com/a.pdf", "a.pdf", [FIRST, "only charts"])], "2026-10-04T00:00:00Z")
        self.assertEqual(rows, [])
        self.assertIn("states none of the figures in words", notes[0])

    def test_a_figure_stated_twice_with_two_values_fails(self):
        with self.assertRaises(ValueError):
            c.figures([BODY, BODY.replace("9042", "9100")])
        self.assertEqual(len(c.figures([BODY, BODY])), 2)        # the same sentence twice is the same figure

    def test_only_a_status_update_is_read(self):
        self.assertTrue(c.is_status_update([FIRST]))
        self.assertFalse(c.is_status_update(["ERCOT Large Load Batch Studies LLWG January 22, 2026", BODY]))
        self.assertFalse(c.is_status_update([]))

    def test_the_day_is_the_first_pages(self):
        self.assertEqual(c.report_date(FIRST), dt.date(2026, 3, 13))
        self.assertEqual(c.report_date("Large Load Interconnection Status Update Large Load Integration Team May 28, 2025"), dt.date(2025, 5, 28))
        self.assertIsNone(c.report_date("Large Load Interconnection Status Update"))
        self.assertIsNone(c.report_date("February 30, 2026"))

    def test_rows_are_dated_by_the_report_and_keep_the_month_as_written(self):
        docs = [("https://www.ercot.com/files/docs/2026/03/12/March-TAC-Report.pdf", "March-TAC-Report.pdf", [FIRST, BODY, BODY2]),
                ("https://www.ercot.com/files/docs/2026/03/25/x.zip#March TAC Report.pdf", "March TAC Report.pdf", [FIRST, BODY, BODY2])]   # the same report, in a zip
        rows, notes = c.rows_of(docs, "2026-10-04T00:00:00Z")
        self.assertEqual(len(rows), 3)                             # one row a figure, the report counted once
        self.assertEqual(notes, [])
        r = {x["variable"]: x for x in rows}
        self.assertEqual(r["observed_nonsimultaneous_peak_mw"]["ts_utc"], "2026-03-13T00:00:00Z")     # the report's day, not "March 2025"
        self.assertEqual(r["observed_nonsimultaneous_peak_mw"]["x_month_as_written"], "March 2025")
        self.assertEqual(r["approved_to_energize_mw"]["source_url"], docs[0][0])
        self.assertEqual(r["approved_to_energize_mw"]["vintage"], "2026-03-13T00:00:00Z")
        # the same day stated with another value in a second file is said, and the first kept
        rows, notes = c.rows_of([docs[0], (docs[1][0], docs[1][1], [FIRST, BODY.replace("9042", "9100"), BODY2])], "2026-10-04T00:00:00Z")
        self.assertEqual(len(rows), 3)
        self.assertTrue(any("the first is kept" in n for n in notes))

    def test_links_and_meetings(self):
        html = ('<a href="/calendar/03132026-LLWG-Meeting">Mar 13</a> <a href="https://www.ercot.com/calendar/12172026-LLWG-Meeting">Dec 17</a>'
                '<a href="/calendar/05132026-Special-TAC-Meeting">x</a> <a href="/files/docs/2026/03/12/March-TAC-Report.pdf">March TAC Report</a>'
                '<a href="/files/docs/2026/01/20/16.-Large-Load-Issues.zip">16. Large Load Issues</a> <a href="/files/a.docx">a form</a>')
        self.assertEqual([d for d, _ in c.meetings(html, "20261004")], ["20260313", "20260513"])       # a meeting still to come is not asked for
        self.assertEqual([u.split("/")[-1] for u, _ in c.links(html)], ["March-TAC-Report.pdf", "16.-Large-Load-Issues.zip"])
        self.assertTrue(c.DOC.search("March-TAC-Report.pdf") and c.DOC.search("LLI Queue Status Update - 2025-08-27.pdf"))
        self.assertTrue(c.ZIP.search("16.-Large-Load-Issues.zip") and c.ZIP.search("11.-LLWG-Report.zip"))
        self.assertFalse(c.ZIP.search("13.-ERCOT-Reports.zip"))

    def test_the_ceiling_the_license_and_the_pause(self):
        code = src("warehouse", "connectors", "ercot_large_load_status.py")
        self.assertEqual(c.CEILING, 20_000)
        self.assertIn("if len(rows) > CEILING:", code)
        self.assertIn('if ip.paused("ercot"):', code)                # every connector asks first (session 89)
        self.assertIn("raw data provided in public portions of this website may be used", code)
        self.assertIn("The ERW does not read a number off a picture", code)


class TheTableAndTheCopy(unittest.TestCase):
    @unittest.skipUnless(os.path.exists(os.path.join(OUT, c.NAME + ".csv")), "ercot_large_load_status is not on this machine")
    def test_the_sites_copy_is_the_table_turned_on_its_side(self):
        path = os.path.join(OUT, c.NAME + ".csv")
        t = pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False)
        self.assertLessEqual(len(t), c.CEILING)
        self.assertTrue(t["source_url"].str.startswith("https://www.ercot.com/").all())
        f = json.loads(src("site", "data", "large_load_status.json"))
        self.assertEqual(f["rows"], len(t))
        self.assertEqual([r["day"] for r in f["reports"]], sorted(set(t["ts_utc"].str[:10])))
        name = {v: k for k, v in snap.FIGURES.items()}
        n = 0
        for r in f["reports"]:
            for k in ("approved", "nonsimultaneous", "simultaneous", "new_count", "new_mw"):
                row = t[(t["ts_utc"].str[:10] == r["day"]) & (t["variable"] == name[k])]
                self.assertEqual(k in r, len(row) == 1, (r["day"], k))
                if k in r:
                    self.assertEqual(r[k], float(row["value"].iloc[0]))
                    n += 1
        self.assertEqual(n, len(t))

    def test_the_pages_sentence_and_what_it_flags(self):
        out = node("const m = await import('./lib/largeload.ts'); const f = JSON.parse((await import('node:fs')).default.readFileSync('data/large_load_status.json', 'utf-8'));"
                   "console.log(JSON.stringify({ s: m.summary(f), odd: m.impossible(f).map((r) => r.day), wrong: f.reports.filter(m.monthMismatch).map((r) => r.day), span: m.span(f),"
                   " none: m.summary({ ...f, reports: [] }),"
                   " fac: m.facilityCounts([{ name: 'a', operator: null, status: 'planned', capacity_mw: 300, state: 'TX', kind: 'news', country: 'US' }, { name: 'b', operator: 'x', status: '', capacity_mw: null, state: 'VA', kind: 'operator', country: '' }]) }));")
        f = json.loads(src("site", "data", "large_load_status.json"))
        last, first = out["span"]["last"], out["span"]["first"]
        self.assertEqual((first["day"], last["day"]), (f["reports"][0]["day"], f["reports"][-1]["day"]))
        self.assertIn(f"{round(last['approved']):,} MW of large load had its approval to energize", out["s"])
        self.assertIn(f"{round(last['nonsimultaneous']):,} MW of it running", out["s"])
        self.assertIsNone(out["none"])
        self.assertEqual(out["odd"], ["2025-08-27"])                 # the one report whose two peaks cannot both be right
        self.assertEqual(out["wrong"], ["2026-01-21", "2026-02-25", "2026-03-13"])   # months written as 2025 in reports of 2026
        # session 166 (the owner's instruction of 8 October 2026, part F): the counts say how many rows are US and how many state no country
        self.assertEqual(out["fac"], {"all": 2, "us": 1, "noCountry": 1, "texas": 1, "withMw": 1, "mw": 300, "texasWithMw": 1, "texasMw": 300, "byKind": {"news": 1, "operator": 1}})


class ThePage(unittest.TestCase):
    def test_two_sections_never_added_and_a_request_is_not_a_facility(self):
        page = src("site", "app", "datacenters", "v2", "page.tsx")
        for piece in ("ToolPage", "ToolHeader", "HeadlineRow", "ToolSection", "ChartFrame", "ToolTable", "Fold", "SourceLine"):
            self.assertIn(f"<{piece}", page)
        self.assertIn("A request is not a built facility", page)
        self.assertIn("Load requested is not held", page)
        self.assertIn("does not read a number off a picture", page)
        self.assertIn("The two are not added", page)
        self.assertIn('title="ERCOT: large load approved and energized, over time"', page)
        self.assertIn('title="Beside it: the facilities the ERW holds"', page)
        self.assertIn("so no number is shown", page)
        self.assertRegex(src("site", "lib", "release.ts"), r'"/datacenters/v2":\s*"review"')
        r = subprocess.run(["git", "log", "--format=%s", "-1", "--", "site/app/datacenters/page.tsx"], cwd=ROOT, capture_output=True, text=True)
        self.assertNotIn("Session 106", r.stdout)

    def test_held_out_of_what_a_visitor_counts(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "supabase"))
        import load
        self.assertIn(c.NAME, load.LIVE["review_hold"])
        self.assertIn(c.SOURCE, load.LIVE["sources_hold"])
        self.assertEqual(load.live_rule(c.NAME), ("full", None))

    def test_no_em_dash(self):
        for rel in ("warehouse/connectors/ercot_large_load_status.py", "warehouse/derived/large_load_snapshot.py", "site/lib/largeload.ts",
                    "site/app/datacenters/v2/page.tsx", "docs/methods/ercot_large_load_status.md"):
            self.assertNotIn(chr(0x2014), src(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()
