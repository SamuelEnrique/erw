"""Session 11407 (chain 770, part C), carried over from wip/audit-conditions-3 (session 10219, the conditions audit of
26 November, finding 3). The alerts heading of /conditions counted rows of the alerts list, and a row is one notice,
region and day it covers, with each reissue of a CAISO notice listed again. On this branch the page lists and counts one
row a notice (byNotice in site/app/conditions/page.tsx): a notice is its kind, start and end; one whose start the source
does not print is its kind and day. CAISO's August 2020 heat wave's "(79)" becomes "(24 notices)" (the audit's 23
merged the Stage 3 rotating outages of 14 and 15 August, which have no start in the file). No site file changes.
"""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "conditions")
PAGE = os.path.join(ROOT, "site", "app", "conditions", "page.tsx")


def load(op):
    with open(os.path.join(DIR, op + ".json"), encoding="utf-8") as fh:
        return json.load(fh)


def page():
    with open(PAGE, encoding="utf-8") as fh:
        return fh.read()


def key(a):
    """byNotice's key, restated: kind, start, end; kind and day when no start is printed."""
    return (a[1], a[2], a[3] or "") if a[2] else (a[1], "day " + a[0])


def by_notice(rows):
    seen, out = set(), []
    for a in rows:
        if key(a) not in seen:
            seen.add(key(a))
            out.append(a)
    return out


def window(f, wid):
    w = [x for x in f["windows"] if x["id"] == wid][0]
    return [a for a in f["alerts"] if w["start"] <= a[0] <= w["end"]]


class ThePageCountsNotices(unittest.TestCase):
    def test_the_page_counts_the_windows_notices(self):
        s = page()
        self.assertIn("const alerts = byNotice(f.alerts.filter((a) => a[0] >= w.start && a[0] <= w.end));", s)
        self.assertIn("const k = a[2] ? `${a[1]}|${a[2]}|${a[3] ?? \"\"}` : `${a[1]}|day ${a[0]}`;", s)
        self.assertIn('({alerts.length} {alerts.length === 1 ? "notice" : "notices"})', s)
        self.assertIn("One row a notice:", s)
        self.assertIsNone(re.search(r"\(\{alerts\.length\}\)", s), "no heading counts rows any more")

    def test_the_method_note_says_so(self):
        with open(os.path.join(ROOT, "docs", "methods", "grid_conditions.md"), encoding="utf-8") as fh:
            self.assertIn("8. **Alerts by notice.**", fh.read())


@unittest.skipUnless(os.path.exists(os.path.join(DIR, "caiso.json")), "the conditions files are not in this checkout")
class TheFiguresMove(unittest.TestCase):
    def test_the_heat_wave_of_2020_is_79_rows_and_24_notices(self):
        rows = window(load("caiso"), "caiso_heat_2020")
        self.assertEqual(len(rows), 79)
        self.assertEqual(len(by_notice(rows)), 24)
        # the reissues of one notice on one day are one row now
        day = [a for a in by_notice(rows) if a[0] == "2020-08-14" and a[1] == "RMO"]
        self.assertEqual(len(day), 1)
        # the two Stage 3 rotating outages with no start printed stay two
        self.assertEqual(len([a for a in by_notice(rows) if a[1] == "Stage 3"]), 2)

    def test_uri_in_california_is_3_notices(self):
        self.assertEqual(len(by_notice(window(load("caiso"), "uri_2021"))), 3)

    def test_ercot_heat_2023_is_15_notices(self):
        rows = window(load("ercot"), "ercot_heat_2023")
        self.assertEqual((len(rows), len(by_notice(rows))), (23, 15))


if __name__ == "__main__":
    unittest.main()
