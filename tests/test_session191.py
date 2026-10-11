"""Session 191: the scanner's repeat guard follows a derived table's lineage (version 1.1.0).

The first run raised Indiana's other gases (eia_state_generation_monthly) and Indiana's oil and other gases (the sum
in state_generation_mix_monthly that holds it) as two record lows of the same month: the repeat guard asked for the
same value, and a sum is another number. A flag is now also a repeat when a table its own table is derived from (its
header line "# Derived from:") has a flag of the same rule, date and direction in the same place. Made-up tables in a
temporary folder; no request, no model call.
"""

import csv
import datetime as dt
import os
import shutil
import sys
import tempfile
import unittest

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FINDINGS = os.path.join(ROOT, "warehouse", "analysis", "findings")
if FINDINGS not in sys.path:
    sys.path.insert(0, FINDINGS)
import findings_scanner as scanner  # noqa: E402

SCAN_DATE = "2026-10-10"
LAST = dt.date(2026, 10, 7)
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url", "retrieved_at", "vintage"]
OWN = [("warehouse", "analysis", "findings", "findings_scanner.py"), ("warehouse", "config", "scanner.yaml"),
       ("docs", "methods", "automated_analysis_scanner.md"), ("tests", "test_session191.py")]


def series(entity, add=0.0, geo="US-IN", last_value=150.0, n=1300, last=LAST, seed=1):
    """A daily series that waves around 100 and ends on a record high; `add` makes it a sum that holds the first."""
    r = np.random.RandomState(seed)
    v = 100.0 + 5.0 * np.sin(np.arange(n) / 9.0) + r.uniform(-1, 1, n) + add
    v[-1] = last_value + add
    days = [last - dt.timedelta(days=n - 1 - i) for i in range(n)]
    return [[entity, "level", f"{d.isoformat()}T00:00:00Z", repr(float(x)), "MWh", "P1D", geo, "", "", "test:source", "", "2026-10-09T00:00:00Z", ""] for d, x in zip(days, v)]


class World:
    def __init__(self):
        self.dir = tempfile.mkdtemp(prefix="erw191_")
        self.out, self.meta = os.path.join(self.dir, "output"), os.path.join(self.dir, "metadata")
        os.makedirs(self.out)
        os.makedirs(self.meta)
        self.cov = []

    def table(self, name, rows, tier="source", derived_from=None):
        with open(os.path.join(self.out, name + ".csv"), "w", encoding="utf-8", newline="") as f:
            f.write("# a made-up table for tests/test_session191.py\n")
            if derived_from:
                f.write(f"# Derived from: {derived_from}\n")
            w = csv.writer(f, lineterminator="\n")
            w.writerow(COLS)
            w.writerows(rows)
        self.cov.append([name, "public", "P1D", tier])

    def scan(self, **over):
        for name, head, rows in (("coverage.csv", ["table", "license", "interval", "tier"], self.cov), ("known_gaps.csv", ["table", "reason"], []),
                                 ("paused_sources.csv", ["scope", "match"], [])):
            with open(os.path.join(self.meta, name), "w", encoding="utf-8", newline="") as f:
                w = csv.writer(f, lineterminator="\n")
                w.writerow(head)
                w.writerows(rows)
        cfg = scanner.load_config()
        cfg.update(over)
        return scanner.scan(self.out, cfg, SCAN_DATE, self.meta, log=lambda m: None)

    def close(self):
        shutil.rmtree(self.dir, ignore_errors=True)


def records(flags):
    return sorted((f["table"], f["series"]["entity"]) for f in flags if f["rule"] == "record")


class TheRepeatFollowsLineage(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.close()

    def test_a_sum_that_holds_the_flagged_series_is_one_flag_kept_in_the_source(self):
        self.w.table("made_up_fuels", series("t:IN:OOG"))
        self.w.table("made_up_mix", series("t:IN", add=40.0), tier="derived", derived_from="made_up_fuels")
        flags, _, drafts, summary = self.w.scan()
        self.assertEqual(records(flags), [("made_up_fuels", "t:IN:OOG")])
        rep = [r for r in summary["repeats_by_lineage"] if r["rule"] == "record"]      # the sum's record: another value, so the older guard did not see it
        self.assertEqual([(r["table"], r["repeat_of_table"], r["rule"], r["date"]) for r in rep], [("made_up_mix", "made_up_fuels", "record", LAST.isoformat())])
        kept = next(f for f in flags if f["rule"] == "record")
        self.assertEqual(rep[0]["repeat_of"], kept["id"])
        self.assertAlmostEqual(rep[0]["value"] - kept["value"], 40.0)
        self.assertTrue(rep[0]["id"].startswith("scan-record-"))
        self.assertNotIn(rep[0]["id"], {d["id"] for d in drafts})

    def test_without_the_lineage_line_both_stand(self):
        self.w.table("made_up_fuels", series("t:IN:OOG"))
        self.w.table("made_up_mix", series("t:IN", add=40.0), tier="derived")
        flags, _, _, summary = self.w.scan()
        self.assertEqual(records(flags), [("made_up_fuels", "t:IN:OOG"), ("made_up_mix", "t:IN")])
        self.assertEqual(summary["repeats_by_lineage"], [])

    def test_another_place_another_day_or_another_direction_is_not_a_repeat(self):
        self.w.table("made_up_fuels", series("t:IN:OOG"))
        self.w.table("made_up_mix", series("t:OH", add=40.0, geo="US-OH"), tier="derived", derived_from="made_up_fuels")
        self.w.table("made_up_late", series("t:IN:late", add=40.0, last=LAST - dt.timedelta(days=1)) + series("t:IN:late", add=40.0, n=1, last_value=100.0),
                     tier="derived", derived_from="made_up_fuels")
        self.w.table("made_up_low", series("t:IN:low", add=40.0, last_value=20.0), tier="derived", derived_from="made_up_fuels")
        flags, _, _, summary = self.w.scan()
        got = {(f["table"], f["date"], f["direction"]) for f in flags if f["rule"] == "record"}
        self.assertEqual(got, {("made_up_fuels", LAST.isoformat(), "high"), ("made_up_mix", LAST.isoformat(), "high"),
                               ("made_up_late", (LAST - dt.timedelta(days=1)).isoformat(), "high"), ("made_up_low", LAST.isoformat(), "low")})
        self.assertEqual([r for r in summary["repeats_by_lineage"] if r["rule"] == "record"], [])

    def test_a_series_without_one_place_is_never_dropped(self):
        self.w.table("made_up_fuels", series("t:IN:OOG", geo=""))
        self.w.table("made_up_mix", series("t:IN", add=40.0, geo=""), tier="derived", derived_from="made_up_fuels")
        flags, _, _, summary = self.w.scan()
        self.assertEqual(len(records(flags)), 2)
        self.assertEqual(summary["repeats_by_lineage"], [])

    def test_the_lineage_is_followed_through_a_table_between(self):
        self.w.table("made_up_fuels", series("t:IN:OOG"))
        self.w.table("made_up_between", series("t:IN:quiet", last_value=100.0), tier="derived", derived_from="made_up_fuels")
        self.w.table("made_up_page", series("t:IN:page", add=7.0), tier="derived", derived_from="made_up_between; made_up_other, made_up_page")
        flags, _, _, summary = self.w.scan()
        self.assertEqual(records(flags), [("made_up_fuels", "t:IN:OOG")])
        self.assertEqual([r["table"] for r in summary["repeats_by_lineage"]], ["made_up_page"])
        self.assertEqual(scanner.ancestors("made_up_page", self.w.out, {}), {"made_up_between", "made_up_other", "made_up_fuels"})
        self.assertEqual(scanner.derived_from("made_up_absent", self.w.out), set())

    def test_the_key_switches_it_off(self):
        self.w.table("made_up_fuels", series("t:IN:OOG"))
        self.w.table("made_up_mix", series("t:IN", add=40.0), tier="derived", derived_from="made_up_fuels")
        flags, _, _, summary = self.w.scan(repeat_follows_lineage=False)
        self.assertEqual(len(records(flags)), 2)
        self.assertEqual(summary["repeats_by_lineage"], [])

    def test_the_same_value_in_two_tables_is_still_one_flag(self):
        self.w.table("made_up_fuels", series("a:x"))
        self.w.table("made_up_copy", series("b:x"), tier="derived")
        flags, _, _, summary = self.w.scan()
        self.assertEqual({f["table"] for f in flags}, {"made_up_fuels"})
        self.assertEqual(summary["repeats_of_a_source_table"], len(flags))


class TheVersionAndTheText(unittest.TestCase):
    def read(self, *parts):
        with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
            return f.read()

    def test_the_version_was_raised_with_the_rule(self):
        cfg = scanner.load_config()
        self.assertEqual(str(cfg["version"]), "1.1.0")
        self.assertIs(cfg["repeat_follows_lineage"], True)

    def test_no_threshold_number_changed(self):
        cfg = scanner.load_config()
        self.assertEqual((cfg["record_min_margin_sigmas"], cfg["spike_multiple"], cfg["spike_percentile"], cfg["weekly_min_excess_share"], cfg["pair_break_sigmas"]),
                         (0.5, 2.0, 99, 0.10, 5.0))
        self.assertEqual(cfg["fresh_days"], {"daily": 10, "weekly": 21, "monthly": 130, "yearly": 120})
        self.assertEqual(cfg["record_stood_points"], {"daily": 365, "weekly": 52, "monthly": 24, "yearly": 5})

    def test_a_flag_stores_its_place(self):
        w = World()
        try:
            w.table("made_up_fuels", series("t:IN:OOG"))
            flags, _, drafts, _ = w.scan()
        finally:
            w.close()
        self.assertEqual({f["geo"] for f in flags}, {"US-IN"})
        self.assertEqual(drafts[0]["flag"]["geo"], "US-IN")
        self.assertEqual(drafts[0]["scanner_version"], "1.1.0")

    def test_the_method_note_says_what_the_review_found(self):
        note = self.read("docs", "methods", "automated_analysis_scanner.md")
        for needle in ("`repeat_follows_lineage`", "# Derived from:", "The review of the first run (session 191)", "one customer", "1.1.0"):
            self.assertIn(needle, note)

    def test_no_em_dash_in_this_sessions_files(self):
        for parts in OWN:
            self.assertNotIn(chr(0x2014), self.read(*parts), parts)


if __name__ == "__main__":
    unittest.main()
