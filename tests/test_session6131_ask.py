"""Session 6131 (chain 281): a period outside a table's own span is said to be one, in both loops.

Energy Research Warehouse (ERW).

The new tables' ch09 (14 November 2026): asked how many changes to utilities' large-load rules the warehouse holds for
March 2026, the chat answered "0 rule changes dated March 2026 ... its first change is dated 2026-08-18". Honest, and a
period the table does not cover is not a count of zero: rule 3 asks for "not in the warehouse". A series bounded by a
start and an end has said whether its window is whole since session 5267; a table of events or things, which has no step
to count by, said only "no rows match these filters". Its result now carries `span` when the period asked lies wholly
outside the table's own first and last date.

No model, no network.
"""
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat"))
import window as W  # noqa: E402


def sec(iso):
    return None if iso is None else int(dt.datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc).timestamp())


FIRST, LAST = "2026-08-18T00:00:00Z", "2026-11-13T00:00:00Z"
CASES = [("march", "2026-03-01T00:00:00Z", "2026-04-01T00:00:00Z"), ("october", "2026-10-01T00:00:00Z", "2026-11-01T00:00:00Z"),
         ("across_the_first_day", "2026-08-01T00:00:00Z", "2026-09-01T00:00:00Z"), ("ends_on_the_first_day", "2026-08-01T00:00:00Z", "2026-08-18T00:00:00Z"),
         ("starts_on_the_last_day", "2026-11-13T00:00:00Z", "2026-12-01T00:00:00Z"), ("after", "2026-11-14T00:00:00Z", "2027-01-01T00:00:00Z"),
         ("open_start_before", None, "2026-01-01T00:00:00Z"), ("open_end_after", "2027-01-01T00:00:00Z", None), ("open_end_inside", "2026-09-01T00:00:00Z", None),
         ("no_bound", None, None)]
OUTSIDE = {"march", "ends_on_the_first_day", "after", "open_start_before", "open_end_after"}


def python_side():
    return {name: W.span_outside(sec(a), sec(b), sec(FIRST), sec(LAST)) for name, a, b in CASES}


class APeriodOutsideTheSpan(unittest.TestCase):
    def test_each_case(self):
        got = python_side()
        for name, _, _ in CASES:
            if name in OUTSIDE:
                self.assertEqual(got[name], {"first": FIRST, "last": LAST, "outside": True, "note": W.SPAN_OUTSIDE}, name)
            else:
                self.assertIsNone(got[name], name)

    def test_a_span_that_cannot_be_read_gives_nothing(self):
        self.assertIsNone(W.span_outside(sec("2026-03-01T00:00:00Z"), sec("2026-04-01T00:00:00Z"), None, sec(LAST)))
        self.assertIsNone(W.span_outside(sec("2026-03-01T00:00:00Z"), sec("2026-04-01T00:00:00Z"), sec(LAST), sec(FIRST)))

    def test_the_note_says_how_to_answer(self):
        self.assertIn("is not a count of zero. Answer with not_in_warehouse true", W.SPAN_OUTSIDE)
        self.assertIn("state no count for it", W.SPAN_OUTSIDE)

    def test_the_query_tool_uses_it_for_events_and_things_only(self):
        py = open(os.path.join(ROOT, "warehouse", "chat", "tools.py"), encoding="utf-8").read()
        self.assertIn('if shape != "series" and (start or end) and tcol in df and df[tcol].notna().any():', py)
        self.assertIn('out["span"] = s', py)

    def test_the_site_returns_the_same(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        r = subprocess.run([exe, "scripts/test-ask-6131.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stdout[-1500:] + r.stderr[-1500:])
        site = json.loads(next(x for x in r.stdout.splitlines() if x.startswith("{")))
        self.assertEqual(site["got"], python_side())
        self.assertEqual(site["note"], W.SPAN_OUTSIDE)


if __name__ == "__main__":
    unittest.main()
